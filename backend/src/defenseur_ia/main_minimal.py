"""
Backend FastAPI minimal pour DEFENSEUR-IA - Connectiques Frontend
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
import json
import os

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Modèles Pydantic pour les APIs
class CaseCreateRequest(BaseModel):
    nom_justiciable: str
    type_contentieux: str
    description: str
    urgence: str = "normale"

class CaseResponse(BaseModel):
    dossier_id: str
    nom_justiciable: str
    type_contentieux: str
    description: str
    status: str
    created_at: str
    updated_at: str

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    type: str
    size: int
    uploaded_at: str

class PipelineStatusResponse(BaseModel):
    dossier_id: str
    status: str
    current_step: int
    total_steps: int
    progress: float
    logs: List[str]

class ChatMessage(BaseModel):
    message: str
    attachments: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    flow_id: Optional[str] = None
    status: str

# Storage en mémoire pour la démo
cases_storage = {}
documents_storage = {}
pipeline_status = {}
chat_sessions = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de durée de vie de l'application"""
    logger.info("🚀 Démarrage de DEFENSEUR-IA Backend Minimal")
    yield
    logger.info("🛑 Arrêt de DEFENSEUR-IA Backend Minimal")

# Création de l'application FastAPI
app = FastAPI(
    title="DEFENSEUR-IA Backend Minimal",
    description="Backend FastAPI minimal pour connecter le frontend",
    version="2024.12.01",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ENDPOINTS CASES =====

@app.get("/api/v1/cases", response_model=List[CaseResponse])
async def get_cases(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    type_contentieux: Optional[str] = None
):
    """Récupérer la liste des dossiers"""
    try:
        cases = list(cases_storage.values())
        
        # Filtrage
        if status:
            cases = [c for c in cases if c.get("status") == status]
        if type_contentieux:
            cases = [c for c in cases if c.get("type_contentieux") == type_contentieux]
        
        # Pagination
        cases = cases[skip:skip + limit]
        
        return cases
    except Exception as e:
        logger.error(f"Erreur récupération dossiers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/cases", response_model=CaseResponse)
async def create_case(case_data: CaseCreateRequest):
    """Créer un nouveau dossier"""
    try:
        dossier_id = f"dossier_{len(cases_storage) + 1:04d}"
        now = datetime.now().isoformat()
        
        case = {
            "dossier_id": dossier_id,
            "nom_justiciable": case_data.nom_justiciable,
            "type_contentieux": case_data.type_contentieux,
            "description": case_data.description,
            "urgence": case_data.urgence,
            "status": "nouveau",
            "created_at": now,
            "updated_at": now
        }
        
        cases_storage[dossier_id] = case
        
        # Initialiser le statut pipeline
        pipeline_status[dossier_id] = {
            "dossier_id": dossier_id,
            "status": "en_attente",
            "current_step": 0,
            "total_steps": 12,
            "progress": 0.0,
            "logs": [f"Dossier {dossier_id} créé"]
        }
        
        logger.info(f"Nouveau dossier créé: {dossier_id}")
        return case
    except Exception as e:
        logger.error(f"Erreur création dossier: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/cases/{dossier_id}", response_model=CaseResponse)
async def get_case(dossier_id: str):
    """Récupérer un dossier spécifique"""
    if dossier_id not in cases_storage:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    return cases_storage[dossier_id]

@app.put("/api/v1/cases/{dossier_id}", response_model=CaseResponse)
async def update_case(dossier_id: str, updates: dict):
    """Mettre à jour un dossier"""
    if dossier_id not in cases_storage:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    case = cases_storage[dossier_id]
    case.update(updates)
    case["updated_at"] = datetime.now().isoformat()
    
    return case

@app.delete("/api/v1/cases/{dossier_id}")
async def delete_case(dossier_id: str):
    """Supprimer un dossier"""
    if dossier_id not in cases_storage:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    del cases_storage[dossier_id]
    if dossier_id in pipeline_status:
        del pipeline_status[dossier_id]
    
    return {"message": "Dossier supprimé"}

# ===== ENDPOINTS DOCUMENTS =====

@app.post("/api/v1/upload", response_model=List[DocumentResponse])
async def upload_documents(files: List[UploadFile] = File(...), dossier_id: str = ""):
    """Upload de documents"""
    try:
        uploaded_docs = []
        
        for file in files:
            doc_id = f"doc_{len(documents_storage) + 1:06d}"
            
            # Simuler la sauvegarde
            doc = {
                "document_id": doc_id,
                "filename": file.filename,
                "type": file.content_type or "application/octet-stream",
                "size": file.size or 0,
                "dossier_id": dossier_id,
                "uploaded_at": datetime.now().isoformat()
            }
            
            documents_storage[doc_id] = doc
            uploaded_docs.append(doc)
        
        logger.info(f"Uploaded {len(files)} documents pour dossier {dossier_id}")
        return uploaded_docs
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents/{dossier_id}", response_model=List[DocumentResponse])
async def get_documents(dossier_id: str):
    """Récupérer les documents d'un dossier"""
    docs = [doc for doc in documents_storage.values() if doc.get("dossier_id") == dossier_id]
    return docs

# ===== ENDPOINTS PIPELINE =====

@app.post("/api/v1/pipeline/{dossier_id}/start")
async def start_pipeline(dossier_id: str):
    """Démarrer le pipeline pour un dossier"""
    if dossier_id not in cases_storage:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    # Simuler le démarrage du pipeline
    pipeline_status[dossier_id] = {
        "dossier_id": dossier_id,
        "status": "en_cours",
        "current_step": 1,
        "total_steps": 12,
        "progress": 8.33,
        "logs": [
            f"Pipeline démarré pour {dossier_id}",
            "Agent 0 - Écouteur: En cours..."
        ]
    }
    
    logger.info(f"Pipeline démarré pour {dossier_id}")
    return {"message": "Pipeline démarré", "dossier_id": dossier_id}

@app.get("/api/v1/pipeline/{dossier_id}/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(dossier_id: str):
    """Récupérer le statut du pipeline"""
    if dossier_id not in pipeline_status:
        raise HTTPException(status_code=404, detail="Statut pipeline non trouvé")
    
    return pipeline_status[dossier_id]

@app.post("/api/v1/pipeline/{dossier_id}/pause")
async def pause_pipeline(dossier_id: str):
    """Mettre en pause le pipeline"""
    if dossier_id in pipeline_status:
        pipeline_status[dossier_id]["status"] = "en_pause"
        pipeline_status[dossier_id]["logs"].append("Pipeline mis en pause")
    
    return {"message": "Pipeline mis en pause"}

@app.post("/api/v1/pipeline/{dossier_id}/resume")
async def resume_pipeline(dossier_id: str):
    """Reprendre le pipeline"""
    if dossier_id in pipeline_status:
        pipeline_status[dossier_id]["status"] = "en_cours"
        pipeline_status[dossier_id]["logs"].append("Pipeline repris")
    
    return {"message": "Pipeline repris"}

# ===== ENDPOINTS CHAT =====

@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(message: ChatMessage):
    """Endpoint pour les messages du chat"""
    try:
        # Simuler une réponse du ChatOrchestrator
        response_text = f"Message reçu: {message.message}"
        
        if message.message.startswith("/"):
            # Commande spéciale
            if message.message == "/help":
                response_text = """Commandes disponibles:
/help - Afficher cette aide
/status - Statut du système
/analyse - Démarrer une analyse
/historique - Voir l'historique"""
            elif message.message == "/status":
                response_text = f"Système opérationnel. {len(cases_storage)} dossiers actifs."
            elif message.message == "/analyse":
                response_text = "Analyse démarrée. Veuillez uploader vos documents."
            else:
                response_text = f"Commande inconnue: {message.message}"
        
        return {
            "response": response_text,
            "flow_id": None,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erreur chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS STATS =====

@app.get("/api/v1/stats/overview")
async def get_stats_overview():
    """Statistiques générales"""
    return {
        "total_cases": len(cases_storage),
        "active_pipelines": len([p for p in pipeline_status.values() if p["status"] == "en_cours"]),
        "total_documents": len(documents_storage),
        "system_status": "operational"
    }

# ===== WEBSOCKET =====

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour les mises à jour temps réel"""
    await websocket.accept()
    try:
        while True:
            # Envoyer des mises à jour périodiques
            await asyncio.sleep(5)
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "active_cases": len(cases_storage),
                    "active_pipelines": len([p for p in pipeline_status.values() if p["status"] == "en_cours"])
                }
            })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")

# ===== ENDPOINT DE SANTÉ =====

@app.get("/health")
async def health_check():
    """Vérification de santé du service"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2024.12.01"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
