# Fase 3 – Validazione: dal segnale accademico alla domanda di mercato

Legenda: **[F]** = fatto (dai dati o da una fonte citata) · **[I]** = mia inferenza · **[V]** = da verificare prima di costruirci sopra.

## 3.1 Il problema

Un tema che cresce nei paper dice che i **ricercatori** ci lavorano, non che qualcuno **pagherà** per una soluzione. Tra le due cose ci sono diversi passaggi, ognuno misurabile con una fonte diversa:

| Livello | Domanda | Segnale | Ritardo tipico rispetto ai paper [I] |
|---|---|---|---|
| L1 Ricerca | Ci si lavora? | Paper, citazioni (**già raccolti**) | — |
| L2 Tecnologia | Qualcuno la protegge? | Brevetti, codici CPC | 1–3 anni |
| L3 Capitale | Qualcuno la finanzia? | Grant pubblici; round venture | Pubblici: contemporanei. VC: 0–2 anni |
| L4 Adozione tecnica | Gli sviluppatori la usano? | Repository, download di librerie, discussioni tecniche | Per software e IA: 0–1 anno |
| L5 Domanda | Le aziende pagano? | Offerte di lavoro, ricerche e attenzione del pubblico, regolamentazione | 1–3 anni |

**[I] Regola pratica:** un trend è "validato" quando almeno **3 livelli su 5** crescono nella stessa direzione e almeno uno è L4 o L5. Se cresce solo L1, è una moda accademica o un segnale troppo precoce.

## 3.2 Fonti disponibili (verificate)

