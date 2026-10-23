# Linee guida della newsletter "Radar tecnologico"

Valgono per chi scrive la newsletter ogni giorno (Claude, routine "Report giornaliero Radar tecnologico"). Il layout è in `email/template.html`.

## Lettore
Chi legge **non è un tecnico né un esperto di ogni campo**: segue i trend per capire dove va la tecnologia. Ogni paper va spiegato in modo che lo capisca anche chi non conosce la disciplina.

## Obiettivo
In 5–8 minuti il lettore deve sapere tre cose:
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
   - nuovi paper del verticale (`paper_verticale.nuovi_oggi`);
   - una cifra del radar;
   - nuovi paper LLM.
6. **Il segnale del giorno:** il paper più importante del verticale del giorno, raccontato in 3–4 frasi.
7. **Paper del giorno · {verticale}:** 4–6 paper, oltre al segnale, presi da `paper_verticale` di `daily.json`. Sono i temi del verticale del giorno, lo stesso del radar.
   - **Raggruppamento:** per tema, massimo 2 paper per tema e, se possibile, almeno 2 temi.
   - **Weekend:** un paper per ciascun verticale (aerospazio, energia, LLM, cybersecurity, robotica), raggruppati per verticale.
   - **Facoltativo, "Anche oggi":** al massimo 1 paper fuori verticale, da `emergenti` o `llm`, solo se è davvero rilevante. Il mercoledì gli LLM sono il verticale.
   - **Se il verticale oggi non ha paper adatti** (pochi, senza abstract, depositi), dirlo in una riga e usare "Anche oggi" per 2–3 paper da `emergenti`/`llm`.
   - **Per ogni tema:** chip della categoria, peso in 3 anni (da `trend`/radar) e un riquadro **"Di cosa si tratta"** di 2–3 frasi: che cos'è il campo, quale problema concreto affronta, dove lo si incontra nella vita reale o nelle aziende.
   - **Per ogni paper**, nell'ordine:
     - **IL CONTESTO:** 1–2 frasi sul problema di partenza e sul perché finora era difficile;
     - **COSA FANNO**;
     - **RISULTATO:** solo se l'abstract lo riporta;
     - **PERCHÉ CONTA.**
