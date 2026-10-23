"""Materiale per il report giornaliero: cosa è arrivato oggi.

Uso:
  python scripts/daily.py --papers data/papers.sqlite --daily data/daily.sqlite \
      --topics data/emerging_topics.meta.json --trends data/trends.json [--date YYYY-MM-DD] [--chunks 3000]

Ogni file è facoltativo: le sezioni senza dati restano vuote.
"Nuovo oggi" = record visto per la prima volta nella data indicata (UTC, default oggi).
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from emerging import TECH_FIELDS, suspicious  # noqa: E402
import verticals  # noqa: E402

RECENT_DAYS = 60
FIRST_EDITION = date(2026, 10, 22)   # N. 1 della newsletter
CLUSTERS = {
    "S1": "IA agentica e multi-agente", "S2": "Fiducia e governance dell'IA", "S3": "Cybersecurity con IA",
    "S4": "IA efficiente e locale", "S5": "Affidabilità del software", "S6": "Robotica ed embodied AI",
    "S7": "IA multimodale e documenti", "S8": "Ricerca e gestione della conoscenza", "S9": "IA per la scienza",
    "S10": "Calcolo quantistico",
}
# Depositi senza revisione o senza rivista: restano in coda alla selezione.
REPOSITORY_DOI_PREFIXES = ("10.5281/", "10.6084/", "10.13140/")   # Zenodo, Figshare, ResearchGate
REPOSITORY_VENUES = ("zenodo", "figshare", "researchgate")


def penalty(d: dict) -> int:
    """0 = rivista o server di preprint riconosciuto in inglese; 1 = altra lingua; 2 = deposito o senza sede."""
    venue = (d.get("venue") or "").lower()
    doi = (d.get("doi") or "").lower()
    if not venue or any(v in venue for v in REPOSITORY_VENUES) or doi.startswith(REPOSITORY_DOI_PREFIXES):
        return 2
    lang = d.get("language")
    return 1 if lang and lang != "en" else 0


def rank_recent(items: list[dict]) -> list[dict]:
    """Prima le sedi migliori, poi i paper con abstract (servono per i takeaway), poi dal più recente."""
    items = sorted(items, key=lambda d: d.get("published_date") or "", reverse=True)
    return sorted(items, key=lambda d: (penalty(d), 0 if d.get("abstract") else 1))


def kind(d: dict) -> str:
    """Etichetta leggibile: rivista, conferenza, preprint (non revisionato) o altro."""
    st, t = (d.get("source_type") or "").lower(), (d.get("type") or "").lower()
    if t == "preprint" or st == "repository":
        return "preprint"
    if st == "journal":
        return "review in rivista" if t == "review" else "rivista"
    if st == "conference":
        return "conferenza"
    return "altro"


def paper(d: dict, chars: int) -> dict:
    abstract = d.get("abstract") or ""
    return {"titolo": d.get("title"), "data": d.get("published_date"), "citazioni": d.get("cited_by_count"),
            "venue": d.get("venue"), "lingua": d.get("language"), "autori": (d.get("authors") or [])[:4], "paesi": d.get("countries") or [],
            "link": d.get("landing_page_url") or (f"https://doi.org/{d['doi']}" if d.get("doi") else None),
            "tipo": kind(d), "pdf_gratuito": d.get("oa_url") or d.get("pdf_url"),
            "estratto": abstract[:chars] + ("…" if len(abstract) > chars else "")}


def new_today(conn, source: str, day: str) -> list[dict]:
    rows = conn.execute("SELECT data FROM records WHERE source=? AND substr(first_seen_at,1,10)=?",
                        (source, day)).fetchall()
    return [json.loads(r[0]) for r in rows]


def llm_section(db: Path, day: str, top: int, chars: int) -> dict:
    conn = sqlite3.connect(db)
    new = new_today(conn, "openalex_llm", day)
    # Prima i paper usciti negli ultimi RECENT_DAYS giorni (dal più recente), poi gli altri per citazioni:
    # così il primo giorno o un recupero di storico non riempiono il report di paper vecchi.
    cutoff = (date.fromisoformat(day) - timedelta(days=RECENT_DAYS)).isoformat()
    # le date future (metadati errati di alcune fonti) restano fuori dalla selezione
    recent = rank_recent([d for d in new if cutoff <= (d.get("published_date") or "") <= day])
    older = sorted((d for d in new if (d.get("published_date") or "") < cutoff),
                   key=lambda d: d.get("cited_by_count") or 0, reverse=True)
    new = recent + older
    last = conn.execute("SELECT status, finished_at, fetched, inserted, updated, requests FROM runs "
                        "WHERE source='openalex_llm' ORDER BY id DESC LIMIT 1").fetchone()
    total = conn.execute("SELECT count(*) FROM records WHERE source='openalex_llm'").fetchone()[0]
    return {"nuovi_oggi": len(new), "recenti_tra_i_nuovi": len(recent), "totale": total,
            "ultima_raccolta": dict(zip(("stato", "fine", "letti", "nuovi", "aggiornati", "richieste"), last)) if last else None,
            "selezione": [paper(d, chars) for d in new[:top]]}


def emerging_section(db: Path, topics: list[dict], day: str, per_topic: int, chars: int,
                     source: str = "daily_emerging") -> dict:
    conn = sqlite3.connect(db)
    new = new_today(conn, source, day)
    by_topic: dict[str, list[dict]] = {}
    for d in new:
        by_topic.setdefault(d.get("primary_topic_id"), []).append(d)
    out = []
    for t in topics:
        items = rank_recent(by_topic.get(t["id"], []))
        if items:
            out.append({"tema": t["tema"], "verticale": t.get("verticale"),
                        "categoria": t.get("categoria"), "disciplina": t.get("disciplina"),
                        "peso_3_anni": t.get("crescita_3a"), "paper_ultimo_anno": t.get("paper_ultimo_anno"),
                        "nuovi_oggi": len(items), "paper": [paper(d, chars) for d in items[:per_topic]]})
    out.sort(key=lambda x: -x["nuovi_oggi"])
    return {"temi_seguiti": len(topics), "nuovi_oggi": len(new), "per_tema": out}


def _prev_year_period(period: str) -> str:
    year, q = period.split("-")
    return f"{int(year) - 1}-{q}"


def adoption_section(db: Path) -> dict:
    """Per cluster: ultimo trimestre chiuso rispetto allo stesso trimestre dell'anno prima,
    per GitHub (nuovi repository) e Hacker News (storie), anche normalizzato sul controllo BASE."""
    conn = sqlite3.connect(db)
    out = {"aggiornato_il": conn.execute("SELECT max(last_seen_at) FROM records").fetchone()[0], "fonti": {}}
    for source in ("github_repos", "hn_stories"):
        sums = defaultdict(lambda: defaultdict(int))
        closed = set()
        for (d,) in conn.execute("SELECT data FROM records WHERE source=?", (source,)):
            r = json.loads(d)
            if r.get("count") is None:
                continue
            sums[r["cluster"]][r["period"]] += int(r["count"])
            if not r.get("partial"):
                closed.add(r["period"])
        if not closed:
            continue
        last = max(closed)
        prev = _prev_year_period(last)
        yoy = {c: (v[last] / v[prev] - 1) if v.get(prev) else None for c, v in sums.items()}
        base = yoy.get("BASE")
        rows = []
        for c, g in sorted(yoy.items()):
            if c == "BASE":
                continue
            rel = (1 + g) / (1 + base) - 1 if g is not None and base is not None and base > -1 else None
            rows.append({"cluster": c, "area": CLUSTERS.get(c, c), "ultimo_trimestre": sums[c][last],
                         "anno_su_anno": round(g, 3) if g is not None else None,
                         "rispetto_al_controllo": round(rel, 3) if rel is not None else None})
        out["fonti"][source] = {"trimestre": last, "confronto_con": prev,
                                "controllo_anno_su_anno": round(base, 3) if base is not None else None, "aree": rows}
    return out


def trend_section(trends: dict, top: int) -> dict:
    tech = [t for t in trends["topics"] if t["disciplina"] in TECH_FIELDS and not suspicious(t)]
    pick = lambda cat: [{"tema": t["tema"], "disciplina": t["disciplina"], "crescita_3a": t["crescita_3a"],
                         "crescita_ytd": t.get("crescita_ytd")}
                        for t in sorted((t for t in tech if t["categoria"] == cat),
                                        key=lambda t: -(t["crescita_3a"] or 0))[:top]]
    return {"calcolato_il": trends.get("generated_at"), "emergenti": pick("emergente"),
            "forte_crescita": pick("forte crescita"), "in_calo": [
                {"tema": t["tema"], "crescita_3a": t["crescita_3a"]}
                for t in sorted((t for t in tech if t["categoria"] == "in calo" and t[f"n{trends['years'][-1]}"] >= 200),
                                key=lambda t: t["crescita_3a"] or 0)[:top]]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--papers")
    ap.add_argument("--daily")
    ap.add_argument("--topics")
    ap.add_argument("--trends")
    ap.add_argument("--vertical-topics", help="temi del verticale del giorno (scripts/verticals.py --meta)")
    ap.add_argument("--signals", help="free_signals.sqlite (GitHub, Hacker News)")
    ap.add_argument("--verticals", default=str(Path(__file__).resolve().parent.parent / "config" / "verticals.yaml"),
                    help="verticali del radar del giorno")
    ap.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    ap.add_argument("--llm-top", type=int, default=12)
    ap.add_argument("--per-topic", type=int, default=3)
    ap.add_argument("--abstract-chars", type=int, default=1500, help="abstract quasi interi: servono per i takeaway")
    ap.add_argument("-o", "--out")
    ap.add_argument("--chunks", type=int, default=0)
    args = ap.parse_args()

    exists = lambda p: p and Path(p).exists()
    topics = json.loads(Path(args.topics).read_text(encoding="utf-8")) if exists(args.topics) else []
    trends = json.loads(Path(args.trends).read_text(encoding="utf-8")) if exists(args.trends) else None
    result = {
        "data": args.date,
        "edizione": (date.fromisoformat(args.date) - FIRST_EDITION).days + 1,
        "llm": llm_section(Path(args.papers), args.date, args.llm_top, args.abstract_chars) if exists(args.papers) else None,
        "emergenti": emerging_section(Path(args.daily), topics, args.date, args.per_topic, args.abstract_chars)
        if exists(args.daily) else None,
        "paper_verticale": emerging_section(Path(args.daily),
                                            json.loads(Path(args.vertical_topics).read_text(encoding="utf-8")),
                                            args.date, args.per_topic, args.abstract_chars, source="daily_vertical")
        if exists(args.daily) and exists(args.vertical_topics) else None,
        "trend": trend_section(trends, 8) if trends else None,
        "adozione": adoption_section(Path(args.signals)) if exists(args.signals) else None,
        "radar_del_giorno": verticals.radar(date.fromisoformat(args.date), verticals.load_config(Path(args.verticals)),
                                            trends, Path(args.signals) if exists(args.signals) else None)
        if exists(args.verticals) else None,
    }
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    if args.chunks:
        for i in range(0, len(text), args.chunks):
            print(f"DAILY|{i // args.chunks:04d}|{text[i:i + args.chunks]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
