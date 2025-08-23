# 🛡️ DEFENSEUR-IA - Plan de développement complet

## Phase 1 : Fondations (Semaine 1-2)

### 1.1 Setup du projet
```bash
# Structure monorepo Poetry
defenseur-ia/
├── pyproject.toml           # Dépendances & scripts Poetry
├── README.md               
├── .env.template           # Variables d'environnement
├── scripts/                # Helpers bash/make
├── tests/                  # pytest unit/integ
└── src/defenseur_ia/
    ├── core/               # BaseNode, Flow, SharedStore
    ├── agents/             # 00_ecouteur.py → 11_export.py
    ├── utils/              # stt, legifrance, ocr, etc.
    ├── types/              # models.py (Pydantic v2)
    ├── cli.py              # Point d'entrée CLI
    └── server/             # FastAPI (optionnel phase 1)
```

### 1.2 Core Engine
```python
# src/defenseur_ia/core/node.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseNode(ABC):
    """Classe abstraite pour tous les agents"""
    id: str
    
    @abstractmethod
    async def exec(self, ctx: 'NodeContext') -> None:
        """Exécute la logique de l'agent"""
        pass

# src/defenseur_ia/core/shared.py
class SharedStore:
    """Store JSON partagé entre agents"""
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.logs = {"history": []}
    
    async def get(self, key: str) -> Any:
        return self.data.get(key)
    
    async def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        await self.save()
    
    async def save(self) -> None:
        # Persist to dossier.json
        pass
```

### 1.3 Modèles Pydantic
```python
# src/defenseur_ia/types/models.py
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class Segment(BaseModel):
    start: float = Field(..., ge=0)
    stop: float = Field(..., ge=0) 
    text: str
    emotion: Literal["neutral","sad","angry","joy","fear","surprise"]

class NarrationJusticiable(BaseModel):
    langue: str = "fr"
    segments: List[Segment]

class HypotheseRecherche(BaseModel):
    id: str
    axe: str  # ex: "abus d'autorité de l'école"
    priorite: int  # 1-5

class CodeArticle(BaseModel):
    cid: str  # LEGITEXT...
    num: str  # "L.211-1" 
    titre: str
    texte_html: str
    source_url: str
    fond: Literal["CODE","LODA"]

class PieceParsed(BaseModel):
    id_piece: str
    annexe_num: str
    type_piece: Literal["email","pdf","image","docx","texte","audio","sms"]
    titre: str
    texte_anonymise: str
    meta_extra: dict | None = None
```

## Phase 2 : Agents prioritaires (Semaine 3-4)

### 2.1 Agent 0 - Écouteur (STT)
```python
# src/defenseur_ia/agents/00_ecouteur.py
from defenseur_ia.core import BaseNode, NodeContext
from defenseur_ia.utils import stt
from defenseur_ia.types.models import NarrationJusticiable, Segment

class EcouteurNode(BaseNode):
    id = "ecouteur"
    
    async def exec(self, ctx: NodeContext) -> None:
        blob = await ctx.shared.get("input_blob")
        
        if isinstance(blob, (bytes, bytearray)):
            # Audio → STT
            text = await stt.transcribe(blob, engine="whisper")
        else:
            # Texte direct
            text = str(blob)
        
        # Segmentation simple (à améliorer)
        segments = [Segment(
            start=0.0,
            stop=len(text)/10,  # estimation
            text=text,
            emotion="neutral"
        )]
        
        narration = NarrationJusticiable(
            langue="fr",
            segments=segments
        )
        
        await ctx.shared.set("narration", narration)
```

### 2.2 Utils STT
```python
# src/defenseur_ia/utils/stt.py
from openai import AsyncOpenAI
import os

async def transcribe(buffer: bytes, *, engine="whisper", lang="fr") -> str:
    """Transcrit audio en texte"""
    if engine == "whisper":
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.wav", buffer, "audio/wav"),
            language=lang,
        )
        return response.text
    
    elif engine == "gemini":
        # TODO: Implémenter Gemini Live
        raise NotImplementedError("Gemini STT à implémenter")
    
    else:
        raise ValueError(f"Engine non supporté: {engine}")
```

