import json
import subprocess
import sys

from collector.config import load_config
from collector.pipeline import run_source
from collector.storage import Storage
from conftest import PROJECT_ROOT, openalex_route


def test_report_script(server, tmp_path, monkeypatch, make_works):
    monkeypatch.setenv("OPENALEX_API_KEY", "k")
    works = make_works(5)
    route = openalex_route(works, page_size=2)

    def handle(query):
        if "group_by" in query:
            assert "from_publication_date:2018-01-01" in query["filter"] and "cursor" not in query
            return 200, {}, {"meta": {"count": 50}, "group_by": [{"key": "2024", "count": 50}]}
        return route(query)

    server.routes["/works"] = handle
    text = (PROJECT_ROOT / "config" / "openalex.yaml").read_text()
    text = text.replace("https://api.openalex.org", server.base_url)
    text = text.replace("data/papers.sqlite", str(tmp_path / "p.sqlite"))
    cfg_path = tmp_path / "c.yaml"
    cfg_path.write_text(text)
    cfg = load_config(cfg_path)
    store = Storage(cfg.database)
    run_source(cfg.sources["openalex_llm"], store)
    store.close()

    out = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "report.py"), "-c", str(cfg_path), "-s", "openalex_llm"],
        capture_output=True, text=True, check=True)
    stats = json.loads(out.stdout)
    assert stats["records"] == 5
    assert stats["by_year"] == [[2024, 5]]
    assert ["Topic Modeling", 5] in stats["top_topics"]
    assert sorted(stats["top_countries"]) == [["IT", 5], ["US", 5]]
    assert stats["remote"] == {"total": 50, "by_year": {"2024": 50}}
    assert stats["eta"]["remaining"] == 45 and stats["eta"]["runs_needed"] == 9
