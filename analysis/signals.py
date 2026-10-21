"""Fase 2 – Analisi dei segnali.

Uso:  python analysis/signals.py --data data -o analysis/results/02_signals.json [--chunks 3000]

Legge dalla cartella --data: trends.sqlite (conteggi per tema), papers.sqlite (corpus LLM),
emerging.sqlite (campioni dei temi emergenti). Ogni blocco è indipendente: se un database manca,
il blocco viene saltato e segnalato.

A. Crescita (universo OpenAlex): quota di ogni tema e sottocampo sul totale, crescita 3 e 6 anni,
   accelerazione, slancio da inizio anno, costanza; punteggio composito per rango.
B. Velocità di citazione (campioni): citazioni al mese dei paper 2024–metà 2025, per tema.
C. Nuovi cluster: parole chiave in crescita nel corpus LLM (popolazione della ricerca) e parole
   chiave più frequenti nei paper recenti rispetto ai più citati, nei temi emergenti.
D. Convergenza: paper i cui temi appartengono a discipline diverse; coppie di discipline in crescita.
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

MIN_LAST = 200        # paper minimi nell'ultimo anno intero per entrare nella classifica dei temi
MIN_BASE = 20         # paper minimi nell'anno base per calcolare una crescita


def suspicious(g3, ytd_rel) -> bool:
    return (g3 is not None and g3 > 4) or (ytd_rel is not None and ytd_rel > 2)


def ratio(a, b):
    return a / b - 1 if b else None


def rnd(x, n=4):
    return None if x is None else round(x, n)


def pct_rank(values: dict) -> dict:
    """Rango percentile (0–1) dei valori non nulli; i nulli valgono 0."""
    items = sorted((v, k) for k, v in values.items() if v is not None)
    n = len(items)
    out = {k: 0.0 for k in values}
    for i, (_, k) in enumerate(items):
        out[k] = (i + 1) / n
    return out


# ---------------------------------------------------------------- A. crescita
def growth_block(db: Path) -> dict:
    conn = sqlite3.connect(db)
    topics = {rid: json.loads(d) for rid, d in conn.execute("SELECT record_id, data FROM records WHERE source='topics'")}
    counts = defaultdict(dict)
    meta = {}
    for (d,) in conn.execute("SELECT data FROM records WHERE source='topic_counts'"):
        r = json.loads(d)
        counts[r["topic_id"]][r["period"]] = int(r["count"] or 0)
        meta[r["period"]] = (r["period_type"], int(r["year"]))
    years = sorted(y for t, y in meta.values() if t == "year")
    ytd = [p for p, _ in sorted(((p, y) for p, (t, y) in meta.items() if t == "ytd"), key=lambda x: x[1])]
    L = years[-1]
    tot = Counter()
    for c in counts.values():
        for p, v in c.items():
            tot[p] += v

    def metrics(c: dict) -> dict:
        share = {y: c.get(str(y), 0) / tot[str(y)] for y in years}
        n = {y: c.get(str(y), 0) for y in years}
        g3 = ratio(share[L], share[L - 3]) if n[L - 3] >= MIN_BASE else None
        g6 = ratio(share[L], share[L - 6]) if L - 6 in share and n[L - 6] >= MIN_BASE else None
        g_last = ratio(share[L], share[L - 1]) if n[L - 1] >= MIN_BASE else None
        g_prev = ((share[L - 1] / share[L - 3]) ** 0.5 - 1) if n[L - 3] >= MIN_BASE and share[L - 3] else None
        accel = g_last - g_prev if g_last is not None and g_prev is not None else None
        ytd_rel = None
        if len(ytd) == 2 and c.get(ytd[0], 0) >= MIN_BASE and tot[ytd[0]]:
            ytd_rel = (c.get(ytd[1], 0) / c[ytd[0]]) / (tot[ytd[1]] / tot[ytd[0]]) - 1
        steady = sum(1 for y in range(L - 2, L + 1) if share[y] > share[y - 1])
        return {"n": n, "quota_ultimo": share[L], "crescita_3a": g3, "crescita_6a": g6, "crescita_ultimo_anno": g_last,
                "accelerazione": accel, "slancio_ytd": ytd_rel, "anni_in_crescita_su_3": steady}

    def rank(rows: dict) -> dict:
        """Punteggio composito per rango: crescita 3a 40%, slancio 2026 25%, accelerazione 20%, costanza 15%."""
        r3 = pct_rank({k: (math.log1p(v["crescita_3a"]) if v["crescita_3a"] is not None else None) for k, v in rows.items()})
        ry = pct_rank({k: v["slancio_ytd"] for k, v in rows.items()})
        ra = pct_rank({k: v["accelerazione"] for k, v in rows.items()})
        for k, v in rows.items():
            v["punteggio"] = round(0.40 * r3[k] + 0.25 * ry[k] + 0.20 * ra[k] + 0.15 * v["anni_in_crescita_su_3"] / 3, 4)
        return rows

    # temi
    trows = {}
    flagged = []
    new_topics = []
    for tid, c in counts.items():
        m = metrics(c)
        t = topics.get(tid, {})
        info = {"id": tid, "tema": t.get("name") or tid, "sottocampo": t.get("subfield"), "disciplina": t.get("field"),
                "dominio": t.get("domain")}
        if m["n"][L - 6 if L - 6 in m["n"] else years[0]] < MIN_BASE and m["n"][L] >= MIN_LAST:
            new_topics.append(info | {"n": m["n"]})
        if m["n"][L] < MIN_LAST:
            continue
        if suspicious(m["crescita_3a"], m["slancio_ytd"]):
            flagged.append(info | {"crescita_3a": rnd(m["crescita_3a"]), "slancio_ytd": rnd(m["slancio_ytd"])})
            continue
        trows[tid] = info | m
    rank(trows)

    # sottocampi (somma dei temi, esclusi i temi sospetti per non contaminare l'aggregato)
    sub_counts = defaultdict(Counter)
    sub_info = {}
    flagged_ids = {f["id"] for f in flagged}
    for tid, c in counts.items():
        if tid in flagged_ids:
            continue
        t = topics.get(tid, {})
        key = t.get("subfield") or "?"
        sub_info[key] = {"sottocampo": key, "disciplina": t.get("field"), "dominio": t.get("domain")}
        for p, v in c.items():
            sub_counts[key][p] += v
    srows = {k: sub_info[k] | metrics(c) for k, c in sub_counts.items() if c.get(str(L), 0) >= MIN_LAST * 5}
    rank(srows)

    def clean(r):
        out = {k: (rnd(v) if isinstance(v, float) else v) for k, v in r.items() if k != "n"}
        out["paper"] = {str(y): r["n"][y] for y in years}
        return out

    top = sorted(trows.values(), key=lambda r: -r["punteggio"])
    return {
        "anni": years, "periodi_ytd": ytd, "totali": {p: tot[p] for p in sorted(tot)},
        "metodo": "quota = paper del tema / paper con tema nello stesso periodo; punteggio = 0.40·rango(crescita quota 3a) "
                  "+ 0.25·rango(slancio 2026 vs 2025 alla stessa data, relativo al totale) + 0.20·rango(accelerazione) "
                  "+ 0.15·anni in crescita su 3. Esclusi temi con meno di %d paper nell'ultimo anno e salti sospetti." % MIN_LAST,
        "temi_valutati": len(trows), "temi_sospetti_esclusi": len(flagged),
        "temi_top": [clean(r) for r in top[:80]],
        "temi_in_calo": [clean(r) for r in sorted(trows.values(), key=lambda r: r["crescita_3a"] if r["crescita_3a"] is not None else 9)[:40]],
        "sottocampi": [clean(r) for r in sorted(srows.values(), key=lambda r: -r["punteggio"])],
        "temi_nuovi": [{**{k: v for k, v in r.items() if k != "n"}, "paper": {str(y): r["n"][y] for y in years}} for r in new_topics],
        "temi_sospetti": flagged,
    }


# ---------------------------------------------------- B. velocità di citazione
def months_between(d: str, ref: date) -> float:
    try:
        p = date.fromisoformat(d[:10])
    except ValueError:
        return 0
    return (ref - p).days / 30.44


def velocity_block(dbs: dict[str, Path], ref: date, topic_names: dict) -> dict:
    out = {}
    for label, (db, source) in dbs.items():
        if not db.exists():
            out[label] = {"saltato": f"manca {db.name}"}
            continue
        conn = sqlite3.connect(db)
        per_topic = defaultdict(list)
        papers = []
        for (d,) in conn.execute("SELECT data FROM records WHERE source=?", (source,)):
            r = json.loads(d)
            pd = r.get("published_date") or ""
            if not ("2024-01-01" <= pd <= "2025-06-30"):
                continue
            m = months_between(pd, ref)
            if m < 3:
                continue
            v = (r.get("cited_by_count") or 0) / m
            tid = r.get("primary_topic_id") or r.get("primary_topic")
            per_topic[tid].append(v)
            papers.append((v, r))
        rows = []
        for tid, vs in per_topic.items():
            if len(vs) < 15:
                continue
            rows.append({"tema": topic_names.get(tid, tid), "paper": len(vs), "citazioni_mese_mediana": round(statistics.median(vs), 2),
                         "citazioni_mese_p90": round(sorted(vs)[int(0.9 * (len(vs) - 1))], 2)})
        papers.sort(key=lambda x: -x[0])
        out[label] = {
            "finestra": "pubblicati 2024-01-01 → 2025-06-30, citazioni al mese fino al %s" % ref.isoformat(),
            "per_tema": sorted(rows, key=lambda r: -r["citazioni_mese_mediana"]),
            "paper_piu_veloci": [{"citazioni_mese": round(v, 1), "titolo": r.get("title"), "data": r.get("published_date"),
                                  "citazioni": r.get("cited_by_count"), "tema": topic_names.get(r.get("primary_topic_id"), r.get("primary_topic")),
                                  "sede": r.get("venue"), "doi": r.get("doi")} for v, r in papers[:40]],
        }
    return out


# ------------------------------------------------------------- C. nuovi cluster
def keyword_block(papers_db: Path, emerging_db: Path) -> dict:
    out = {}
    if papers_db.exists():
        conn = sqlite3.connect(papers_db)
        per_year = defaultdict(Counter)
        n_year = Counter()
        for (d,) in conn.execute("SELECT data FROM records WHERE source='openalex_llm'"):
            r = json.loads(d)
            y = (r.get("published_date") or "")[:4]
            if not y:
                continue
            n_year[y] += 1
            for k in set(r.get("keywords") or []):
                per_year[y][k.lower()] += 1
        rows = []
        for k, c26 in per_year["2026"].items():
            if c26 < 100:
                continue
            s24 = per_year["2024"][k] / n_year["2024"] if n_year["2024"] else 0
            s26 = c26 / n_year["2026"]
            rows.append({"parola_chiave": k, "paper_2026": c26, "paper_2024": per_year["2024"][k],
                         "quota_2024_pct": round(100 * s24, 2), "quota_2026_pct": round(100 * s26, 2),
                         "rapporto_quota": round(s26 / s24, 2) if s24 else None})
        rising = sorted((r for r in rows if r["rapporto_quota"]), key=lambda r: -r["rapporto_quota"])
        new = sorted((r for r in rows if r["paper_2024"] < 10), key=lambda r: -r["paper_2026"])
        out["llm"] = {"paper_per_anno": dict(sorted(n_year.items())), "in_crescita": rising[:40], "nuove": new[:25],
                      "metodo": "quota = paper con la parola chiave / paper dell'anno nel corpus LLM; solo parole con almeno 100 paper nel 2026"}
    else:
        out["llm"] = {"saltato": "manca papers.sqlite"}
    if emerging_db.exists():
        conn = sqlite3.connect(emerging_db)
        cnt = {"emerging_cited": Counter(), "emerging_recent": Counter()}
        n = Counter()
        for source in cnt:
            for (d,) in conn.execute("SELECT data FROM records WHERE source=?", (source,)):
                r = json.loads(d)
                n[source] += 1
                for k in set(r.get("keywords") or []):
                    cnt[source][k.lower()] += 1
        rows = []
        for k, cr in cnt["emerging_recent"].items():
            if cr < 30:
                continue
            sr, sc = cr / n["emerging_recent"], cnt["emerging_cited"][k] / n["emerging_cited"]
            rows.append({"parola_chiave": k, "paper_recenti": cr, "paper_citati": cnt["emerging_cited"][k],
                         "rapporto": round(sr / sc, 2) if sc else None})
        out["temi_emergenti"] = {
            "metodo": "frequenza nei 10.000 paper più recenti (2026) rispetto ai 10.000 più citati (2024–25) degli stessi 50 temi; "
                      "rapporto > 1 = parola più presente nella ricerca nuova. Esplorativo: i due campioni non sono casuali.",
            "piu_nuove": sorted((r for r in rows if r["rapporto"]), key=lambda r: -r["rapporto"])[:40],
            "solo_nei_recenti": sorted((r for r in rows if not r["rapporto"]), key=lambda r: -r["paper_recenti"])[:20],
        }
    return out


# ------------------------------------------------------------- D. convergenza
def convergence_block(dbs: dict[str, Path], topic_field: dict) -> dict:
    out = {}
    for label, (db, sources) in dbs.items():
        if not db.exists():
            out[label] = {"saltato": f"manca {db.name}"}
            continue
        conn = sqlite3.connect(db)
        by_period = defaultdict(lambda: {"paper": 0, "multi": 0, "coppie": Counter()})
        for source in sources:
            for (d,) in conn.execute("SELECT data FROM records WHERE source=?", (source,)):
                r = json.loads(d)
                y = (r.get("published_date") or "")[:4]
                if not y:
                    continue
                period = y if y >= "2023" else "2018-2022"
                fields = sorted({topic_field[t] for t in (r.get("topics") or []) if t in topic_field})
                b = by_period[period]
                b["paper"] += 1
                if len(fields) > 1:
                    b["multi"] += 1
                    for i in range(len(fields)):
                        for j in range(i + 1, len(fields)):
                            b["coppie"][f"{fields[i]} + {fields[j]}"] += 1
        periods = sorted(by_period)
        summary = {p: {"paper": b["paper"], "multidisciplinari_pct": round(100 * b["multi"] / b["paper"], 1) if b["paper"] else None,
                       "coppie_top": b["coppie"].most_common(10)} for p, b in by_period.items()}
        rising = []
        if "2024" in by_period and "2026" in by_period:
            a, z = by_period["2024"], by_period["2026"]
            for pair, c in z["coppie"].items():
                if c < 30:
                    continue
                s24 = a["coppie"][pair] / a["paper"] if a["paper"] else 0
                s26 = c / z["paper"]
                rising.append({"coppia": pair, "paper_2026": c, "paper_2024": a["coppie"][pair],
                               "rapporto_quota": round(s26 / s24, 2) if s24 else None})
        out[label] = {"per_periodo": {p: summary[p] for p in periods},
                      "coppie_in_crescita_2024_2026": sorted((r for r in rising if r["rapporto_quota"]), key=lambda r: -r["rapporto_quota"])[:25]}
    out["metodo"] = ("un paper è multidisciplinare se i suoi temi (fino a 3, assegnati da OpenAlex) appartengono a più discipline. "
                     "Misura possibile solo sui campioni: per l'intero corpus servirebbero conteggi per coppie di temi.")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data")
    ap.add_argument("-o", "--out")
    ap.add_argument("--chunks", type=int, default=0)
    args = ap.parse_args()
    data = Path(args.data)
    ref = datetime.now(timezone.utc).date()
    result = {"generato_il": ref.isoformat()}

    topic_names, topic_field = {}, {}
    if (data / "trends.sqlite").exists():
        conn = sqlite3.connect(data / "trends.sqlite")
        for rid, d in conn.execute("SELECT record_id, data FROM records WHERE source='topics'"):
            t = json.loads(d)
            topic_names[rid] = t.get("name")
            if t.get("name"):
                topic_field[t["name"]] = t.get("field")
        result["A_crescita"] = growth_block(data / "trends.sqlite")
    else:
        result["A_crescita"] = {"saltato": "manca trends.sqlite"}

    result["B_velocita_citazioni"] = velocity_block(
        {"temi_emergenti_piu_citati": (data / "emerging.sqlite", "emerging_cited"),
         "corpus_llm": (data / "papers.sqlite", "openalex_llm")}, ref, topic_names)
    result["C_nuovi_cluster"] = keyword_block(data / "papers.sqlite", data / "emerging.sqlite")
    result["D_convergenza"] = convergence_block(
        {"corpus_llm": (data / "papers.sqlite", ["openalex_llm"]),
         "temi_emergenti": (data / "emerging.sqlite", ["emerging_cited", "emerging_recent"])}, topic_field)

    text = json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    if args.chunks:
        for i in range(0, len(text), args.chunks):
            print(f"RESULT|{i // args.chunks:04d}|{text[i:i + args.chunks]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
