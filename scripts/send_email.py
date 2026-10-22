"""Invia una newsletter preparata da Claude, via SMTP (Gmail).

Il file è un JSON con: subject, html, text (testo semplice); facoltativo "to" (lista).
Credenziali da variabili d'ambiente (secrets del repository):
  SMTP_USER       indirizzo mittente, es. jobnewsletter.fra@gmail.com
  SMTP_PASSWORD   password per le app di Google (non la password normale)
  NEWSLETTER_TO   destinatari separati da virgola (se il file non ha "to")
  SMTP_HOST / SMTP_PORT  facoltativi (default smtp.gmail.com:465)

Uso: python scripts/send_email.py newsletter/outbox/2026-10-23.json [altro.json ...]
"""
from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path


def build(path: Path, sender: str, default_to: list[str]) -> EmailMessage:
    d = json.loads(path.read_text(encoding="utf-8"))
    for key in ("subject", "html", "text"):
        if not d.get(key):
            raise ValueError(f"{path}: campo '{key}' mancante o vuoto")
    if "{{" in d["html"] or "{{" in d["text"]:
        raise ValueError(f"{path}: segnaposto {{{{ }}}} rimasto nel testo")
    to = d.get("to") or default_to
    if not to:
        raise ValueError("nessun destinatario: imposta NEWSLETTER_TO o il campo 'to'")
    msg = EmailMessage()
    msg["Subject"] = d["subject"]
    msg["From"] = formataddr((d.get("from_name", "Radar tecnologico"), sender))
    msg["To"] = ", ".join(to)
    msg.set_content(d["text"])
    msg.add_alternative(d["html"], subtype="html")
    return msg


def main(argv: list[str]) -> int:
    paths = [Path(p) for p in argv if p.endswith(".json")]
    if not paths:
        print("nessun file da inviare")
        return 0
    user, password = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD")
    if not user or not password:
        print("::error::Mancano i secrets SMTP_USER / SMTP_PASSWORD")
        return 2
    default_to = [a.strip() for a in os.environ.get("NEWSLETTER_TO", "").split(",") if a.strip()]
    messages = [build(p, user, default_to) for p in paths]   # valida tutto prima di inviare
    host, port = os.environ.get("SMTP_HOST", "smtp.gmail.com"), int(os.environ.get("SMTP_PORT", "465"))
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=60) as s:
        s.login(user, password)
        for p, m in zip(paths, messages):
            s.send_message(m)
            print(f"inviata: {p} → {m['To']} · {m['Subject']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
