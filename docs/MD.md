

| Brique | Statut | Notes |
| ----- | ----- | ----- |
| **Architecture générale (ASCII)** | ✔ | Node \+ TS *et* Python/FastAPI |
| **Découpage mono-repo** | ✔ | dossiers \+ conventions nommage |
| **Core (Node/Flow/Shared)** | ✔ design ✖ code complet à écrire (facile) |  |
| **Agents 0 & 1 (Écouteur / Cadreur)** | ✔ design \+ pseudo-code |  |
| **Utils STT (OpenAI/Gemini)** | ✔ pseudo-code |  |
| **Utils OAuth Legifrance** | ✔ pseudo-code |  |
| **Autres agents (parseur, matching, export…)** | ✔ liste \+ rôle ✖ implémentation détaillée |  |
| **Tests \+ CI** | ✔ structure ✖ fichiers réels |  |
| **Docker / déploiement** | ✖ à écrire |  |
| **Docs Markdown** | ✖ à générer (prochaine étape) |  |

---

## **📚 Bundle de documentation Markdown proposé**

*Chaque fichier est autonome et peut vivre dans un dossier `docs/` à la racine.*

| Fichier | Contenu principal |
| ----- | ----- |
| **README.md** | Pitch, pré-requis rapides, `poetry install`, `uvicorn` |
| **docs/00\_OVERVIEW.md** | Diagramme ASCII, data-flow, liste des services externes |
| **docs/01\_INSTALL.md** | Node *ou* Python : setup, variables d’environnement, Docker |
| **docs/02\_CLI.md** | Exemples d’usage `python -m defenseur_ia.cli demo.mp3` |
| **docs/03\_SERVER\_API.md** | Routes FastAPI (+ format JSON du SharedStore) |
| **docs/04\_AGENTS.md** | Tableau détaillé (id, rôle, input, output, tags) |
| **docs/05\_MODELS.md** | Schémas Pydantic / Zod \+ explications champs |
| **docs/06\_UTILS.md** | STT, Legifrance, OCR, Embeddings — signature, quotas, limites |
| **docs/07\_DEV\_GUIDE.md** | Conventions code, tests Pytest/Jest, lint |
| **docs/08\_DEPLOY.md** | Dockerfile multi-stage, volumes, Nginx reverse proxy |
| **docs/CHANGELOG.md** | Versioning sémantique, dates |

---

### **Exemple de gabarit : `docs/04_AGENTS.md`**

md  
CopierModifier  
`# 04 · Catalogue des Agents`

`| ID | Nom | Input clé | Output clé | Actions majeures | Tags |`  
`|----|-----|-----------|------------|------------------|------|`  
``| 0  | Écouteur        | `input_blob` (buffer / texte) | `narration` | STT (OpenAI/Gemini) · segmentation · émotions | STT, NLP |``  
``| 1  | CadreurJuridique| `narration` | `axes`, `legal_corpus` | extraction axes · search Legifrance | LLM, API |``  
``| 3  | ParseurPreuves  | fichier(s) brut | `pieces[]` | OCR/PDF, mailparser, anonymisation | OCR, ETL |``  
``| 4  | JuristeMatching | `pieces`, `legal_corpus` | `match_table` | embeddings FAISS, scoring similarité | FAISS |``  
`| …  | …               | …          | …          | … | … |`

`## Cycle de vie d’un agent`

```` ```mermaid ````  
`flowchart LR`  
  `A(SharedStore) -->|read| B(Agent X)`  
  `B -->|write| A`  
  `B -->|log| C{history}`

Voir `docs/00_OVERVIEW.md` pour le flow complet.

yaml  
CopierModifier

`---`

`## 🎯 Étapes pour générer tout cela`

`1. **Valider la liste ci-dessus**`    
   `*Ajoute/enlève les rubriques que tu souhaites.*`

`2. **Choisir la langue**`    
   `*Full FR ? Mix FR/EN pour le code ?*`

``3. **Je génère le *squelette* `.md` complet**``    
   `*Sections vides & TODO placés où il manque des décisions.*`

`4. **On itère** : tu remplis ou me demandes de rédiger les blocs techniques (ex. exemple de requête Legifrance, snippet curl, etc.).`

`---`

`### Prochaine action ?`

`- **“OK pour les 10 fichiers -> génère-les”**`    
`- **“Ajoute un doc pour le front-end plus tard”**`    
`- **“Commence par remplir README.md et 04_AGENTS.md »**`

`Dis-moi et je lance la production !`  
`::contentReference[oaicite:0]{index=0}`

Sources

##### **Vous avez dit :**

Commence depuis le début readme file et ainsi de suite

###### **ChatGPT a dit :**

Réflexion durant 4 secondes

### **Voici la première fournée de fichiers Markdown prêts à déposer dans le dossier `docs/` (le `README.md` va à la racine).**

Pour chaque fichier : copiez le bloc dans le chemin indiqué.  
 Les TODO 🔧 signalent les sections qu’on remplira quand tu le souhaites — ou que tu peux compléter toi-même.

---

md  
CopierModifier  
`/* README.md  (racine) */`  
`# DEFENSEUR-IA 🛡️`

`> **IA de défense personnelle** pour préparer un dossier juridique complet (OQTF, contentieux étrangers, etc.)`    
`> 100 % open-source · Python 3.12 · FastAPI · Uvicorn · OpenAI & Gemini 🧠`

`---`

`## 🚀 Quick Start`

```` ```bash ````  
`# 1. Cloner`  
`git clone https://github.com/<ton-org>/defenseur-ia.git && cd defenseur-ia`

`# 2. Installer`  
`poetry install  # Python`  
`# 👉 ou, pour la version Node, voir docs/01_INSTALL.md`

`# 3. Variables d'environnement`  
`cp .env.template .env`  
`# OPENAI_API_KEY=sk-...`  
`# GEMINI_API_KEY=...`  
`# LEGIFRANCE_ID=...`  
`# LEGIFRANCE_SECRET=...`

`# 4. Lancer le flow lot + CLI`  
`poetry run python -m defenseur_ia.cli demo.mp3`

`# 5. Serveur (option)`  
`poetry run uvicorn defenseur_ia.server.main:app --host 0.0.0.0 --port 8000 --reload`

---

## **🗂️ Monorepo**

bash  
CopierModifier  
`defenseur-ia/`  
`├── pyproject.toml           # deps Poetry & scripts`  
`├── README.md                # ce fichier`  
`├── docs/                    # ← documentation complète`  
`├── scripts/                 # helpers bash`  
`├── tests/                   # unit / integration (pytest)`  
`└── src/defenseur_ia/        # code source`  
    `├── core/                # BaseNode · Flow · SharedStore`  
    `├── agents/              # 00_ecouteur.py … 12_avocat_ia.py`  
    `├── utils/               # stt.py, legifrance.py, ocr.py …`  
    `├── types/               # models.py (Pydantic v2)`  
    `├── cli.py               # entry CLI`  
    `└── server/main.py       # FastAPI app`

---

## **🏗️ Fonctionnement (TL;DR)**

1. **Écouteur** : transcrit audio (OpenAI / Gemini) ou prend du texte brut.

2. **Cadreur juridique** : extrait axes & interroge l’API Légifrance.

3. **Parseur de preuves** : OCR / nettoyage e-mails, PDF, images.

4. **Matching FAISS** : relie lois ↔ preuves.

5. **Recherche web** : forums, assos, jurisprudence hors Legifrance.

6. **Rédaction narrative** : brouillon humain \+ preuves.

7. **Double relecture IA** : QA & agrégation.

8. **Synthèse stratégique** : angles d’attaque & scoring.

9. **Avocat IA** : pièce finale (.doc / .pdf).

Plus de détails dans `docs/00_OVERVIEW.md`.

