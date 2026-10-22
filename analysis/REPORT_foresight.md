# Report di technology foresight – ottobre 2026

**Domanda:** quali trend tecnologici stanno emergendo dalla ricerca, quali hanno già segnali di adozione, e dove conviene costruire un prodotto o un'azienda.

**Data:** 22 ottobre 2026 (finanziamenti pubblici aggiunti alle 01:00 UTC). **Autore:** Claude, sui dati raccolti da `francyrussotti/data-collector`.

**Legenda:**
- **[F]** fatto, dai dati o da una fonte citata;
- **[I]** inferenza;
- **[V]** da verificare.

**Livelli di validazione:**
- L1 ricerca;
- L2 brevetti;
- L3 capitale;
- L4 adozione tecnica;
- L5 domanda e attenzione.

Dettagli: [01 Ispezione](01_ispezione_dati.md) · [02 Segnali](02_segnali.md) · [03 Validazione](03_validazione.md) · [04 Opportunità](04_opportunita.md).

---

## 1. In sintesi

1. **[F] I segnali più forti hanno tre livelli in accordo.** Sono IA agentica, sicurezza dell'IA e software scritto con agenti: crescono nella ricerca (L1), nei nuovi repository GitHub e nelle discussioni su Hacker News (L4). La sicurezza cresce anche nell'attenzione pubblica, cioè le visite a Wikipedia (L5).
   - "coding agent": da 9.129 a **141.189** nuovi repository in un anno.
   - "prompt injection": da 717 a 8.585.
   - La voce Wikipedia "Prompt injection" cresce del +46% rispetto al controllo.
2. **[F] Due aree molto attive nella ricerca non mostrano adozione.**
   - **Calcolo quantistico:** quota di paper +78% in 3 anni, ma GitHub +8% rispetto al controllo, `qiskit` −13% e `pennylane` −31% su PyPI.
   - **IA per i materiali:** GitHub −10% rispetto al controllo, `rdkit` −27%.
   - È il classico gap tra trend accademico e mercato.
3. **[F/I] L'infrastruttura RAG sta diventando una commodity.**
   - [F] Le storie su Hacker News sul tema scendono da 101 a 36.
   - [F] Le librerie dedicate perdono il 33–54% dei download in sei mesi.
   - [F] Intanto la ricerca su information retrieval cresce.
   - [I] Il valore si sposta dagli strumenti ai contenuti.
4. **[I] Tre opportunità emergono con più forza:**
   - sicurezza per applicazioni LLM e agenti;
   - verifica del codice scritto da agenti;
   - governance degli strumenti degli agenti (MCP).

   Hanno i segnali più concordi e richiedono poco capitale per partire.
5. **[F] I fondi pubblici dividono i trend in due gruppi.** Quota di paper con finanziamento di 9 grandi finanziatori (2025), contro una media del 9,4%:
   - **alta** in IA per i materiali (28,5%), satellite (28,5%), robotica (19,8%), quantum (19,0%) e multimodale (16,4%);
   - **bassa** in sicurezza (4,3%), etica e governance (2,8%) e RAG (4,2%).

   **[I]** I primi sono spinti dal denaro pubblico; i secondi crescono dal basso e vanno validati sul mercato. Dettagli: [04, sezione 4.5](04_opportunita.md).
6. **[F] Limite principale:** mancano ancora brevetti (L2), round venture e offerte di lavoro (L5). Nessuna opportunità è ancora validata come domanda pagante. Il paragrafo 7 dice come chiudere questi buchi.

## 2. Dati e metodo

