import importlib.util
import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_signals", ROOT / "analysis" / "validate_signals.py")
vs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vs)


def _quarters(n_closed):
    out, y, q = [], 2024, 1
    for _ in range(n_closed):
        out.append(f"{y}-Q{q}")
        q += 1
        if q == 5:
            y, q = y + 1, 1
    return out


def test_count_growth_normalized_on_base():
    rows = []
    for i, p in enumerate(_quarters(8)):
        recent = i >= 4
        rows.append({"query_id": "a", "query": "a", "cluster": "S1", "period": p, "partial": False,
                     "count": 300 if recent else 100})
        rows.append({"query_id": "b", "query": "b", "cluster": "BASE", "period": p, "partial": False,
                     "count": 150 if recent else 100})
    rows.append({"query_id": "a", "query": "a", "cluster": "S1", "period": "2026-Q1", "partial": True, "count": 999})
    res = vs.count_growth(rows)
    assert res["crescita_base"] == 0.5
    assert res["per_cluster"]["S1"]["crescita"] == 2.0
    assert res["per_cluster"]["S1"]["crescita_vs_base"] == 1.0  # 3 / 1.5 - 1
    assert "2026-Q1" not in res["finestra_ultimi"]


def test_count_growth_needs_enough_quarters():
    rows = [{"query_id": "a", "cluster": "S1", "period": p, "partial": False, "count": 1} for p in _quarters(5)]
    assert "errore" in vs.count_growth(rows)


def test_pypi_and_wiki_and_summary(tmp_path):
    start = date(2026, 4, 1)
    rows = []
    for d in range(180):
        day = (start + timedelta(days=d)).isoformat()
        rows.append({"package": "x", "cluster": "S1", "date": day, "category": "without_mirrors",
                     "downloads": 20 if d >= 90 else 10})
        rows.append({"package": "base", "cluster": "BASE", "date": day, "category": "without_mirrors",
                     "downloads": 10})
        rows.append({"package": "x", "cluster": "S1", "date": day, "category": "with_mirrors", "downloads": 999})
    p = vs.pypi_growth(rows)
    assert p["per_libreria"]["x"]["crescita"] == 1.0
    assert p["per_cluster"]["S1"]["mediana_vs_base"] == 1.0

    wiki = []
    for i in range(26):  # 2024-08 .. 2026-09, più il mese in corso
        y, m = 2024 + (7 + i) // 12, (7 + i) % 12 + 1
        recent = i >= 14
        wiki.append({"article": "A", "cluster": "S8", "timestamp": f"{y}{m:02d}0100", "views": 200 if recent else 100})
        wiki.append({"article": "B", "cluster": "BASE", "timestamp": f"{y}{m:02d}0100", "views": 100})
    wiki.append({"article": "A", "cluster": "S8", "timestamp": "2026100100", "views": 1})
    w = vs.wiki_growth(wiki, date(2026, 10, 21))
    assert w["finestra_ultimi"] == ["202510", "202609"]
    assert w["per_voce"]["A"]["crescita"] == 1.0

    # end to end sul database
    db = tmp_path / "fs.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE records (source TEXT, record_id TEXT, data TEXT)")
    for i, r in enumerate(rows):
        con.execute("INSERT INTO records VALUES (?,?,?)", ("pypi_downloads", str(i), json.dumps(r)))
    for i, r in enumerate(wiki):
        con.execute("INSERT INTO records VALUES (?,?,?)", ("wiki_pageviews", str(i), json.dumps(r)))
    con.commit()
    con.close()
    out = tmp_path / "out.json"
    import sys
    sys.argv = ["x", str(db), "-o", str(out), "--today", "2026-10-21"]
    vs.main()
    s = json.loads(out.read_text())["sintesi"]
    assert s["S1"]["pypi_downloads"] == 1.0
    assert s["S8"]["wiki_pageviews"] == 1.0
    assert s["S8"]["fonti_positive"] == 1