---

## **📜 Licence**

MIT – utilise des API tierces (OpenAI, Google) soumises à leurs CGU.

---

## **✨ Roadmap courte**

* Intégration Tesseract Docker (OCR image-pdf).

* Export DOCX \+ citations connectées (pandoc).

* Dashboard Vue 3 \+ Tailwind.

*Contributions bienvenues \!*

yaml  
CopierModifier

`---`

```` ```md ````  
`/* docs/00_OVERVIEW.md */`  
`# 00 · Vue d’ensemble`

`## 1. Architecture globale`

```` ```ascii ````  
                         `┌────────────────────────────┐`  
                         `│        DEFENSEUR-IA        │`  
                         `│ Python 3 · FastAPI · LLM 🧠 │`  
                         `└────────────────────────────┘`  
                                     `│`  
        `┌───────────────────────────────────────────────────────┐`  
        `│  SharedStore (dossier.json) – mémoire & persistance  │`  
        `└───────────────────────────────────────────────────────┘`  
          `▲           ▲          ▲         ▲             ▲`  
          `│           │          │         │             │`  
  `0 Écouteur   1 Cadreur   3 Parseur   …   10 Avocat    Export`  
 `(stt.py)     (legif.)     (ocr)            (gpt-4o)    (Weasy)`

*(chaîne complète 0→11 détaillée dans le README)*

---

## **2\. Agents**

| ID | Nom | Entrée | Sortie | LL M / Outils |
| ----- | ----- | ----- | ----- | ----- |
| 0 | Écouteur 🗣️ | `input_blob` | `narration` | OpenAI / Gemini STT |
| 1 | Cadreur 🎯 | `narration` | `axes`, `legal_corpus` | GPT-4 / Legifrance API |
| 3 | Parseur 📄 | fichiers | `pieces[]` | pdf-parse, tesseract |
| … | … |  |  |  |

(voir `docs/04_AGENTS.md`)

---

## **3\. Services externes**

* **OpenAI Audio** `POST /audio/transcriptions`

* **Gemini Live 2.5 Flash** (`google-ai/sdk`) – streaming

* **Légifrance sandbox** (`/search`, `/consult`) via OAuth 2

---

## **4\. Workflow CI/CD (bientôt)**

1. **Tests Pytest** → **GitHub Actions**.

2. Build **Docker multi-stage** :

   * Stage 1 : `python:3.12-slim` \+ deps ;

   * Stage 2 : `tesseractshadow/tesseract4re` pour l’OCR.

3. Push image → GHCR.

---

## **5\. Glossaire rapide**

| Terme | Signification |
| ----- | ----- |
| **OQTF** | Obligation de Quitter le Territoire Français |
| **SharedStore** | dictionnaire JSON partagé entre agents |
| **PieceParsed** | objet typé (Pydantic) représentant une preuve débruitée |

yaml  
CopierModifier

`---`

```` ```md ````  
`/* docs/01_INSTALL.md */`  
`# 01 · Installation & pré-requis`

`## A. Version Python (préconisée)`

```` ```bash ````  
`# 0. Clé OpenAI / Google / Legifrance`  
`cp .env.template .env`

`# 1.  Poésie 🎼`  
`curl -sSL https://install.python-poetry.org | python3 -`

`# 2.  Dépendances`  
`poetry install`

`# 3.  Test rapide`  
`poetry run python -m defenseur_ia.cli "Bonjour je m'appelle Alice"`

## **B. Version Node / TypeScript (option)**

bash  
CopierModifier  
`pnpm i`  
`pnpm run dev demo.mp3`

**Nota :** les deux piles partagent la même logique ; choisis celle que ton équipe préfère.

## **C. Tesseract (+ Docker)**

bash  
CopierModifier  
`docker run --rm -it -p 9876:9876 \`  
  `-v $(pwd):/workspace tesseractshadow/tesseract4re bash`

*(voir `docs/06_UTILS.md`)*

---

## **Variables `.env`**

| Nom | Exemple | Rôle |
| ----- | ----- | ----- |
| `OPENAI_API_KEY` | `sk-x…` | Audio \+ GPT 4o |
| `GEMINI_API_KEY` | `AIza…` | Streaming live |
| `LEGIFRANCE_ID` / `LEGIFRANCE_SECRET` | `app_xxx` | OAuth sandbox |
| `PIECES_DIR` | `./pieces` | stockage annexes |

yaml  
CopierModifier

`---`

```` ```md ````  
`/* docs/02_CLI.md */`  
`# 02 · Interface CLI`

```` ```bash ````  
`python -m defenseur_ia.cli <fichier|texte> [--json dossier.json]`

| Option | Description |
| ----- | ----- |
| `fichier` | audio (mp3/wav), PDF, TXT, etc. |
| `--json` | recharge un SharedStore existant pour reprise de flow |
| `--list-agents` | affiche l’ordre des agents |
| `--step n` | exécute le flow jusqu’au n-ième agent puis s’arrête |

### **Exemples**

bash  
CopierModifier  
`# 1. Audio court`  
`poetry run python -m defenseur_ia.cli vox_15s.wav`

`# 2. Texte direct`  
`poetry run python -m defenseur_ia.cli "J’ai reçu une OQTF en 2024…"`

`# 3. Reprendre un dossier interrompu`  
`poetry run python -m defenseur_ia.cli --json dossier_AF23.json --step 5`

yaml  
CopierModifier

`---`

`### Étape suivante ?`

``- Générer les fichiers suivants (`03_SERVER_API.md`, `04_AGENTS.md`, etc.)``    
`- Remplir les TODO techniques (quotas réels, exemples JSON, etc.)`    
`- Ajouter un guide Docker.`

`Dis-moi quel document tu veux développer en priorité !`  
`::contentReference[oaicite:0]{index=0}`

Sources

##### **Vous avez dit :**

Overview md

###### **ChatGPT a dit :**

md  
CopierModifier  
`<!-- docs/00_OVERVIEW.md -->`  
`# 00 · OVERVIEW`

`Bienvenue !`    
`Ce document donne **la vue macro** de DEFENSEUR-IA : pourquoi, comment, avec`  
`quels blocs logiciels et quelles données.`

`---`

`## 1. Vision & objectifs`

`| 🎯 Problème | 🛠️ Solution |`  
`|-------------|-------------|`  
`| Un justiciable isolé peine à <br> rassembler des **preuves disparates** et <br> trouver les **textes juridiques** pertinents (OQTF, contentieux étranger & co). | Un **pipeline multi-agents** qui :<br>1. collecte (voix / texte / PDF)<br>2. structure & anonymise<br>3. interroge Légifrance + web<br>4. génère un **dossier narratif**<br>5. produit la ***requête finale*** (PDF). |`

`---`

`## 2. Pile technologique`

`| Couche | Choix | Pourquoi |`  
`|--------|-------|----------|`  
`| Langage | **Python 3.12** | Écosystème NLP, Pydantic v2, FastAPI |`  
`| Serveur | **FastAPI + Uvicorn** | Async IO, websockets natifs |`  
`| LLM | OpenAI (GPT-4o) • Google (Gemini 2.5) | complémentarité coût / vitesse |`  
`| STT | OpenAI Whisper *ou* Gemini Live | haute qualité FR |`  
`| DB légère | **SharedStore JSON** (+ S3 option) | pas de BDD complexe au départ |`  
`| OCR | Tesseract 5 (Docker) | gratuit, multi-langue |`  
`| Vector DB | FAISS-CPU (faiss-python) | local, offline |`  
`| Packaging | Poetry + Make • Docker | iso-prod, simplicité CI |`

`---`

`## 3. Architecture haut-niveau`

