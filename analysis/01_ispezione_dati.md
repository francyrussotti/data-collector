# Fase 1 – Ispezione dei dati

Fonte dei numeri: `analysis/results/01_inspection.json`, prodotto da `analysis/inspect_data.py` sui database della release `data` (21 ottobre 2026). Per rigenerarlo: Actions → *analysis* → `step = inspect`.

Legenda: **[F]** = fatto dai dati · **[I]** = mia inferenza.

## 1. Cosa c'è nel database

| Dataset | Cosa contiene | Record | Periodo | Come è stato selezionato |
|---|---|---|---|---|
| `trends.sqlite` | Conteggi di paper per **tema principale** e periodo, su tutta OpenAlex (articoli, review, preprint) | 4.516 temi (4.423 con conteggi) × 10 periodi | 2018–2025 + gennaio–21 ottobre di 2025 e 2026 | Nessuna selezione: è l'universo OpenAlex con un tema assegnato |
| `papers.sqlite` (LLM) | Paper completi (metadati + abstract) | 88.059 (91,6% dei 96.137 trovati) | 2018-01-01 → 2026-12-31 | Ricerca "large language model" in titolo/abstract, solo `type:article` |
| `emerging.sqlite` – più citati | Paper completi dei 50 temi scelti | 10.000 (200 per tema) | 2024 → ott. 2026 | I 200 più citati dal 2024 per tema |
| `emerging.sqlite` – più recenti | idem | 10.000 (200 per tema) | 97% del 2026 | I 200 più recenti per tema |
| `daily.sqlite` | Novità giornaliere dei 50 temi | 1.125 | 7–21 ott. 2026 | I 25 più recenti per tema |

**[F]** Volume totale coperto dai conteggi: 6,2–8,0 milioni di paper l'anno con un tema assegnato.

| Periodo | Paper con tema |
|---|---|
| 2018 | 6.167.496 |
| 2019 | 6.449.615 |
| 2020 | 6.828.670 |
| 2021 | 6.425.962 |
| 2022 | 5.950.013 |
| 2023 | 6.237.632 |
| 2024 | 6.788.696 |
| 2025 | 7.950.127 |
| 2025 (1 gen–21 ott) | 6.215.568 |
| 2026 (1 gen–21 ott) | 7.701.581 |

## 2. Qualità dei campi (% di record con il campo valorizzato) [F]

| Campo | LLM | Emergenti – citati | Emergenti – recenti | Giornaliero |
|---|---|---|---|---|
| Abstract | 85,3 | 80,8 | 85,3 | 80,4 |
| DOI | 95,5 | 99,4 | 95,0 | 96,7 |
| Lingua | 84,7 | 95,0 | **43,9** | **49,1** |
| Istituzioni | 80,6 | 89,8 | **53,4** | **49,1** |
| Paesi | 79,8 | 89,2 | **52,6** | **48,3** |
| Parole chiave | 99,8 | 99,8 | 89,7 | 59,6 |
| Link Open Access | 76,6 | 75,1 | 88,7 | 88,4 |
| Tipo di fonte (rivista/archivio) | 0 | 0 | 0 | 0 |

Il tipo di fonte è stato aggiunto alla raccolta solo il 21 ottobre: sarà disponibile dalle prossime esecuzioni.

## 3. Composizione delle fonti [F]

| | LLM | Citati | Recenti | Giornaliero |
|---|---|---|---|---|
| Depositi senza revisione (Zenodo, Figshare, ResearchGate…) | 6,9% | 2,9% | **23,6%** | **31,1%** |
| Preprint (tipo) | 0% (escluso dal filtro) | 4,2% | 34,6% | 32,3% |
| Sedi distinte | 16.187 | 2.965 | 2.750 | 417 |
| Quota delle prime 10 sedi | 13,3% | 13,6% | 48,6% | 52,5% |
| Prima sede | Zenodo (4.742) | IEEE Access (281) | arXiv (2.153) | Zenodo (265) |
| Paesi più presenti | CN 19.506, US 17.210, GB 4.829 | CN, US, GB | CN, US, **ID** | CN, US, **ID** |
| Date nel futuro | 7 | 0 | 0 | 0 |
| DOI duplicati | 37 | 0 | 0 | 0 |

