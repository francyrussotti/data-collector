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

import copy
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
    user = (os.environ.get("SMTP_USER") or "").strip()
    # la password per le app di Google viene mostrata a gruppi di 4 con spazi: si tolgono
    password = "".join((os.environ.get("SMTP_PASSWORD") or "").split())
    if not user or not password:
        print("::error::Mancano i secrets SMTP_USER / SMTP_PASSWORD")
        return 2
    default_to = [a.strip() for a in os.environ.get("NEWSLETTER_TO", "").split(",") if a.strip()]
    messages = [build(p, user, default_to) for p in paths]   # valida tutto prima di inviare
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    local, _, domain = user.partition("@")
    print(f"mittente: {len(local)} caratteri @{domain or '(manca la @)'} · solo ASCII: {user.isascii()} · "
          f"password di {len(password)} caratteri (una password per le app Google ne ha 16)")
    if not password.isascii():
        print("::error::SMTP_PASSWORD contiene caratteri non ASCII: ricopia la password per le app")
        return 2
    try:
        send_all(host, int(os.environ.get("SMTP_PORT", "465")), user, password, paths, messages)
    except (smtplib.SMTPServerDisconnected, smtplib.SMTPAuthenticationError) as exc:
        print(f"::warning::porta 465 non riuscita ({exc}); riprovo con STARTTLS sulla 587")
        try:
            send_all(host, 587, user, password, paths, messages)
        except smtplib.SMTPAuthenticationError as exc2:
            print(f"::error::Gmail rifiuta le credenziali ({exc2.smtp_code}): controlla SMTP_USER e che SMTP_PASSWORD "
                  "sia una password per le app dell'account (serve la verifica in due passaggi attiva)")
            return 1
    return 0


def send_all(host: str, port: int, user: str, password: str, paths, messages) -> None:
    ctx = ssl.create_default_context()
    if port == 465:
        server = smtplib.SMTP_SSL(host, port, context=ctx, timeout=60)
    else:
        server = smtplib.SMTP(host, port, timeout=60)
    with server as s:
        if port != 465:
            s.ehlo()
            s.starttls(context=ctx)
            s.ehlo()
        s.ehlo_or_helo_if_needed()
        print(f"porta {port}: il server offre AUTH {s.esmtp_features.get('auth', '(nessuno)')}")
        s.login(user, password)
        for p, m in zip(paths, messages):
            # una copia per destinatario: nessuno vede gli indirizzi degli altri
            for rcpt in [a.strip() for a in m["To"].split(",") if a.strip()]:
                one = copy.deepcopy(m)
                one.replace_header("To", rcpt)
                s.send_message(one)
                print(f"inviata: {p} → destinatario {rcpt.split('@')[-1]} · {m['Subject']}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
