"""
Application FastAPI principale pour DEFENSEUR-IA
Backend complet avec pipeline IA en 12 étapes
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn

from defenseur_ia.core.pipeline import PipelineOrchestrator
from defenseur_ia.core.websocket_manager import WebSocketManager
from defenseur_ia.services.storage_service import StorageService
from defenseur_ia.api.routes import router

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
pipeline_manager = PipelineOrchestrator()
websocket_manager = WebSocketManager()
storage_service = StorageService()

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

# Montage des fichiers statiques
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