```` ```ascii ````  
`┌───────────────────────────────────────────────────────────────────┐`  
`│                        DEFENSEUR-IA (FastAPI)                    │`  
`│                     ── pipeline 0 ➜ 11 agents ──                 │`  
`└───────────────────────────────────────────────────────────────────┘`  
         `▲ CLI upload / HTTP POST                │`  
         `│                                        ▼`  
`┌────────┴───────────┐         read/write   ┌──────────────┐`  
`│   Input (audio…)   │ ────────────────────► │ SharedStore  │`  
`│  + annexes / pièces│                      │ dossier.json │`  
`└────────────────────┘ ◄──────────────────── └──────┬───────┘`  
         `│ logs.history append()                     │`  
         `▼                                           │`  
 `(0) Écouteur  →  (1) Cadreur  →  (3) Parseur  → …  →│←─\`  
         `│            │             │                │   |`  
         `└────────────┴─────────────┴────────────────┴───┘ persist`

---

## **4\. Chaîne des agents (0 → 11\)**

mermaid  
CopierModifier  
`flowchart LR`  
  `U([Utilisateur<br/>audio/pdf/txt]) -->|upload| A0(Écouteur)`  
  `A0 -->|narration| A1(Cadreur<br/>Juridique)`  
  `A1 -->|axes+lois| P(Parseur Preuves)`  
  `P --> M(Matching FAISS)`  
  `M --> W(Web Scraper)`  
  `W --> R1(Rédacteur Narratif)`  
  `R1 --> QA1(Relecteur IA 1)`  
  `QA1 --> Agg(Agrégateur)`  
  `Agg --> QA2(Relecteur IA 2)`  
  `QA2 --> Synth(Synthèse Stratégique)`  
  `Synth --> Avocat(Avocat IA)`  
  `Avocat --> Exp(Export PDF / ZIP)`  
  `Exp --> U`  
  `classDef box fill:#f9f,stroke:#333`  
  `class P,M,W,R1,QA1,Agg,QA2,Synth,Avocat,Exp box`

**Idée clef** : chaque bloc écrit **uniquement** ses sorties dans le  
 `SharedStore`; pas de paramètre caché.

---

## **5\. Structure du `SharedStore`**

jsonc  
CopierModifier  
`{`  
  `"meta":      { "dossier_id": "0xAF23", "langue": "fr", "created_at": "…" },`  
  `"narration": { /* NarrationJusticiable */ },`  
  `"axes":      [ /* HypothèsesRecherche */ ],`  
  `"legal_corpus": [ /* CorpusLegalBrut */ ],`  
  `"pieces":    [ /* PieceParsed[] */ ],`  
  `"draft": {`  
    `"v0": {/* DraftNarratif */},`  
    `"v1": {/* DraftCorrigé1 */},`  
    `"latest": "v1"`  
  `},`  
  `"plan":      { /* PlanStratégique */ },`  
  `"requete_finale": {/* RequêteFinale */},`  
  `"logs": {`  
    `"history": [`  
      `"2025-07-26T14:32 ▶ START écouteur",`  
      `"2025-07-26T14:33 ✔ END   écouteur",`  
      `…`  
    `]`  
  `}`  
`}`

*Snapshot* écrit sur disque à chaque étape → reprise de session possible.

---

## **6\. Externes & quotas**

| Service | End-point clé | Limite sandbox |
| ----- | ----- | ----- |
| **Légifrance** | `/search`, `/consult/legi/tableMatieres` | 30 req/min |
| **OpenAI** | `/v1/chat/completions` (gpt-4o) | dépend de l’abonnement |
| **Gemini 2.5 Flash** | `POST /v1beta/models/**:generateContent` | 60 req/min |
| **Whisper** | `/audio/transcriptions` | 25 MB/fichier |
| **Tesseract** | \- | CPU-bound |

---

## **7\. Modules & dépendances (import graph)**

mermaid  
CopierModifier  
`graph TD`  
  `core[node.py & flow.py] --> agents`  
  `core --> shared`  
  `agents --> utils`  
  `utils -->|OCR| tesseract`  
  `utils -->|LLM| openai`  
  `utils -->|Legifrance| httpx`  
  `server --> core`  
  `cli --> core`

---

## **8\. Parcours de développement**

1. **Fork / clone** le repo.

2. `poetry install` puis `poetry run pytest` → tout doit passer \= ✅.

3. Implémente ton agent dans `src/defenseur_ia/agents/`.

4. Ajoute un test dans `tests/`, mets à jour `docs/04_AGENTS.md`.

5. Ouvre une PR.

---

## **9\. Roadmap macro**

* **v0.1** : pipeline local, export PDF ok.

* **v0.2** : API FastAPI \+ websocket streaming.

* **v0.3** : Dashboard Vue 3\.

* **v1.0** : stockage cloud, authentification, multi-dossiers.

---

Besoin d’un zoom (ex. “comment faire le call OAuth ?”)  
 Demande et on complète dans le doc approprié \!

makefile  
CopierModifier  
`::contentReference[oaicite:0]{index=0}`

Sources

##### **Vous avez dit :**

Install md

###### **ChatGPT a dit :**

md  
CopierModifier  
`<!-- docs/01_INSTALL.md -->`  
`# 01 · INSTALLATION & SET-UP`  
`> **Deux piles possibles** :`    
`> • **Python (FastAPI + Uvicorn)** – recommandée pour un départ rapide`    
`> • **Node (TypeScript 18 + pnpm)** – si ton équipe est JS-centric`    
`>`   
``> Les deux partagent les mêmes modèles, le même `SharedStore.json` et la même logique d’agents.``

`---`

