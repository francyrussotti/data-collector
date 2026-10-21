import copy
import json
import re
import subprocess
import sys

from collector.config import load_config
from collector.pipeline import run_source
from collector.storage import Storage
from conftest import PROJECT_ROOT

SCRIPT = str(PROJECT_ROOT / "scripts" / "emerging.py")


def trends_fixture():
    def topic(tid, field, cat, c3, sl, n=500):
        return {"id": tid, "tema": f"Tema {tid}", "sottocampo": "S", "disciplina": field, "categoria": cat,
                "crescita_3a": c3, "crescita_ytd": 0.5, "slancio_ytd": sl, "parole_chiave": "a, b",
                "n2024": n // 2, "n2025": n}
    return {"topics": [
        topic("T1", "Computer Science", "forte crescita", 0.7, 0.2),
        topic("T2", "Computer Science", "emergente", 1.5, 0.3),
        topic("T3", "Medicine", "emergente", 3.0, 0.3),            # non tecnologico
        topic("T4", "Engineering", "emergente", 9.0, 0.3),          # salto sospetto
        topic("T5", "Engineering", "stabile", 0.0, 0.0),
    ]}


def test_select(tmp_path):
    (tmp_path / "trends.json").write_text(json.dumps(trends_fixture()))
    out = tmp_path / "topics.json"
    subprocess.run([sys.executable, SCRIPT, "select", "--trends", str(tmp_path / "trends.json"), "--out", str(out)],
                   check=True, capture_output=True)
    assert json.loads(out.read_text()) == ["T2", "T1"]
    meta = json.loads(out.with_suffix(".meta.json").read_text())
    assert meta[0]["id"] == "T2" and meta[0]["paper_ultimo_anno"] == 500


def test_top_lists_and_digest(server, tmp_path, monkeypatch, sample_work):
    monkeypatch.setenv("OPENALEX_API_KEY", "k")
    monkeypatch.setenv("TODAY", "2026-10-21")
    seen = []

    def works(query):
        seen.append(query)
        tid = re.search(r"primary_topic\.id:(T\d+)", query["filter"]).group(1)
        assert query["filter"].endswith("to_publication_date:2026-10-21,primary_topic.id:" + tid)
        assert "cursor" not in query and query["page"] == "1"
        res = []
        for i in range(3):
            w = copy.deepcopy(sample_work)
            w["id"] = f"https://openalex.org/W{tid}{i}"
            w["doi"] = f"https://doi.org/10.1/{tid}.{i}"
            w["cited_by_count"] = 10 * (3 - i)
            w["publication_date"] = f"2026-0{i + 1}-01"
            w["primary_topic"]["id"] = f"https://openalex.org/{tid}"
            res.append(w)
        return 200, {}, {"meta": {}, "results": res}

    server.routes["/works"] = works
    (tmp_path / "topics.json").write_text(json.dumps(["T1", "T2"]))
    (tmp_path / "topics.meta.json").write_text(json.dumps([{"id": "T1", "tema": "Uno"}, {"id": "T2", "tema": "Due"}]))
    text = (PROJECT_ROOT / "config" / "emerging.yaml").read_text()
    text = text.replace("https://api.openalex.org", server.base_url)
    text = text.replace("data/emerging.sqlite", str(tmp_path / "e.sqlite"))
    text = text.replace("data/emerging_topics.json", str(tmp_path / "topics.json"))
    cfg_path = tmp_path / "c.yaml"
    cfg_path.write_text(text)
    cfg = load_config(cfg_path)
    store = Storage(cfg.database, cfg.store_raw)
    for name in ("emerging_cited", "emerging_recent"):
        r = run_source(cfg.sources[name], store)
        assert r.status == "success" and r.counts["inserted"] == 6 and r.requests == 2
    store.close()
    assert {q["sort"] for q in seen} == {"cited_by_count:desc", "publication_date:desc"}

    out = subprocess.run([sys.executable, SCRIPT, "digest", "-c", str(cfg_path), "--topics",
                          str(tmp_path / "topics.meta.json"), "--per-list", "2"],
                         check=True, capture_output=True, text=True)
    res = json.loads(out.stdout)
    assert len(res["paper"]) == 8  # 2 temi x 2 liste x 2 paper
    cited = [p for p in res["paper"] if p["tema_id"] == "T1" and p["lista"] == "più citati"]
    assert [p["citazioni"] for p in cited] == [30, 20]
    recent = [p for p in res["paper"] if p["tema_id"] == "T1" and p["lista"] == "più recenti"]
    assert recent[0]["data"] == "2026-03-01" and recent[0]["estratto"].startswith("We study")


def test_missing_values_file(tmp_path, monkeypatch):
    monkeypatch.setenv("TODAY", "2026-10-21")
    text = (PROJECT_ROOT / "config" / "emerging.yaml").read_text()
    text = text.replace("data/emerging_topics.json", str(tmp_path / "nope.json"))
    text = text.replace("data/emerging.sqlite", str(tmp_path / "e.sqlite"))
    (tmp_path / "c.yaml").write_text(text)
    cfg = load_config(tmp_path / "c.yaml")
    store = Storage(cfg.database)
    r = run_source(cfg.sources["emerging_cited"], store)
    assert r.status == "failed" and "non trovato" in r.error
    store.close()
