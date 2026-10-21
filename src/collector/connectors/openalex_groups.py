"""Connettore OpenAlex per conteggi aggregati (group_by), suddivisi per periodo.

Per ogni periodo esegue la stessa query con un filtro di data in più e restituisce
un record per gruppo:  {id, period, period_type, year, key, key_display_name, count}
con id = "<periodo>|<chiave>", unico per periodo e gruppo.

Opzioni (in config, `options:`):
  from_year:     primo anno intero (obbligatorio)
  year_to_date:  se true aggiunge due periodi "da inizio anno" alla stessa data
                 per l'anno corrente e il precedente (confronto a parità di giorni)
  as_of:         data di riferimento YYYY-MM-DD (default: oggi, UTC)
  all_groups:    true = tutti i gruppi con paginazione a cursore (ordinati per chiave);
                 false = solo la prima pagina (i primi 200 per conteggio)
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterator

from ..config import ConfigError
from .base import Connector, Page


def build_periods(from_year: int, as_of: date, year_to_date: bool) -> list[dict]:
    periods = [{"period": str(y), "period_type": "year", "year": y,
                "filter": f"publication_year:{y}"} for y in range(from_year, as_of.year)]
    if year_to_date:
        for y in (as_of.year - 1, as_of.year):
            day = min(as_of.day, 28) if as_of.month == 2 else as_of.day
            end = date(y, as_of.month, day).isoformat()
            periods.append({"period": f"{y}-ytd", "period_type": "ytd", "year": y,
                            "filter": f"from_publication_date:{y}-01-01,to_publication_date:{end}"})
    return periods


class OpenAlexGroupsConnector(Connector):
    def _periods(self) -> list[dict]:
        opts = self.source.options
        if "from_year" not in opts:
            raise ConfigError(f"{self.source.name}: options.from_year obbligatorio")
        as_of = (date.fromisoformat(opts["as_of"]) if opts.get("as_of")
                 else datetime.now(timezone.utc).date())
        return build_periods(int(opts["from_year"]), as_of, bool(opts.get("year_to_date")))

    def fetch(self, since: str | None, checkpoint: str | None) -> Iterator[Page]:
        if not self.source.params.get("group_by"):
            raise ConfigError(f"{self.source.name}: params.group_by obbligatorio")
        all_groups = bool(self.source.options.get("all_groups", True))
        periods = self._periods()

        # checkpoint = "<indice periodo>|<cursore>"
        start, cursor = 0, None
        if checkpoint:
            idx, _, cursor = checkpoint.partition("|")
            start = int(idx)

        for i in range(start, len(periods)):
            p = periods[i]
            params = dict(self.source.params)
            params["filter"] = ",".join(f for f in (params.get("filter"), p["filter"]) if f)
            if all_groups:
                params["cursor"] = cursor or "*"
            cursor = None
            while True:
                data = self.http.get_json(self.source.url, params)
                groups = data.get("group_by") or []
                next_cursor = (data.get("meta") or {}).get("next_cursor") if all_groups else None
                if not groups:
                    break
                records = [{"id": f'{p["period"]}|{g.get("key")}', "period": p["period"], "period_type": p["period_type"], "year": p["year"],
                            "key": g.get("key"), "key_display_name": g.get("key_display_name"),
                            "count": g.get("count")} for g in groups]
                last_page = not next_cursor
                if last_page:
                    ckpt = f"{i + 1}|" if i + 1 < len(periods) else None
                else:
                    ckpt = f"{i}|{next_cursor}"
                yield Page(records=records, checkpoint=ckpt)
                if last_page:
                    break
                params["cursor"] = next_cursor