`## sommaire rapide`  
`1. [Prérequis communs](#prérequis-communs)`    
`2. [Installation Python (Poetry)](#a-version-python)`    
`3. [Installation Node / TypeScript](#b-version-node--typescript)`    
``4. [Variables d’environnement (`.env`)](#c-variables-denvironnement)``    
`5. [OCR & Docker (option)](#d-ocr--docker-optionnel)`    
`6. [Tests & lint](#e-tests--lint)`    
`7. [Dépannage](#f-dépannage)`

`---`

`## Prérequis communs`  
`| Outil | Min. version | Pourquoi |`  
`|-------|--------------|----------|`  
`| **Git** | ≥ 2.40 | cloner le repo |`  
`| **Make** | (Unix) | scripts « one-line » |`  
`| **Docker** | ≥ 24 | isoler Tesseract / Whisper |`  
`| **curl / wget** | – | récup scripts, health-checks |`

`---`

`## A · Version **Python**`

`### 1. Installer Poetry`  
```` ```bash ````  
`curl -sSL https://install.python-poetry.org | python3 -`  
`# ou pipx install poetry`

### **2\. Cloner & installer les dépendances**

bash  
CopierModifier  
`git clone https://github.com/<ton-org>/defenseur-ia.git`  
`cd defenseur-ia`  
`poetry install --without dev  # ajoute --with dev pour tests/lint`

### **3\. Configurer l’environnement**

bash  
CopierModifier  
`cp .env.template .env`  
`# puis remplis OPENAI_API_KEY, GEMINI_API_KEY, LEGIFRANCE_ID, LEGIFRANCE_SECRET…`

### **4\. Premier run – mode CLI**

bash  
CopierModifier  
`poetry run python -m defenseur_ia.cli "Je suis bloqué par une OQTF…"`  
`# -> dossier.json + dossier.pdf générés dans le répertoire courant`

### **5\. Serveur FastAPI**

bash  
CopierModifier  
`poetry run uvicorn defenseur_ia.server.main:app \`  
             `--host 0.0.0.0 --port 8000 --reload`  
`# check ➜  http://localhost:8000/docs`

---

## **B · Version Node / TypeScript**

### **1\. Installer pnpm & Node 18 LTS**

bash  
CopierModifier  
`corepack enable`  
`corepack prepare pnpm@latest --activate   # active pnpm`

### **2\. Install & build**

bash  
CopierModifier  
`pnpm i`  
`pnpm run build          # compile TS → dist/`

### **3\. Run**

bash  
CopierModifier  
`# CLI`  
`node dist/apps/cli/main.js "texte ou path.wav"`

`# Dev watch`  
`pnpm run dev <fichier>`

*(Le serveur REST n’est pas encore porté en TS – focus Python pour l’instant.)*

---

## **C · Variables d’environnement**

`.env.template` extrait :

env  
CopierModifier  
`# LLM`  
`OPENAI_API_KEY=sk-...`  
`GEMINI_API_KEY=AIza-...`

`# Legifrance OAuth (https://developer.aife.economie.gouv.fr)`  
`LEGIFRANCE_ID=mon_client_id`  
`LEGIFRANCE_SECRET=mon_secret`

`# Répertoires`  
`PIECES_DIR=./pieces`  
`SHARED_PATH=./dossier.json`

`# Misc`  
`PROXY_URL=            # ex. http://user:pass@proxy:3128`

**Conseil sécurité :** ajoute `.env` dans `.gitignore` (déjà présent).

---

## **D · OCR & Docker (optionnel)**

| Cas | Commande |
| ----- | ----- |
| **Tesseract “on demand”** | `docker run --rm -v $(pwd):/workspace tesseractshadow/tesseract4re fr+eng -l fra < fichier.png` |
| **Whisper GPU** | `docker run --gpus all -v $(pwd):/w openai/whisper --model large <audio.wav>` |

Les scripts utilitaires (`scripts/ocr.sh`, `scripts/whisper.sh`) encapsulent ces appels.

---

## **E · Tests & Lint**

bash  
CopierModifier  
`# Python`  
`poetry install --with dev`  
`poetry run pytest -q        # tests rapides`  
`poetry run ruff check src/  # lint`

`# Node`  
`pnpm run test`  
`pnpm run lint`

---

## **F · Dépannage**

| Problème | Diagnostic |
| ----- | ----- |
| `ModuleNotFoundError ... uvicorn` | `poetry install` sans le flag `--without dev` installe aussi uvicorn |
| 401 OAuth Légifrance | Vérifie que tu utilises l’**URL sandbox** `https://sandbox-api.piste.gouv.fr` et que ton token n’est pas expiré |
| Whisper trop lent | Coupe le modèle (`--model base`) ou active GPU |
| `OSError: FAISS not compiled for avx2` | Installe `faiss-cpu` depuis PyPI (déjà dans `pyproject.toml`) |

---

## **Next ➜**

*Lire `docs/02_CLI.md` pour les commandes avancées,*  
 *puis `docs/04_AGENTS.md` pour comprendre chaque agent.*  
 Bonne contribution \!

makefile  
CopierModifier  
`::contentReference[oaicite:0]{index=0}`

Sources

##### **Vous avez dit :**

CLI md stp

###### **ChatGPT a dit :**

md  
CopierModifier  
`<!-- docs/02_CLI.md -->`  
`# 02 · Interface CLI`

``Le binaire **`defenseur-cli`** (alias``  
`` `python -m defenseur_ia.cli`) est la façon la plus rapide ``  
`d’exécuter le pipeline complet **hors serveur** : idéal pour tester,`  
`déboguer ou lancer un traitement par lot.`

█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█  
 █ TL;DR █  
 █───────────────────█  
 █ defenseur-cli  
 █ \<entrée\>  
 █ \[options…\]  
 █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█

yaml  
CopierModifier

`---`

`## 1. Synthèse rapide`

`| Argument          | Exemple                         | Effet |`  
`|-------------------|---------------------------------|-------|`  
``| `<entrée>`        | `dossier/audio.wav` \| `"texte brut"` | Fichier ou texte direct (UTF-8). |``  
``| `--json PATH`     | `--json dossier_AF23.json`      | Recharge un `SharedStore` existant pour reprendre un flow. |``  
``| `--step N`        | `--step 4`                      | Exécuter **jusqu’au** N-ième agent (inclus) puis s’arrêter. |``  
``| `--list-agents`   | *flag*                          | Affiche l’ordre exact des agents avec leurs ID. |``  
``| `--dump`          | `--dump`                        | Imprime le `SharedStore` final sur stdout. |``  
``| `--log-level LVL` | `--log-level DEBUG`             | Override (TRACE, DEBUG, INFO, WARNING…). |``  
``| `--help`          |                                 | Aide intégrée. |``

`> **Raccourci** : pendant le dev, tu peux simplement lancer :`  
``> `poetry run defenseur-cli fichier.pdf`.``

`---`

`## 2. Installation du binaire`

```` ```bash ````  
`# via poetry (recommandé)`  
`poetry run python -m defenseur_ia.cli --help`

`# ou symlink dans /usr/local/bin`  
`poetry run pip install --editable .`  
`ln -s $(poetry env info -p)/bin/defenseur-cli /usr/local/bin/defenseur-cli`

---

## **3\. Exemples concrets**

### **3.1 Audio court**

bash  
CopierModifier  
`defenseur-cli vox_15s.mp3`  
`# • transcrit vox_15s.mp3 avec Whisper / Gemini`  
`# • génère dossier_AF23.json + dossier_AF23.pdf`

### **3.2 Texte direct**

bash  
CopierModifier  
`defenseur-cli "Depuis 2020, mon titre de séjour..."`

### **3.3 Pipeline étape-par-étape**

bash  
CopierModifier  
`# 1ᵉʳ appel : jusqu’à l’agent 3 (parse des preuves)`  
`defenseur-cli preuve.pdf --step 3`

`# 2ᵉ appel : reprendre la suite`  
`defenseur-cli --json dossier_AF23.json --step 8`

### **3.4 Lister les agents**

bash  
CopierModifier  
`defenseur-cli --list-agents`  
`# 0  écouteur`  
`# 1  cadreur_juridique`  
`# 3  parseur_preuves`  
`# 4  juriste_matching`  
`# …`

---

## **4\. Schéma d’I/O**

mermaid  
CopierModifier  
`flowchart TD`  
  `S0([Entrée<br/>(fichier / texte)])`  
  `S0 --> CLI`  
  `CLI -->|write| Shared[(SharedStore<br/>JSON)]`  
  `Shared --> CLI`  
  `CLI -->|stdout| User`

* **Répertoires générés**

lua  
CopierModifier  
`.`  
`└── output/`  
    `├── dossier_AF23.json   <-- mémoire persistée`  
    `├── dossier_AF23.pdf    <-- export final`  
    `└── pieces/             <-- annexes OCR / pièces brutes`

*(Personnalise le chemin via env `OUTPUT_DIR=`)*

---

## **5\. Détails techniques**

### **5.1 Détection du type d’entrée**

| Condition | Branch |
| ----- | ----- |
| Extension `.wav` `.mp3` `.ogg` | branche STT (`utils/stt.py`) |
| Extension `.pdf` | branche ParseurPreuves direct |
| `stdin` / texte brut | passe direct à l’agent 1 |

### **5.2 Comportement `--step`**

1. Charge (ou crée) `SharedStore`.

2. Exécute la boucle `for agents[i]` **tant que i ≤ step**.

3. Sauvegarde (`save()`) et sort avec code `0`.

### **5.3 Fichiers volumineux**

* Les blobs PDF \> 15 Mo sont **conservés sur disque**, seule la  
   **chemin** est stocké dans le JSON pour éviter les dumps \> MB.

---

## **6\. Astuces**

* **Debug** : ajoute `--log-level DEBUG` \+ consulte  
   `SharedStore["logs"]["history"]`.

* **Replay complet** : `defenseur-cli --json dossier.json` sans `--step`  
   relance les agents manquants seulement.

* **Batch** : simple boucle :

bash  
CopierModifier  
`for f in samples/*.mp3; do`  
  `defenseur-cli "$f"`  
`done`

---

**Prochain document conseillé ➜**  
 `docs/04_AGENTS.md` – détail rôle par rôle des agents.  
 Bonne exploration \!

makefile  
CopierModifier  
`::contentReference[oaicite:0]{index=0}`

Sources

##### **Vous avez dit :**

allons y prochia 04

###### **ChatGPT a dit :**

md  
CopierModifier  
`<!-- docs/04_AGENTS.md -->`  
`# 04 · CATALOGUE DES AGENTS`  
`> **Version α 0.1** — liste exhaustive & mise à jour automatique`    
`` > Chaque agent est un **Nœud** PocketFlow ; il écrit/relit le `SharedStore` ``  
`> et pousse un log d’étape.`

`---`

`## 1. Tableau récapitulatif`

`| ID | Nom (classe) | Input(s) clé | Output(s) clé | Action(s) majeure(s) | Tags |`  
`|:--:|--------------|--------------|---------------|----------------------|------|`  
``| **0** | **Écouteur**<br>`EcouteurNode` | `input_blob` (audio / texte) | `narration` (`NarrationJusticiable`) | STT Whisper / Gemini · segmentation · émotions | STT, NLP |``  
``| **1** | **Cadreur Juridique**<br>`CadreurJuridiqueNode` | `narration` | `axes[]`, `legal_corpus[]` | Extraction de faits / axes · requêtes Légifrance | LLM, API |``  
``| **3** | **Parseur Preuves**<br>`ParseurPreuvesNode` | Fichiers (pdf, mail, img) | `pieces[]` (`PieceParsed`) | OCR, mailparser, anonymisation | OCR, ETL |``  
``| **4** | **Juriste Matching**<br>`MatchingNode` | `pieces`, `legal_corpus` | `match_table` | Embeddings (sbert) · FAISS similitude | FAISS |``  
``| **5** | **Web Scout**<br>`WebScoutNode` | `axes` | `web_corpus[]` | Scraping forums/asso · boilerplate removal | Scraper, Async |``  
``| **6** | **Rédacteur Narratif**<br>`NarrativeWriterNode` | `narration`, `match_table`, `web_corpus` | `draft.v0` | Brouillon humain + preuves | GPT-4 |``  
``| **7** | **Relecteur IA #1**<br>`QA1Node` | `draft.v0` | `draft.v1` | QA de cohérence · suggestions | LLM, QA |``  
``| **7b** | **Agrégateur**<br>`AggregatorNode` | `draft.v1`, `axes` | `draft.v1b` | Vérifie couverture axes, fusionne remarques | Rule, Diff |``  
``| **8** | **Relecteur IA #2**<br>`QA2Node` | `draft.v1b` | `draft.v2` | Contre-lecture “avocat du diable” | LLM |``  
``| **9** | **Synthèse Stratégique**<br>`SyntheseNode` | `draft.v2`, `match_table` | `plan` (`PlanStratégique`) | Liste angles + scoring force juridique | Reasoning |``  
``| **10** | **Avocat IA**<br>`AvocatNode` | `plan`, `draft.v2`, `pieces` | `requete_finale` | Rédige requête argumentée & émotion | GPT-4o |``  
``| **11** | **Export Final**<br>`ExporterNode` | `requete_finale`, `pieces` | `dossier.pdf`, `zip` | WeasyPrint + annexes | PDF, ZIP |``  
``| **★** | *(service)* **SharedInfoBox**<br>`InfoBoxNode` | requête (`query`) | réponse | API interne de consultation du `SharedStore` | helper |``

`---`

`## 2. Carte d’identité détaillée : **Agent 0 – Écouteur**`

`| Champ | Valeur |`  
`|-------|--------|`  
``| **ID** | `0_ecouteur` |``  
``| **Classe** | `EcouteurNode` *(src/agents/0_ecouteur.py)* |``  
``| **Entrées** | `input_blob: bytes | str` |``  
``| **Sorties** | `narration: NarrationJusticiable` |``  
``| **Pipeline interne** | 1 ) *detect type* (mimetype)<br>2 ) if audio → `stt.transcribe()`<br>3 ) `nlp.segment()` (phrases, dates, émotions)<br>4 ) `shared.set("narration", obj)` |``  
``| **Libs** | `openai` (*/audio/transcriptions*), `transformers[fr-core-news-md]` |``  
``| **Erreurs gérées** | `AudioTooLong`, `UnsupportedFormat`, `STTQuotaExceeded` |``  
``| **Tests** | `tests/test_ecouteur.py` — vérifie qu’un texte de 3 phrases => 3 segments |``  
`| **TODO 🔧** | – Option multi-canal (stereo → speaker diarization) |`

