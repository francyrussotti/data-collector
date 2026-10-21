import json
import subprocess
import sys

from collector.storage import Storage, now_iso
from conftest import PROJECT_ROOT

SCRIPT = str(PROJECT_ROOT / "scripts" / "daily.py")


def test_daily_digest(tmp_path):
    today = now_iso()[:10]
    papers = Storage(tmp_path / "papers.sqlite")
    papers.commit_page("openalex_llm", [
        ("W1", "10.1/a", {"title": "Vecchio", "cited_by_count": 5, "published_date": "2026-10-01"}, None),
    ], None, None)
    papers.conn.execute("UPDATE records SET first_seen_at='2026-01-01T00:00:00+00:00'")
    papers.conn.commit()
    papers.commit_page("openalex_llm", [
        ("W2", "10.1/b", {"title": "Nuovo poco citato", "cited_by_count": 0, "published_date": "2026-10-20",
                          "abstract": "x" * 500, "doi": "10.1/b"}, None),
        ("W3", "10.1/c", {"title": "Nuovo citato", "cited_by_count": 3, "published_date": "2026-10-19"}, None),
    ], None, None)
    run = papers.start_run("openalex_llm", None)
    from collections import Counter
    papers.finish_run(run, "success", Counter(fetched=3, inserted=2), 5, None)
    papers.close()

    daily = Storage(tmp_path / "daily.sqlite")
    daily.commit_page("daily_emerging", [
        ("W9", None, {"title": "Quantum", "published_date": "2026-10-20", "primary_topic_id": "T1"}, None),
        ("W8", None, {"title": "Altro tema", "published_date": "2026-10-20", "primary_topic_id": "T99"}, None),
    ], None, None)
    daily.close()
    (tmp_path / "topics.json").write_text(json.dumps([{"id": "T1", "tema": "Quantum Computing", "categoria": "forte crescita"}]))
    trends = {"generated_at": "x", "years": [2024, 2025], "topics": [
        {"tema": "A", "disciplina": "Computer Science", "categoria": "emergente", "crescita_3a": 1.5, "slancio_ytd": 0.3, "n2025": 300},
        {"tema": "B", "disciplina": "Computer Science", "categoria": "emergente", "crescita_3a": 9, "slancio_ytd": 0.3, "n2025": 300},
        {"tema": "C", "disciplina": "Engineering", "categoria": "in calo", "crescita_3a": -0.5, "slancio_ytd": 0, "n2025": 500},
    ]}
    (tmp_path / "trends.json").write_text(json.dumps(trends))

    out = subprocess.run([sys.executable, SCRIPT, "--papers", str(tmp_path / "papers.sqlite"), "--daily",
                          str(tmp_path / "daily.sqlite"), "--topics", str(tmp_path / "topics.json"),
                          "--trends", str(tmp_path / "trends.json"), "--date", today],
                         check=True, capture_output=True, text=True)
    r = json.loads(out.stdout)
    assert r["llm"]["nuovi_oggi"] == 2 and r["llm"]["totale"] == 3
    # entrambi recenti rispetto al 2026-10-21 → ordinati per data, il più recente prima
    assert [p["titolo"] for p in r["llm"]["selezione"]][:2] in (["Nuovo poco citato", "Nuovo citato"], ["Nuovo citato", "Nuovo poco citato"])
    sel = {p["titolo"]: p for p in r["llm"]["selezione"]}
    assert sel["Nuovo poco citato"]["estratto"].endswith("…") and sel["Nuovo poco citato"]["link"] == "https://doi.org/10.1/b"
    assert r["llm"]["ultima_raccolta"]["nuovi"] == 2
    assert r["emergenti"]["nuovi_oggi"] == 2 and r["emergenti"]["per_tema"][0]["tema"] == "Quantum Computing"
    assert len(r["emergenti"]["per_tema"]) == 1  # il tema non seguito resta fuori
    assert [t["tema"] for t in r["trend"]["emergenti"]] == ["A"]  # B è un salto sospetto
    assert r["trend"]["in_calo"][0]["tema"] == "C"


def test_ranking_prefers_journals_and_skips_future():
    import importlib.util
    spec = importlib.util.spec_from_file_location("daily", SCRIPT)
    daily = importlib.util.module_from_spec(spec)
    import sys as _s
    _s.path.insert(0, str(PROJECT_ROOT / "scripts"))
    spec.loader.exec_module(daily)
    items = [
        {"title": "zenodo", "venue": "Zenodo (CERN European Organization for Nuclear Research)", "published_date": "2026-10-21"},
        {"title": "rg", "venue": None, "doi": "10.13140/rg.2.2.1", "published_date": "2026-10-21"},
        {"title": "journal-old", "venue": "Nature", "language": "en", "published_date": "2026-10-10"},
        {"title": "journal-new", "venue": "Science", "language": "en", "published_date": "2026-10-20"},
        {"title": "other-lang", "venue": "Rivista", "language": "id", "published_date": "2026-10-21"},
    ]
    assert [d["title"] for d in daily.rank_recent(items)] == ["journal-new", "journal-old", "other-lang", "zenodo", "rg"]


def test_daily_without_files(tmp_path):
    out = subprocess.run([sys.executable, SCRIPT, "--papers", str(tmp_path / "nope.sqlite")],
                         check=True, capture_output=True, text=True)
    r = json.loads(out.stdout)
    assert r["llm"] is None and r["emergenti"] is None and r["trend"] is None
