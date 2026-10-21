"""Temi emergenti: scelta dei temi e selezione di paper da leggere.

  python scripts/emerging.py select --trends data/trends.json --out data/emerging_topics.json
      Sceglie fino a --limit temi delle discipline tecnologiche con categoria emergente, nuovo
      o forte crescita, escludendo i salti sospetti (stessa regola della dashboard).
      Scrive l'elenco degli id (per config/emerging.yaml) e accanto <out>.meta.json con i dettagli.

  python scripts/emerging.py digest -c config/emerging.yaml --topics data/emerging_topics.json
      Per ogni tema: i paper più citati e i più recenti già raccolti, con un estratto dell'abstract.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from collector.config import load_config  # noqa: E402

TECH_FIELDS = {
    "Computer Science", "Engineering", "Materials Science", "Energy", "Chemical Engineering",
    "Physics and Astronomy", "Chemistry", "Mathematics", "Decision Sciences",
    "Biochemistry, Genetics and Molecular Biology", "Environmental Science",
}
PRIORITY = {"emergente": 0, "nuovo": 1, "forte crescita": 2}


def suspicious(t: dict) -> bool:
    """Salti troppo bruschi per essere solo crescita: probabile riclassificazione o nuove fonti."""
    c3, sl = t.get("crescita_3a"), t.get("slancio_ytd")
    return (c3 is not None and c3 > 4) or (sl is not None and sl > 2)


def select(trends: dict, limit: int) -> list[dict]:
    chosen = [t for t in trends["topics"]
              if t["disciplina"] in TECH_FIELDS and t["categoria"] in PRIORITY and not suspicious(t)]
    chosen.sort(key=lambda t: (PRIORITY[t["categoria"]], -(t.get("crescita_3a") or 0)))
    return chosen[:limit]


def digest(db: Path, topics: list[dict], per_list: int, abstract_chars: int) -> list[dict]:
    conn = sqlite3.connect(db)
    out = []
    orders = {"emerging_cited": "CAST(json_extract(data,'$.cited_by_count') AS INTEGER) DESC",
              "emerging_recent": "json_extract(data,'$.published_date') DESC"}
    for t in topics:
        for source, order in orders.items():
            rows = conn.execute(
                f"SELECT record_id, data FROM records WHERE source=? AND json_extract(data,'$.primary_topic_id')=? "
                f"ORDER BY {order} LIMIT ?", (source, t["id"], per_list)).fetchall()
            for rank, (rid, data) in enumerate(rows, 1):
                d = json.loads(data)
                abstract = d.get("abstract") or ""
                out.append({
                    "id": f"{source}|{rid}", "tema_id": t["id"], "tema": t["tema"],
                    "lista": "più citati" if source == "emerging_cited" else "più recenti", "posizione": rank,
                    "titolo": d.get("title"), "anno": d.get("year"), "data": d.get("published_date"),
                    "citazioni": d.get("cited_by_count"), "doi": d.get("doi"), "venue": d.get("venue"),
                    "link": d.get("landing_page_url") or (f"https://doi.org/{d['doi']}" if d.get("doi") else None),
                    "estratto": abstract[:abstract_chars] + ("…" if len(abstract) > abstract_chars else ""),
                })
    return out


def emit(obj, out: str | None, chunks: int, tag: str) -> None:
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    if out:
        Path(out).write_text(text, encoding="utf-8")
    if chunks:
        for i in range(0, len(text), chunks):
            print(f"{tag}|{i // chunks:04d}|{text[i:i + chunks]}")
    elif not out:
        print(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--trends", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--limit", type=int, default=50)
    d = sub.add_parser("digest")
    d.add_argument("-c", "--config", required=True)
    d.add_argument("--topics", required=True, help="il file .meta.json scritto da select")
    d.add_argument("--per-list", type=int, default=5)
    d.add_argument("--abstract-chars", type=int, default=400)
    d.add_argument("-o", "--out")
    d.add_argument("--chunks", type=int, default=0)
    args = ap.parse_args()

    if args.cmd == "select":
        chosen = select(json.loads(Path(args.trends).read_text(encoding="utf-8")), args.limit)
        Path(args.out).write_text(json.dumps([t["id"] for t in chosen]), encoding="utf-8")
        meta = [{k: t.get(k) for k in ("id", "tema", "sottocampo", "disciplina", "categoria", "crescita_3a",
                                       "crescita_ytd", "parole_chiave")} | {"paper_ultimo_anno": t[f"n{max(int(k[1:]) for k in t if k[:1] == 'n' and k[1:].isdigit())}"]}
                for t in chosen]
        Path(args.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        print(f"scelti {len(chosen)} temi → {args.out}")
    else:
        cfg = load_config(args.config)
        topics = json.loads(Path(args.topics).read_text(encoding="utf-8"))
        emit({"temi": topics, "paper": digest(cfg.database, topics, args.per_list, args.abstract_chars)},
             args.out, args.chunks, "EMERGING")
    return 0


if __name__ == "__main__":
    sys.exit(main())
