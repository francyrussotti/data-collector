import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import quality as q  # noqa: E402

CACHE = {
    "sources": {
        "S1": {"type": "journal", "is_core": True, "summary_stats": {"2yr_mean_citedness": 8.0}},
        "S2": {"type": "journal", "is_core": False, "summary_stats": {"2yr_mean_citedness": 0.2}},
        "S3": {"type": "repository", "summary_stats": {"2yr_mean_citedness": 0.1}},
        "S4": {"type": "journal", "is_core": True, "summary_stats": {"2yr_mean_citedness": 0.0}},
    },
    "authors": {"A1": {"display_name": "Ada", "summary_stats": {"h_index": 60},
                       "last_known_institutions": [{"display_name": "MIT"}]},
                "A3": {"display_name": "Cy", "summary_stats": {"h_index": 70}, "last_known_institutions": None},
                "A2": {"display_name": "Bob", "summary_stats": {"h_index": 3}}},
}


def test_levels_and_score():
    assert q.venue_level(CACHE["sources"]["S1"]) == "alta"
    assert q.venue_level(CACHE["sources"]["S2"]) == "debole"
    assert q.venue_level(CACHE["sources"]["S3"]) == "preprint"
    assert q.venue_level(None) is None
    assert q.venue_level(CACHE["sources"]["S4"]) == "debole"   # core ma mai citata
    a = q.assess({"source_id": "S1", "author_ids": ["https://openalex.org/A2", "A1"]}, CACHE)
    assert a["livello_fonte"] == "alta" and a["autore_di_spicco"]["nome"] == "Ada"
    assert a["autore_di_spicco"]["istituzione"] == "MIT" and a["punteggio"] == 4.5
    assert q.assess({"source_id": "S1", "author_ids": ["A3"]}, CACHE)["autore_di_spicco"]["istituzione"] is None
    weak = q.assess({"source_id": "S2", "author_ids": ["A2"]}, CACHE)
    assert weak["punteggio"] < 1


def test_update_cache_batches_and_skips_fresh(tmp_path):
    calls = []

    class FakeHttp:
        def get_json(self, url, params):
            calls.append((url, params["filter"]))
            ids = params["filter"].split(":", 1)[1].split("|")
            return {"results": [{"id": f"https://openalex.org/{i}", "summary_stats": {"h_index": 1}} for i in ids]}

    cache = {"authors": {"A0": {"_aggiornato": "2026-10-20"}}}
    authors = {f"A{i}" for i in range(0, 61)}
    q.update_cache(cache, {"S9"}, authors, date(2026, 10, 23), FakeHttp(), None, None)
    author_calls = [c for c in calls if c[0].endswith("/authors")]
    assert len(author_calls) == 2                      # 60 da scaricare, blocchi da 50
    assert "A0" not in "|".join(c[1] for c in author_calls)   # ancora fresco in cache
    assert cache["sources"]["S9"]["_aggiornato"] == "2026-10-23"


def test_ids_seen_on(tmp_path):
    db = tmp_path / "d.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE records (source TEXT, record_id TEXT, data TEXT, first_seen_at TEXT)")
    con.execute("INSERT INTO records VALUES ('x','1',?, '2026-10-23T01:00:00')",
                (json.dumps({"source_id": "S1", "author_ids": ["A1", "A2"]}),))
    con.execute("INSERT INTO records VALUES ('x','2',?, '2026-10-22T01:00:00')",
                (json.dumps({"source_id": "S8", "author_ids": ["A8"]}),))
    con.commit()
    con.close()
    assert q.ids_seen_on(db, "2026-10-23") == ({"S1"}, {"A1", "A2"})


def test_ranking_uses_quality():
    import daily
    daily.QUALITY.clear()
    daily.QUALITY.update(CACHE)
    try:
        items = [{"title": "weak", "venue": "J", "language": "en", "abstract": "x", "source_id": "S2", "author_ids": ["A2"],
                  "published_date": "2026-10-22"},
                 {"title": "strong", "venue": "Nature", "language": "en", "abstract": "x", "source_id": "S1",
                  "author_ids": ["A1"], "published_date": "2026-10-20"}]
        assert [d["title"] for d in daily.rank_recent(items)] == ["strong", "weak"]
        assert daily.paper(items[1], 100)["qualita"]["livello_fonte"] == "alta"
    finally:
        daily.QUALITY.clear()