| Fase | Cosa | Dati | Risultato |
|---|---|---|---|
| 1. Ispezione | Qualità e copertura dei dati | 4.516 temi OpenAlex × 10 periodi (6–8 milioni di paper l'anno); 88.059 paper LLM; 20.000 paper dei 50 temi emergenti; 1.125 novità giornaliere | [01](01_ispezione_dati.md) |
| 2. Segnali | Crescita, velocità di citazione, parole chiave nuove, convergenza tra discipline | Quota di ogni tema sul totale, 2022→2025 e 2026 | 14 cluster S1–S14 · [02](02_segnali.md) |
| 3. Validazione | Scala L1–L5, fonti gratuite verificate, raccolta automatica | GitHub, Hacker News, NSF, PyPI, Wikipedia: 5.455 righe | [03](03_validazione.md) · `results/03_validation.json` |
| 4. Opportunità | 15 opportunità ordinate per attrattività e fattibilità | Fasi 2 e 3 + finanziamenti OpenAlex (`results/05_funding.json`) | [04](04_opportunita.md) |

**Scelte di metodo [F]**
- **Crescita nella ricerca:** si misura come **quota** di paper sul totale, non come numero assoluto, per neutralizzare i salti di indicizzazione di OpenAlex (2022 e 2026).
- **Crescita dei segnali di adozione:** si **normalizza** sul controllo della stessa fonte. Per esempio, su GitHub tutti i repository "machine learning" crescono del +74%.

## 3. Mappa dei trend: ricerca contro adozione

| Cluster | Ricerca (L1) | GitHub (L4, vs controllo) | Hacker News (L4, grezzo) | PyPI (L4, 6 mesi) | Wikipedia (L5) | Lettura [I] |
|---|---|---|---|---|---|---|
| S1 Agenti / multi-agente | Tema n.1 su 3.895; "multi-agent systems" ×5,3; MCP da 1 a 232 paper | +208% | +192% | stabile (mcp +3%, langgraph 0%) | MCP: 505.621 visite in 12 mesi | Adozione ampia, già a regime per gli sviluppatori |
| S2 Fiducia / governance | Ethics of AI +254%; XAI +97% | +377% | +100% | −27% (strumenti di valutazione) | AI safety +8% | Interesse in crescita, strumenti open source in difficoltà |
| S3 Sicurezza IA | Network security +81%; "prompt injection" ×6,2 | **+473%** | +157% | — | **+46%** | **Il più convalidato** |
| S4 IA efficiente / locale | Energy efficiency +152% | +254% | +145% | vllm −55% | Edge −31% | Segnali misti |
| S5 Software con IA | Affidabilità del software +183% | **+592%** | **+356%** | — | — | Il mercato precede la ricerca |
| S6 Robotica | Manipolazione 2026 +97%; VLA ×4,5 | +84% | +86% | lerobot +18% | Humanoid −21% | Precoce, ma reale |
| S7 Multimodale / documenti | Multimodale +244% | +130% | +42% | docling −50% | — | Lo strato di parsing diventa commodity |
| S8 Ricerca / RAG | IR 2026 +163% | +47% | +7% | −40% | RAG +5% | Si consolida nelle piattaforme |
| S9 IA per la scienza | ML per i materiali, 2ª velocità di citazione | +1% | +1% | rdkit −27% | — | **Gap ricerca-mercato** |
| S10 Quantum | +78%; 2026 +177% | +8% | −10% | qiskit −13% | −34% | **Gap ricerca-mercato** |
| S11–S14 Educazione, salute, finanza verde, satellite | Tra +54% e +151% | non misurato | | | | Solo L1 |

**[F] La colonna NSF (grant pubblici USA) non è riportata.** Il calo è quasi uniforme (−15…−20%) su temi diversi, mentre la query di controllo sale del +40%: probabilmente misura il volume generale dei grant più che il tema **[V]**.

**Limiti di misura [F/I]**
- Lo storico PyPI copre solo 180 giorni.
- I download possono riflettere cambi nel modo di installare i pacchetti, non solo nell'uso.

## 4. Il gap tra trend accademico e domanda di mercato [I]

- **Ricerca e adozione insieme (S1, S2, S3, S5).** Finestra aperta. Il rischio non è la mancanza di domanda ma la **concorrenza delle piattaforme**: fornitori di modelli, cloud, IDE.
- **Adozione più veloce della ricerca (S5).** Gli strumenti si diffondono prima che la ricerca ne abbia dimostrato l'affidabilità. È un'opportunità per chi offre **verifica e controllo**.
- **Ricerca senza adozione (S9, S10).** I paper crescono ma sviluppatori e pubblico no.
  - Servono anni e acquirenti specifici (R&D industriale).
  - Ha senso solo con team di dominio e capitale paziente.
- **Adozione in calo nonostante la ricerca (S8).** Una tecnologia che matura e viene assorbita: non conviene costruire infrastruttura, conviene costruire sopra.
- **Non misurati (S11–S14).** Educazione, salute, finanza verde e spazio hanno solo segnali di ricerca. Prima di sceglierli servono almeno L4 e L5.

## 5. Opportunità ordinate

**Criteri:** attrattività A (1–5) e fattibilità F (1–5); **punteggio = 0,6·A + 0,4·F**.
- **A:** forza della ricerca, numero di livelli concordi, ampiezza e urgenza del bisogno.
- **F:** capitale, tempo al primo ricavo, barriere tecniche e regolatorie, dipendenza da hardware o da pochi clienti.

Schede complete, con evidenza, bisogno, idee, profilo del team, rischi e verifiche: [04_opportunita.md](04_opportunita.md).

| # | Opportunità | A | F | Punteggio | Livelli ✓ | Confidenza | Capitale per partire [I] |
|---|---|---|---|---|---|---|---|
| 1 | Sicurezza per applicazioni LLM e agenti (firewall, red teaming continuo, permessi) | 5 | 4 | **4,6** | L1, L4, L5 (attenzione) | Alta | Seed |
| 2 | Verifica e review del codice scritto da agenti | 5 | 4 | **4,6** | L1, L4 (molto forte) | Alta / media | Basso |
| 3 | Gateway e governance per MCP; server MCP verticali | 4 | 4 | 4,0 | L1, L4, L5 (attenzione) | Media-alta | Basso-medio |
| 4 | Affidabilità degli agenti in produzione (test di stress, monitoraggio) | 4 | 4 | 4,0 | L1, L4 (PyPI contrario) | Media | Medio |
| 5 | Governance e conformità dell'IA (registro, audit, documentazione) | 4 | 3 | 3,6 | L1, L4 | Media | Basso (servizio) / medio |
| 6 | Costo ed energia dell'IA (FinOps/GreenOps, instradamento, IA locale) | 4 | 3 | 3,6 | L1, L4 (PyPI contrario) | Media | Medio |
| 7 | Automazione documentale verticale | 3 | 4 | 3,4 | L1, L3, L4 (PyPI contrario) | Media | Basso |
| 8 | Dati e strumenti per il robot learning | 4 | 2 | 3,2 | L1, L3 (grant), L4 | Media | Medio-alto |
| 12 | Simulazione con IA per materiali e chimica | 4 | 2 | 3,2 | L1 forte, L3 (grant 28,5%) | Bassa-media | Alto (o grant) |
| 9 | Tutor IA adattivi | 3 | 3 | 3,0 | L1 | Bassa | Basso |
| 10 | Dati e reporting per la finanza della transizione | 3 | 3 | 3,0 | L1 (debole) | Bassa | Basso |
| 11 | Cura della conoscenza aziendale per assistenti IA | 2 | 4 | 2,8 | L1 (L4 in calo) | Bassa | Basso |
| 13 | ML clinico e salute mentale digitale | 3 | 2 | 2,6 | L1 | Bassa | Alto |
| 14 | Software per il calcolo quantistico | 2 | 1 | 1,6 | L1 forte, L3 | Bassa | Alto |
| 15 | Servizi per comunicazioni satellitari | 2 | 1 | 1,6 | L1, L3 | Bassa | Alto |

**[I] Profili di fondatore diversi trovano posto in punti diversi della lista:**
- **Ingegnere software o di sicurezza:** 1–4.
- **Esperto di un settore regolato** (finanza, assicurazioni, PA, legale): 5 e 7.
- **Ricercatore con dottorato e accesso a laboratori:** 8 e 12, con fondi pubblici più che venture.
- **Profilo commerciale con poco capitale:** 3 (server MCP verticali), 5 (servizio di audit), 7 (pilota in un settore).

## 6. Dove posizionarsi [I]

| Dimensione | Scelta suggerita | Perché |
|---|---|---|
| **Strato tecnologico** | Sopra le piattaforme (controllo, verifica, sicurezza, verticali), non sotto (modelli, database vettoriali, framework RAG) | [F] Gli strumenti generici perdono download (vllm, llama-index, docling); quelli di controllo crescono su GitHub |
| **Ecosistema** | Agenti e MCP: [F] `mcp` ha circa 9 milioni di download al giorno, 122.648 nuovi repository "mcp server" in un anno | Uno standard diffuso è un canale di distribuzione: chi costruisce server, gateway e sicurezza MCP raggiunge clienti senza piattaforma propria |
| **Mercato geografico** | Europa, Italia come base | La regolazione europea dell'IA crea domanda di conformità e sicurezza (date da verificare **[V]**); meno concorrenza locale nei verticali |
| **Settori clienti** | Regolati e con dati sensibili: banche, assicurazioni, sanità (lato amministrativo), PA, studi professionali | Pagano per controllo, audit e dati che restano in casa |
| **Distribuzione** | Open source o gratuito per gli sviluppatori, poi versione enterprise | [F] L'adozione oggi si vede su GitHub e Hacker News: è lì che nasce la domanda |
| **Fondi** | Venture o autofinanziamento per 1–7; grant e programmi pubblici per 8, 12, 14, 15 | [F] Quota di paper finanziati 18–28% in robotica, materiali, quantum e satellite, contro il 3–4% di sicurezza e governance (media 9,4%) |
| **Da evitare ora** | Infrastruttura RAG generica, framework per agenti generici, software quantistico | [F] Adozione in calo, oppure assente rispetto alla ricerca |

## 7. Cosa costruire per primo [I]

**Proposta:** uno **strato di sicurezza e controllo per agenti che usano MCP**. Unisce le opportunità 1 e 3, ed è la base per la 4. Contiene:
- un proxy tra l'agente e i server MCP;
- policy sugli strumenti (chi può fare cosa);
- rilevamento di prompt injection nei contenuti che arrivano dagli strumenti;
- registro di audit esportabile.

**Perché questo** [F]: ha i segnali più concordi, cioè sicurezza +473% e MCP +86% su GitHub rispetto al controllo, e Prompt injection +46% su Wikipedia. Richiede un team piccolo e si distribuisce dal basso. Apre la strada alla governance (5) e all'affidabilità (4).

**Piano in 90 giorni.** Ogni passo ha un criterio per continuare o fermarsi.

| Settimane | Cosa | Criterio per continuare |
|---|---|---|
| 1–3 | 20 interviste a responsabili sicurezza e piattaforma di aziende che usano agenti | Almeno 8 su 20 hanno già incidenti o blocchi di rilascio legati all'IA |
| 2–6 | Prototipo open source del proxy MCP con 3 policy e il log di audit | 300 stelle o 20 installazioni attive in 4 settimane |
| 4–8 | Validazione L5: offerte di lavoro "AI security" e "agent" (Adzuna), round nella categoria | Crescita delle offerte di almeno +30% in un anno |
| 6–12 | 3 pilota a pagamento in settori regolati | Almeno 1 pilota diventa contratto |

**Cosa falsificherebbe la scelta [I]:**
- i fornitori di modelli o di cloud rilasciano gratis un gateway MCP con policy;
- le interviste non trovano budget dedicato.

**Alternativa a basso capitale:** server MCP verticali per software gestionali europei (dal punto 3), venduti a integratori e system integrator.

## 8. Cosa manca e prossimi passi sui dati

| Livello | Stato | Prossimo passo |
|---|---|---|
| L2 Brevetti | Non raccolto | Google Patents su BigQuery: serve un progetto Google Cloud e l'autorizzazione del connettore BigQuery |
| L3 Grant per tema | **Raccolto il 22/10** | 9 finanziatori via OpenAlex (`results/05_funding.json`), aggiornato ogni lunedì con *trends*. Da aggiungere: finanziatori italiani ed europei nazionali; importi (CORDIS). NSF Award Search da rifare con frasi esatte **[V]** |
| L3 Venture | Non raccolto | SEC EDGAR Form D (gratuito) o ricerca manuale per le prime 3 opportunità |
| L5 Lavoro | Non raccolto | Adzuna: servono `ADZUNA_APP_ID` e `ADZUNA_APP_KEY` (gratuiti) come secret del repository |
| L4 PyPI | Solo 180 giorni | Si accumula ogni martedì; tra 3–6 mesi il confronto diventa affidabile |
| L1 2026 | Indicizzazione in corso | Rieseguire `signals` a gennaio per confermare gli slanci 2026 |

**Riproducibilità [F].** Tutti i numeri si rigenerano da GitHub Actions:
- *analysis* → `inspect`, `signals`, `validate`;
- *free_signals* ogni martedì;
- *trends* ogni lunedì.

I risultati sono versionati in `analysis/results/`.
