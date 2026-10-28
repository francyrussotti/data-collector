import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAPER = {"titolo": "A paper", "link": "https://doi.org/10.1/x", "fonte": "Science", "data": "26 October",
         "tipo": "Journal", "alto_impatto": True, "pdf": "https://doi.org/10.1/x", "firma": "A. B. · Univ (Italy)",
         "contesto": "c", "cosa": "w", "risultato": "r", "perche": "p"}
CONTENT = {
    "anteprima": "preview", "titolo": "Title", "sottotitolo": "No. 6 · Tuesday 27 October 2026 · 6 min read",
    "in30": ["one", "two", "three"], "numeri": [["1", "a"], ["2", "b"], ["3", "c"]],
    "segnale": {"titolo": "S", "link": "https://doi.org/10.1/s", "meta": "Nature · 26 October", "tipo": "Journal",
                "alto_impatto": True, "firma": "X · Y (UK)", "contesto": "ctx", "testo": "text"},
    "sezioni": [{"titolo": "PAPERS OF THE DAY · ENERGY", "nota": "note",
                 "temi": [{"nome": "Batteries", "cat": "growing", "peso": "+3%", "contesto": "about", "paper": [PAPER]}]}],
    "radar_v": {"nome": "Energy", "contesto": "ctx", "cifre": [["+3%", "a"], ["-10%", "b"], ["28%", "c"]],
                "temi": [["Batteries", "x", 0.2]], "adozione": [["battery", 1.8, None], ["guardrails", 27.116, 0.062]], "nota": "n", "sintesi": "s"},
    "radar_w": {"colonne": ["A", "B"], "righe": [["Energy", "t", [0.1, "28%"]]], "intro": "i", "nota": "n", "sintesi": "s"},
    "glossario": [["h-index", "x"]], "occhio": "watch", "limiti": "limits",
}


def test_render_is_english(tmp_path):
    src, out = tmp_path / "content.json", tmp_path / "out.html"
    src.write_text(json.dumps(CONTENT), encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "render_newsletter.py"), str(src), str(out)], check=True)
    html = out.read_text(encoding="utf-8")
    for label in ("TECH RADAR", "IN 30 SECONDS", "SIGNAL OF THE DAY", "Who wrote it:", "WHY IT MATTERS",
                  "High-impact journal", "Free PDF", "RADAR OF THE DAY · ENERGY", "WEEKEND RADAR", "WORDS OF THE DAY",
                  "WORTH WATCHING", "In short:", "max-width:960px", "+2,712%"):
        assert label in html, label
    for italian in ("Chi lo firma", "PERCHÉ CONTA", "Di cosa si tratta", "PAROLE DEL GIORNO", "In sintesi", "Rivista"):
        assert italian not in html, italian
    assert "{{" not in html
