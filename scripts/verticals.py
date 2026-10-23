"""Radar del giorno per verticale (aerospazio, energia, LLM, cybersecurity, robotica).

Usa config/verticals.yaml, trends.json (ricerca e finanziamenti) e free_signals.sqlite (adozione).
Ogni giorno feriale ha un verticale; nel weekend una panoramica di tutti.
"""
from __future__ import annotations

import json
import re
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

MIN_PAPERS = 200   # temi più piccoli: crescite poco affidabili


def load_config(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def match_topics(topics: list[dict], spec: dict) -> list[dict]:
    subs = set(spec.get("sottocampi") or [])
    rx = re.compile(spec["nome_regex"], re.I) if spec.get("nome_regex") else None
    ex = re.compile(spec["escludi"], re.I) if spec.get("escludi") else None
    fields = set(spec.get("discipline") or [])
    out = []
    for t in topics:
        name = t.get("tema") or ""
        if ex and ex.search(name):
            continue
        if t.get("sottocampo") in subs or (rx and rx.search(name) and (not fields or t.get("disciplina") in fields)):
            out.append(t)
    return out


def _r(x, n=3):
    return None if x is None else round(x, n)


def research(trends: dict, spec: dict) -> dict:
    years = trends["years"]
    last, base = years[-1], years[-4]
    topics = match_topics(trends["topics"], spec)
    tot = {str(t["periodo"]): t["paper"] for t in trends.get("totals", [])}
    n_last = sum(t.get(f"n{last}") or 0 for t in topics)
    n_base = sum(t.get(f"n{base}") or 0 for t in topics)
    share_l = n_last / tot[str(last)] if tot.get(str(last)) else None
    share_b = n_base / tot[str(base)] if tot.get(str(base)) else None
    peso = share_l / share_b - 1 if share_l and share_b else None
    ytd = trends.get("ytd_periods") or []
    slancio = None
    if len(ytd) == 2:
        prev = sum(t.get("ytd_prec") or 0 for t in topics)
        cur = sum(t.get("ytd_corr") or 0 for t in topics)
        if prev and tot.get(ytd[0]) and tot.get(ytd[1]):
            slancio = (cur / prev) / (tot[ytd[1]] / tot[ytd[0]]) - 1
    funded = [t for t in topics if t.get(f"finanziati{last}") is not None]
    quota_fin = (sum(t[f"finanziati{last}"] for t in funded) / sum(t.get(f"n{last}") or 0 for t in funded)
                 if funded and sum(t.get(f"n{last}") or 0 for t in funded) else None)
    big = [t for t in topics if (t.get(f"n{last}") or 0) >= MIN_PAPERS and t.get("crescita_3a") is not None]

    def row(t):
        return {"tema": t["tema"], "paper_ultimo_anno": t.get(f"n{last}"), "peso_3_anni": t.get("crescita_3a"),
                "slancio_anno_in_corso": t.get("slancio_ytd"), "categoria": t.get("categoria"),
                "quota_finanziata": t.get("quota_finanziata")}
    return {
        "anno": last, "confronto_con": base, "temi_nel_verticale": len(topics), "paper_ultimo_anno": n_last,
        "peso_3_anni": _r(peso), "slancio_anno_in_corso": _r(slancio), "quota_finanziata": _r(quota_fin),
        "in_crescita": [row(t) for t in sorted(big, key=lambda t: -t["crescita_3a"])[:5]],
        "piu_grandi": [row(t) for t in sorted(topics, key=lambda t: -(t.get(f"n{last}") or 0))[:3]],
        "in_calo": [row(t) for t in sorted((t for t in big if t["crescita_3a"] < -0.2), key=lambda t: t["crescita_3a"])[:3]],
    }


def _prev_year_period(period: str) -> str:
    y, q = period.split("-Q")
    return f"{int(y) - 1}-Q{q}"


def adoption(db: Path, clusters: list[str]) -> dict:
    """Ultimo trimestre chiuso contro lo stesso trimestre dell'anno prima, per query; anche rispetto al controllo."""
    conn = sqlite3.connect(db)
    out = {"aggiornato_il": conn.execute("SELECT max(last_seen_at) FROM records").fetchone()[0], "fonti": {}}
    for source in ("github_repos", "hn_stories"):
        counts = defaultdict(dict)
        meta = {}
        closed = set()
        for (d,) in conn.execute("SELECT data FROM records WHERE source=?", (source,)):
            r = json.loads(d)
            if r.get("count") is None:
                continue
            counts[r["query_id"]][r["period"]] = int(r["count"])
            meta[r["query_id"]] = (r.get("query"), r.get("cluster"))
            if not r.get("partial"):
                closed.add(r["period"])
        if not closed:
            continue
        last = max(closed)
        prev = _prev_year_period(last)
        base_now = sum(c.get(last, 0) for q, c in counts.items() if meta[q][1] == "BASE")
        base_prev = sum(c.get(prev, 0) for q, c in counts.items() if meta[q][1] == "BASE")
        g_base = base_now / base_prev - 1 if base_prev else None
        rows = []
        for q, c in counts.items():
            if meta[q][1] not in clusters or not c.get(prev):
                continue
            g = c.get(last, 0) / c[prev] - 1
            rel = (1 + g) / (1 + g_base) - 1 if g_base is not None and g_base > -1 else None
            rows.append({"query": meta[q][0], "ultimo_trimestre": c.get(last, 0), "anno_su_anno": _r(g),
                         "rispetto_al_controllo": _r(rel)})
        out["fonti"][source] = {"trimestre": last, "confronto_con": prev, "controllo_anno_su_anno": _r(g_base),
                                "query": sorted(rows, key=lambda r: -(r["anno_su_anno"] or -9))}
    conn.close()
    return out


def wiki(db: Path, articles: list[str], today: date) -> list[dict]:
    """Visite degli ultimi 12 mesi completi contro i 12 precedenti."""
    conn = sqlite3.connect(db)
    series = defaultdict(dict)
    current = f"{today.year:04d}{today.month:02d}"
    for (d,) in conn.execute("SELECT data FROM records WHERE source='wiki_pageviews'"):
        r = json.loads(d)
        ym = str(r["timestamp"])[:6]
        if r["article"] in articles and ym < current:
            series[r["article"]][ym] = r["views"]
    conn.close()
    out = []
    for a in articles:
        months = sorted(series.get(a, {}))
        if len(months) < 24:
            out.append({"voce": a, "visite_12_mesi": sum(series.get(a, {}).get(m, 0) for m in months[-12:]) or None,
                        "variazione": None, "nota": "storico inferiore a 24 mesi"})
            continue
        now = sum(series[a][m] for m in months[-12:])
        before = sum(series[a][m] for m in months[-24:-12])
        out.append({"voce": a, "visite_12_mesi": now, "variazione": _r(now / before - 1) if before else None})
    return out


def radar(day: date, cfg: dict, trends: dict | None, signals_db: Path | None) -> dict:
    key = cfg["giorni"][day.weekday()]
    verts = cfg["verticali"]

    def one(k):
        spec = verts[k]
        r = {"id": k, "nome": spec["nome"]}
        if trends and len(trends.get("years") or []) >= 4 and trends.get("topics"):
            r["ricerca"] = research(trends, spec)
        if signals_db and Path(signals_db).exists():
            r["adozione"] = adoption(signals_db, spec.get("cluster") or [])
            r["wikipedia"] = wiki(signals_db, spec.get("wiki") or [], day)
        return r

    if key == "panoramica":
        rows = []
        for k in verts:
            v = one(k)
            gh = (v.get("adozione") or {}).get("fonti", {}).get("github_repos", {}).get("query", [])
            top = (v.get("ricerca") or {}).get("in_crescita") or [{}]
            gh_vals = sorted(q["anno_su_anno"] for q in gh if q["anno_su_anno"] is not None)
            rows.append({"id": k, "nome": v["nome"],
                         "peso_3_anni": (v.get("ricerca") or {}).get("peso_3_anni"),
                         "slancio_anno_in_corso": (v.get("ricerca") or {}).get("slancio_anno_in_corso"),
                         "quota_finanziata": (v.get("ricerca") or {}).get("quota_finanziata"),
                         "tema_in_maggiore_crescita": top[0].get("tema"),
                         "github_mediana_anno_su_anno": gh_vals[len(gh_vals) // 2] if gh_vals else None})
        return {"tipo": "panoramica", "giorno": day.isoformat(), "verticali": rows}
    return {"tipo": "verticale", "giorno": day.isoformat(), **one(key)}


def topic_list(trends: dict, spec: dict, vertical_id: str) -> list[dict]:
    """Temi del verticale con i dati utili alla newsletter (id OpenAlex, nome, crescita)."""
    last = trends["years"][-1]
    return [{"id": t["id"], "tema": t["tema"], "categoria": t.get("categoria"), "disciplina": t.get("disciplina"),
             "crescita_3a": t.get("crescita_3a"), "paper_ultimo_anno": t.get(f"n{last}"), "verticale": vertical_id}
            for t in match_topics(trends["topics"], spec) if t.get("id")]


def topics_for_day(day: date, cfg: dict, trends: dict) -> list[dict]:
    """Temi da cui pescare i paper del giorno: il verticale del giorno, oppure tutti nel weekend."""
    key = cfg["giorni"][day.weekday()]
    keys = list(cfg["verticali"]) if key == "panoramica" else [key]
    out, seen = [], set()
    for k in keys:
        for t in topic_list(trends, cfg["verticali"][k], k):
            if t["id"] not in seen:
                seen.add(t["id"])
                out.append(t)
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Temi del verticale del giorno (per config/daily.yaml)")
    ap.add_argument("--trends", required=True)
    ap.add_argument("--config", default=str(Path(__file__).resolve().parent.parent / "config" / "verticals.yaml"))
    ap.add_argument("--date", required=True)
    ap.add_argument("-o", "--out", required=True, help="lista degli id dei temi (JSON)")
    ap.add_argument("--meta", required=True, help="temi con nome, verticale e crescita (JSON)")
    args = ap.parse_args()
    trends_path = Path(args.trends)
    topics = []
    if trends_path.exists():
        topics = topics_for_day(date.fromisoformat(args.date), load_config(Path(args.config)),
                                json.loads(trends_path.read_text(encoding="utf-8")))
    Path(args.out).write_text(json.dumps([t["id"] for t in topics]), encoding="utf-8")
    Path(args.meta).write_text(json.dumps(topics, ensure_ascii=False), encoding="utf-8")
    print(f"{len(topics)} temi per {args.date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
