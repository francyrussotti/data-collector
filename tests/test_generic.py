from datetime import date

import pytest

from collector.config import ConfigError, HttpConfig, SourceConfig
from collector.connectors.generic import build_periods
from collector.http_client import HttpClient
from collector.pipeline import run_source
from collector.storage import Storage


def source(server, connector, endpoint, options, fields, params=None, headers=None):
    return SourceConfig(
        name="s", connector=connector, base_url=server.base_url, endpoint=endpoint, id_field="id",
        fields=fields, http=HttpConfig(user_agent="t", requests_per_second=1000, headers=headers or {}),
        params=params or {}, options=options)


def test_build_periods():
    q = build_periods("quarter", "2025-02", date(2025, 8, 15))
    assert [p["period"] for p in q] == ["2025-Q1", "2025-Q2", "2025-Q3"]
    assert q[0]["start"] == date(2025, 1, 1) and q[-1]["end"] == date(2025, 8, 15) and q[-1]["partial"]
    m = build_periods("month", "2024-11", date(2025, 1, 31))
    assert [p["period"] for p in m] == ["2024-11", "2024-12", "2025-01"] and not m[-1]["partial"]
    assert build_periods("snapshot", None, date(2025, 1, 2))[0]["period"] == "2025-01-02"
    with pytest.raises(ConfigError):
        build_periods("year", "2025-01", date(2025, 1, 2))


def test_query_counts(server, tmp_path):
    seen = []

    def handle(query):
        seen.append(query)
        return 200, {}, {"meta": {"total": len(query["q"]) * 10}, "items": []}

    server.routes["/gb/search"] = handle
    src = source(server, "query_counts", "/{country}/search", {
        "queries": [{"id": "agents", "query": "ai agent", "country": "gb", "cluster": "S1"},
                    {"id": "mcp", "query": "mcp", "country": "gb", "cluster": "S1"}],
        "params": {"q": "{query} created:{start}..{end}", "ts": "{start_ts}"},
        "count_path": "meta.total", "granularity": "quarter", "from": "2025-01", "as_of": "2025-05-10"},
        {"query_id": "query_id", "cluster": "cluster", "period": "period", "count": "count", "partial": "partial"})
    store = Storage(tmp_path / "c.sqlite")
    r = run_source(src, store)
    assert r.status == "success" and r.counts["inserted"] == 4 and r.requests == 4
    assert seen[0]["q"] == "ai agent created:2025-01-01..2025-03-31" and seen[0]["ts"] == "1735689600"
    assert seen[1]["q"] == "ai agent created:2025-04-01..2025-05-10"
    rows = {rid: d for rid, d in ((r[0], r[1]) for r in store.conn.execute("SELECT record_id, data FROM records"))}
    assert set(rows) == {"agents|2025-Q1", "agents|2025-Q2", "mcp|2025-Q1", "mcp|2025-Q2"}
    assert '"count":390' in rows["agents|2025-Q1"] and '"partial":true' in rows["agents|2025-Q2"]
    store.close()


def test_api_list(server, tmp_path):
    server.routes["/packages/langgraph/overall"] = lambda q: (200, {}, {"data": [
        {"category": "without_mirrors", "date": "2025-01-01", "downloads": 5},
        {"category": "without_mirrors", "date": "2025-01-02", "downloads": 7}]})
    server.routes["/packages/nope/overall"] = lambda q: (404, {}, "not found")
    src = source(server, "api_list", "/packages/{package}/overall", {
        "items": [{"package": "langgraph", "cluster": "S1"}, {"package": "nope", "cluster": "S1"}],
        "records_path": "data", "id_template": "{package}|{date}|{category}", "as_of": "2025-02-01"},
        {"package": "package", "date": "date", "downloads": "downloads", "cluster": "cluster"},
        params={"mirrors": "false", "until": "{today_compact}"})
    store = Storage(tmp_path / "a.sqlite")
    r = run_source(src, store)
    assert r.status == "success" and r.counts["inserted"] == 2 and r.requests == 2
    assert store.count("s") == 2   # il pacchetto inesistente (404) è saltato senza far fallire il run
    store.close()


def test_headers_skip_empty_token():
    c = HttpClient(HttpConfig(user_agent="t", headers={"Authorization": "Bearer ", "X-Test": "1"}))
    assert "Authorization" not in c.session.headers and c.session.headers["X-Test"] == "1"
