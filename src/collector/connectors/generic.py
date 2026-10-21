"""Connettori generici per API JSON con GET, configurati interamente dal YAML.

QueryCountsConnector – per ogni (query, periodo) salva il totale dei risultati.
  options:
    queries:          lista di {id, query, ...altri campi liberi (es. cluster, country)}
    params:           parametri della richiesta; segnaposto disponibili:
                      {query} {start} {end} {start_ts} {end_ts} {start_mdy} {end_mdy}
                      più ogni campo della query (es. {country}); anche nell'endpoint
    count_path:       percorso del totale nella risposta (es. "total_count", "nbHits")
    granularity:      quarter | month | snapshot (snapshot = un solo valore "ad oggi")
    from:             primo periodo, "YYYY-MM" (non serve per snapshot)
    as_of:            data di riferimento "YYYY-MM-DD" (default: oggi UTC)

ApiListConnector – per ogni elemento di una lista scarica le righe che l'API restituisce.
  options:
    items:            lista di dict (es. {package: "langgraph", cluster: "S1"})
    params:           parametri, con segnaposto dai campi dell'elemento
    records_path:     dove sta la lista nella risposta (es. "data", "items")
    id_template:      id univoco della riga, con segnaposto da elemento + riga
"""
from __future__ import annotations

import calendar
from datetime import date, datetime, timezone
from typing import Iterator

import logging

from ..config import ConfigError
from ..http_client import HttpError
from ..mapping import compile_expr
from .base import Connector, Page

log = logging.getLogger(__name__)
SKIP_STATUSES = (404, 422)  # elemento inesistente o query non valida: si salta e si continua


class _Fmt(dict):
    def __missing__(self, key):
        raise ConfigError(f"segnaposto sconosciuto {{{key}}}")


def _fill(template, ctx: dict):
    if isinstance(template, str):
        return template.format_map(_Fmt(ctx))
    return template


def _as_of(opts: dict) -> date:
    return date.fromisoformat(opts["as_of"]) if opts.get("as_of") else datetime.now(timezone.utc).date()


def build_periods(granularity: str, start: str | None, as_of: date) -> list[dict]:
    """Periodi chiusi [start, end]; l'ultimo può essere parziale (fino ad as_of)."""
    if granularity == "snapshot":
        return [{"period": as_of.isoformat(), "start": as_of, "end": as_of, "partial": False}]
    if granularity not in ("month", "quarter"):
        raise ConfigError(f"granularity non valida: {granularity}")
    if not start:
        raise ConfigError("options.from obbligatorio per granularity month/quarter")
    y, m = map(int, start.split("-")[:2])
    step = 1 if granularity == "month" else 3
    if granularity == "quarter":
        m = 3 * ((m - 1) // 3) + 1
    out = []
    while date(y, m, 1) <= as_of:
        ey, em = (y, m + step - 1) if m + step - 1 <= 12 else (y + 1, m + step - 13)
        end = date(ey, em, calendar.monthrange(ey, em)[1])
        label = f"{y}-{m:02d}" if granularity == "month" else f"{y}-Q{(m - 1) // 3 + 1}"
        out.append({"period": label, "start": date(y, m, 1), "end": min(end, as_of), "partial": end > as_of})
        m += step
        if m > 12:
            y, m = y + 1, m - 12
    return out


def _ctx(p: dict) -> dict:
    ts = lambda d, end=False: int(datetime(d.year, d.month, d.day, 23 if end else 0, 59 if end else 0,
                                           59 if end else 0, tzinfo=timezone.utc).timestamp())
    return {"start": p["start"].isoformat(), "end": p["end"].isoformat(),
            "start_ts": ts(p["start"]), "end_ts": ts(p["end"], True),
            "start_mdy": p["start"].strftime("%m/%d/%Y"), "end_mdy": p["end"].strftime("%m/%d/%Y")}


class QueryCountsConnector(Connector):
    def fetch(self, since: str | None, checkpoint: str | None) -> Iterator[Page]:
        opts = self.source.options
        for key in ("queries", "count_path"):
            if not opts.get(key):
                raise ConfigError(f"{self.source.name}: options.{key} obbligatorio")
        periods = build_periods(opts.get("granularity", "quarter"), opts.get("from"), _as_of(opts))
        count = compile_expr(opts["count_path"])
        jobs = [(q, p) for q in opts["queries"] for p in periods]
        start = int(checkpoint) if checkpoint else 0
        for i in range(start, len(jobs)):
            q, p = jobs[i]
            ctx = {**q, **_ctx(p)}
            params = {k: _fill(v, ctx) for k, v in {**self.source.params, **opts.get("params", {})}.items()}
            url = _fill(self.source.url, ctx)
            try:
                value = count(self.http.get_json(url, params))
            except HttpError as exc:
                if exc.status not in SKIP_STATUSES:
                    raise
                log.warning("%s: %s saltato (HTTP %s)", self.source.name, q["id"], exc.status)
                yield Page(records=[], checkpoint=str(i + 1) if i + 1 < len(jobs) else None)
                continue
            record = {**{k: v for k, v in q.items() if not isinstance(v, (dict, list))},
                      "id": f'{q["id"]}|{p["period"]}', "query_id": q["id"], "period": p["period"],
                      "start": ctx["start"], "end": ctx["end"], "partial": p["partial"],
                      "count": int(value) if value is not None else None}
            yield Page(records=[record], checkpoint=str(i + 1) if i + 1 < len(jobs) else None)


class ApiListConnector(Connector):
    def fetch(self, since: str | None, checkpoint: str | None) -> Iterator[Page]:
        opts = self.source.options
        for key in ("items", "records_path", "id_template"):
            if not opts.get(key):
                raise ConfigError(f"{self.source.name}: options.{key} obbligatorio")
        rows_of = compile_expr(opts["records_path"])
        items = opts["items"]
        today = _as_of(opts)
        start = int(checkpoint) if checkpoint else 0
        for i in range(start, len(items)):
            # segnaposto disponibili: i campi dell'elemento + {today} (YYYY-MM-DD) e {today_compact} (YYYYMMDD)
            item = {**items[i], "today": today.isoformat(), "today_compact": today.strftime("%Y%m%d")}
            params = {k: _fill(v, item) for k, v in {**self.source.params, **opts.get("params", {})}.items()}
            try:
                rows = rows_of(self.http.get_json(_fill(self.source.url, item), params)) or []
            except HttpError as exc:
                if exc.status not in SKIP_STATUSES:
                    raise
                log.warning("%s: elemento %s saltato (HTTP %s)", self.source.name, items[i], exc.status)
                rows = []
            item = items[i]
            records = []
            for row in rows:
                merged = {**row, **item}
                merged["id"] = _fill(opts["id_template"], merged)
                records.append(merged)
            yield Page(records=records, checkpoint=str(i + 1) if i + 1 < len(items) else None)
