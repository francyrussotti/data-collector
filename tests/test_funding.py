import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_funding_per_cluster(tmp_path):
    trends = {"years": [2022, 2023, 2024, 2025], "funded_totals": {"2025": 300},
              "topics": [
                  {"tema": "Quantum Computing Algorithms and Architecture", "disciplina": "Computer Science",
                   "n2025": 1000, "finanziati2025": 200, "quota_finanziata": 0.2, "var_quota_finanziata_3a": -0.1,
                   "crescita_peso_finanziamenti_3a": 0.4},
                  {"tema": "Other", "disciplina": "Engineering", "n2025": 1000, "finanziati2025": 100,
                   "quota_finanziata": 0.1, "var_quota_finanziata_3a": 0.0, "crescita_peso_finanziamenti_3a": 0.0}],
              "fields": [{"disciplina": "Computer Science", "quota_finanziata": 0.2}]}
    src = tmp_path / "trends.json"
    src.write_text(json.dumps(trends))
    out = tmp_path / "f.json"
    subprocess.run([sys.executable, str(ROOT / "analysis" / "funding.py"), str(src), "-o", str(out)], check=True,
                   capture_output=True)
    r = json.loads(out.read_text())
    assert r["quota_finanziata_media"] == 0.15
    assert r["per_cluster"]["S10"]["quota_finanziata"] == 0.2
    assert r["per_cluster"]["S1"]["temi"] == []
    assert r["tech_peso_finanziamenti_in_crescita"][0]["tema"].startswith("Quantum")
