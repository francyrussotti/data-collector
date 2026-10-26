import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verticals as v  # noqa: E402

TRENDS = {
    "years": [2022, 2023, 2024, 2025], "ytd_periods": ["2025-ytd", "2026-ytd"],
    "totals": [{"periodo": "2022", "paper": 1000}, {"periodo": "2025", "paper": 2000},
               {"periodo": "2025-ytd", "paper": 1500}, {"periodo": "2026-ytd", "paper": 1500}],
    "topics": [
        {"tema": "Spacecraft Dynamics and Control", "disciplina": "Engineering", "n2022": 10, "n2025": 40,
         "ytd_prec": 30, "ytd_corr": 45, "crescita_3a": 1.0, "categoria": "forte crescita"},
        {"tema": "Ocean Waves and Remote Sensing", "disciplina": "Earth and Planetary Sciences", "n2022": 5, "n2025": 5},
        {"tema": "Satellite marketing", "disciplina": "Business, Management and Accounting", "n2022": 5, "n2025": 5},
    ],
}
SPEC = {"nome": "Aerospazio", "sottocampi": [], "nome_regex": "spacecraft|satellite|ocean",
        "discipline": ["Engineering", "Earth and Planetary Sciences"], "escludi": "ocean waves", "cluster": ["V_AERO"],
        "wiki": ["Small_satellite"]}


def test_match_and_research():
    m = v.match_topics(TRENDS["topics"], SPEC)
    assert [t["tema"] for t in m] == ["Spacecraft Dynamics and Control"]   # escluso e disciplina sbagliata
    r = v.research(TRENDS, SPEC)
    assert r["paper_ultimo_anno"] == 40
    assert r["peso_3_anni"] == 1.0          # quota 1% -> 2%
    assert r["slancio_anno_in_corso"] == 0.5  # +50% contro totale stabile


def test_adoption_wiki_and_weekday(tmp_path):
    db = tmp_path / "fs.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE records (source TEXT, record_id TEXT, data TEXT, last_seen_at TEXT)")
    rows = []
    for q, cl, a, b in (("satellite", "V_AERO", 100, 300), ("machine learning", "BASE", 100, 150)):
        rows += [("github_repos", {"query_id": q, "query": q, "cluster": cl, "period": "2025-Q3", "partial": False, "count": a}),
                 ("github_repos", {"query_id": q, "query": q, "cluster": cl, "period": "2026-Q3", "partial": False, "count": b})]
    for i in range(24):
        y, m = 2024 + (9 + i) // 12, (9 + i) % 12 + 1
        rows.append(("wiki_pageviews", {"article": "Small_satellite", "timestamp": f"{y}{m:02d}0100", "views": 200 if i >= 12 else 100}))
    for i, (s, d) in enumerate(rows):
        con.execute("INSERT INTO records VALUES (?,?,?,?)", (s, str(i), json.dumps(d), "2026-10-21T22:00:00"))
    con.commit()
    con.close()
    a = v.adoption(db, ["V_AERO"])["fonti"]["github_repos"]
    assert a["query"][0]["anno_su_anno"] == 2.0 and a["query"][0]["rispetto_al_controllo"] == 1.0
    w = v.wiki(db, ["Small_satellite"], date(2026, 10, 23))
    assert w[0]["variazione"] == 1.0
    cfg = {"giorni": {0: "aero", 1: "aero", 2: "aero", 3: "aero", 4: "aero", 5: "panoramica", 6: "panoramica"},
           "verticali": {"aero": SPEC}}
    assert v.radar(date(2026, 10, 23), cfg, TRENDS, db)["tipo"] == "verticale"     # venerdì
    p = v.radar(date(2026, 10, 24), cfg, TRENDS, db)                                  # sabato
    assert p["tipo"] == "panoramica" and p["verticali"][0]["github_mediana_anno_su_anno"] == 2.0


def test_real_config_loads():
    cfg = v.load_config(ROOT / "config" / "verticals.yaml")
    assert set(cfg["giorni"].values()) == set(cfg["verticali"]) | {"panoramica"}
    topics = [{"tema": "Quantum Information and Cryptography", "disciplina": "Computer Science"},
              {"tema": "Cryptography and Data Security", "disciplina": "Computer Science"}]
    assert [t["tema"] for t in v.match_topics(topics, cfg["verticali"]["cyber"])] == ["Cryptography and Data Security"]


def test_topics_for_day_and_cli(tmp_path):
    trends = dict(TRENDS, topics=[dict(t, id=f"T{i}") for i, t in enumerate(TRENDS["topics"])])
    other = dict(SPEC, nome="Altro", nome_regex="satellite marketing", discipline=[], escludi="")
    cfg = {"giorni": {0: "aero", 1: "altro", 2: "aero", 3: "aero", 4: "aero", 5: "panoramica", 6: "panoramica"},
           "verticali": {"aero": SPEC, "altro": other}}
    mon = v.topics_for_day(date(2026, 10, 26), cfg, trends)
    assert [t["id"] for t in mon] == ["T0"] and mon[0]["verticale"] == "aero"
    sat = v.topics_for_day(date(2026, 10, 24), cfg, trends)
    assert {t["id"] for t in sat} == {"T0", "T2"}

    import subprocess
    tp = tmp_path / "trends.json"
    tp.write_text(json.dumps(trends))
    out, meta = tmp_path / "ids.json", tmp_path / "meta.json"
    subprocess.run([sys.executable, str(ROOT / "scripts" / "verticals.py"), "--trends", str(tp), "--date", "2026-10-23",
                    "-o", str(out), "--meta", str(meta)], check=True, capture_output=True)
    assert isinstance(json.loads(out.read_text()), list)
    # senza trends.json: lista vuota, nessun errore
    subprocess.run([sys.executable, str(ROOT / "scripts" / "verticals.py"), "--trends", str(tmp_path / "manca.json"),
                    "--date", "2026-10-23", "-o", str(out), "--meta", str(meta)], check=True, capture_output=True)
    assert json.loads(out.read_text()) == []


def test_daily_vertical_section(tmp_path):
    import daily
    db = tmp_path / "daily.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE records (source TEXT, record_id TEXT, data TEXT, first_seen_at TEXT)")
    rec = {"title": "Robot paper", "primary_topic_id": "T9", "venue": "Science Robotics", "language": "en",
           "abstract": "x", "published_date": "2026-10-22", "doi": "10.1/x"}
    con.execute("INSERT INTO records VALUES (?,?,?,?)", ("daily_vertical", "W1", json.dumps(rec), "2026-10-23T05:00:00"))
    con.execute("INSERT INTO records VALUES (?,?,?,?)", ("daily_emerging", "W2", json.dumps(rec), "2026-10-23T05:00:00"))
    con.commit()
    con.close()
    topics = [{"id": "T9", "tema": "Robot Manipulation", "verticale": "robotica", "crescita_3a": 0.6}]
    s = daily.emerging_section(db, topics, "2026-10-23", 3, 500, source="daily_vertical")
    assert s["nuovi_oggi"] == 1 and s["per_tema"][0]["verticale"] == "robotica"
