Qui Claude deposita la newsletter del giorno (`AAAA-MM-GG.json` con `subject`, `html`, `text`).
Ogni nuovo file avvia il workflow `send_newsletter`, che la invia via Gmail dall'account in `SMTP_USER`.