### 2.3 Agent 1 - Cadreur Juridique  
```python
# src/defenseur_ia/agents/01_cadreur_juridique.py
from defenseur_ia.core import BaseNode, NodeContext
from defenseur_ia.utils import legifrance
from defenseur_ia.types.models import HypotheseRecherche, CodeArticle

class CadreurJuridiqueNode(BaseNode):
    id = "cadreur_juridique"
    
    async def exec(self, ctx: NodeContext) -> None:
        narration = await ctx.shared.get("narration")
        
        # 1. Extraire axes juridiques via LLM
        axes = await self._extract_axes(narration.full_text)
        
        # 2. Rechercher dans Légifrance
        legal_corpus = []
        for axe in axes:
            articles = await legifrance.search(axe.axe, size=10)
            legal_corpus.extend(articles)
        
        await ctx.shared.set("axes", axes)
        await ctx.shared.set("legal_corpus", legal_corpus)
    
    async def _extract_axes(self, text: str) -> List[HypotheseRecherche]:
        # TODO: Appel GPT-4 pour extraire axes juridiques
        return [
            HypotheseRecherche(
                id="axe_1",
                axe="analyse du récit juridique",
                priorite=5
            )
        ]
```

### 2.4 Utils Légifrance
```python
# src/defenseur_ia/utils/legifrance/auth.py
import httpx
import os
import time
from typing import Dict

_token_cache: Dict[str, any] = {}

async def oauth_token() -> str:
    """Récupère token OAuth2 Légifrance (avec cache)"""
    if _token_cache and _token_cache.get("exp", 0) > time.time() + 60:
        return _token_cache["access_token"]
    
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("LEGIFRANCE_ID"),
            "client_secret": os.getenv("LEGIFRANCE_SECRET")
        }
        
        response = await client.post(
            "https://sandbox-oauth.piste.gouv.fr/api/oauth/token",
            data=data,
            timeout=10
        )
        response.raise_for_status()
        
        token_data = response.json()
        _token_cache.update(token_data)
        _token_cache["exp"] = time.time() + token_data["expires_in"]
        
        return token_data["access_token"]

async def search(query: str, size: int = 20) -> list[dict]:
    """Recherche dans Légifrance"""
    token = await oauth_token()
    
    payload = {
        "recherche": {
            "champs": [{
                "typeChamp": "ALL",
                "criteres": [{
                    "typeRecherche": "EXACTE",
                    "valeur": query,
                    "operateur": "ET"
                }],
                "operateur": "ET"
            }],
            "pageNumber": 1,
            "pageSize": size,
            "operateur": "ET",
            "sort": "PERTINENCE",
            "typePagination": "DEFAUT"
        },
        "fond": "CODE_DATE"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/search",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        
    return response.json().get("results", [])
```

## Phase 3 : Pipeline complet (Semaine 5-8)

### 3.1 Agents restants
- **Agent 3** : ParseurPreuves (OCR Tesseract)
- **Agent 4** : JuristeMatching (FAISS embeddings)  
- **Agent 5** : WebScout (scraping forums)
- **Agent 6** : RédacteurNarratif (GPT-4o)
- **Agent 7-8** : Relecteurs IA (QA)
- **Agent 9** : SynthèseStratégique
- **Agent 10** : AvocatIA (requête finale)
- **Agent 11** : ExportFinal (WeasyPrint PDF)

