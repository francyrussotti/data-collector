"""Fase 1 – Ispezione dei dati: copertura, periodo, qualità e bias delle fonti.

Uso:  python analysis/inspect_data.py data/papers.sqlite data/emerging.sqlite data/daily.sqlite \
          --trends-db data/trends.sqlite [-o analysis/results/01_inspection.json] [--chunks 3000]

Per ogni database e fonte calcola: numero di record, periodo di pubblicazione, completezza dei campi,
distribuzioni (tipo, lingua, sede, paese), quota di depositi senza revisione, date future, doppioni DOI.
Per i conteggi per tema: totali per periodo, temi senza conteggi, concentrazione.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPOSITORY_HINTS = ("zenodo", "figshare", "researchgate", "ssrn", "osf preprints")
REPOSITORY_DOI = ("10.5281/", "10.6084/", "10.13140/")
FIELDS = ["doi", "title", "abstract", "published_date", "language", "type", "venue", "source_type", "authors",
          "institutions", "countries", "primary_topic", "field", "topics", "keywords", "cited_by_count",
          "oa_url", "is_oa"]


def empty(v) -> bool:
    return v is None or v == "" or v == [] or v == {}


def pct(n: int, tot: int) -> float:
    return round(100 * n / tot, 1) if tot else 0.0


def inspect_source(rows: list[dict], today: str) -> dict:
    n = len(rows)
    dates = sorted(d["published_date"] for d in rows if d.get("published_date"))
    years = Counter(int(d["published_date"][:4]) for d in rows if d.get("published_date"))
    present = [f for f in FIELDS if any(f in d for d in rows[:500])]
    completeness = {f: pct(sum(not empty(d.get(f)) for d in rows), n) for f in present}
    venues = Counter((d.get("venue") or "(nessuna)") for d in rows)
    repo = sum(1 for d in rows
               if any(h in (d.get("venue") or "").lower() for h in REPOSITORY_HINTS)
               or (d.get("doi") or "").lower().startswith(REPOSITORY_DOI))
    countries = Counter(c for d in rows for c in (d.get("countries") or []))
    fields = Counter(d.get("field") or "(nessuna)" for d in rows)
    dois = Counter(d.get("doi") for d in rows if d.get("doi"))
    cites = [d.get("cited_by_count") or 0 for d in rows]
    cites_by_year = {}
    for y in sorted(years):
        c = [d.get("cited_by_count") or 0 for d in rows if (d.get("published_date") or "")[:4] == str(y)]
        cites_by_year[y] = {"mediana": statistics.median(c), "media": round(statistics.mean(c), 1), "zero_pct": pct(sum(x == 0 for x in c), len(c))}
    return {
        "record": n,
        "periodo": {"min": dates[0] if dates else None, "max": dates[-1] if dates else None,
                    "date_future": sum(1 for x in dates if x > today), "per_anno": dict(sorted(years.items()))},
        "completezza_pct": completeness,
        "tipo": dict(Counter(d.get("type") or "(nessuno)" for d in rows).most_common(8)),
        "tipo_fonte": dict(Counter(d.get("source_type") or "(non raccolto)" for d in rows).most_common(8)),
        "lingua": dict(Counter(d.get("language") or "(nessuna)" for d in rows).most_common(10)),
        "sedi_top": venues.most_common(15),
        "sedi_distinte": len(venues),
        "quota_top10_sedi_pct": pct(sum(c for _, c in venues.most_common(10)), n),
        "depositi_senza_revisione_pct": pct(repo, n),
        "open_access_pct": pct(sum(1 for d in rows if d.get("is_oa")), n),
        "paesi_top": countries.most_common(12),
        "paper_senza_paese_pct": pct(sum(1 for d in rows if empty(d.get("countries"))), n),
        "discipline_top": fields.most_common(10),
        "doi_duplicati": sum(c - 1 for c in dois.values() if c > 1),
        "citazioni": {"mediana": statistics.median(cites) if cites else None, "per_anno": cites_by_year},
    }


def inspect_db(path: Path, today: str) -> dict:
    conn = sqlite3.connect(path)
    out = {}
    for (source,) in conn.execute("SELECT DISTINCT source FROM records"):
        rows = [json.loads(r[0]) for r in conn.execute("SELECT data FROM records WHERE source=?", (source,))]
        runs = conn.execute("SELECT status, count(*) FROM runs WHERE source=? GROUP BY status", (source,)).fetchall()
        out[source] = inspect_source(rows, today) | {"run": dict(runs)}
    return out


def inspect_trends(path: Path) -> dict:
    conn = sqlite3.connect(path)
    topics = {rid: json.loads(d) for rid, d in conn.execute("SELECT record_id, data FROM records WHERE source='topics'")}
    counts = [json.loads(d) for (d,) in conn.execute("SELECT data FROM records WHERE source='topic_counts'")]
    per_period = Counter()
    for c in counts:
        per_period[c["period"]] += int(c["count"] or 0)
    with_counts = {c["topic_id"] for c in counts}
    last_year = max((c["year"] for c in counts if c["period_type"] == "year"), default=None)
    last = sorted((int(c["count"]) for c in counts if c["period"] == str(last_year)), reverse=True)
    domains = Counter(t.get("domain") for t in topics.values())
    return {
        "temi_in_anagrafica": len(topics), "temi_con_conteggi": len(with_counts),
        "paper_con_tema_per_periodo": dict(sorted(per_period.items())),
        "domini": dict(domains),
        "concentrazione_ultimo_anno": {
            "anno": last_year, "temi": len(last),
            "quota_top1pct_temi_pct": pct(sum(last[: max(1, len(last) // 100)]), sum(last)),
            "temi_sotto_50_paper": sum(1 for x in last if x < 50),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dbs", nargs="*")
    ap.add_argument("--trends-db")
    ap.add_argument("-o", "--out")
    ap.add_argument("--chunks", type=int, default=0)
    args = ap.parse_args()
    today = datetime.now(timezone.utc).date().isoformat()
    result = {"generato_il": today, "database": {}}
    for db in args.dbs:
        if Path(db).exists():
            result["database"][Path(db).name] = inspect_db(Path(db), today)
    if args.trends_db and Path(args.trends_db).exists():
        result["trends"] = inspect_trends(Path(args.trends_db))
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    if args.chunks:
        for i in range(0, len(text), args.chunks):
            print(f"RESULT|{i // args.chunks:04d}|{text[i:i + args.chunks]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
