"""Qualità di riviste e autori per scegliere i paper della newsletter (dati gratuiti di OpenAlex).

Per i paper visti oggi (daily.sqlite, papers.sqlite) scarica in blocco, con il filtro `openalex:ID1|ID2|…`:
- riviste/fonti: `summary_stats` (2yr_mean_citedness, h_index), `is_core` (lista CWTS di Leiden), `is_in_doaj`, `type`;
- autori: `summary_stats` (h_index), `last_known_institutions`.
Tiene una cache (JSON) per non riscaricare gli stessi id; le voci più vecchie di CACHE_DAYS si aggiornano.

Uso: python scripts/quality.py --db data/daily.sqlite --db data/papers.sqlite --date 2026-10-23 --cache data/quality_cache.json
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

BATCH = 50          # id per richiesta (filtro in OR con "|", massimo 100)
CACHE_DAYS = 30
SOURCE_FIELDS = "id,display_name,type,is_core,is_in_doaj,summary_stats"
AUTHOR_FIELDS = "id,display_name,summary_stats,last_known_institutions"


def _short(oa_id: str | None) -> str | None:
    return oa_id.rsplit("/", 1)[-1] if oa_id else None


def ids_seen_on(db: Path, day: str) -> tuple[set[str], set[str]]:
    """Id di fonti e autori dei record visti per la prima volta nel giorno indicato."""
    sources, authors = set(), set()
    conn = sqlite3.connect(db)
    for (data,) in conn.execute("SELECT data FROM records WHERE substr(first_seen_at,1,10)=?", (day,)):
        d = json.loads(data)
        if d.get("source_id"):
            sources.add(_short(d["source_id"]))
        for a in (d.get("author_ids") or [])[:20]:   # i primi 20 autori bastano (paper con centinaia di firme)
            if a:
                authors.add(_short(a))
    conn.close()
    return sources, authors


def _stale(entry: dict | None, today: date) -> bool:
    return not entry or entry.get("_aggiornato", "") < (today - timedelta(days=CACHE_DAYS)).isoformat()


def fetch(http, entity: str, ids: list[str], fields: str, api_key: str | None, mailto: str | None) -> dict[str, dict]:
    out = {}
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i + BATCH]
        data = http.get_json(f"https://api.openalex.org/{entity}",
                             {"filter": "openalex:" + "|".join(chunk), "select": fields, "per-page": BATCH,
                              "api_key": api_key, "mailto": mailto})
        for r in data.get("results") or []:
            out[_short(r["id"])] = r
    return out


def update_cache(cache: dict, sources: set[str], authors: set[str], today: date, http,
                 api_key: str | None, mailto: str | None) -> dict:
    for entity, ids, fields in (("sources", sources, SOURCE_FIELDS), ("authors", authors, AUTHOR_FIELDS)):
        store = cache.setdefault(entity, {})
        todo = sorted(i for i in ids if i and _stale(store.get(i), today))
        for k, v in fetch(http, entity, todo, fields, api_key, mailto).items():
            v["_aggiornato"] = today.isoformat()
            store[k] = v
        print(f"{entity}: {len(ids)} visti oggi, {len(todo)} scaricati, {len(store)} in cache")
    return cache


# ---------- punteggio usato da daily.py ----------

def venue_level(src: dict | None) -> str | None:
    """alta / buona / media / debole per le riviste; preprint per gli archivi; None se sconosciuta."""
    if not src:
        return None
    if src.get("type") == "repository":
        return "preprint"
    stats = src.get("summary_stats") or {}
    # Conta soprattutto quanto vengono citati in media gli articoli recenti della rivista
    # (2yr_mean_citedness). L'appartenenza alla lista CWTS "core" da sola non basta: ci sono
    # riviste core con citazioni medie quasi a zero (verificato con analysis/probe_sources.py).
    cit = stats.get("2yr_mean_citedness") or 0
    core = bool(src.get("is_core"))
    if cit >= 3:
        return "alta"
    if cit >= 1.5 or (core and cit >= 0.8):
        return "buona"
    if cit >= 0.5:
        return "media"
    return "debole"


VENUE_POINTS = {"alta": 3.0, "buona": 2.0, "media": 1.0, "preprint": 1.0, "debole": 0.0, None: 0.5}


def assess(d: dict, cache: dict) -> dict:
    """Qualità di un paper: livello della fonte, autore più affermato, punteggio (0–5)."""
    src = (cache.get("sources") or {}).get(_short(d.get("source_id")))
    level = venue_level(src)
    best = None
    for a in (d.get("author_ids") or [])[:20]:
        info = (cache.get("authors") or {}).get(_short(a))
        h = ((info or {}).get("summary_stats") or {}).get("h_index")
        if h is not None and (best is None or h > best["h_index"]):
            inst = ((info.get("last_known_institutions") or [{}])[0] or {}).get("display_name")
            best = {"nome": info.get("display_name"), "h_index": h, "istituzione": inst}
    max_h = best["h_index"] if best else 0
    score = VENUE_POINTS[level] + min(max_h, 80) / 40
    stats = (src or {}).get("summary_stats") or {}
    return {"livello_fonte": level, "fonte_core": bool((src or {}).get("is_core")),
            "fonte_citazioni_medie_2_anni": round(stats["2yr_mean_citedness"], 2) if stats.get("2yr_mean_citedness") is not None else None,
            "autore_di_spicco": best, "punteggio": round(score, 2)}


def load_cache(path: str | Path | None) -> dict:
    p = Path(path) if path else None
    return json.loads(p.read_text(encoding="utf-8")) if p and p.exists() else {}


def main() -> int:
    from collector.config import HttpConfig
    from collector.http_client import HttpClient

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", action="append", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--max-requests", type=int, default=200)
    args = ap.parse_args()
    today = date.fromisoformat(args.date)
    sources, authors = set(), set()
    for db in args.db:
        if Path(db).exists():
            s, a = ids_seen_on(Path(db), args.date)
            sources |= s
            authors |= a
    cache = load_cache(args.cache)
    http = HttpClient(HttpConfig(user_agent=f"data-collector/0.1 (mailto:{os.environ.get('OPENALEX_MAILTO', 'not-set')})",
                                 requests_per_second=5, timeout=60, max_retries=5, backoff_base=1.0,
                                 backoff_max=60, respect_robots=False), max_requests=args.max_requests)
    try:
        update_cache(cache, sources, authors, today, http, os.environ.get("OPENALEX_API_KEY"),
                     os.environ.get("OPENALEX_MAILTO"))
    except Exception as exc:  # la qualità è un di più: se OpenAlex non risponde, la newsletter parte lo stesso
        print(f"::warning::qualità non aggiornata: {exc}")
    Path(args.cache).write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
