"""Finanziamenti pubblici per cluster (livello L3), da data/trends.json.

trends.json contiene, se la fonte funded_topic_counts è stata raccolta, per ogni tema:
finanziati<anno>, quota_finanziata, quota_finanziata_base, var_quota_finanziata_3a,
crescita_peso_finanziamenti_3a. Questo script estrae i temi dei cluster della Fase 2
(nomi esatti dei temi OpenAlex citati in 02_segnali.md), le discipline e i totali.

Uso: python analysis/funding.py data/trends.json -o analysis/results/05_funding.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# Temi citati in 02_segnali.md, per sottostringa (minuscolo) del nome OpenAlex
CLUSTERS = {
    "S1": ["multi-agent systems"],
    "S2": ["ethics and social impacts of ai", "explainable artificial intelligence", "technostress"],
    "S3": ["network security and intrusion", "web application security", "spam and phishing"],
    "S4": ["energy efficiency in computing", "green it"],
    "S5": ["software system performance", "software engineering research", "distributed systems and fault"],
    "S6": ["robot manipulation", "reinforcement learning in robotics"],
    "S7": ["multimodal machine learning"],
    "S8": ["information retrieval and search", "knowledge management and technology"],
    "S9": ["machine learning in materials", "model reduction and neural"],
    "S10": ["quantum computing algorithms"],
    "S11": ["intelligent tutoring"],
    "S12": ["machine learning in healthcare", "digital mental health"],
    "S14": ["satellite communication"],
}
KEYS = ("tema", "disciplina", "crescita_3a", "quota_finanziata", "quota_finanziata_base",
        "var_quota_finanziata_3a", "crescita_peso_finanziamenti_3a")


def pick(row: dict, last: int) -> dict:
    out = {k: row.get(k) for k in KEYS}
    out["paper_ultimo_anno"] = row.get(f"n{last}")
    out["finanziati_ultimo_anno"] = row.get(f"finanziati{last}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("trends", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    t = json.loads(args.trends.read_text())
    last = t["years"][-1]
    topics = t["topics"]
    if not any("quota_finanziata" in r for r in topics):
        raise SystemExit("trends.json non contiene i dati di finanziamento (fonte funded_topic_counts)")
    funded = [r for r in topics if r.get("quota_finanziata") is not None]
    tot_funded = sum(r.get(f"finanziati{last}") or 0 for r in funded)
    tot_papers = sum(r.get(f"n{last}") or 0 for r in topics)

    clusters = {}
    for cl, needles in CLUSTERS.items():
        rows = [pick(r, last) for r in topics if any(n in (r.get("tema") or "").lower() for n in needles)]
        n = sum(r["paper_ultimo_anno"] or 0 for r in rows)
        f = sum(r["finanziati_ultimo_anno"] or 0 for r in rows)
        clusters[cl] = {"temi": rows, "paper_ultimo_anno": n, "finanziati_ultimo_anno": f,
                        "quota_finanziata": round(f / n, 4) if n else None}

    tech = [r for r in funded if r.get("disciplina") in ("Computer Science", "Engineering")
            and (r.get(f"finanziati{last}") or 0) >= 100 and r.get("var_quota_finanziata_3a") is not None]
    result = {
        "anno": last,
        "anni": t["years"],
        "totali_finanziati_per_periodo": t.get("funded_totals"),
        "quota_finanziata_media": round(tot_funded / tot_papers, 4) if tot_papers else None,
        "per_cluster": clusters,
        "discipline": sorted(({"disciplina": r["disciplina"], "quota_finanziata": r.get("quota_finanziata"),
                               "var_quota_finanziata_3a": r.get("var_quota_finanziata_3a"),
                               "crescita_peso_finanziamenti_3a": r.get("crescita_peso_finanziamenti_3a")}
                              for r in t.get("fields", []) if r.get("quota_finanziata") is not None),
                             key=lambda r: -(r["quota_finanziata"] or 0)),
        "tech_peso_finanziamenti_in_crescita": [pick(r, last) for r in sorted(
            tech, key=lambda r: -(r.get("crescita_peso_finanziamenti_3a") or -9))[:25]],
        "tech_quota_finanziata_piu_alta": [pick(r, last) for r in sorted(
            tech, key=lambda r: -(r.get("quota_finanziata") or 0))[:25]],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    pct = lambda v: f"{v:.1%}" if isinstance(v, (int, float)) else "—"
    print(f"quota finanziata media {last}: {pct(result['quota_finanziata_media'])}")
    for cl, c in clusters.items():
        print(f"{cl:4} {pct(c['quota_finanziata']):>7}  {len(c['temi'])} temi")
        for r in c["temi"]:
            print(f"      {r['tema'][:60]:60} q={pct(r['quota_finanziata'])} var3a={r['var_quota_finanziata_3a']} "
                  f"peso3a={r['crescita_peso_finanziamenti_3a']}")


if __name__ == "__main__":
    main()