| Fonte | Livello | Cosa misura | Accesso (verificato) | Limiti / costo | Si integra nello scraper? |
|---|---|---|---|---|---|
| **OpenAlex – awards/funders** | L3 | Paper finanziati per tema e per finanziatore (NSF, NIH, Commissione UE, NSFC…) | Già disponibile: filtro e `group_by` su `awards.funder_id` nelle works ([recipe ufficiale](https://developers.openalex.org/guides/recipe-funder-portfolio), [campi works](https://developers.openalex.org/api-reference/works.md)). Il vecchio campo `grants` è stato rimosso ([deprecazioni](https://developers.openalex.org/guides/deprecations.md)) | Budget OpenAlex già in uso; collegamenti grant→paper incompleti ([help awards](https://help.openalex.org/data/awards/)) | **Sì, subito**: connettore `openalex_groups` esistente |
| **NSF Award Search API** | L3 | Grant NSF (USA) per parola chiave, importi, date | `GET api.nsf.gov/services/v1/awards.json?keyword=…`, nessuna chiave ([doc ufficiale](https://resources.research.gov/common/webapi/awardapisearch-v1.htm)) | Dati dal 2007 ([data.gov](https://catalog.data.gov/dataset/nsf-award-search-web-api)); nomi di alcuni parametri **[V]** | Sì: connettore GET con offset |
| **NIH RePORTER v2** | L3 | Grant sanitari USA | `POST api.reporter.nih.gov/v2/projects/search` con `criteria`, `offset`, `limit` ([vignetta repoRter.nih](https://bikeactuary.r-universe.dev/repoRter.nih/doc/repoRter_nih.html)); chiave non citata **[V]** | Massimo 10.000 risultati per query | Sì, ma serve il POST nel client HTTP |
| **CORDIS (Horizon Europe)** | L3 | Progetti UE: temi, partner, budget | Dataset bulk CSV/JSON su data.europa.eu, licenza CC0/CC BY 4.0 ([CORDIS](https://cordis.europa.eu/llms.txt)); API per utenti registrati **[V]** | Download bulk con velocità limitata ([KTH](https://github.com/KTH-Library/cordis)) | Sì: connettore "file" (download + parsing) |
| **SEC EDGAR full-text search** | L3 (VC USA) | Depositi societari; i Form D segnalano raccolte private | `efts.sec.gov/LATEST/search-index`, nessuna chiave, serve User-Agent con email ([guida](https://orthogonal.info/sec-edgar-full-text-search-api-efts-python/)) | 10 risultati per pagina, massimo 10.000; ricerca dei Form D **[V]** | Sì: connettore GET |
| Crunchbase / Dealroom / PitchBook | L3 (VC) | Round, investitori, valutazioni | API a pagamento | Costo alto | Solo se paghi; in alternativa ricerca manuale mirata |
| **Google Patents su BigQuery** | L2 | Brevetti mondiali, CPC, testo completo USA | Tabella `patents-public-data.patents.publications`; primo TB al mese gratuito ([Google Cloud](https://cloud.google.com/blog/products/gcp/google-patents-public-datasets-connecting-public-paid-and-private-patent-data), [repo](https://github.com/google/patents-public-data), archiviato ad aprile 2026) | Serve un progetto Google Cloud; il tuo connettore BigQuery va autorizzato | Analisi SQL separata (non serve lo scraper) |
| **PatentsView PatentSearch** | L2 | Brevetti USA | `search.patentsview.org/api/v1/`, header `X-Api-Key` ([reference](https://search.patentsview.org/docs/docs/Search%20API/SearchAPIReference)), 45 req/min | Il modulo per richiedere la chiave è stato rimosso, futuro incerto ([r-bloggers 2026](https://www.r-bloggers.com/2026/03/breaking-release-of-the-patentsview-r-package/)) **[V]** | Sì, se ottieni la chiave |
| **EPO OPS** | L2 | Brevetti europei e mondiali | Registrazione gratuita, OAuth; 4 GB a settimana gratis, 10 ricerche al minuto ([fair use](https://www.epo.org/en/service-support/ordering/fair-use), [FAQ](https://epo.org/en/service-support/faq/searching-patents/open-patent-services/general-information/are-there-any)) | Oltre: €2.800/anno | Sì, con OAuth (più lavoro) |
| Lens.org | L2+L1 | Brevetti collegati ai paper | Token gratuito per uso non commerciale secondo fonti secondarie ([esempio](https://www.getdrio.com/mcp/io-github-pipeworx-io-lens-org)); cambio di proprietà nel 2026 ([CASRAI](https://casrai.org/news/cambia-sells-the-lens-ownership-change-2026)) **[V]** | Termini incerti | Dopo verifica |
| **GitHub Search API** | L4 | Repository per parola chiave e data di creazione | 30 richieste al minuto autenticate, massimo 4.000 repository esaminati ([doc](https://docs.github.com/en/rest/search/search)) | Il conteggio totale basta per i trend | Sì: il token è già disponibile in Actions |
| **Hacker News (Algolia)** | L4 | Attenzione degli sviluppatori: storie per parola chiave e periodo | `hn.algolia.com/api/v1/search_by_date` con `numericFilters=created_at_i>…`, nessuna chiave ([doc](https://hn.algolia.com/api)) | Massimo 1.000 risultati per query; per i trend basta il totale | Sì |
| **pypistats** | L4 | Download delle librerie Python | API JSON ([pypi](https://pypi.org/project/pypistats)) | Solo gli ultimi 180 giorni → serve raccolta continua | Sì |
| **Wikimedia Pageviews** | L5 | Attenzione del pubblico per voce di Wikipedia | REST API per articolo, granularità giornaliera o mensile ([client R](https://rdrr.io/cran/pageviews/)) | Percorsi esatti **[V]** | Sì |
| **Adzuna** | L5 | Offerte di lavoro per parola chiave e paese, istogramma salari | `app_id`/`app_key` gratuiti, endpoint per paese ([SDK](https://cdn.jsdelivr.net/npm/adzuna-sdk@0.1.2/README.md)) | Limiti del piano gratuito contrastanti (250/giorno oppure ~1.000/mese) **[V]** | Sì |
| arXiv API | L1 | Preprint (più veloci delle riviste) | Metadati CC0; circa 1 richiesta ogni 3 secondi ([ToU](https://info.arxiv.org/help/api/tou.html)) | OpenAlex include già arXiv | Bassa priorità |
| Semantic Scholar | L1 | Citazioni "influenti" | Chiave gratuita, 1 richiesta al secondo ([API](https://semanticscholar.org/product/api/license)) | Ridondante con OpenAlex | Bassa priorità |

## 3.3 Piano di validazione per cluster

Le query sono un punto di partenza. Nomi di librerie e codici CPC vanno **verificati** prima di usarli **[V]**.

| Cluster (Fase 2) | L2 Brevetti | L3 Capitale | L4 Adozione | L5 Domanda | Cosa lo falsificherebbe [I] |
|---|---|---|---|---|---|
| S1 IA agentica / multi-agente | CPC G06N + "multi-agent", "tool use" | OpenAlex: paper finanziati per tema; NSF "multi-agent"; Form D che citano "AI agents" | GitHub: repository "mcp server", "ai agent" al mese; PyPI: `mcp`, `langgraph`, `crewai`; HN: "MCP", "agents" | Adzuna: "AI agent engineer", "agentic"; voce Wikipedia "AI agent" | Repository in crescita ma offerte di lavoro ferme: hype tra sviluppatori senza budget aziendali |
| S2 Fiducia/governance IA | Brevetti "AI model monitoring", "explainability" | Grant su AI safety (NSF, Horizon) | PyPI: librerie di valutazione e guardrail (es. `ragas`, `deepeval`) | Offerte "AI governance", "AI risk", "AI compliance"; scadenze dell'AI Act UE **[V]** | Nessuna crescita di offerte di lavoro di compliance dopo le scadenze normative |
| S3 Cybersecurity con IA | CPC H04L63 + "machine learning" | Form D cybersecurity; grant NSF SaTC | HN e GitHub "prompt injection", "LLM security" | Offerte "AI security engineer" | Solo paper, nessun prodotto o lavoro |
| S4 IA efficiente/locale | Brevetti "model compression", "on-device inference" | — | PyPI `llama-cpp-python`, `vllm`, `onnxruntime`; GitHub/HN "ollama", "local LLM" | Offerte "ML inference engineer", "edge AI" | Download in calo mentre il costo delle API cloud scende |
| S5 Affidabilità del software | — | Form D devtools | GitHub "coding agent", "AI code review"; HN | Offerte SRE/QA che citano l'IA | — |
| S6 Robotica / embodied | CPC B25J (manipolatori) + "learning" | Form D robotics/humanoid; grant NSF robotics | GitHub "vision-language-action", "lerobot" **[V]** | Offerte "robot learning engineer" | Brevetti fermi: resta ricerca |
| S7 IA multimodale / documenti | Brevetti "document understanding" | — | PyPI `docling`, `unstructured` **[V]** | Offerte "document AI", "IDP" | — |
| S8 Ricerca e conoscenza | — | — | PyPI `llama-index`, `qdrant-client`, `chromadb`; HN "RAG" | Offerte "RAG engineer", "knowledge management AI" | — |
| S9 IA per la scienza | CPC G16C, G16B | NIH/NSF/Horizon: grant su "machine learning potentials", "foundation model" in biologia | PyPI `rdkit`, `mace-torch` **[V]** | Offerte "computational chemist ML" | Pochi acquirenti (pharma e materiali) → domanda concentrata |
| S10 Calcolo quantistico | CPC G06N10 | Form D quantum; grant | PyPI `qiskit` | Offerte "quantum software" | Brevetti in crescita ma nessun cliente: orizzonte oltre i 5 anni |

## 3.4 Fonti da aggiungere allo scraper (priorità)

**Priorità 1: gratuite, si integrano con poco codice, coprono L3–L5.**
1. **Finanziamenti per tema via OpenAlex.** Una nuova fonte in `tech_trends.yaml` con il connettore esistente `openalex_groups`:
   - `group_by=primary_topic.id`, filtro `awards.funder_id:<finanziatore>`;
   - per i finanziatori principali (NSF, NIH, Commissione Europea, NSFC; ID da risolvere via API, mai per nome);
   - costo stimato: ~4 finanziatori × 10 periodi × ~23 pagine ≈ 900 chiamate a $0,0001 ≈ **$0,09** a esecuzione.
2. **Un connettore generico "conteggi per query"** (`query_counts`): per ogni coppia (query, mese) chiama un endpoint e salva il numero totale di risultati. Con un'unica classe copre:
   - GitHub Search (`total_count`);
   - Hacker News Algolia (`nbHits`);
   - Adzuna (`count`).

   Si configura tutto nel YAML: URL, parametri, campo del totale, query, periodi.
3. **pypistats**: download giornalieri di una lista di librerie. Va raccolto in continuo, perché lo storico è di soli 180 giorni.

**Priorità 2**
- NSF Award Search (GET).
- NIH RePORTER (richiede il POST nel client HTTP: piccola estensione).
- SEC EDGAR full-text (Form D) **[V]**.
- Wikimedia Pageviews.
- CORDIS bulk (connettore "file").

**Priorità 3**
- Brevetti: Google Patents su BigQuery (ti basta autorizzare il connettore BigQuery e avere un progetto GCP), oppure PatentsView/EPO OPS se ottieni le chiavi.
- Lens.org dopo aver verificato i termini.

## 3.5 Trappole tipiche [I]

- **Incentivi a pubblicare.** Alcuni temi crescono per ragioni accademiche (riviste nazionali, quote di pubblicazione, mode nei titoli), non per bisogni reali. Esempi visti nella Fase 2: il peso di alcune riviste indonesiane, i temi di filosofia/teologia, "AI in Education" ×22.
- **Effetto denominatore.** Una quota in calo può nascondere un campo stabile e maturo, cioè un mercato già esistente.
- **Hype tra sviluppatori.** Stelle su GitHub e post su HN crescono più in fretta della spesa aziendale: vanno sempre confermati con L5.
- **Regolamentazione.** Può *creare* domanda (compliance) o *bloccarla* (sanità): va letta caso per caso.
- **Ritardi diversi.** Per software e IA la domanda segue la ricerca in 0–2 anni. Per hardware, materiali e biotech in 5–10 anni.
