# Fase 4 – Opportunità

Legenda: **[F]** = fatto, dai dati o da una fonte citata · **[I]** = mia inferenza · **[V]** = da verificare.

## Fonti dei numeri

- `analysis/results/02_signals.json`: segnali dalla ricerca (Fase 2), descritti in `02_segnali.md`.
- `analysis/results/03_validation.json`: segnali di adozione e attenzione, prodotti da `analysis/validate_signals.py` sui dati di `config/free_signals.yaml` raccolti il 21 ottobre 2026.
- **Finanziamenti per tema da OpenAlex:** non ancora disponibili. Vengono raccolti dopo le 00:25 UTC del 22 ottobre e saranno aggiunti in una revisione di questo documento.

## 4.1 Cosa dicono i segnali di validazione [F]

Per GitHub, Hacker News e NSF si confrontano gli **ultimi 4 trimestri chiusi** (2025-Q4 → 2026-Q3) con i 4 precedenti (2024-Q4 → 2025-Q3).

La crescita "vs BASE" è normalizzata sul controllo della stessa fonte: (1+g)/(1+g_BASE) − 1. Il controllo è:
- "machine learning" per GitHub e Hacker News;
- "artificial intelligence" per NSF;
- `scikit-learn` per PyPI;
- le voci "Artificial intelligence" e "Large language model" per Wikipedia.

| Cluster | GitHub nuovi repo (vs BASE) | Hacker News storie (grezzo · vs BASE) | NSF grant (vs BASE) | PyPI download, ultimi vs primi 90 gg (mediana vs BASE) | Wikipedia, 12 mesi (vs BASE) |
|---|---|---|---|---|---|
| S1 Agenti / multi-agente | **+208%** | +192% · +278% | −39% | +2% | −45% (voce "Intelligent agent") |
| S2 Fiducia / governance IA | **+377%** | +100% · +159% | −4% | −27% | +8% (AI safety) |
| S3 Sicurezza IA / cyber | **+473%** | +157% · +233% | −42% | n.d. | **+46%** (Prompt injection) |
| S4 IA efficiente / locale | +254% | +145% · +217% | −42% | −7% | −31% (Edge computing) |
| S5 Software con IA | **+592%** | **+356% · +490%** | n.d. | n.d. | n.d. |
| S6 Robotica / embodied | +84% | +86% · +141% | −43% | **+17%** (lerobot) | −21% (Humanoid robot) |
| S7 Multimodale / documenti | +130% | +42% · +84% | −42% | −29% | n.d. |
| S8 Ricerca / conoscenza (RAG) | +47% | +7% · +38% | n.d. | **−40%** | +5% (RAG) |
| S9 IA per la scienza | +1% | +1% · +31% | −42% | −28% | n.d. |
| S10 Quantum | +8% | −10% · +17% | −31% | −14% | −34% |
| BASE (controllo) | grezzo +74% | grezzo −23% | grezzo +40% | grezzo +1% | grezzo +4% |

Per Hacker News il valore grezzo di cluster è `per_cluster.crescita` in `03_validation.json`.

### Dettagli che contano [F]

**GitHub, nuovi repository negli ultimi 4 trimestri**
- "coding agent": 9.129 → **141.189**;
- "ai agent": 94.377 → 554.853;
- "mcp server": 37.805 → 122.648;
- "prompt injection": 717 → 8.585;
- "llm guardrails": 206 → 4.924;
- "ai governance": 958 → 15.533.

**Hacker News**
- "coding agent": 872 → 4.556 storie;
- "ai governance": 80 → 390;
- "retrieval augmented generation": 101 → **36**, l'unico calo netto tra le query IA.

**PyPI**, media giornaliera dei primi 90 giorni contro gli ultimi 90:

| Andamento | Libreria | Download al giorno | Variazione |
|---|---|---|---|
| In calo | vllm | 226.826 → 101.866 | −55% |
| In calo | llama-index | 334.815 → 154.169 | −54% |
| In calo | docling | 368.678 → 184.222 | −50% |
| In calo | qdrant-client | | −40% |
| In calo | chromadb | | −33% |
| In calo | deepeval | | −27% |
| In calo | guardrails-ai | | −26% |
| In calo | rdkit | | −27% |
| Stabile | mcp | circa 9,1–9,4 milioni | +3% |
| Stabile | langgraph | circa 1,85 milioni | 0% |
| Stabile | onnxruntime | | +4% |
| In crescita | crewai | | +10% |
| In crescita | lerobot | | +18% |

