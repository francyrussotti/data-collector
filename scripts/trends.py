"""Indicatori di trend per tema e disciplina dai conteggi OpenAlex (config/tech_trends.yaml).

Uso:  python scripts/trends.py -c config/tech_trends.yaml [-o trends.json] [--chunks 3000]

Definizioni (L = ultimo anno intero):
  quota_<anno>     paper del tema / paper di tutti i temi nello stesso anno
  crescita_3a      variazione della quota tra L-3 e L (crescita rispetto a tutta la letteratura)
  crescita_ytd     paper da inizio anno quest'anno / stesso periodo dell'anno scorso - 1
  slancio_ytd      crescita_ytd del tema rispetto a quella di tutta la letteratura
  categoria        vedi classify()
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from collector.config import load_config  # noqa: E402

MIN_BASE = 20         # paper minimi nell'anno di partenza per calcolare una crescita
MIN_LAST = 50         # paper minimi nell'ultimo anno per includere un tema


def classify(n_base: int, n_last: int, cresc3: float | None, slancio: float | None) -> str:
    if n_base < MIN_BASE and n_last >= 200:
        return "nuovo"
    if cresc3 is None:
        return "n.d."
    if cresc3 >= 1.0 and (slancio is None or slancio >= 0.10):
        return "emergente"          # quota almeno raddoppiata in 3 anni e ancora in accelerazione
    if cresc3 >= 0.5:
        return "forte crescita"
    if cresc3 >= 0.15:
        return "in crescita"
    if cresc3 > -0.15:
        return "stabile"
    return "in calo"


def ratio(a, b):
    return a / b - 1 if b else None


def keyword_text(k) -> str:
    """Le parole chiave dei temi possono arrivare come testo o come oggetto."""
    if isinstance(k, dict):
        for name in ("display_name", "keyword", "name"):
            if isinstance(k.get(name), str):
                return k[name]
        return next((v for v in k.values() if isinstance(v, str)), "")
    return str(k)


def rnd(x, n=4):
    return None if x is None else round(x, n)


def load(db: Path):
    conn = sqlite3.connect(db)
    topics = {rid: json.loads(data) for rid, data in conn.execute(
        "SELECT record_id, data FROM records WHERE source='topics'")}
    counts = defaultdict(dict)   # topic_id -> period -> count
    meta = {}                    # period -> (type, year)
    for (data,) in conn.execute("SELECT data FROM records WHERE source='topic_counts'"):
        d = json.loads(data)
        counts[d["topic_id"]][d["period"]] = int(d["count"] or 0)
        meta[d["period"]] = (d["period_type"], int(d["year"]))
    funded = defaultdict(dict)   # stessi conteggi, solo paper con finanziamento (fonte facoltativa)
    for (data,) in conn.execute("SELECT data FROM records WHERE source='funded_topic_counts'"):
        d = json.loads(data)
        funded[d["topic_id"]][d["period"]] = int(d["count"] or 0)
    return topics, counts, meta, funded


def funded_metrics(n: dict, f: dict, tot_f: dict, years: list[int]) -> dict:
    """Paper finanziati del tema: quota sul tema, sua variazione, peso del tema tra tutti i finanziati.

    I collegamenti paper→finanziamento in OpenAlex sono incompleti e arrivano in ritardo:
    i valori assoluti sottostimano, i confronti tra temi nello stesso anno sono più affidabili.
    """
    last, base = years[-1], years[-4]
    fl, fb = f.get(str(last), 0), f.get(str(base), 0)
    nl, nb = n.get(str(last), 0), n.get(str(base), 0)
    q_last = fl / nl if nl else None
    q_base = fb / nb if nb else None
    w_last = fl / tot_f[str(last)] if tot_f.get(str(last)) else None
    w_base = fb / tot_f[str(base)] if tot_f.get(str(base)) else None
    return {f"finanziati{last}": fl,
            "quota_finanziata": rnd(q_last),
            "quota_finanziata_base": rnd(q_base),
            "var_quota_finanziata_3a": rnd(ratio(q_last, q_base) if q_base and fb >= MIN_BASE else None),
            "crescita_peso_finanziamenti_3a": rnd(ratio(w_last, w_base) if w_base and fb >= MIN_BASE else None)}


def metrics(n: dict, tot: dict, years: list[int], ytd: list[str]) -> dict:
    last, base = years[-1], years[-4]
    n_last, n_base = n.get(str(last), 0), n.get(str(base), 0)
    share = {y: (n.get(str(y), 0) / tot[str(y)] if tot.get(str(y)) else 0) for y in years}
    cresc3 = ratio(share[last], share[base]) if n_base >= MIN_BASE else None
    cagr3 = ((n_last / n_base) ** (1 / 3) - 1) if n_base >= MIN_BASE and n_last else None
    out = {f"n{y}": n.get(str(y), 0) for y in years}
    out.update({"quota_base": rnd(share[base], 7), "quota_ultimo": rnd(share[last], 7),
                "crescita_3a": rnd(cresc3), "cagr_3a": rnd(cagr3),
                "crescita_ultimo_anno": rnd(ratio(n_last, n.get(str(last - 1), 0)) if n.get(str(last - 1), 0) >= MIN_BASE else None)})
    slancio = None
    if len(ytd) == 2:
        prev, cur = n.get(ytd[0], 0), n.get(ytd[1], 0)
        out["ytd_prec"], out["ytd_corr"] = prev, cur
        g = ratio(cur, prev) if prev >= MIN_BASE else None
        g_tot = ratio(tot.get(ytd[1], 0), tot.get(ytd[0], 0))
        out["crescita_ytd"] = rnd(g)
        slancio = (1 + g) / (1 + g_tot) - 1 if g is not None and g_tot is not None and g_tot > -1 else None
        out["slancio_ytd"] = rnd(slancio)
    out["categoria"] = classify(n_base, n_last, cresc3, slancio)
    return out


def build(db: Path) -> dict:
    topics, counts, meta, funded = load(db)
    years = sorted(y for t, y in meta.values() if t == "year")
    ytd = [p for p, _ in sorted(((p, y) for p, (t, y) in meta.items() if t == "ytd"), key=lambda x: x[1])]
    if len(years) < 4:
        raise SystemExit("servono almeno 4 anni interi di conteggi")
    tot = defaultdict(int)
    for per_topic in counts.values():
        for period, c in per_topic.items():
            tot[period] += c

    tot_f = defaultdict(int)
    for per_topic in funded.values():
        for period, c in per_topic.items():
            tot_f[period] += c

    rows = []
    by_field = defaultdict(lambda: defaultdict(int))
    by_field_f = defaultdict(lambda: defaultdict(int))
    field_domain = {}
    for tid, n in counts.items():
        t = topics.get(tid, {})
        field = t.get("field") or "Sconosciuto"
        field_domain[field] = t.get("domain")
        for period, c in n.items():
            by_field[field][period] += c
        for period, c in funded.get(tid, {}).items():
            by_field_f[field][period] += c
        if n.get(str(years[-1]), 0) < MIN_LAST:
            continue
        row = {"id": tid, "tema": t.get("name") or tid, "sottocampo": t.get("subfield"),
               "disciplina": field, "dominio": t.get("domain"),
               "parole_chiave": ", ".join(filter(None, map(keyword_text, (t.get("keywords") or [])[:6]))),
               **metrics(n, tot, years, ytd)}
        if funded:
            row.update(funded_metrics(n, funded.get(tid, {}), tot_f, years))
        rows.append(row)
    fields = [{"disciplina": f, "dominio": field_domain.get(f), **metrics(n, tot, years, ytd),
               **(funded_metrics(n, by_field_f.get(f, {}), tot_f, years) if funded else {})}
              for f, n in by_field.items()]
    totals = [{"periodo": p, "tipo": meta[p][0], "anno": meta[p][1], "paper": tot[p]} for p in sorted(tot)]
    return {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "years": years, "ytd_periods": ytd, "totals": totals,
            "topics": sorted(rows, key=lambda r: -(r[f"n{years[-1]}"])), "fields": fields,
            "topics_in_db": len(topics), "topics_with_counts": len(counts),
            "funded_totals": {p: tot_f[p] for p in sorted(tot_f)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", required=True)
    ap.add_argument("-o", "--out")
    ap.add_argument("--chunks", type=int, default=0, help="stampa il JSON in righe 'TRENDS|n|...' (log CI)")
    args = ap.parse_args()
    cfg = load_config(args.config)
    result = build(cfg.database)
    text = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    if args.chunks:
        for i in range(0, len(text), args.chunks):
            print(f"TRENDS|{i // args.chunks:04d}|{text[i:i + args.chunks]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
