"""Fase 3/4 – validazione dei cluster con i segnali gratuiti di adozione e attenzione.

Legge data/free_signals.sqlite (config/free_signals.yaml) e calcola, per ogni cluster S1–S10:
- GitHub (nuovi repository) e Hacker News (storie): ultimi 4 trimestri chiusi vs i 4 precedenti;
- grant NSF: stesso confronto;
- download PyPI: media giornaliera degli ultimi 90 giorni vs i primi 90 disponibili;
- visite Wikipedia: ultimi 12 mesi completi vs i 12 precedenti.
Ogni crescita è anche normalizzata sul controllo BASE della stessa fonte: (1 + g) / (1 + g_base) - 1.
Così un +40% quando tutto cresce del +40% vale 0.

Uso: python analysis/validate_signals.py data/free_signals.sqlite -o analysis/results/03_validation.json
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

COUNT_SOURCES = ("github_repos", "hn_stories", "nsf_awards")
BASE = "BASE"


def load(db: Path) -> dict[str, list[dict]]:
    con = sqlite3.connect(db)
    out = defaultdict(list)
    for source, data in con.execute("SELECT source, data FROM records"):
        out[source].append(json.loads(data))
    con.close()
    return out


def growth(new: float | None, old: float | None) -> float | None:
    if new is None or not old:
        return None
    return round(new / old - 1, 4)


def normalize(g: float | None, g_base: float | None) -> float | None:
    if g is None or g_base is None or g_base <= -1:
        return None
    return round((1 + g) / (1 + g_base) - 1, 4)


def _quarter_key(period: str) -> tuple[int, int]:
    y, q = period.split("-Q")
    return int(y), int(q)


def count_growth(rows: list[dict], window: int = 4) -> dict:
    """Ultimi `window` trimestri chiusi vs i `window` precedenti, per query e per cluster."""
    closed = [r for r in rows if not r.get("partial") and r.get("count") is not None]
    periods = sorted({r["period"] for r in closed}, key=_quarter_key)
    if len(periods) < 2 * window:
        return {"errore": f"servono {2 * window} trimestri chiusi, disponibili {len(periods)}"}
    last, prev = set(periods[-window:]), set(periods[-2 * window:-window])
    per_query: dict[str, dict] = {}
    for r in closed:
        q = per_query.setdefault(r["query_id"], {"query": r.get("query"), "cluster": r.get("cluster"),
                                                 "ultimi": 0, "precedenti": 0})
        if r["period"] in last:
            q["ultimi"] += r["count"]
        elif r["period"] in prev:
            q["precedenti"] += r["count"]
    base_g = growth(sum(q["ultimi"] for q in per_query.values() if q["cluster"] == BASE),
                    sum(q["precedenti"] for q in per_query.values() if q["cluster"] == BASE))
    for q in per_query.values():
        q["crescita"] = growth(q["ultimi"], q["precedenti"])
        q["crescita_vs_base"] = normalize(q["crescita"], base_g)
    clusters: dict[str, dict] = {}
    for q in per_query.values():
        c = clusters.setdefault(q["cluster"], {"ultimi": 0, "precedenti": 0, "query": []})
        c["ultimi"] += q["ultimi"]
        c["precedenti"] += q["precedenti"]
        c["query"].append(q["query"])
    for c in clusters.values():
        c["crescita"] = growth(c["ultimi"], c["precedenti"])
        c["crescita_vs_base"] = normalize(c["crescita"], base_g)
    return {"finestra_ultimi": sorted(last, key=_quarter_key), "finestra_precedenti": sorted(prev, key=_quarter_key),
            "crescita_base": base_g, "per_cluster": clusters, "per_query": per_query}


def pypi_growth(rows: list[dict], days: int = 90) -> dict:
    """Media giornaliera degli ultimi `days` giorni vs i primi `days` disponibili, per libreria."""
    cats = {r.get("category") for r in rows}
    cat = "without_mirrors" if "without_mirrors" in cats else next(iter(sorted(c for c in cats if c)), None)
    series: dict[str, dict] = {}
    for r in rows:
        if r.get("category") != cat or r.get("downloads") is None:
            continue
        s = series.setdefault(r["package"], {"cluster": r.get("cluster"), "giorni": {}})
        s["giorni"][r["date"]] = r["downloads"]
    per_pkg = {}
    for pkg, s in series.items():
        ds = sorted(s["giorni"])
        if len(ds) < 2 * days:
            n = len(ds) // 2
        else:
            n = days
        if n < 30:
            per_pkg[pkg] = {"cluster": s["cluster"], "errore": f"solo {len(ds)} giorni"}
            continue
        first = [s["giorni"][d] for d in ds[:n]]
        last = [s["giorni"][d] for d in ds[-n:]]
        per_pkg[pkg] = {"cluster": s["cluster"], "giorni_confrontati": n, "dal": ds[0], "al": ds[-1],
                        "media_primi": round(sum(first) / n), "media_ultimi": round(sum(last) / n),
                        "crescita": growth(sum(last) / n, sum(first) / n)}
    base = [p for p in per_pkg.values() if p["cluster"] == BASE and "crescita" in p]
    base_g = base[0]["crescita"] if base else None
    for p in per_pkg.values():
        if "crescita" in p:
            p["crescita_vs_base"] = normalize(p["crescita"], base_g)
    clusters: dict[str, dict] = defaultdict(lambda: {"librerie": {}})
    for pkg, p in per_pkg.items():
        if "crescita" in p:
            clusters[p["cluster"]]["librerie"][pkg] = p["crescita_vs_base"]
    for c in clusters.values():
        vals = sorted(v for v in c["librerie"].values() if v is not None)
        c["mediana_vs_base"] = vals[len(vals) // 2] if vals else None
    return {"categoria": cat, "crescita_base": base_g, "per_cluster": dict(clusters), "per_libreria": per_pkg}


def wiki_growth(rows: list[dict], today: date, months: int = 12) -> dict:
    """Ultimi `months` mesi completi vs i `months` precedenti, per voce."""
    current = f"{today.year:04d}{today.month:02d}"
    series: dict[str, dict] = {}
    for r in rows:
        ym = str(r["timestamp"])[:6]
        if ym >= current:  # mese in corso: incompleto
            continue
        s = series.setdefault(r["article"], {"cluster": r.get("cluster"), "mesi": {}})
        s["mesi"][ym] = r["views"]
    all_months = sorted({m for s in series.values() for m in s["mesi"]})
    if len(all_months) < 2 * months:
        return {"errore": f"servono {2 * months} mesi, disponibili {len(all_months)}"}
    last, prev = all_months[-months:], all_months[-2 * months:-months]
    per_art = {}
    for art, s in series.items():
        a = sum(s["mesi"].get(m, 0) for m in last)
        b = sum(s["mesi"].get(m, 0) for m in prev)
        mesi_prev = sum(1 for m in prev if m in s["mesi"])
        per_art[art] = {"cluster": s["cluster"], "visite_ultimi": a, "visite_precedenti": b,
                        "mesi_precedenti_con_dati": mesi_prev,
                        "crescita": growth(a, b) if mesi_prev == months else None}
        if mesi_prev < months:
            per_art[art]["nota"] = "voce più recente della finestra: crescita non confrontabile"
    base = [p for p in per_art.values() if p["cluster"] == BASE and p["crescita"] is not None]
    base_g = growth(sum(p["visite_ultimi"] for p in base), sum(p["visite_precedenti"] for p in base)) if base else None
    for p in per_art.values():
        p["crescita_vs_base"] = normalize(p["crescita"], base_g)
    clusters: dict[str, dict] = defaultdict(lambda: {"voci": {}})
    for art, p in per_art.items():
        clusters[p["cluster"]]["voci"][art] = p["crescita_vs_base"]
    return {"finestra_ultimi": [last[0], last[-1]], "finestra_precedenti": [prev[0], prev[-1]],
            "crescita_base": base_g, "per_cluster": dict(clusters), "per_voce": per_art}


def summary(result: dict) -> dict:
    """Tabella cluster × fonte con la crescita normalizzata su BASE."""
    table: dict[str, dict] = defaultdict(dict)
    for src in COUNT_SOURCES:
        for cl, c in result.get(src, {}).get("per_cluster", {}).items():
            table[cl][src] = c.get("crescita_vs_base")
    for cl, c in result.get("pypi_downloads", {}).get("per_cluster", {}).items():
        table[cl]["pypi_downloads"] = c.get("mediana_vs_base")
    for cl, c in result.get("wiki_pageviews", {}).get("per_cluster", {}).items():
        vals = sorted(v for v in c["voci"].values() if v is not None)
        table[cl]["wiki_pageviews"] = vals[len(vals) // 2] if vals else None
    for cl, row in table.items():
        vals = [v for v in row.values() if v is not None]
        row["fonti_positive"] = sum(1 for v in vals if v > 0)
        row["fonti_disponibili"] = len(vals)
    return dict(sorted(table.items()))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("db", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--today", help="data di riferimento YYYY-MM-DD (default oggi UTC)")
    args = ap.parse_args()
    today = date.fromisoformat(args.today) if args.today else datetime.now(timezone.utc).date()
    data = load(args.db)
    result: dict = {"generato": today.isoformat(),
                    "metodo": "crescita = ultimi/precedenti - 1; vs_base = (1+g)/(1+g_BASE) - 1",
                    "righe_per_fonte": {k: len(v) for k, v in data.items()}}
    for src in COUNT_SOURCES:
        if data.get(src):
            result[src] = count_growth(data[src])
    if data.get("pypi_downloads"):
        result["pypi_downloads"] = pypi_growth(data["pypi_downloads"])
    if data.get("wiki_pageviews"):
        result["wiki_pageviews"] = wiki_growth(data["wiki_pageviews"], today)
    result["sintesi"] = summary(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    print(f"{'cluster':8} {'github':>8} {'hn':>8} {'nsf':>8} {'pypi':>8} {'wiki':>8}  positive")
    fmt = lambda v: f"{v:+.0%}" if isinstance(v, (int, float)) else "—"
    for cl, row in result["sintesi"].items():
        print(f"{cl:8} " + " ".join(f"{fmt(row.get(s)):>8}" for s in
              ("github_repos", "hn_stories", "nsf_awards", "pypi_downloads", "wiki_pageviews"))
              + f"  {row['fonti_positive']}/{row['fonti_disponibili']}")


if __name__ == "__main__":
    main()