### 3.2 CLI fonctionnel
```python
# src/defenseur_ia/cli.py
import asyncio
import argparse
from pathlib import Path
from defenseur_ia.core.flow import Flow
from defenseur_ia.core.shared import SharedStore

async def main():
    parser = argparse.ArgumentParser(description="DEFENSEUR-IA CLI")
    parser.add_argument("input", help="Fichier audio/texte ou texte direct")
    parser.add_argument("--json", help="Reprendre dossier existant")
    parser.add_argument("--step", type=int, help="Arrêter à l'étape N")
    
    args = parser.parse_args()
    
    # Initialiser SharedStore
    if args.json:
        shared = SharedStore.load(args.json)
    else:
        shared = SharedStore()
        
        # Charger input
        if Path(args.input).exists():
            with open(args.input, "rb") as f:
                await shared.set("input_blob", f.read())
        else:
            await shared.set("input_blob", args.input)
    
    # Exécuter pipeline
    flow = Flow()
    await flow.run(shared, stop_step=args.step)
    
    print(f"✅ Dossier généré : {shared.data.get('output_path', 'dossier.json')}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Phase 4 : API & Interface (Semaine 9-10)

### 4.1 FastAPI Server
```python
# src/defenseur_ia/server/main.py
from fastapi import FastAPI, File, UploadFile, WebSocket
from defenseur_ia.core.flow import Flow
from defenseur_ia.core.shared import SharedStore

app = FastAPI(title="DEFENSEUR-IA API")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/upload_piece")
async def upload_piece(file: UploadFile = File(...)):
    # Sauvegarder pièce
    return {"piece_id": "...", "status": "uploaded"}

@app.post("/run_full_flow")
async def run_flow(dossier_id: str = None, input_text: str = None):
    shared = SharedStore()
    if input_text:
        await shared.set("input_blob", input_text)
    
    flow = Flow()
    await flow.run(shared)
    
    return {"dossier_id": shared.data["meta"]["dossier_id"]}

@app.websocket("/stream/{dossier_id}")
async def websocket_endpoint(websocket: WebSocket, dossier_id: str):
    await websocket.accept()
    # Stream logs en temps réel
```

## Phase 5 : Tests & Documentation (Semaine 11-12)

### 5.1 Tests unitaires
```python
# tests/test_ecouteur.py
import pytest
from defenseur_ia.agents.ecouteur import EcouteurNode
from defenseur_ia.core.shared import SharedStore

@pytest.mark.asyncio
async def test_ecouteur_texte():
    shared = SharedStore()
    await shared.set("input_blob", "Je m'appelle Alice et j'ai un problème.")
    
    node = EcouteurNode()
    ctx = NodeContext(shared=shared)
    await node.exec(ctx)
    
    narration = await shared.get("narration")
    assert narration.langue == "fr"
    assert len(narration.segments) > 0
```

### 5.2 Documentation complète
- README.md (setup rapide)
- docs/00_OVERVIEW.md (architecture)
- docs/01_INSTALL.md (installation détaillée)
- docs/02_CLI.md (utilisation CLI)
- docs/04_AGENTS.md (catalogue agents)
- docs/05_MODELS.md (schémas Pydantic)
- docs/06_UTILS.md (modules utilitaires)

## Variables d'environnement

```env
# .env.template
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
LEGIFRANCE_ID=mon_client_id
LEGIFRANCE_SECRET=mon_secret
PIECES_DIR=./pieces
SHARED_PATH=./dossier.json
LOG_LEVEL=INFO
```

## Commandes de développement

```bash
# Installation
poetry install

# Tests
poetry run pytest -v

# Lint
poetry run ruff check src/

# CLI
poetry run python -m defenseur_ia.cli "texte test"

# Serveur
poetry run uvicorn defenseur_ia.server.main:app --reload --port 8000
```

## Priorités de développement

1. ✅ **Core engine fonctionnel** (BaseNode, Flow, SharedStore)
2. ✅ **Agent 0 + 1** (Écouteur STT + Cadreur Légifrance)  
3. 🔧 **Utils robustes** (gestion erreurs, cache, quotas)
4. 🔧 **Pipeline complet** (agents 3-11)
5. 🔧 **CLI stable** + tests
6. 🔧 **API FastAPI** optionnelle
7. 📋 **Documentation** complète

Le projet est ambitieux mais bien structuré. L'approche modulaire avec les agents permet un développement incrémental et des tests isolés.