`*(Répéter ce gabarit si tu veux une fiche pour chaque agent.)*`

`---`

`## 3. Diagramme de dépendances agents ↔ SharedStore`

```` ```mermaid ````  
`graph TD`  
  `S[SharedStore] ---|read/write| A0`  
  `A0 -->|narration| S`  
  `S --- A1`  
  `A1 -->|axes & lois| S`  
  `S --- P(Parseur)`  
  `classDef node fill:#fdf,stroke:#333,stroke-width:1px;`  
  `class A0,A1,P node`

---

## **4\. Implémentation type (template Node)**

python  
CopierModifier  
`from defenseur_ia.core import BaseNode, NodeContext`  
`from defenseur_ia.utils import stt`

`class EcouteurNode(BaseNode):`  
    `id = "ecouteur"`

    `async def exec(self, ctx: NodeContext) -> None:`  
        `blob = await ctx.shared.get("input_blob")`  
        `text = await stt.transcribe(blob) if isinstance(blob, (bytes, bytearray)) else str(blob)`  
        `narration = segment(text)            # ← ta fonction maison`  
        `await ctx.shared.set("narration", narration)`

---

## **5\. Ajouter un nouvel agent**

1. Créer le fichier `src/defenseur_ia/agents/<id>_<nom>.py`.

2. Hériter de `BaseNode` et implémenter `async exec`.

3. Ajouter dans `src/defenseur_ia/flow.py` :

python  
CopierModifier  
`FLOW_ORDER = [`  
    `EcouteurNode(),`  
    `CadreurNode(),`  
    `…,`  
    `MonNouvelAgent(),`  
`]`

4. Documenter la ligne dans **ce fichier** (section tableau).

5. Écrire un test `tests/test_<id>.py`.

---

## **6\. Convention de tags**

| Tag | Signification rapide |
| ----- | ----- |
| **STT** | Speech-to-Text |
| **NLP** | traitement langage naturel |
| **LLM** | appel grand modèle |
| **OCR** | reconnaissance caractères |
| **ETL** | Extract-Transform-Load |
| **FAISS** | vector search |
| **QA** | quality-assurance |
| **PDF** | génération PDF |
| **ZIP** | compression/packaging |

*(Utilise ces tags dans la colonne « Tags » pour homogénéité doc & UI.)*

---

## **7\. Feuille de route agents (suivi dev)**

| Agent | Statut | Dev | Test | Notes |
| ----- | ----- | ----- | ----- | ----- |
| Écouteur | ✅ | ✅ | 🟡 | speaker diarization pending |
| Cadreur Juridique | ✅ | ✅ | 🟡 | whitelist Legifrance quotas |
| Parseur Preuves | 🔧 | 🟡 | 🔴 | tesseract docker image à valider |
| Matching FAISS | 🔧 | 🔴 | 🔴 | embeddings SBERT-FR |
| Web Scout | 🟡 | 🔴 | 🔴 | scrapegleam / newspaper |
| … | … | … | … | … |

