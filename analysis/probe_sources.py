"""Sonda: una chiamata reale per ogni fonte gratuita, stampa stato e struttura della risposta.
Serve a configurare i connettori sui formati veri, senza indovinarli.

Uso: python analysis/probe_sources.py   (legge GITHUB_TOKEN, OPENALEX_API_KEY, ADZUNA_APP_ID/KEY se presenti)
"""
from __future__ import annotations

import json
import os
import time

import requests

UA = {"User-Agent": "data-collector/0.1 (mailto:%s)" % os.environ.get("OPENALEX_MAILTO", "not-set")}


def shape(obj, depth=0, max_depth=3):
    """Struttura sintetica: chiavi, tipi, lunghezze delle liste, primo elemento."""
    if depth >= max_depth:
        return type(obj).__name__
    if isinstance(obj, dict):
        return {k: shape(v, depth + 1, max_depth) for k, v in list(obj.items())[:25]}
    if isinstance(obj, list):
        return [f"list[{len(obj)}]", shape(obj[0], depth + 1, max_depth) if obj else None]
    if isinstance(obj, str):
        return obj[:60]
    return obj


def probe(name, url, params=None, headers=None):
    h = dict(UA)
    h.update(headers or {})
    try:
        r = requests.get(url, params=params, headers=h, timeout=30)
        print(f"\n=== {name}: HTTP {r.status_code} {r.url.split('?')[0]}")
        try:
            print(json.dumps(shape(r.json()), ensure_ascii=False)[:2500])
        except ValueError:
            print(r.text[:500])
    except requests.RequestException as exc:
        print(f"\n=== {name}: ERRORE {exc}")
    time.sleep(1)


gh = os.environ.get("GITHUB_TOKEN")
probe("github_search_repos", "https://api.github.com/search/repositories",
      {"q": "mcp server created:2025-01-01..2025-03-31", "per_page": 1},
      {"Authorization": f"Bearer {gh}", "Accept": "application/vnd.github+json"} if gh else None)
probe("hn_algolia", "https://hn.algolia.com/api/v1/search_by_date",
      {"query": "MCP", "tags": "story", "numericFilters": "created_at_i>1735689600,created_at_i<1743465600", "hitsPerPage": 1})
probe("nsf_awards", "https://api.nsf.gov/services/v1/awards.json",
      {"keyword": "multi-agent", "dateStart": "01/01/2024", "dateEnd": "12/31/2024", "rpp": 1})
probe("pypistats_overall", "https://pypistats.org/api/packages/langgraph/overall", {"mirrors": "false"})
probe("wikimedia_pageviews",
      "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Large_language_model/monthly/2025010100/2025033100")
key = os.environ.get("OPENALEX_API_KEY")
probe("openalex_funders_search", "https://api.openalex.org/funders",
      {"search": "National Institutes of Health", "per-page": 3, "select": "id,display_name,works_count", "api_key": key})
probe("openalex_group_by_funder", "https://api.openalex.org/works",
      {"filter": "primary_topic.id:T10028,publication_year:2024", "group_by": "awards.funder_id", "per-page": 5, "api_key": key})
aid, akey = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
if aid and akey:
    probe("adzuna_search", "https://api.adzuna.com/v1/api/jobs/gb/search/1",
          {"app_id": aid, "app_key": akey, "what": "AI agent", "results_per_page": 1})
else:
    print("\n=== adzuna: saltato (ADZUNA_APP_ID/ADZUNA_APP_KEY non impostati)")
