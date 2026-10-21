"""Connettore OpenAlex: paginazione a cursore (cursor=* → meta.next_cursor)."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterator

from ..config import ConfigError
from .base import Connector, Page

log = logging.getLogger(__name__)


class OpenAlexConnector(Connector):
    def fetch(self, since: str | None, checkpoint: str | None) -> Iterator[Page]:
        params = dict(self.source.params)
        if not params.get("api_key"):
            log.warning("%s: nessuna api_key; OpenAlex consente solo un uso dimostrativo senza chiave",
                        self.source.name)

        # I filtri OpenAlex si combinano in AND separandoli con la virgola.
        filters = [params.pop("filter")] if params.get("filter") else []
        if since is not None and self.source.incremental:
            filters.append(self.source.incremental.filter.format(since=since))
        if filters:
            params["filter"] = ",".join(filters)

        params["cursor"] = checkpoint or "*"
        while True:
            data = self.http.get_json(self.source.url, params)
            results = data.get("results") or []
            next_cursor = (data.get("meta") or {}).get("next_cursor")
            if not results:
                return
            yield Page(records=results, checkpoint=next_cursor)
            if not next_cursor:
                return
            params["cursor"] = next_cursor


class OpenAlexTopListsConnector(Connector):
    """Le prime pagine di una lista ordinata, ripetuta per ogni valore di un elenco.

    Esempio: i 200 paper più citati per ciascun tema. Usa la paginazione a pagine (`page`),
    documentata per i primi 10.000 risultati, così l'ordinamento (`sort` nei params) è garantito.

    Opzioni (in config, `options:`):
      values_file:   file JSON con l'elenco dei valori (es. ["T10028", "T11714"])
      slice_filter:  filtro da aggiungere per ogni valore, con {value} (es. "primary_topic.id:{value}")
      max_pages:     pagine per valore (default 1)
    """

    def _values(self) -> list[str]:
        opts = self.source.options
        for key in ("values_file", "slice_filter"):
            if not opts.get(key):
                raise ConfigError(f"{self.source.name}: options.{key} obbligatorio")
        try:
            values = json.loads(Path(opts["values_file"]).read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ConfigError(f"{self.source.name}: file dei valori non trovato: {opts['values_file']}") from exc
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise ConfigError(f"{self.source.name}: {opts['values_file']} deve contenere una lista di stringhe")
        return values

    def fetch(self, since: str | None, checkpoint: str | None) -> Iterator[Page]:
        values = self._values()
        max_pages = int(self.source.options.get("max_pages", 1))
        start_i, start_page = 0, 1
        if checkpoint:  # "<indice valore>|<pagina>"
            i, _, p = checkpoint.partition("|")
            start_i, start_page = int(i), int(p or 1)
        for i in range(start_i, len(values)):
            params = dict(self.source.params)
            slice_filter = self.source.options["slice_filter"].format(value=values[i])
            params["filter"] = ",".join(f for f in (params.get("filter"), slice_filter) if f)
            first = start_page if i == start_i else 1
            for page in range(first, max_pages + 1):
                params["page"] = page
                results = self.http.get_json(self.source.url, params).get("results") or []
                last = not results or len(results) < int(params.get("per-page", 25)) or page == max_pages
                nxt = (f"{i + 1}|1" if i + 1 < len(values) else None) if last else f"{i}|{page + 1}"
                if results:
                    yield Page(records=results, checkpoint=nxt)
                if last:
                    break