*(Met à jour au fur et à mesure.)*

---

## **8\. Questions fréquentes**

**Q : Peut-on lancer un seul agent pour debugging ?**  
 **R :** oui : `defenseur-cli input.txt --step N` exécute jusqu’à N et stop ;  
 ou via Python :

python  
CopierModifier  
`node = ParseurPreuvesNode()`  
`await node.exec(ctx)`

**Q : Comment partager une info entre deux agents non consécutifs ?**  
 **R :** écris dans `shared.set("clé", valeur)` puis lis dans l’agent cible.  
 La *Shared Info Box* expose aussi une mini-API JSON.

---

➡️ **Next :**

* `docs/05_MODELS.md` — schémas Pydantic/Zod complets

* `docs/06_UTILS.md` — détails Legifrance, STT, OCR

* ou toute autre section que tu veux approfondir \!

CopierModifier

##### **Vous avez dit :**

docs/05\_MODELS.md

###### **ChatGPT a dit :**

md  
CopierModifier  
`<!-- docs/05_MODELS.md -->`  
`# 05 · DONNÉES & MODÈLES`

`> **“Pas de pipeline fiable sans schémas stricts.”**`    
`>`    
``> Tous les échanges entre agents passent par le `SharedStore`.``    
`> Chaque clé pointe vers **un objet typé** — défini en **Pydantic v2** *(Python)*`  
`> et **Zod** *(TypeScript)*.`    
`>`    
`> Les deux définitions sont **isomorphes** : même champs, même contraintes.`

`---`

`## 1. Vue d’ensemble : arbre des modèles`

```` ```text ````  
`SharedStore`  
`├── meta               → MetaInfo`  
`├── narration          → NarrationJusticiable`  
`├── axes               → List[HypotheseRecherche]`  
`├── legal_corpus       ─┬─ CodeArticle`  
`│                       └─ Jurisprudence`  
`├── pieces[]           ─┬─ PieceParsed (pdf, mail…)`  
`│                       └─ PieceMetaOCR`  
`├── draft`  
`│   ├── v0             → DraftNarratif`  
`│   ├── v1             → DraftCorrige`  
`│   └── latest         → str (ex : "v1")`  
`├── plan               → PlanStrategique`  
`├── requete_finale     → RequeteFinale`  
`└── logs.history[]     → str (horodatés)`

Chaque sous‐objet est **auto-documenté** ; ci-dessous les définitions.

---

## **2\. Schémas Pydantic v2 (Python)**

py  
CopierModifier  
`# packages/types/py/narration.py`  
`from pydantic import BaseModel, Field`  
`from typing import List, Literal`  
`from datetime import datetime`

`class Segment(BaseModel):`  
    `start: float = Field(..., ge=0)        # secondes`  
    `stop:  float = Field(..., ge=0)`  
    `text:  str`  
    `emotion: Literal["neutral","sad","angry","joy","fear","surprise"]`

`class NarrationJusticiable(BaseModel):`  
    `langage: str = "fr"`  
    `segments: List[Segment]`  
    `# champ dérivé`  
    `@property`  
    `def full_text(self) -> str:`  
        `return " ".join(s.text for s in self.segments)`

`# Hypothèses de recherche`  
`class HypotheseRecherche(BaseModel):`  
    `id: str`  
    `axe: str            # ex : "abus d’autorité de l’école"`  
    `priorité: int       # 1‒5`

`# Article / jurisprudence`  
`class CodeArticle(BaseModel):`  
    `cid: str                  # LEGITEXT…`  
    `num: str                  # "L.211-1"`  
    `titre: str`  
    `texte_html: str`  
    `source_url: str`  
    `fond: Literal["CODE","LODA"]`

`class Jurisprudence(BaseModel):`  
    `ecli: str`  
    `juridiction: str`  
    `date: datetime`  
    `résumé: str`  
    `lien: str`

`# Pièce parsée`  
`class PieceParsed(BaseModel):`  
    `id_piece: str`  
    `annexe_num: str          # pour export PDF`  
    `type_piece: Literal["email","pdf","image","docx","texte","audio","sms","virtuel"]`  
    `titre: str`  
    `texte_anonymise: str`  
    `meta_extra: dict | None = None`

`# Brouillons narratifs`  
`class DraftNarratif(BaseModel):`  
    `version: str`  
    `texte_markdown: str`  
    `tokens_llm: int`

`class DraftCorrige(DraftNarratif):  # même champs + diff`  
    `suggestions: list[str]`

`# Plan stratégique`  
`class PlanStrategique(BaseModel):`  
    `angles: list[str]`  
    `scoring: list[tuple[str,int]]      # (angle, score/100)`  
    `roadmap: list[str]                 # étapes recommandées`

`# Requête finale`  
`class RequeteFinale(BaseModel):`  
    `titre: str`  
    `corps_markdown: str`  
    `annexes: list[str]                 # chemins des pièces`

`# META & LOGS`  
`class MetaInfo(BaseModel):`  
    `dossier_id: str`  
    `langue: str`  
    `created_at: datetime`

---

## **3\. Schémas Zod (TypeScript)**

*(extraits ; les champs correspondent 1-pour-1)*

ts  
CopierModifier  
`// packages/types/ts/narration.ts`  
`import { z } from "zod";`

`export const Segment = z.object({`  
  `start: z.number().nonnegative(),`  
  `stop:  z.number().nonnegative(),`  
  `text:  z.string(),`  
  `emotion: z.enum([`  
    `"neutral","sad","angry","joy","fear","surprise"`  
  `]),`  
`});`

`export const NarrationJusticiable = z.object({`  
  `langage: z.literal("fr"),`  
  `segments: z.array(Segment),`  
`});`  
`export type NarrationJusticiable = z.infer<typeof NarrationJusticiable>;`

*(les autres fichiers reprennent les mêmes champs que la partie*  
 *Pydantic ; voir `packages/types/ts/`.)*

---

## **4\. Mapping clé Shared ➜ modèle**

| Clé `shared[...]` | Modèle Pydantic / Zod | Créé par agent | Consommé par |
| ----- | ----- | ----- | ----- |
| `narration` | `NarrationJusticiable` | Écouteur | Cadreur, Rédacteur |
| `axes` | `HypotheseRecherche[]` | Cadreur | Matching, WebScout |
| `legal_corpus` | `CodeArticle[]`, `Jurisprudence[]` | Cadreur | Matching |
| `pieces` | `PieceParsed[]` | ParseurPreuves | Matching, Export |
| `draft.v0` | `DraftNarratif` | Rédacteur | QA1 |
| `draft.v1` | `DraftCorrige` | QA1 | Agrégateur |
| `plan` | `PlanStrategique` | Synthèse | Avocat |
| `requete_finale` | `RequeteFinale` | Avocat | Export |
| `logs.history` | `str[]` | **auto** | Human / debug |

---

## **5\. Validation & sérialisation**

* **Autosave** : chaque appel `SharedStore.save()` → `json.dumps(obj, allow_nan=False, indent=2, ensure_ascii=False)`.

* **Backward-compatibilité** : ajoute **`version: 1`** en racine dès que tu  
   changes un schéma. Les agents doivent gérer `if meta.version < 2: migrate()`.

---

## **6\. Stratégies d’anonymisation**

`texte_anonymise` dans `PieceParsed` est produit par :

1. `regex` sur mails, n°-tél, accents…

2. appel LLM → “Replace real names by `PERSON_X`”.

Le champ `meta_extra.original_path` conserve le chemin brut  
 (local ou S3) — **jamais** commit dans le JSON partagé.

---

## **7\. TODO (roadmap modèles)**