8. **Radar del giorno, ogni giorno**, dal campo `radar_del_giorno` di `daily.json`. Ogni giorno feriale ha un verticale:

   | Giorno | Verticale |
   |---|---|
   | Lunedì | Aerospazio |
   | Martedì | Energia |
   | Mercoledì | LLM e IA generativa |
   | Giovedì | Cybersecurity |
   | Venerdì | Robotica e automazione |
   | Sabato e domenica | Panoramica dei 5 verticali |

   - **Contenuto nei giorni feriali:**
     - riquadro "Di cosa si tratta";
     - 3 cifre del verticale (peso nella ricerca in 3 anni, slancio di quest'anno, quota di paper finanziati);
     - 3–5 temi in crescita, ognuno con una riga di spiegazione;
     - segnali di adozione per query (GitHub e Hacker News, trimestre contro lo stesso trimestre dell'anno prima), con il trimestre confrontato e la data di aggiornamento;
     - una frase finale "In sintesi".
   - **Panoramica del weekend:** una riga per verticale e 2–3 frasi di confronto.
   - **Senza dati di adozione** per un verticale, lo si dice in una riga.
9. **Parole del giorno:** 3–5 termini tecnici usati nella mail, ognuno spiegato in una frase, con un esempio quotidiano quando possibile.
10. **Da tenere d'occhio:** 2–3 frasi.
11. **Piede:** come da template.

## Regole sui contenuti
- **Solo fatti presenti nei dati o negli abstract.** Se l'abstract non riporta un risultato, la riga "Risultato" non c'è.
- **Contesto ammesso, ma solo di base.** "Di cosa si tratta", "Il contesto" e "Parole del giorno" possono usare conoscenze generali consolidate (cos'è un attacco informatico, a cosa serve la chimica computazionale). Valgono tre limiti:
  - niente numeri;
  - niente notizie o affermazioni su aziende e prodotti che non siano nei dati;
  - niente affermazioni incerte presentate come certe.
- **I numeri si copiano dall'abstract**, con le unità. Non si arrotondano in modo da cambiarne il senso.
- **"Perché conta"** è in corsivo e formulato come lettura ("può…", "suggerisce…"), mai attribuito agli autori.
- **Autori e istituzioni, sempre.** Sotto la riga fonte/data di ogni paper (e del segnale del giorno) c'è la riga "Chi lo firma":
  - **Autori:** dai campi `autori` (primi 4) e `n_autori`. Con 1–3 autori tutti i nomi; con più di 3 il primo autore + "e altri N".
  - **Istituzioni:** dal campo `istituzioni` (fino a 3) e dal paese (`paesi`, in italiano).
  - **Autore di spicco:** se `qualita.autore_di_spicco.h_index` è almeno 20, va citato con istituzione e h-index, anche se non è il primo autore. Esempio: "Chi lo firma: Wang L. e altri 5 · Ningbo University of Technology (Cina) · tra gli autori Lin Wang, h-index 76".
  - **Dati mancanti:** se mancano autori o istituzioni, si scrive solo ciò che c'è; non si inventa nulla.
  - **Chip "Rivista di alto impatto"** (colori #1E40AF/#DBEAFE) se `livello_fonte` è `alta`.
  - **H-index:** si spiega in "Parole del giorno" la prima volta che compare.
- **Etichetta del tipo sempre visibile.** Per i preprint va aggiunto che i risultati non sono ancora revisionati.
- **Titoli dei paper in originale.** Nel "Segnale del giorno" si può usare un titolo breve in italiano, con il link all'originale.
- **Qualità e autorevolezza.** Ogni paper ha il campo `qualita` (da `scripts/quality.py`, dati OpenAlex):
  - **`livello_fonte`:**
    - `alta`: articoli della rivista citati in media 3+ volte nei primi 2 anni;
    - `buona`: almeno 1,5;
    - `media`: almeno 0,5;
    - `debole`: meno di 0,5;
    - `preprint`: archivio senza revisione, valutato solo dagli autori.
  - **`autore_di_spicco`:** l'autore con l'h-index più alto, con la sua istituzione.
  - **`punteggio`:** da 0 a 5.

  Come usarli:
  - preferire le fonti `alta` e `buona` e gli autori affermati, con h-index almeno 20;
  - una fonte `debole` solo se il contenuto è eccezionale, dicendolo;
  - un preprint vale se gli autori sono affermati;
  - il segnale del giorno va scelto tra i paper con punteggio più alto, a parità di interesse.
- **Selezione dei paper.** Da scartare:
  - depositi senza contenuto scientifico (log, brevetti, materiale promozionale);
  - paper senza abstract, salvo eccezioni importanti;
  - lingue diverse dall'inglese, se non c'è un abstract leggibile.
- **Varietà.** Massimo 2 paper per tema; almeno 3 temi diversi.

## Stile
- **Italiano semplice e frasi brevi.** Al primo uso un termine tecnico ha una spiegazione tra parentesi, per esempio: "boson sampling (un test del vantaggio dei computer quantistici)". I termini più importanti vanno anche in "Parole del giorno".
- **Analogie.** Quando aiutano, si usano paragoni con la vita quotidiana, per esempio: "come un antivirus che impara le abitudini del tuo computer".
- **"Cosa fanno" e "Risultato" senza gergo:** acronimi e metriche (ROC-AUC, F1…) vanno spiegati o tradotti in parole, per esempio: "ROC-AUC 0,95 (un punteggio che va da 0,5, cioè tirare a caso, a 1, cioè perfetto)". Mai convertire una metrica in un'altra che l'abstract non riporta.
- **Niente aggettivi da comunicato** (rivoluzionario, incredibile, game changer) e niente punti esclamativi.
- **Massimo 1.500 parole** nel corpo, radar compreso. Se si sfora, meglio un paper in meno che il contesto più corto.
- **Colori solo dalla palette del template.** Niente emoji nei titoli; le frecce ▲ ▼ ■ solo nel radar.

## Controlli prima dell'invio
- [ ] Nessun segnaposto `{{ }}` rimasto nel testo.
- [ ] Ogni numero è presente nei dati del giorno o nell'abstract.
- [ ] Ogni paper ha il link, e il PDF solo se `pdf_gratuito` non è vuoto.
- [ ] La versione in testo semplice (`body`) contiene le stesse informazioni, senza HTML né Markdown.