**Citazioni (mediana per anno di pubblicazione, campione LLM)** [F]: 8 per il 2018–2023 e 6 per il 2024. Scendono a 2 per il 2025 (37% a zero) e a 0 per il 2026 (79% a zero).

## 4. Limiti e bias

1. **Le citazioni non dicono nulla sul 2026** [F/I]. Il 79–99% dei paper recenti ha zero citazioni. La "velocità di citazione" è utilizzabile solo per i paper 2024–2025, e solo nei campioni con paper completi, non sull'intero corpus.
2. **Il calo del 2022 e il salto del 2026 sono probabilmente artefatti** [F/I].
   - **Fatto:** nel 2022 il totale scende del 7% rispetto al 2021, contro il trend. Nel 2026 il periodo da inizio anno è +23,9% sullo stesso periodo del 2025.
   - **Inferenza:** sono variazioni più probabilmente dovute all'indicizzazione di OpenAlex (nuove fonti, recupero di arretrati, depositi Zenodo/arXiv) che alla produzione scientifica reale.
   - **Effetto:** le crescite misurate rispetto al 2022 sono gonfiate per tutti. Per questo il radar usa la **quota** sul totale. Resta però il rischio per i temi che dipendono dalle fonti appena aggiunte.
3. **I temi sono assegnati da un modello e rivisti nel tempo** [F/I]. 46 temi mostrano salti non plausibili, come "AI in Education" ×22 in quota e diversi temi di fisica e matematica +200–1.700% nel 2026. Li tratto come "da verificare". Inoltre l'analisi usa solo il **tema principale** di ogni paper.
4. **I campioni di paper non sono rappresentativi** [I].
   - **LLM:** è una ricerca per parole, non per frase, limitata agli articoli (niente arXiv).
   - **50 temi emergenti:** sono stati scelti *perché* crescono. Usarli per dimostrare una crescita sarebbe un ragionamento circolare. Servono a capire *cosa* c'è dentro un trend, non *se* esiste.
5. **Metadati recenti incompleti** [F]. Sui paper del 2026 mancano lingua e paesi in circa metà dei casi, e il 23–31% sono depositi senza revisione. Le analisi geografiche sul periodo recente sono deboli.
6. **Sovrarappresentazioni** [F/I]. Cina e USA dominano. L'Indonesia è molto presente nei recenti, per la forte produzione su riviste nazionali. Le sedi sono estremamente frammentate (16.187 nel solo campione LLM).
7. **Cosa manca del tutto** [F]: brevetti, finanziamenti, dati di mercato e di investimento, testo completo dei paper, collegamenti tra temi sull'intero corpus. Senza questi dati un trend accademico **non è ancora domanda di mercato** (vedi Fase 3).

## 5. Cosa si può analizzare con affidabilità nella Fase 2

| Analisi | Dati | Affidabilità |
|---|---|---|
| Crescita della quota per tema/disciplina 2018→2025 | `trends.sqlite` | Buona, esclusi i temi "da verificare" |
| Slancio 2026 vs 2025 alla stessa data | `trends.sqlite` | Media: risente dell'indicizzazione 2026 |
| Velocità di citazione | campioni (`counts_by_year`) | Solo paper 2024–2025, campioni non rappresentativi |
| Nuovi cluster (parole chiave/temi emergenti nei paper) | campioni | Esplorativa |
| Convergenza tra discipline | campioni (`topics` multipli per paper) | Esplorativa; per l'intero corpus servono altri conteggi |
| Geografia | campioni | Debole sul 2026 |