**Wikipedia**
- La voce "Model Context Protocol" ha avuto **505.621** visite negli ultimi 12 mesi. È più recente della finestra, quindi la crescita non è confrontabile.
- "Prompt injection": 53.824 → 81.749.

### Limiti di questi dati [F/I]

- **NSF** [I]: il calo è quasi uniforme (−15…−20% grezzo) su query molto diverse, mentre "artificial intelligence" sale del +40%. Questo fa pensare che il conteggio misuri il volume generale dei grant NSF più che il singolo tema: l'API potrebbe trattare le parole come OR **[V]**. Inoltre i grant dei trimestri recenti possono essere registrati in ritardo. **Lo tratto come non conclusivo.**
- **PyPI** [F/I]: lo storico è di soli 180 giorni (dall'8 aprile 2026), quindi è un confronto di breve periodo. I download misurano anche CI e installazioni automatiche. Un calo può riflettere cambi di distribuzione (immagini Docker, cache, altri gestori di pacchetti) e non per forza meno utenti **[I]**. Il controllo `scikit-learn` è stabile (+1%), quindi il calo non è stagionale in generale.
- **GitHub** [I]: tutti i repository crescono (+74% il controllo), anche per i repository generati o di prova. Conta il valore normalizzato, e i valori molto alti partono da basi piccole (guardrails: 206).
- **Hacker News** [F/I]: il conteggio è approssimato. Il controllo "machine learning" scende del −23% perché l'attenzione si sposta su altri termini ("AI"): il valore normalizzato gonfia la crescita, per questo riporto anche il grezzo.
- **Wikipedia** [I]: misura l'attenzione del pubblico, non la domanda. Le voci generiche ("Intelligent agent", "Quantum computing") non sono quelle che si cercano oggi.
- **Mancano del tutto:**
  - L2 (brevetti);
  - L3 venture;
  - L5 offerte di lavoro (Adzuna non è configurato).

  Nessuna opportunità qui sotto arriva quindi oltre L4 + attenzione L5.

### Il gap tra ricerca e mercato [I]

| Situazione | Cluster | Lettura |
|---|---|---|
| Ricerca **e** adozione crescono | S1, S2, S3, S5 | Finestra aperta ora |
| Adozione **più veloce** della ricerca | S5 (coding agent) | Il mercato precede l'accademia; la ricerca rincorre su affidabilità e test |
| Ricerca cresce, adozione ferma o in calo | S9, S10 | Gap classico: tempi lunghi, pochi acquirenti; non è ancora domanda |
| Ricerca cresce, attenzione degli sviluppatori in **calo** | S8 (RAG) | Tecnologia che diventa commodity: l'infrastruttura RAG si sta consolidando o assorbendo nelle piattaforme |
| Solo ricerca (non misurata altrove) | S11 educazione, S12 salute, S13 finanza verde, S14 satellite | Da validare prima di qualunque scelta |

## 4.2 Criteri di ordinamento

**Attrattività (A, 1–5):**
- forza del segnale di ricerca (L1);
- numero di livelli di validazione concordi (L3–L5);
- ampiezza del bisogno (quanti settori e clienti lo hanno);
- urgenza (il problema esiste già oggi).

**Fattibilità (F, 1–5):**
- capitale per arrivare al primo prodotto;
- tempo al primo ricavo;
- barriere tecniche e regolatorie;
- dipendenza da hardware o da pochi acquirenti.

**Punteggio = 0,6 × A + 0,4 × F.** L'attrattività pesa di più perché il fondatore non ha vincoli dichiarati: la fattibilità serve a ordinare, non a escludere.

Livelli di validazione: **L1** ricerca · **L2** brevetti · **L3** capitale · **L4** adozione tecnica · **L5** domanda/attenzione (vedi `03_validazione.md`). ✓ = segnale positivo · ✗ = negativo · ? = non misurato o non conclusivo.

| # | Opportunità | Cluster | A | F | Punteggio | L1 | L2 | L3 | L4 | L5 | Confidenza |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Sicurezza per applicazioni LLM e agenti | S3+S1 | 5 | 4 | **4,6** | ✓ | ? | ? | ✓ | ✓ (attenzione) | Alta |
| 2 | Verifica e review del codice scritto da agenti | S5 | 5 | 4 | **4,6** | ✓ | ? | ? | ✓✓ | ? | Alta (adozione) / media (disponibilità a pagare) |
| 3 | Gateway e governance per MCP e strumenti degli agenti | S1+S2 | 4 | 4 | **4,0** | ✓ | ? | ? | ✓ | ✓ (attenzione) | Media-alta |
| 4 | Affidabilità degli agenti in produzione (test di stress, tracciamento, ripristino) | S1+S2 | 4 | 4 | **4,0** | ✓ | ? | ? | ✓ / ✗ PyPI | ? | Media |
| 5 | Governance e conformità dell'IA (documentazione, audit) | S2 | 4 | 3 | **3,6** | ✓ | ? | ? | ✓ | ✓ debole | Media |
| 6 | Costo ed energia dell'IA: inferenza locale e misura dei consumi | S4 | 4 | 3 | **3,6** | ✓ | ? | ? | ✓ / ✗ PyPI | ✗ | Media |
| 7 | Automazione documentale multimodale verticale | S7 | 3 | 4 | **3,4** | ✓ | ? | ? | ✓ / ✗ PyPI | ? | Media |
| 8 | Dati e strumenti per il robot learning | S6 | 4 | 2 | **3,2** | ✓ | ? | ? | ✓ | ✗ | Media |
| 9 | Tutor IA adattivi | S11 | 3 | 3 | 3,0 | ✓ | ? | ? | ? | ? | Bassa |
| 10 | Dati e reporting per la finanza della transizione | S13 | 3 | 3 | 3,0 | ✓ (debole) | ? | ? | ? | ? | Bassa |
| 11 | Basi di conoscenza curate per assistenti IA (non infrastruttura RAG) | S8 | 2 | 4 | 2,8 | ✓ | ? | ? | ✗ | ✓ debole | Bassa |
| 12 | Simulazione con IA per materiali e chimica | S9 | 3 | 2 | 2,6 | ✓✓ | ? | ? | ✗ | ? | Bassa-media |
| 13 | ML clinico e salute mentale digitale | S12 | 3 | 2 | 2,6 | ✓ | ? | ? | ? | ? | Bassa |
| 14 | Software per il calcolo quantistico | S10 | 2 | 1 | 1,6 | ✓✓ | ? | ? | ✗ | ✗ | Bassa |
| 15 | Servizi per comunicazioni satellitari | S14 | 2 | 1 | 1,6 | ✓ | ? | ? | ? | ? | Bassa |

## 4.3 Le opportunità nel dettaglio

### 1. Sicurezza per applicazioni LLM e agenti — punteggio 4,6

**Trend.** Le applicazioni con LLM e gli agenti con accesso a strumenti aprono una nuova superficie di attacco: prompt injection, esfiltrazione di dati, abuso di strumenti.

**Evidenza**
- Ricerca [F]:
  - parola chiave "prompt injection" ×6,2 nel corpus LLM 2024→2026;
  - Network Security & Intrusion Detection: quota +81% in 3 anni, 3ª velocità di citazione;
  - Web Application Security +62%;
  - survey su sicurezza e privacy degli LLM: 34 citazioni al mese.
- Adozione [F]: GitHub "prompt injection" 717 → 8.585 repository (+587% vs BASE) e "llm security" +401%; Hacker News rispettivamente +187% e +128% grezzo.
- Attenzione [F]: la voce Wikipedia "Prompt injection" cresce del +46% vs BASE, l'unica voce tecnica con una crescita netta.
- Un paper del 19 ottobre (Applied Sciences) mostra che i rilevatori ML di attacchi web, addestrati altrove, danno il 99,5% di falsi allarmi in produzione. Addestrati sul traffico del proprio dominio scendono allo 0,42–0,61% [F].

**Bisogno [I].** Chi mette un LLM o un agente in produzione deve:
- impedire che contenuti esterni ne prendano il controllo;
- limitare cosa può fare;
- dimostrarlo a chi controlla (sicurezza, audit).

**Idee di prodotto [I]**
- **Firewall per LLM e agenti:** filtro di input e output, rilevamento di injection, policy sugli strumenti. Adattato sul traffico del cliente, come suggerisce il paper sopra.
- **Red teaming continuo come servizio:** batterie di attacchi aggiornate, eseguite a ogni rilascio.
- **Analisi dei permessi degli agenti:** quali strumenti e dati può toccare ogni agente; principio del minimo privilegio.

**Profilo adatto [I]**
- Team: 2–4 persone con esperienza in sicurezza applicativa e ML; credibilità verso i responsabili della sicurezza.
- Capitale: seed (centinaia di migliaia di euro) per arrivare a un prodotto vendibile.
- Distribuzione: un core open source e una versione enterprise funzionano bene in questo mercato.

**Rischi [I]**
- I fornitori di modelli e di cloud integrano queste difese gratis.
- Il mercato della sicurezza è affollato e i cicli di vendita sono lunghi.
- Gli attacchi evolvono in fretta, quindi serve ricerca continua.

**Confidenza: alta** che il bisogno esista e cresca: L1, L4 e L5 come attenzione concordano. **Media** sulla disponibilità a pagare un fornitore indipendente.

**Come chiudere i livelli mancanti [V]**
- L5: offerte di lavoro "AI security", "LLM security" (Adzuna; servono le chiavi).
- L3: round venture nella categoria (SEC Form D o ricerca manuale).
- L2: brevetti CPC H04L63 + "language model" (BigQuery).

### 2. Verifica e review del codice scritto da agenti — punteggio 4,6

**Trend.** Gli agenti di programmazione producono una quantità crescente di codice. Il collo di bottiglia si sposta dallo scrivere al **verificare**.

**Evidenza**
- Ricerca [F]:
  - Software System Performance & Reliability: quota +183% in 3 anni;
  - Software Engineering Research: +78%, con il 2026 a +119%;
  - review "LLMs for Software Engineering": 40,6 citazioni al mese;
  - "coding agents" compare nei paper recenti.
- Adozione [F], il segnale più forte di tutto il dataset:
  - GitHub "coding agent": 9.129 → 141.189 repository (+787% vs BASE);
  - Hacker News "coding agent": 872 → 4.556 storie;
  - "ai code review": +159% (GitHub) e +182% grezzo (HN).

**Bisogno [I].** Chi accetta codice generato deve sapere se è corretto, sicuro e manutenibile, senza rileggerlo tutto a mano.

**Idee di prodotto [I]**
- Review automatica con prove: test generati ed eseguiti, controllo delle regressioni, spiegazione delle modifiche.
- "Contratti" per gli agenti: specifiche verificabili, ad esempio tramite test di proprietà o verifica formale leggera.
- Metriche di qualità del codice generato per i responsabili tecnici.

**Profilo adatto [I]**
- Team: ingegneri software con esperienza in testing, analisi statica, developer tools.
- Capitale: basso per iniziare, perché la distribuzione può partire dal basso (sviluppatori singoli). Più alto per l'enterprise.

**Rischi [I]**
- Gli stessi fornitori degli agenti (IDE, piattaforme Git) integrano la review.
- Mercato molto rumoroso, differenziazione difficile.
- La crescita di GitHub include molti progetti personali e di prova.

**Confidenza: alta** sull'adozione, perché L4 è molto forte su GitHub e HN. **Media** sulla possibilità di un'azienda indipendente.

**Come chiudere i livelli mancanti [V]**
- Offerte di lavoro che citano agenti di programmazione e review.
- Download di librerie di test e analisi da aggiungere a PyPI, da scegliere.
- Interviste a 15–20 responsabili tecnici: quanto tempo spendono oggi in review.

### 3. Gateway e governance per MCP e strumenti degli agenti — punteggio 4,0

**Trend.** Il Model Context Protocol sta diventando lo standard per collegare agenti e strumenti.

**Evidenza**
- Ricerca [F]: "model context protocol" passa da 1 a 232 paper nel corpus LLM (×68); Multi-Agent Systems ha il punteggio più alto tra 3.895 temi.
- Adozione [F]:
  - GitHub "mcp server": 37.805 → 122.648 nuovi repository (+86% vs BASE);
  - Hacker News "mcp server": +84% grezzo;
  - PyPI `mcp`: circa 9,1–9,4 milioni di download al giorno, stabile (+3%) nei 6 mesi: adozione già ampia, non più esplosiva.
- Attenzione [F]: la voce Wikipedia ha avuto 505.621 visite in 12 mesi.

**Bisogno [I].** Le aziende che collegano agenti a centinaia di strumenti devono decidere chi può usare cosa, registrare le azioni e controllare quali server MCP sono affidabili.

**Idee di prodotto [I]**
- **Gateway MCP aziendale:** autenticazione, permessi, log di audit, filtro dei contenuti (si unisce all'opportunità 1).
- **Registro e certificazione di server MCP:** verifica di sicurezza e qualità dei server pubblici.
- **Server MCP verticali** per sistemi diffusi (ERP, CRM, gestionali italiani ed europei): l'idea più semplice da avviare.

**Profilo adatto [I]**
- Team: ingegneri di piattaforma e sicurezza.
- Capitale: basso-medio.
- Per i server verticali basta un team piccolo con conoscenza del dominio.

**Rischi [I]**
- Lo standard è guidato da grandi aziende, che possono offrire gateway gratuiti.
- Il protocollo cambia in fretta.
- Il plateau dei download PyPI può indicare un mercato già occupato.

**Confidenza: media-alta.**

**Come chiudere i livelli mancanti [V]**
- Adottano MCP le aziende o solo gli sviluppatori? Verificare con offerte di lavoro e casi d'uso pubblici.
- Quanti server MCP aziendali esistono (registri pubblici).

### 4. Affidabilità degli agenti in produzione — punteggio 4,0

**Trend.** Dal "funziona nella demo" al "regge quando le cose cambiano".

**Evidenza**
- Ricerca [F]:
  - "llm-as-a-judge" da 2 a 156 paper;
  - "multi-agent systems" ×5,3;
  - "human-in-the-loop" ×3,3;
  - due survey sugli agenti LLM a 60 e 45 citazioni al mese.
  - Un paper del 20 ottobre (Scientific Reports) testa tre architetture di agenti su 8.640 episodi con regole che cambiano a metà compito. Nessuna vince ovunque: Plan-and-Execute ottiene 0,711 nella pianificazione con strumenti e 0,114 con i vincoli. Avvisare l'agente del cambiamento non migliora il risultato medio.
- Adozione [F]: GitHub "llm evaluation" +225% vs BASE, "llm guardrails" 206 → 4.924, "ai agent" 94.377 → 554.853.
- **Segnale contrario [F]:** le librerie open source di valutazione e guardrail perdono download in 6 mesi: deepeval −27%, ragas −10%, guardrails-ai −26%.

**Lettura del contrasto [I].** L'interesse cresce, ma gli strumenti open source generici non catturano l'uso: la valutazione si sposta dentro le piattaforme (osservabilità, fornitori di modelli) oppure resta "fatta in casa". Un prodotto deve offrire qualcosa che le piattaforme non danno: test di stress specifici per dominio, ripristino automatico, certificazione.

**Idee di prodotto [I]**
- Banco di prova per agenti con perturbazioni (strumenti negati, obiettivi che cambiano), sulla linea del paper sopra.
- Monitoraggio delle azioni degli agenti con allarmi e "interruttore".
- Valutazione verticale certificata, ad esempio agenti per il customer service bancario.

**Profilo adatto [I]**
- Team: ingegneri ML con esperienza di MLOps.
- Capitale: medio.

**Rischi [I]**
- Consolidamento verso le piattaforme di osservabilità esistenti.
- Il calo PyPI può segnalare un mercato open source già saturo.

**Confidenza: media.**

**Come chiudere i livelli mancanti [V]**
- Offerte di lavoro "AI reliability", "LLM evaluation".
- Interviste a team che hanno agenti in produzione.

### 5. Governance e conformità dell'IA — punteggio 3,6

**Trend.** Regole, audit e documentazione dell'IA nelle organizzazioni.

**Evidenza**
- Ricerca [F]:
  - Ethics and Social Impacts of AI: 13.816 paper, quota +254% in 3 anni;
  - XAI +97%;
  - parole chiave "ai governance" ×4,0, "auditability" ×3,3, "data governance" ×3,4.
- Adozione [F]: GitHub "ai governance" 958 → 15.533 nuovi repository (+830% vs BASE); Hacker News 80 → 390 storie.
- Attenzione [F]: Wikipedia "AI safety" +8% vs BASE; "Explainable AI" −28%.

**Bisogno [I].** Le aziende europee devono documentare i sistemi di IA, gestire i rischi e rispondere agli auditor. La domanda dipende dalle scadenze normative (AI Act UE), le cui date vanno verificate **[V]**.

**Idee di prodotto [I]**
- Registro dei sistemi di IA con classificazione del rischio e documentazione generata in automatico dal codice e dai log.
- Servizio di audit tecnico (per partire senza prodotto).
- Strumenti di conformità per settori specifici: banche, assicurazioni, sanità, PA.

**Profilo adatto [I]**
- Team misto legale e tecnico.
- Capitale: basso per il servizio, medio per il prodotto.
- È un buon ingresso per chi sta in Europa e in Italia, dove la normativa crea domanda.

**Rischi [I]**
- Domanda trainata dalla regola: se le scadenze slittano, la domanda slitta.
- Concorrenza delle società di consulenza e dei software GRC esistenti.
- Vendita lenta alle grandi organizzazioni.

**Confidenza: media.** La forte crescita su GitHub parte da una base piccola e include progetti di policy, non solo software.

**Come chiudere i livelli mancanti [V]**
- Offerte di lavoro "AI governance", "AI compliance" in Europa.
- Calendario ufficiale dell'AI Act.
- Bandi pubblici collegati.

### 6. Costo ed energia dell'IA — punteggio 3,6

**Trend.** Inferenza più efficiente, modelli locali, misura dell'energia consumata.

**Evidenza**
- Ricerca [F]:
  - Energy Efficiency in Computing: quota +152%, ma è un tema piccolo (253 paper nel 2025);
  - Green IT +154%;
  - parole chiave "edge deployment" ×3,6, "large language model inference" ×3,6;
  - "ollama" da 4 a 119 paper.
- Adozione [F]: GitHub "local llm" +246% vs BASE, "llm inference" +282%; Hacker News +166% e +101% grezzo.
- **Segnali contrari [F]:**
  - PyPI `vllm` −55% (da 226.826 a 101.866 download al giorno);
  - `llama-cpp-python` −6%;
  - `onnxruntime` +4%;
  - Wikipedia "Edge computing" −31%.

**Lettura [I].** L'interesse per l'inferenza locale e efficiente cresce, ma l'uso degli strumenti si sposta: immagini Docker, binari, servizi gestiti al posto di `pip install`. Il dato PyPI da solo non basta per dire che l'uso cala **[V]**.

**Idee di prodotto [I]**
- **FinOps e GreenOps per l'IA:** misura di costo ed energia per chiamata, per team e per funzionalità; suggerimenti su quale modello usare.
- Instradamento automatico verso il modello più economico che dà lo stesso risultato.
- Appliance o servizi di IA locale per settori con dati sensibili (studi professionali, sanità, PA).

**Profilo adatto [I]**
- Team: ingegneri di sistemi e ML.
- Capitale: medio; alto per l'hardware.

**Rischi [I]**
- Il prezzo delle API cloud scende e riduce il vantaggio economico del locale.
- I fornitori cloud integrano la misura dei costi.

**Confidenza: media.**

**Come chiudere i livelli mancanti [V]**
- Download da altre fonti (Docker Hub, release GitHub).
- Offerte di lavoro "inference engineer".
- Interviste sui budget dell'IA.

### 7. Automazione documentale multimodale verticale — punteggio 3,4

**Trend.** L'IA legge insieme documenti, immagini e tabelle.

**Evidenza**
- Ricerca [F]: Multimodal Machine Learning Applications cresce del +244% in quota, la crescita più alta tra i temi grandi; "optical character recognition" ×3,4.
- Adozione [F]: GitHub "document ai" +134% vs BASE; Hacker News +52% grezzo.
- **Segnale contrario [F]:** PyPI `docling` −50%, `unstructured` −29%.

**Lettura [I].** Lo strato di parsing open source diventa una commodity o cambia rapidamente. Il valore si sposta sul **processo completo di un settore**: sinistri, pratiche legali, bandi, documenti doganali.

**Idee di prodotto [I]**
- Automazione end to end di un singolo processo documentale in un settore regolato, con controllo umano e audit.

**Profilo adatto [I]**
- Fondatore con conoscenza del settore e team piccolo.
- Capitale basso: si parte con pochi clienti pilota.

**Rischi [I]**
- Gli LLM multimodali generalisti diventano "abbastanza buoni" per tutti.
- Vendite lente nei settori regolati.

**Confidenza: media.**

**Come chiudere i livelli mancanti [V]**
- Offerte di lavoro "intelligent document processing".
- Volume di processi nel settore scelto (dati di settore).

### 8. Dati e strumenti per il robot learning — punteggio 3,2

**Trend.** Robot guidati da modelli visione-linguaggio-azione; umanoidi.

**Evidenza**
- Ricerca [F]:
  - Robot Manipulation & Learning: quota +62%, 2026 a +97%;
  - Reinforcement Learning in Robotics: 2026 a +103%;
  - "vision-language-action models" ×4,5 nei paper recenti.
- Adozione [F]:
  - GitHub "humanoid robot" 562 → 3.544 (+262% vs BASE), "robot learning" +40%;
  - Hacker News "humanoid robot" +90% grezzo;
  - PyPI `lerobot` +18%, una delle due sole librerie in crescita.
- **Contrario [F]:** Wikipedia "Humanoid robot" −21%.

**Bisogno [I].** Questi modelli richiedono grandi quantità di dati di dimostrazione e di valutazione nel mondo reale, costosi da raccogliere.

**Idee di prodotto [I]**
- Raccolta e cura di dati di teleoperazione.
- Ambienti di simulazione e benchmark.
- Integrazione di robot in compiti industriali precisi (pick and place, ispezione).

**Profilo adatto [I]**
- Team di robotica con accesso a hardware e laboratori.
- Capitale medio-alto.
- Ecosistemi vicini a università e distretti industriali.

**Rischi [I]**
- Hardware costoso e cicli lunghi.
- Pochi clienti iniziali.
- I grandi laboratori raccolgono i propri dati.

**Confidenza: media.**

**Come chiudere i livelli mancanti [V]**
- Brevetti CPC B25J + learning.
- Finanziamenti pubblici: OpenAlex awards dopo le 00:25 UTC, CORDIS.
- Offerte di lavoro "robot learning engineer".

### 9. Tutor IA adattivi — punteggio 3,0

**Evidenza [F]**
- Intelligent Tutoring Systems & Adaptive Learning: quota +151%, 2026 a +83%.
- Il tema "AI in Education" (×22) è stato escluso perché sospetto.
- Nessun segnale di adozione è stato raccolto.

**Idea [I].** Tutor per materie specifiche o per la formazione aziendale, con misura dei risultati di apprendimento.

**Rischi [I]**
- Adozione lenta nella scuola.
- Gli assistenti generalisti sono gratuiti.
- Difficile dimostrare l'efficacia.

**Confidenza: bassa.**

**Verifiche da fare [V]**
- Aggiungere query GitHub/HN ("ai tutor") e voci Wikipedia.
- Offerte di lavoro edtech.
- Bandi scuola e PNRR.

### 10. Dati e reporting per la finanza della transizione — punteggio 3,0

**Evidenza [F]**
- Nei campioni recenti: "green finance" ×1,9, "green jobs" ×1,9, "climate governance" ×2,8.
- Le coppie di discipline Economia + Ambiente ed Economia + Energia crescono ×1,6.
- Segnali deboli, su campioni non rappresentativi.

**Idea [I].** Raccolta automatica di dati ESG e di transizione per PMI e banche: reporting, rating, documentazione per i finanziamenti verdi.

**Rischi [I]**
- Dipende molto dalla regolamentazione.
- Mercato già presidiato dai grandi fornitori di dati.

**Confidenza: bassa.**

### 11. Basi di conoscenza curate per assistenti IA — punteggio 2,8

**Evidenza**
- Ricerca [F]: Information Retrieval nel 2026 a +163%, Knowledge Management +104%, "hybrid retrieval" ×7,4.
- **Ma l'attenzione degli sviluppatori cala [F]:**
  - Hacker News "retrieval augmented generation": 101 → 36 storie;
  - PyPI `llama-index` −54%, `qdrant-client` −40%, `chromadb` −33%;
  - GitHub "rag" +47% vs BASE, il più basso tra i cluster IA.

**Lettura [I].** L'infrastruttura RAG (database vettoriali, framework) sta diventando una funzione delle piattaforme: **non** è il posto dove costruire oggi. Resta un bisogno sui **contenuti**: basi di conoscenza aziendali pulite, aggiornate, con permessi, da cui gli assistenti possano attingere.

**Idea [I].** Servizio di cura della conoscenza aziendale per assistenti IA: pulizia, deduplicazione, aggiornamento, permessi.

**Confidenza: bassa** come azienda di prodotto; **media** come servizio.

### 12. Simulazione con IA per materiali e chimica — punteggio 2,6

**Evidenza**
- Ricerca [F]:
  - Machine Learning in Materials Science: 2ª velocità di citazione tra i temi emergenti, quota +73%;
  - foundation model per la single-cell multi-omics (scGPT): 43,8 citazioni al mese;
  - un articolo di prospettiva su JACS (20 ottobre) sostiene che i potenziali interatomici "foundation" potrebbero sostituire la DFT in meno di un decennio.
- **Adozione ferma o in calo [F]:** GitHub "materials machine learning" −10% vs BASE; "protein design" +24%; PyPI `rdkit` −27%.

**Gap [I].** È il caso più chiaro di trend accademico forte senza domanda visibile. Gli acquirenti sono pochi (pharma, chimica, materiali), le vendite lunghe e le competenze profonde.

**Idea [I].** Servizi di simulazione accelerata per R&D industriale, con risultati verificati sperimentalmente da partner.

**Profilo adatto [I].** Dottorati nel dominio, capitale medio-alto, partnership con aziende chimiche e farmaceutiche.

**Confidenza: bassa-media.**

### 13. ML clinico e salute mentale digitale — punteggio 2,6

**Evidenza [F]**
- ML in Healthcare: quota +54%.
- Digital Mental Health: +62%.
- "Informatica + Medicina" è la coppia di discipline più frequente nel corpus LLM.
- Nessun dato di adozione raccolto.

**Idea [I].** Strumenti di supporto clinico non diagnostici (documentazione, triage amministrativo), che evitano le barriere regolatorie più alte.

**Rischi [I].** Regolazione (dispositivi medici), vendite alle strutture sanitarie, responsabilità.

**Confidenza: bassa.**

### 14. Software per il calcolo quantistico — punteggio 1,6

**Evidenza**
- Ricerca [F]: Quantum Computing Algorithms: quota +78%, 2026 a +177% (probabilmente gonfiato dall'indicizzazione dei preprint di fisica); correzione d'errore sotto soglia (Nature) a 34 citazioni al mese.
- **Adozione [F]:** GitHub +8% vs BASE; Hacker News −10% grezzo; PyPI `qiskit` −13%, `pennylane` −31%; Wikipedia −34% vs BASE.

**Lettura [I].** Orizzonte lungo. Ha senso **seguirlo**, non costruirci un'azienda oggi, salvo con team di ricerca e capitale paziente.

**Confidenza: bassa.**

### 15. Servizi per comunicazioni satellitari — punteggio 1,6

**Evidenza [F].** Satellite Communication Systems: quota +68%. Nessun altro segnale raccolto.

**Lettura [I].** Ad alta intensità di capitale. Ha senso solo come software o servizi sopra le costellazioni esistenti.

**Confidenza: bassa.**

## 4.4 Cosa cambierebbe questa classifica

| Se… | Allora… |
|---|---|
| Le offerte di lavoro (Adzuna) per "AI security" e "coding agent" crescono come GitHub | Le opportunità 1 e 2 passano a L5 pieno: confidenza alta anche sulla domanda |
| I finanziamenti OpenAlex mostrano molti grant per robotica e materiali | 8 e 12 salgono in attrattività per chi cerca fondi pubblici e non venture |
| Il calo PyPI di vllm, docling e llama-index continua per altri 6 mesi | 6, 7 e 11 scendono: segno di consolidamento sulle piattaforme |
| L'API NSF tratta le parole chiave come OR **[V]** | La colonna NSF va rifatta con frasi esatte o con un'altra fonte (OpenAlex awards) |
