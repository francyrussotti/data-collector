# Fase 2 – Analisi dei segnali

Fonti: `analysis/results/02_signals.json` (script `analysis/signals.py`, eseguito il 21 ottobre 2026 con Actions → *analysis* → `step = signals`). Per i numeri sul singolo tema citati dal radar: `trends.json` (script `scripts/trends.py`).

Legenda: **[F]** = fatto dai dati · **[I]** = mia inferenza.

## 2.1 Metodo in breve

| Segnale | Dati | Misura | Affidabilità |
|---|---|---|---|
| A. Crescita | Universo OpenAlex, ~6–8 milioni di paper/anno, 3.895 temi valutati (≥200 paper nel 2025), 40 esclusi come sospetti | **Quota** del tema sul totale: crescita 2022→2025 ("3a"), slancio 2026 rispetto a 2025 alla stessa data e relativo al totale ("26"), accelerazione, costanza | Buona |
| B. Velocità di citazione | Paper 2024–metà 2025 dei campioni | Citazioni al mese fino al 21/10/2026 | Media: i campioni non sono casuali |
| C. Nuovi cluster | Corpus LLM (88.059 paper, l'intera popolazione della ricerca) e campioni dei 50 temi | Quota delle parole chiave 2024 → 2026 | Buona sul corpus LLM, esplorativa sui campioni |
| D. Convergenza | Campioni (fino a 3 temi per paper) | % di paper che toccano più discipline; coppie in crescita | Esplorativa |

Punteggio composito dei temi: 40% rango della crescita della quota in 3 anni, 25% slancio 2026, 20% accelerazione, 15% anni in crescita su 3.

## 2.2 Il quadro generale [F]

- **Sottocampo "Artificial Intelligence":** 147.410 paper nel 2025, quota **+42% in 3 anni**, e il 2026 cresce di un altro +58% relativo. È il motore di quasi tutti i segnali che seguono.
- **Sottocampi in crescita oltre a IA:**
  - Safety Research: +32%;
  - Human-Computer Interaction: +33%;
  - Computer Vision: +23%;
  - Industrial & Manufacturing Engineering: +21%.
- **Sottocampi in calo di quota:**
  - Toxicology: −33%, e −49% nel 2026;
  - Surfaces, Coatings and Films: −23%;
  - Organic Chemistry: −21%;
  - Hepatology: −22%;
  - Biotechnology: −20%;
  - Inorganic Chemistry: −18%.
- **[I] Lettura del calo:** la quota misura un peso relativo. Un calo può voler dire che il campo è stabile mentre l'IA "si mangia" spazio, non che la ricerca si stia fermando.

## 2.3 I cluster di segnali

Per ogni cluster: evidenza [F], poi lettura [I]. "3a" = variazione della quota 2022→2025; "26" = slancio 2026.

### S1. IA agentica e sistemi multi-agente: il segnale più forte
- [F] **Multi-Agent Systems and Negotiation:** punteggio più alto di tutti i 3.895 temi. Quota 3a **+78%**, 26 **+183%**, accelerazione +0,60, tre anni consecutivi di crescita.
- [F] **Parole chiave nel corpus LLM (quota 2024 → 2026):**

  | Parola chiave | Paper | Quota | Variazione |
  |---|---|---|---|
  | multi-agent systems | 54 → 961 | 0,48% → 2,5% | ×5,3 |
  | llm agents | | | ×4,0 |
  | agentic ai | | | ×3,9 |
  | **model context protocol** | **1 → 232** | | ×68 |
  | llm-as-a-judge | 2 → 156 | | |

  Nei campioni recenti compare "coding agents", assente tra i più citati.
- [F] **Paper più veloci:** due survey sugli agenti LLM raccolgono **60** e **45 citazioni al mese**.
- [I] La ricerca sta passando dal modello singolo ai sistemi di agenti che usano strumenti. Ne nascono bisogni di orchestrazione, valutazione degli agenti (LLM-as-a-judge), interoperabilità (MCP) e affidabilità.

### S2. Fiducia, sicurezza e governance dell'IA
- [F] **Temi in crescita:**
  - **Ethics and Social Impacts of AI:** 13.816 paper, quota 3a **+254%**, 26 +129%;
  - **XAI:** 3a +97%, 26 +98%, 4ª velocità di citazione tra i temi emergenti (mediana 3,3 al mese);
  - **Technostress:** +91%.
- [F] **Parole chiave LLM:**

  | Parola chiave | Variazione |
  |---|---|
  | prompt injection | ×6,2 (anche ×3,1 nei campioni recenti) |
  | ai governance | ×4,0 |
  | hallucination detection | ×3,6 |
  | data governance | ×3,4 |
  | auditability | ×3,3 |
  | human-in-the-loop | ×3,3 |

  Tra i paper più veloci: survey sull'allucinazione (**107 citazioni al mese**) e su sicurezza e privacy degli LLM (34 al mese).
- [I] Più l'IA entra nei processi, più servono strumenti per controllarla, spiegarla e documentarla. È un bisogno trasversale a tutti i settori.

### S3. Cybersecurity nell'era dell'IA
- [F] **Temi:**
  - Network Security & Intrusion Detection: 9.725 paper, 3a **+81%**;
  - Web Application Security: +62%;
  - Spam & Phishing Detection: +80%.
- [F] **Velocità:** Network Security è la **3ª** velocità di citazione (mediana 3,55 al mese).
- [I] La superficie di attacco cresce: nuovi attacchi via IA (prompt injection, phishing generato) e nuovi bersagli (agenti, modelli).

### S4. IA efficiente, locale e "green"
- [F] **Temi:**
  - Energy Efficiency in Computing: 3a **+152%**, 26 +84%;
  - Green IT & Sustainability: **+154%**.
- [F] **Parole chiave LLM:**
  - edge deployment: ×3,6;
  - large language model inference: ×3,6;
  - mixture of experts: ×3,1;
  - ollama: 4 → 119 paper;
  - modelli aperti nuovi nel 2026: deepseek 664, qwen 119, llama 3.1 139.
- [I] I costi energetici e di calcolo dell'IA spingono verso modelli più piccoli, eseguiti in locale, e verso la misura dell'impronta energetica.

### S5. Ingegneria del software e affidabilità dei sistemi con IA
- [F] **Temi:**
  - Software System Performance & Reliability: 3a **+183%**;
  - Software Engineering Research: +78%, 26 +119%;
  - Distributed Systems & Fault Tolerance: 26 +111%.
- [F] **Velocità:** la review "LLMs for Software Engineering" raccoglie 40,6 citazioni al mese.
- [I] Il codice scritto con l'IA aumenta il volume di software, e con esso il bisogno di test, osservabilità e affidabilità.

### S6. Robotica "intelligente" ed embodied AI
- [F] **Temi:**
  - Robot Manipulation & Learning: 3a +62%, 26 **+97%**;
  - Reinforcement Learning in Robotics: +48% e 26 +103%.
- [F] **Parole chiave più frequenti tra i paper recenti** che tra i più citati:
  - vision-language-action models: ×4,5;
  - humanoid robots: ×2,4.
- [I] Il ponte tra modelli linguistici e robotica sta passando dalla ricerca alla prototipazione.

### S7. IA multimodale e generativa
- [F] **Multimodal Machine Learning Applications:** quota 3a **+244%**, la crescita più alta tra i temi tecnologici grandi (6.001 paper).
- [F] **Parole chiave:**
  - cross-modal alignment: ×3,3;
  - optical character recognition: ×3,4;
  - nei campioni, "flow matching" 1 → 39.
- [I] L'IA capisce documenti, immagini, video e audio insieme. È la base per automatizzare i processi documentali e visivi.

### S8. Ricerca dell'informazione e gestione della conoscenza
- [F] **Temi:**
  - Information Retrieval & Search Behavior: 26 **+163%**;
  - Knowledge Management and Technology: 3a **+104%**;
  - Research Data Management: 26 +103%;
  - Scientific Computing & Data Management: 26 +169%.
- [F] **Parole chiave:** hybrid retrieval ×7,4. La survey "LLM + Knowledge Graphs" raccoglie 40,6 citazioni al mese.
- [I] La ricerca di informazioni si sta spostando sugli assistenti AI: c'è bisogno di basi di conoscenza curate e interrogabili.

### S9. IA per la scienza (materiali, chimica, biologia)
- [F] **Machine Learning in Materials Science:** 2ª velocità di citazione tra i temi emergenti (mediana 3,6 al mese), quota 3a +73% (radar).
- [F] **Paper più veloci:** foundation model per la single-cell multi-omics (scGPT, 43,8 al mese) e per la patologia digitale (31,1 al mese).
- [F] **Model Reduction & Neural Networks:** +80% (radar).
- [I] I "foundation model" scientifici stanno sostituendo parti della simulazione classica: è coerente con il calo di quota della chimica tradizionale (2.2).

### S10. Calcolo quantistico
- [F] **Quantum Computing Algorithms & Architecture:** 7.282 paper, 3a **+78%**, 26 **+177%**, velocità mediana 2,5 al mese.
- [F] **Paper:** "Quantum error correction below the surface code threshold" (Nature) raccoglie 34 citazioni al mese.
- [I] È un segnale forte ma a lungo termine. Il +177% del 2026 va preso con cautela, perché nel 2026 OpenAlex sta indicizzando molti nuovi preprint di fisica.

### S11. Educazione con IA
- [F] **Intelligent Tutoring Systems & Adaptive Learning:** 3a **+151%**, 26 +83%. (Il tema "AI in Education", ×22, è escluso come sospetto.)
- [I] I tutor personalizzati basati su LLM sono un'area molto attiva, ma l'adozione nelle scuole resta un'incognita.

### S12. Salute digitale
- [F] **Temi:**
  - Machine Learning in Healthcare: 3a +54%;
  - Digital Mental Health Interventions: +62%;
  - Innovation in Digital Healthcare Systems: +103% (tema piccolo).
- [F] **Convergenza:** nel corpus LLM, "Computer Science + Medicine" è la coppia di discipline più frequente nel 2023–2025.
- [I] La domanda c'è, ma il settore è regolato: tempi e costi di ingresso sono alti.

### S13. Economia della transizione verde
- [F] **Parole chiave più frequenti nei campioni recenti:**
  - green finance: ×1,9;
  - green jobs: ×1,9;
  - green investment: ×1,4;
  - waste sorting: ×2,7;
  - climate governance: ×2,8.
- [F] **Coppie di discipline in crescita:**
  - Economia + Scienze ambientali: ×1,6;
  - Economia + Energia: ×1,6.
- [I] La transizione sta diventando una questione di finanza, reporting e lavoro, non solo di tecnologia.

### S14. Reti satellitari e spazio
- [F] Satellite Communication Systems: 3a +68%.
- [I] Il segnale è coerente con le costellazioni in orbita bassa, ma è un tema capital intensive.

## 2.4 Convergenza tra discipline [F]

- **Corpus LLM:** i paper che toccano più discipline salgono dal 60% (2018–22) al **65–68%** (2023–26).
- **Coppie in crescita nel corpus LLM (2024 → 2026):**
  - Ingegneria + Scienze sociali: ×1,8;
  - Business + Ingegneria: ×1,9;
  - Ingegneria + Scienze ambientali: ×1,9;
  - Informatica + Scienze della Terra: ×2,2;
  - Odontoiatria + Medicina: ×4,1, ma su numeri piccoli.
- **Nei temi emergenti:** Informatica + Matematica ×1,66, insieme a "lean 4" e "flow matching" tra le parole più nuove.
- **[I] Lettura:** l'IA esce dall'informatica ed entra nei domini applicativi (medicina, ingegneria, ambiente, business). Le opportunità più interessanti stanno in queste intersezioni.

## 2.5 Cosa questi segnali NON dicono

1. **Crescita accademica non vuol dire domanda di mercato.** Nessun dato su clienti, spesa o investimenti: va verificato nella Fase 3.
2. **Lo slancio 2026 è gonfiato per alcune discipline**, in particolare la fisica, dall'indicizzazione di OpenAlex.
3. **Velocità di citazione e parole chiave dei campioni** derivano da temi scelti perché crescono: confermano il contenuto dei trend, non la loro esistenza.
4. **Temi molto piccoli** (Energy Efficiency in Computing: 253 paper nel 2025) crescono tanto partendo da poco: il segnale è precoce ma fragile.
5. **Parole chiave** di nomi di prodotto (DeepSeek, GPT-5, Grok) misurano l'attenzione per un modello, non un bisogno.
