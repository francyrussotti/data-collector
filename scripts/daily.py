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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from emerging import TECH_FIELDS, suspicious  # noqa: E402

RECENT_DAYS = 60
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


def paper(d: dict, chars: int) -> dict:
    abstract = d.get("abstract") or ""
    return {"titolo": d.get("title"), "data": d.get("published_date"), "citazioni": d.get("cited_by_count"),
            "venue": d.get("venue"), "lingua": d.get("language"), "autori": (d.get("authors") or [])[:4], "paesi": d.get("countries") or [],
            "link": d.get("landing_page_url") or (f"https://doi.org/{d['doi']}" if d.get("doi") else None),
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


def emerging_section(db: Path, topics: list[dict], day: str, per_topic: int, chars: int) -> dict:
    conn = sqlite3.connect(db)
    new = new_today(conn, "daily_emerging", day)
    by_topic: dict[str, list[dict]] = {}
    for d in new:
        by_topic.setdefault(d.get("primary_topic_id"), []).append(d)
    out = []
    for t in topics:
        items = rank_recent(by_topic.get(t["id"], []))
        if items:
            out.append({"tema": t["tema"], "categoria": t.get("categoria"), "disciplina": t.get("disciplina"),
                        "nuovi_oggi": len(items), "paper": [paper(d, chars) for d in items[:per_topic]]})
    out.sort(key=lambda x: -x["nuovi_oggi"])
    return {"temi_seguiti": len(topics), "nuovi_oggi": len(new), "per_tema": out}


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
    ap.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    ap.add_argument("--llm-top", type=int, default=12)
    ap.add_argument("--per-topic", type=int, default=3)
    ap.add_argument("--abstract-chars", type=int, default=1500, help="abstract quasi interi: servono per i takeaway")
    ap.add_argument("-o", "--out")
    ap.add_argument("--chunks", type=int, default=0)
    args = ap.parse_args()

    exists = lambda p: p and Path(p).exists()
    topics = json.loads(Path(args.topics).read_text(encoding="utf-8")) if exists(args.topics) else []
    result = {
        "data": args.date,
        "llm": llm_section(Path(args.papers), args.date, args.llm_top, args.abstract_chars) if exists(args.papers) else None,
        "emergenti": emerging_section(Path(args.daily), topics, args.date, args.per_topic, args.abstract_chars)
        if exists(args.daily) else None,
        "trend": trend_section(json.loads(Path(args.trends).read_text(encoding="utf-8")), 8) if exists(args.trends) else None,
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
