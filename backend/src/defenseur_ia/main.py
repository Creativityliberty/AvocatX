"""
Application FastAPI principale pour DEFENSEUR-IA
"""

import asyncio
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
from pydantic import BaseModel
import uvicorn

from defenseur_ia.api.routes import router
from defenseur_ia.api.flow_endpoints import flow_router
from defenseur_ia.core.pipeline import PipelineOrchestrator
from defenseur_ia.core.websocket_manager import WebSocketManager
from defenseur_ia.services.storage_service import StorageService
from defenseur_ia.agents.agent_recherche_web_enhanced import AgentRechercheWebEnhanced, WebResearchConfig
from defenseur_ia.config.settings import settings

# Configuration logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
pipeline_manager = PipelineOrchestrator()
websocket_manager = WebSocketManager()
storage_service = StorageService()

# Instance de l'agent de recherche web amélioré
web_research_agent = AgentRechercheWebEnhanced()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de durée de vie de l'application"""
    logger.info("🚀 Démarrage de DEFENSEUR-IA Backend")
    
    # Initialisation des services
    await storage_service.initialize()
    await pipeline_manager.initialize()
    
    yield
    
    # Nettoyage
    logger.info("🛑 Arrêt de DEFENSEUR-IA Backend")
    await pipeline_manager.shutdown()
    await storage_service.shutdown()

# Création de l'application FastAPI
app = FastAPI(
    title="DEFENSEUR-IA Backend",
    description="Backend FastAPI pour le système d'IA juridique DEFENSEUR-IA",
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

# Montage des routes
app.include_router(router, prefix="/api/v1")
app.include_router(flow_router, prefix="/api")

# Montage des fichiers statiques
# S'assurer que le répertoire d'upload existe avant le montage
upload_dir = settings.UPLOAD_DIR or "uploads"
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Modèles Pydantic pour l'API de recherche web
class WebSearchRequest(BaseModel):
    query: str
    case_data: Dict[str, Any] = None
    urgency: str = "normal"
    config: Dict[str, Any] = None

class WebSearchResponse(BaseModel):
    success: bool
    content: str
    confidence_score: float
    execution_time: float
    metadata: Dict[str, Any] = None

@app.post("/api/agents/recherche-web-enhanced", response_model=WebSearchResponse)
async def enhanced_web_search(request: WebSearchRequest):
    """
    Endpoint pour la recherche web avancée avec OpenAI Deep Research API
    """
    try:
        logger.info(f"Recherche web avancée: {request.query[:100]}...")
        
        # Configuration de l'agent si fournie
        if request.config:
            config = WebResearchConfig(**request.config)
            agent = AgentRechercheWebEnhanced(config)
        else:
            agent = web_research_agent
        
        # Préparation des données d'entrée
        input_data = {
            "query": request.query,
            "case_data": request.case_data,
            "urgency": request.urgency
        }
        
        # Exécution de la recherche
        result = await agent.process_async(input_data)
        
        # Adapter au nouveau schéma AgentResult
        payload = getattr(result, "result", {}) if result else {}
        metrics = payload.get("metrics", {}) if isinstance(payload, dict) else {}
        response = WebSearchResponse(
            success=(getattr(result, "status", "error") == "success"),
            content=payload.get("content", ""),
            confidence_score=float(metrics.get("average_confidence", 0.0) or 0.0),
            execution_time=getattr(result, "execution_time", 0.0),
            metadata=payload
        )
        
        logger.info(
            f"Recherche terminée - Statut: {getattr(result, 'status', 'unknown')}, Temps: {getattr(result, 'execution_time', 0.0):.2f}s"
        )
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche web avancée: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche: {str(e)}"
        )

@app.get("/api/agents/recherche-web-enhanced/stats")
async def get_web_search_stats():
    """
    Endpoint pour récupérer les statistiques de l'agent de recherche web
    """
    try:
        stats = web_research_agent.get_agent_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )

@app.post("/api/agents/recherche-web-enhanced/test")
async def test_web_search_capabilities():
    """
    Endpoint pour tester les capacités de l'agent de recherche web
    """
    try:
        test_results = await web_research_agent.test_capabilities()
        return test_results
    except Exception as e:
        logger.error(f"Erreur lors du test des capacités: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du test: {str(e)}"
        )

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "DEFENSEUR-IA Backend est opérationnel",
        "version": "2024.12.01",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "pipeline": "running",
            "storage": "connected",
            "websocket": "active"
        }
    }

@app.websocket("/ws/{dossier_id}")
async def websocket_endpoint(websocket: WebSocket, dossier_id: str):
    """WebSocket pour monitoring temps réel"""
    await websocket_manager.connect(websocket, dossier_id)
    try:
        while True:
            # Récupération du statut du pipeline
            status = await pipeline_manager.get_status(dossier_id)
            await websocket.send_json(status)
            await asyncio.sleep(2)  # Mise à jour toutes les 2 secondes
    except WebSocketDisconnect:
        websocket_manager.disconnect(dossier_id)
    except Exception as e:
        logger.error(f"Erreur WebSocket pour {dossier_id}: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