| ⚙️ Tâche | Description |
| ----- | ----- |
| `CodeArticle.state` | Enum étendu (`VIGUEUR`, `ABROGE`, …) |
| `Segment.lang` | multi-langue segmenté (FR/EN mix) |
| `PieceParsed.hash_sha256` | déduplication pièces |
| `Draft*`.markdown → HTML | pré-render pour le front |

---

**Source of truth** :  
 `packages/types/py/*.py` & `packages/types/ts/*.ts`.  
 Si ton PR modifie un champ, **mets à jour ce doc** \!

makefile  
CopierModifier  
`::contentReference[oaicite:0]{index=0}`

Sources

##### **Vous avez dit :**

docs/06\_UTILS.md

###### **ChatGPT a dit :**

md  
CopierModifier  
`<!-- docs/06_UTILS.md -->`  
`# 06 · MODULE **UTILS**`

``Tous les “muscles” techniques vivent dans `packages/utils/`.``    
`Les agents ne font **qu’orchestrer** : ils appellent ces helpers pour la`  
`vraie I/O (API, OCR, embeddings, export PDF…).`

`---`

`## Index rapide`

`| Dossier | Fonction(s) | Dépendances lourdes |`  
`|---------|-------------|---------------------|`  
``| `stt/` | `transcribe()` | OpenAI Whisper · Gemini Live |``  
``| `legifrance/` | `oauth_token()`, `search()`, `consult()` | `httpx` |``  
``| `ocr/` | `ocr_image()` | docker-tesseract |``  
``| `anonymise/` | `anon_text()` | GPT-4o · regex |``  
``| `embedding/` | `embed()`, `faiss_index()` | `sentence-transformers`, `faiss` |``  
``| `export/` | `render_pdf()`, `zip_dossier()` | WeasyPrint, ZipFile |``  
``| `scraper/` | `scrape_forums()` | `playwright` (headless) |``  
``| `logger/` | `setup_logging()` | `loguru` |``

`---`

`## 1. STT (**Speech-to-Text**)`

```` ```py ````  
`# utils/stt.py`  
`from openai import AsyncOpenAI`  
`import asyncio, httpx`

`async def transcribe(buffer: bytes, *, engine="whisper", lang="fr") -> str:`  
    `if engine == "whisper":`  
        `client = AsyncOpenAI()`  
        `return (`  
            `await client.audio.transcriptions.create(`  
                `model="whisper-1",`  
                `file=("audio.wav", buffer, "audio/wav"),`  
                `language=lang,`  
            `)`  
        `).text`  
    `if engine == "gemini":`  
        `# streaming via Google Gemini Live`  
        `resp = await httpx.post(`  
            `"https://generativelanguage.googleapis.com/v1beta/models/speech:transcribe",`  
            `headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},`  
            `params={"model": "gemini-live-2.5-flash-preview"},`  
            `files={"audio": buffer},`  
        `)`  
        `resp.raise_for_status()`  
        `return resp.json()["text"]`

| Astuce | Détail |
| ----- | ----- |
| Buffer ≤ **25 Mo** | Limite Whisper API |
| Multi-canal | Passe `diarize=True` (TODO) |
| Cache | `(sha256(buffer) → s3://cache/stt/<hash>.txt)` |

---

## **2\. Légifrance API wrapper**

### **2.1 Authentification OAuth2**

py  
CopierModifier  
`# utils/legifrance/auth.py`  
`from httpx import AsyncClient`  
`from fastapi import BackgroundTasks`  
`import os, time`

`_token: dict[str,str] = {}`

`async def oauth_token() -> str:`  
    `if _token and _token["exp"] > time.time() + 60:`  
        `return _token["access_token"]`

    `async with AsyncClient() as cli:`  
        `data = {`  
            `"grant_type": "client_credentials",`  
            `"client_id": os.getenv("LEGIFRANCE_ID"),`  
            `"client_secret": os.getenv("LEGIFRANCE_SECRET")`  
        `}`  
        `res = await cli.post(`  
            `"https://sandbox-oauth.piste.gouv.fr/api/oauth/token",`  
            `data=data,`  
            `timeout=10,`  
        `)`  
        `res.raise_for_status()`  
        `_token.update(res.json(), exp=time.time()+res.json()["expires_in"])`  
        `return _token["access_token"]`

### **2.2 Recherche générique**

py  
CopierModifier  
`async def search(q:str, size:int=20) -> list[dict]:`  
    `tok = await oauth_token()`  
    `payload = {"query": q, "pageNumber": 1, "pageSize": size}`  
    `async with AsyncClient() as cli:`  
        `res = await cli.post(`  
            `"https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/search",`  
            `headers={"Authorization": f"Bearer {tok}",`  
                     `"Accept": "application/json"},`  
            `json=payload, timeout=15,`  
        `)`  
    `res.raise_for_status()`  
    `return res.json().get("results", [])`

**Quota sandbox** : 30 req/min.  
 Utilise `asyncio.Semaphore(5)` \+ *exponential backoff* dans le helper.

---

## **3\. OCR (Tesseract)**

bash  
CopierModifier  
`docker build -t ocr --file docker/tesseract.Dockerfile .`  
`docker run --rm -v $(pwd)/pieces:/in ocr /in/scan1.jpg > out.txt`

Python wrapper :

py  
CopierModifier  
`import subprocess, tempfile, pathlib, asyncio`

`async def ocr_image(img_bytes: bytes, lang="fra+eng") -> str:`  
    `with tempfile.TemporaryDirectory() as td:`  
        `fp = pathlib.Path(td)/"img.png"`  
        `fp.write_bytes(img_bytes)`  
        `cmd = ["docker","run","--rm","-v",f"{td}:/data","ocr",`  
               `"tesseract","/data/img.png","stdout","-l",lang,"--psm","6"]`  
        `proc = await asyncio.create_subprocess_exec(`  
            `*cmd, stdout=asyncio.subprocess.PIPE)`  
        `out, _ = await proc.communicate()`  
        `return out.decode("utf8")`

---

## **4\. Anonymisation texte**

py  
CopierModifier  
`import re, openai, os`

`_regex = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")`

`async def anon_text(txt:str) -> str:`  
    `txt = _regex.sub("PERSON_X", txt)`  
    `gpt = openai.AsyncOpenAI()`  
    `out = await gpt.chat.completions.create(`  
        `model="gpt-4o-mini",`  
        `messages=[`  
            `{"role":"system","content":"Replace any remaining personal data with placeholders."},`  
            `{"role":"user","content":txt}`  
        `],`  
        `max_tokens=len(txt)//4 + 20,`  
    `)`  
    `return out.choices[0].message.content`

---

## **5\. Embeddings \+ FAISS**

py  
CopierModifier  
`from sentence_transformers import SentenceTransformer`  
`import faiss, numpy as np`

`_model = SentenceTransformer("dangvantuan/sentence-camembert-base")`  
`_index = faiss.IndexFlatIP(768)`

`def embed(texts:list[str]) -> np.ndarray:`  
    `return _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)`

`def faiss_index(texts:list[str]):`  
    `vecs = embed(texts)`  
    `_index.add(vecs)`  
    `return _index`

* Stockage index : `_index.write_index("faiss.index")`, \> 50 MB file.

* Similarité requête → `D, I = index.search(embed([query]), k=5)`.

---

## **6\. Export PDF \+ ZIP**

py  
CopierModifier  
`from weasyprint import HTML`  
`from pathlib import Path, PurePosixPath`  
`from zipfile import ZipFile`

`def render_pdf(md:str, dest:Path):`  
    `html = markdown.markdown(md, extensions=['tables'])`  
    `HTML(string=html, base_url=".").write_pdf(dest)`

`def zip_dossier(pdf:Path, pieces_dir:Path, out_zip:Path):`  
    `with ZipFile(out_zip, "w") as z:`  
        `z.write(pdf, pdf.name)`  
        `for p in pieces_dir.glob("*"):`  
            `z.write(p, PurePosixPath("annexes")/p.name)`

