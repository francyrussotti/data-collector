import json
import re
import subprocess
import sys
from datetime import date

from collector.config import load_config
from collector.connectors.openalex_groups import build_periods
from collector.pipeline import run_source
from collector.storage import Storage
from conftest import PROJECT_ROOT

# conteggi simulati: T1 cresce molto, T2 stabile, T3 in calo
BASE = {"T1": 100, "T2": 100000, "T3": 100000}
GROWTH = {"T1": 2.0, "T2": 1.1, "T3": 0.8}


def count_for(topic, year, ytd=False):
    c = BASE[topic] * GROWTH[topic] ** (year - 2018)
    return int(c * (0.8 if ytd else 1))


def works_route(query):
    assert query["group_by"] == "primary_topic.id" and query["filter"].startswith("type:article|preprint|review,")
    m = re.search(r"publication_year:(\d{4})", query["filter"])
    if m:
        year, ytd = int(m.group(1)), False
    else:
        year, ytd = int(re.search(r"from_publication_date:(\d{4})", query["filter"]).group(1)), True
    groups = [{"key": f"https://openalex.org/{t}", "key_display_name": f"Tema {t}", "count": count_for(t, year, ytd)}
              for t in BASE]
    # due pagine: T1+T2, poi T3; dopo l'ultima pagina next_cursor è None
    if query["cursor"] == "*":
        return 200, {}, {"meta": {"next_cursor": "c2"}, "group_by": groups[:2], "results": []}
    return 200, {}, {"meta": {"next_cursor": None}, "group_by": groups[2:], "results": []}


def topics_route(query):
    results = [{"id": f"https://openalex.org/{t}", "display_name": f"Tema {t}", "description": "d",
                "keywords": ["k1", {"id": "x", "display_name": "k2"}], "subfield": {"display_name": "Sub"},
                "field": {"display_name": "Computer Science" if t != "T3" else "Medicine"},
                "domain": {"display_name": "Physical Sciences"}, "works_count": 1} for t in BASE]
    if query["cursor"] == "*":
        return 200, {}, {"meta": {"next_cursor": "x"}, "results": results}
    return 200, {}, {"meta": {"next_cursor": None}, "results": []}


def test_build_periods():
    p = build_periods(2018, date(2026, 10, 21), True)
    assert [x["period"] for x in p][:2] == ["2018", "2019"] and p[7]["period"] == "2025"
    assert p[-2]["filter"] == "from_publication_date:2025-01-01,to_publication_date:2025-10-21"
    assert p[-1]["period"] == "2026-ytd"
    assert build_periods(2018, date(2028, 2, 29), True)[-2]["filter"].endswith("2027-02-28")


def test_trends_end_to_end(server, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENALEX_API_KEY", "k")
    server.routes["/works"] = works_route
    server.routes["/topics"] = topics_route
    text = (PROJECT_ROOT / "config" / "tech_trends.yaml").read_text()
    text = text.replace("https://api.openalex.org", server.base_url)
    text = text.replace("data/trends.sqlite", str(tmp_path / "t.sqlite"))
    text = text.replace("      all_groups: true", "      all_groups: true\n      as_of: '2026-10-21'")
    cfg_path = tmp_path / "c.yaml"
    cfg_path.write_text(text)
    cfg = load_config(cfg_path)
    store = Storage(cfg.database, cfg.store_raw)
    assert run_source(cfg.sources["topics"], store).status == "success"
    r = run_source(cfg.sources["topic_counts"], store)
    assert r.status == "success"
    assert r.counts["inserted"] == 3 * 10  # 3 temi x (8 anni + 2 periodi da inizio anno)
    assert r.requests == 20                # 2 pagine per periodo

    # interruzione a metà e ripresa dal checkpoint: nessun periodo perso
    store2 = Storage(tmp_path / "t2.sqlite")
    src = cfg.sources["topic_counts"]
    src.max_requests_per_run = 5
    assert run_source(src, store2).status == "partial"
    src.max_requests_per_run = None
    assert run_source(src, store2).status == "success"
    assert store2.count("topic_counts") == 30
    store.close()
    store2.close()

    out = subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / "trends.py"), "-c", str(cfg_path)],
                         capture_output=True, text=True, check=True)
    res = json.loads(out.stdout)
    assert res["years"] == list(range(2018, 2026)) and res["ytd_periods"] == ["2025-ytd", "2026-ytd"]
    t = {row["id"]: row for row in res["topics"]}
    assert t["T1"]["categoria"] == "emergente" and t["T1"]["disciplina"] == "Computer Science"
    assert t["T3"]["categoria"] == "in calo"
    assert t["T1"]["n2025"] == count_for("T1", 2025)
    assert abs(t["T1"]["crescita_ytd"] - 1.0) < 0.01
    assert {f["disciplina"] for f in res["fields"]} == {"Computer Science", "Medicine"}
    assert t["T1"]["parole_chiave"] == "k1, k2"


def test_funded_metrics():
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from trends import funded_metrics
    years = [2022, 2023, 2024, 2025]
    n = {"2022": 1000, "2025": 2000}
    f = {"2022": 100, "2025": 400}
    tot_f = {"2022": 10_000, "2025": 20_000}
    m = funded_metrics(n, f, tot_f, years)
    assert m["finanziati2025"] == 400
    assert m["quota_finanziata"] == 0.2
    assert m["quota_finanziata_base"] == 0.1
    assert m["var_quota_finanziata_3a"] == 1.0
    assert m["crescita_peso_finanziamenti_3a"] == 1.0   # 2% del portafoglio contro 1%
    assert funded_metrics(n, {}, tot_f, years)["var_quota_finanziata_3a"] is None
