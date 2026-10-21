"""Statistiche sui dati raccolti e stima dei tempi per completare lo storico.

Uso:  python scripts/report.py -c config/openalex.yaml -s openalex_llm [-o report.json] [--no-remote]

Legge il database SQLite e, se non c'è --no-remote, chiede a OpenAlex quanti record
corrispondono ai filtri per anno (group_by=publication_year), per stimare la copertura.
Stampa un JSON con tutte le statistiche.
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from collector.config import load_config  # noqa: E402
from collector.http_client import HttpClient  # noqa: E402


def q(conn, sql, *args):
    return [tuple(r) for r in conn.execute(sql, args).fetchall()]


def remote_counts(src) -> dict:
    """Totali OpenAlex per anno con gli stessi filtri della raccolta (una sola chiamata)."""
    params = {k: v for k, v in src.params.items() if k not in ("select", "per-page", "cursor")}
    filters = [params.pop("filter")] if params.get("filter") else []
    if src.incremental and src.incremental.start:
        filters.append(src.incremental.filter.format(since=src.incremental.start))
    params["filter"] = ",".join(filters)
    params["group_by"] = "publication_year"
    data = HttpClient(src.http, max_requests=3).get_json(src.url, params)
    by_year = {str(g.get("key")): g.get("count", 0) for g in data.get("group_by") or []}
    return {"total": (data.get("meta") or {}).get("count"), "by_year": by_year}


def build(conn, source: str) -> dict:
    s = source
    j = "json_extract(data, '$.{}')".format
    out: dict = {"source": s, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    out["records"] = q(conn, "SELECT count(*) FROM records WHERE source=?", s)[0][0]
    out["with_doi"] = q(conn, f"SELECT count(*) FROM records WHERE source=? AND {j('doi')} IS NOT NULL", s)[0][0]
    out["distinct_doi"] = q(conn, "SELECT count(DISTINCT dedup_key) FROM records WHERE source=?", s)[0][0]
    out["by_year"] = q(conn, f"SELECT {j('year')} y, count(*) FROM records WHERE source=? GROUP BY y ORDER BY y", s)
    out["by_type"] = q(conn, f"SELECT {j('type')} t, count(*) c FROM records WHERE source=? GROUP BY t ORDER BY c DESC LIMIT 10", s)
    out["by_language"] = q(conn, f"SELECT {j('language')} l, count(*) c FROM records WHERE source=? GROUP BY l ORDER BY c DESC LIMIT 8", s)
    out["by_field"] = q(conn, f"SELECT {j('field')} f, count(*) c FROM records WHERE source=? GROUP BY f ORDER BY c DESC LIMIT 15", s)
    out["field_by_year"] = q(conn, f"SELECT {j('year')} y, {j('field')} f, count(*) FROM records WHERE source=? GROUP BY y, f", s)
    out["oa_by_year"] = q(conn, f"SELECT {j('year')} y, sum({j('is_oa')}), count(*) FROM records WHERE source=? GROUP BY y", s)
    out["citations_by_year"] = q(conn, f"SELECT {j('year')} y, avg({j('cited_by_count')}), sum({j('cited_by_count')}) FROM records WHERE source=? GROUP BY y", s)

    def list_field(name, limit, per_year=False):
        group = f"{j('year')}, " if per_year else ""
        sql = (f"SELECT {group}e.value v, count(*) c FROM records, json_each(records.data, '$.{name}') e "
               f"WHERE source=? GROUP BY {group}v ORDER BY c DESC")
        rows = q(conn, sql, s)
        if not per_year:
            return rows[:limit]
        kept, seen = [], {}
        for year, value, count in rows:  # già ordinati per count: i primi `limit` di ogni anno
            if seen.get(year, 0) < limit:
                kept.append((year, value, count))
                seen[year] = seen.get(year, 0) + 1
        return kept

    out["top_topics"] = list_field("topics", 30)
    out["topics_by_year"] = list_field("topics", 40, per_year=True)
    out["top_keywords"] = list_field("keywords", 30)
    out["keywords_by_year"] = list_field("keywords", 40, per_year=True)
    out["top_countries"] = list_field("countries", 20)
    out["countries_by_year"] = list_field("countries", 15, per_year=True)
    out["top_institutions"] = list_field("institutions", 25)
    out["top_venues"] = q(conn, f"SELECT {j('venue')} v, count(*) c FROM records WHERE source=? AND v IS NOT NULL GROUP BY v ORDER BY c DESC LIMIT 20", s)
    out["most_cited"] = q(conn, f"SELECT {j('title')}, {j('year')}, {j('cited_by_count')}, {j('doi')} FROM records WHERE source=? ORDER BY {j('cited_by_count')} DESC LIMIT 15", s)
    out["runs"] = [dict(zip(("started_at", "finished_at", "status", "fetched", "inserted", "unchanged", "requests"), r))
                   for r in q(conn, "SELECT started_at, finished_at, status, fetched, inserted, unchanged, requests FROM runs WHERE source=? ORDER BY id", s)]
    state = q(conn, "SELECT watermark, checkpoint IS NOT NULL FROM sync_state WHERE source=?", s)
    out["watermark"], out["has_checkpoint"] = (state[0] if state else (None, False))
    return out


def eta(stats: dict, remote: dict | None, max_requests: int | None) -> dict:
    done = [r for r in stats["runs"] if r["status"] in ("success", "partial") and r["requests"]]
    per_run = sum(r["inserted"] for r in done) / len(done) if done else None
    dup_rate = (sum(r["unchanged"] for r in done) / max(1, sum(r["fetched"] for r in done))) if done else None
    res = {"new_per_run": per_run, "duplicate_rate": dup_rate, "max_requests_per_run": max_requests}
    if remote and remote.get("total") and per_run:
        remaining = max(0, remote["total"] - stats["records"])
        res.update(total_remote=remote["total"], remaining=remaining,
                   runs_needed=math.ceil(remaining / per_run))
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", required=True)
    ap.add_argument("-s", "--source", required=True)
    ap.add_argument("-o", "--out")
    ap.add_argument("--no-remote", action="store_true")
    ap.add_argument("--chunks", type=int, default=0,
                    help="stampa il JSON in righe 'REPORT|n|...' di N caratteri (log CI)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    src = cfg.sources[args.source]
    conn = sqlite3.connect(cfg.database)
    stats = build(conn, src.name)
    remote = None
    if not args.no_remote:
        try:
            remote = remote_counts(src)
        except Exception as exc:  # noqa: BLE001 - il report resta utile anche senza i totali
            stats["remote_error"] = str(exc)
    stats["remote"] = remote
    stats["eta"] = eta(stats, remote, src.max_requests_per_run)
    text = json.dumps(stats, ensure_ascii=False, separators=(",", ":"))
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    if args.chunks:
        for i in range(0, len(text), args.chunks):
            print(f"REPORT|{i // args.chunks:04d}|{text[i:i + args.chunks]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