---

## **7\. Scraper Web Scout**

* **Playwright headless** (`pip install playwright && playwright install chrome`)

* Limite à `*.asso.fr`, `*.org`, `forum.immigrés.gouv`…

* Respecte **robots.txt** via `robotexclusionrulesparser`.

Snippet :

py  
CopierModifier  
`from playwright.async_api import async_playwright`

`async def scrape_forums(keyword:str, limit:int=5) -> list[str]:`  
    `async with async_playwright() as p:`  
        `browser = await p.chromium.launch(headless=True)`  
        `page = await browser.new_page()`  
        `await page.goto(f"https://duckduckgo.com/?q={keyword}+site:forum.immigration.fr")`  
        `links = await page.eval_on_selector_all("a.result__url", "els => els.map(e=>e.href)")`  
        `results = []`  
        `for href in links[:limit]:`  
            `await page.goto(href)`  
            `body = await page.inner_text("body")`  
            `results.append(body[:10_000])`  
        `return results`

---

## **8\. Logging**

py  
CopierModifier  
`from loguru import logger`  
`import sys, os`

`def setup_logging(level="INFO"):`  
    `logger.remove()`  
    `logger.add(sys.stderr, level=level,`  
               `format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} | {message}")`  
    `if path := os.getenv("LOG_FILE"):`  
        `logger.add(path, rotation="10 MB", compression="zip")`

Agents appellent `logger` **et** `shared.log()` pour garder un  
 historique léger dans JSON.

---

## **9\. Cache (très léger)**

`utils/cache.py` expose `@ttl_cache(seconds=3600)` à la sauce  
 functools LRU \+ TTL ; utilisé sur `oauth_token()` et `embed()`.

---

## **10\. TODO utils**

| Module | Améliorations |
| ----- | ----- |
| STT | diacritics fixing, diarization |
| OCR | vision-api fallback (cloud) |
| Legifrance | field‐select pour réduire payload |
| Embedding | switch `microsoft/xtremedistil-l6-h384` for speed |
| PDF | sign / timestamp PDF (PyHanko) |

---

Besoin de code plus détaillé ?

**Ping un module précis** & on jette un œil au fichier source ensemble.

makefile  
CopierModifier  
`::contentReference[oaicite:0]{index=0}`

Sources

##### **Vous avez dit :**

07 dev guide , changelog

###### **ChatGPT a dit :**

md  
CopierModifier  
`<!-- docs/07_DEV_GUIDE.md -->`  
`# 07 · GUIDE DEV / CONTRIBUTING`  
`_“Ship small, test hard, document tout.”_`

`---`

`## 1. Workflow Git`

`| Étape | Branche | Règle |`  
`|-------|---------|-------|`  
``| _Main / Prod_ | **`main`** | Toujours stable ; protégé. |``  
``| _Intégration_ | **`develop`** | Merge squash from feature/* ; CI complète. |``  
``| _Fonction_ | **`feature/<ticket>-<slug>`** | 1 tâche ≈ 1 PR. |``  
``| _Correctif hot_ | **`hotfix/<x.x.x>`** | Patch rapide, merge→ main + develop. |``

```` ```bash ````  
`git switch -c feature/1234-legifrance-wrapper`

⚠️ Pas de commit direct sur `main`.

---

## **2\. Commits convention (Conventional Commits)**

bash  
CopierModifier  
`<type>(scope): sujet bref`

`body éventuel…`

| Type | Exemple |
| ----- | ----- |
| **feat** | `feat(ocr): add fra+eng lang auto-detect` |
| **fix** | `fix(stt): handle >25 MB by chunking` |
| **docs** | `docs(models): update PieceParsed spec` |
| **refactor** | `refactor(shared): extract save() helper` |
| **test** | `test(api): stub legifrance sandbox` |
| **chore** | banalités (ci, deps) |

---

## **3\. Lint \+ Tests**

bash  
CopierModifier  
`pnpm lint      # eslint + prettier --check`  
`pnpm test      # jest`  
`poetry run pytest  # si partie py modifiée`

`# pre-commit hook`  
`npx lefthook run pre-commit`

CI GitHub → bloque merge si **lint ou tests** échouent.

---

## **4\. Ajout d’un module utils**

1. Créer `packages/utils/<module>/`.

2. Exposer **index.ts / init.py**.

3. Ajouter doc dans `docs/06_UTILS.md`.

4. Écrire tests → cover ≥ 80 % lignes.

5. Mettre à jour CHANGELOG dans `## [Unreleased]`.

---

## **5\. Versioning & Release**

* **SemVer** : `MAJOR.MINOR.PATCH`

* Merge PR → `develop`

* Maintainer exécute :

bash  
CopierModifier  
`pnpm version patch   # ou minor/major`  
`pnpm changelog       # auto-bump & tag`  
`git push --follow-tags`

* GitHub Action : crée release \+ upload artefact docker (server) & npm (cli).

---

## **6\. ENVs & Secrets**

| Fichier | Contenu |
| ----- | ----- |
| `.env.example` | clés API **FAUSSES** (template) |
| GitHub → Secrets | `OPENAI_KEY`, `LEGIFRANCE_ID`, `LEGIFRANCE_SECRET`, `GEMINI_KEY` |

Jamais de secret dans le repo.

---

## **7\. Docs**

* Tous les fichiers sous `docs/` (numérotés).

* Schémas UML / Mermaid autorisés \-\> gardés légers.

---

## **8\. Diagramme CI (GitHub Actions)**

mermaid  
CopierModifier  
`graph TD`  
  `PR --> Lint --> UnitTests --> BuildDocker --> DeployDocs`  
  `BuildDocker -->|push| ghcr`

---

## **9\. Checklist PR**

* Branche \= feature/\* ou fix/\*

* Lint OK

* Tests ajoutés / mis à jour

* CHANGELOG entrée

* Docs modifiées si nécessaire

* ✅ Review \> 1 reviewer

---

## **10\. Ressources utiles**

* **OpenAI Node SDK**: [https://github.com/openai/openai-node](https://github.com/openai/openai-node)

* **Legifrance Swagger**: `sandbox-api.piste.gouv.fr/…/swagger.json`

* **WeasyPrint** guide : https://weasyprint.org/docs/

*Build, test, repeat — et restons polis dans les revues \!*

yaml  
CopierModifier

`---`

```` ```md ````  
`<!-- CHANGELOG.md -->`  
`# Changelog`

`Toutes les modifications notables de ce projet seront documentées`  
`dans ce fichier, suivant la norme **[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)**`    
`et la version **SemVer**.`

`## [Unreleased]`

`### Added`  
``- `docs/07_DEV_GUIDE.md` & `CHANGELOG.md` premier jet.``  
``- Module utils `legifrance/auth.py` (OAuth2 token cache).``  
`- Section _“05 MODELS”_ (spec Pydantic + Zod).`

`### Changed`  
``- Table récap agents dans `docs/04_AGENTS.md` (tags normalisés).``

`### Fixed`  
`- N/A`

`---`

`## [0.1.0] – 2025-07-26`

`### Added`  
`- Scaffolding Node 18 + pnpm workspace.`  
``- Core engine (`BaseNode`, `Flow`, `SharedStore`).``  
`- Agents 0 (Écouteur) & 1 (Cadreur Juridique) MVP.`  
`- Utils : STT Whisper, basic Legifrance search, OCR docker.`  
`- Docs : 01 README, 02 CLI, 03 Architecture ASCII.`

`### Changed`  
`- N/A`

`### Fixed`  
`- N/A`

`---`

`\* Date au format ISO 8601 (YYYY-MM-DD).`    
``Prochaine release = merge de `Unreleased` -> tag.``  
