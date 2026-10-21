# Linee guida della newsletter "Radar tecnologico"

Valgono per chi scrive la newsletter ogni giorno (Claude, routine "Report giornaliero Radar tecnologico"). Il layout è in `email/template.html`.

## Obiettivo
In 5 minuti il lettore deve sapere tre cose:
1. quali novità della ricerca contano oggi;
2. perché contano;
3. come si collegano ai trend di fondo.

Deve poter decidere se aprire un paper.

## Struttura (in quest'ordine)
1. **Oggetto:** `Radar · {segnale principale in 4-6 parole} · {gg mese}`, ad esempio `Radar · Agenti AI sotto stress · 22 ott`.
2. **Anteprima** (testo nascosto): 90–110 caratteri, il riassunto del giorno.
3. **Testata:** titolo del giorno (8–12 parole), numero dell'edizione, data, minuti di lettura (circa 200 parole al minuto).
4. **In 30 secondi:** 3 frasi, ognuna con un fatto e il suo perché.
5. **Numeri del giorno:** 3 cifre presenti nei dati, per esempio:
   - nuovi paper nei temi seguiti;
   - nuovi paper LLM;
   - il tema con più novità.
6. **Il segnale del giorno:** il paper più importante, raccontato in 3–4 frasi.
7. **Temi emergenti** e **LLM:** 6–9 paper in tutto, raggruppati per tema. Per ogni tema: chip della categoria e peso in 3 anni (da `trend`/radar).
8. **Radar della settimana:** solo quando trend o segnali di adozione sono stati aggiornati da al massimo 2 giorni (lunedì o martedì).
9. **Da tenere d'occhio:** 2–3 frasi.
10. **Piede:** come da template.

## Regole sui contenuti
- **Solo fatti presenti nei dati o negli abstract.** Se l'abstract non riporta un risultato, la riga "Risultato" non c'è.
- **I numeri si copiano dall'abstract**, con le unità. Non si arrotondano in modo da cambiarne il senso.
- **"Perché conta"** è in corsivo e formulato come lettura ("può…", "suggerisce…"), mai attribuito agli autori.
- **Etichetta del tipo sempre visibile.** Per i preprint va aggiunto che i risultati non sono ancora revisionati.
- **Titoli dei paper in originale.** Nel "Segnale del giorno" si può usare un titolo breve in italiano, con il link all'originale.
- **Selezione dei paper.** Da scartare:
  - depositi senza contenuto scientifico (log, brevetti, materiale promozionale);
  - paper senza abstract, salvo eccezioni importanti;
  - lingue diverse dall'inglese, se non c'è un abstract leggibile.
- **Varietà.** Massimo 2 paper per tema; almeno 3 temi diversi.

## Stile
- **Italiano semplice e frasi brevi.** Al primo uso un termine tecnico ha una spiegazione tra parentesi, per esempio: "boson sampling (un test del vantaggio dei computer quantistici)".
- **Niente aggettivi da comunicato** (rivoluzionario, incredibile, game changer) e niente punti esclamativi.
- **Massimo 900 parole** nel corpo.
- **Colori solo dalla palette del template.** Niente emoji nei titoli; le frecce ▲ ▼ ■ solo nel radar.

## Controlli prima dell'invio
- [ ] Nessun segnaposto `{{ }}` rimasto nel testo.
- [ ] Ogni numero è presente nei dati del giorno o nell'abstract.
- [ ] Ogni paper ha il link, e il PDF solo se `pdf_gratuito` non è vuoto.
- [ ] La versione in testo semplice (`body`) contiene le stesse informazioni, senza HTML né Markdown.
