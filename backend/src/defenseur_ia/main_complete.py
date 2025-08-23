"""
Backend FastAPI complet pour DEFENSEUR-IA - Pipeline Complet avec Vraies API
"""

import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
import json

# Imports des services DEFENSEUR-IA
try:
    from .core.pipeline import PipelineOrchestrator
    from .services.chat_orchestrator import ChatOrchestrator
    from .services.storage_service import StorageService
    from .services.unified_embedding_service import UnifiedEmbeddingService
    from .services.gemini_embedding_service import GeminiEmbeddingService
    from .services.legifrance_service import LegifranceService
    from .services.openai_service import OpenAIService
    from .services.pinecone_service import PineconeService
    from .services.mongodb_service import MongoDBService
    from .core.websocket_manager import WebSocketManager
    from .api.mongodb_routes import router as mongodb_router
except ImportError:
    # Imports absolus pour exécution directe
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from core.pipeline import PipelineOrchestrator
    from services.chat_orchestrator import ChatOrchestrator
    from services.storage_service import StorageService
    from services.unified_embedding_service import UnifiedEmbeddingService
    from services.gemini_embedding_service import GeminiEmbeddingService
    from services.legifrance_service import LegifranceService
    from config.legifrance_config import LegifranceConfigManager
    from services.openai_service import OpenAIService
    from services.pinecone_service import PineconeService
    from services.mongodb_service import MongoDBService
    from core.websocket_manager import WebSocketManager
    from api.mongodb_routes import router as mongodb_router

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
    progress: Optional[float] = 0.0
    pipeline_status: Optional[str] = "en_attente"

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    type: str
    size: int
    uploaded_at: str
    analysis_status: Optional[str] = "pending"

class PipelineStatusResponse(BaseModel):
    dossier_id: str
    status: str
    current_step: int
    total_steps: int
    progress: float
    logs: List[str]
    agent_results: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    message: str
    attachments: Optional[List[str]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    flow_id: Optional[str] = None
    status: str
    session_id: Optional[str] = None
    suggestions: Optional[List[str]] = None

class LegalSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    scope: Optional[List[str]] = None

class LegalSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int
    query_analysis: Optional[Dict[str, Any]] = None

# Services globaux
pipeline_orchestrator: Optional[PipelineOrchestrator] = None
chat_orchestrator: Optional[ChatOrchestrator] = None
storage_service: Optional[StorageService] = None
embedding_service: Optional[UnifiedEmbeddingService] = None
legifrance_service: Optional[LegifranceService] = None
openai_service: Optional[OpenAIService] = None
pinecone_service: Optional[PineconeService] = None
mongodb_service: Optional[MongoDBService] = None
websocket_manager: Optional[WebSocketManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de durée de vie de l'application"""
    global pipeline_orchestrator, chat_orchestrator, storage_service
    global embedding_service, legifrance_service, openai_service, pinecone_service, mongodb_service, websocket_manager
    
    logger.info("🚀 Démarrage de DEFENSEUR-IA Backend Complet")
    
    try:
        # Initialisation des services
        logger.info("Initialisation des services...")
        
        # Storage Service
        storage_service = StorageService()
        await storage_service.initialize()
        
        # Embedding Service
        embedding_service = UnifiedEmbeddingService()
        await embedding_service.initialize()
        
        # Légifrance Service
        legifrance_service = LegifranceService()
        
        # OpenAI Service
        openai_service = OpenAIService()
        
        # Pinecone Service
        pinecone_service = PineconeService()
        await pinecone_service.initialize()
        
        # MongoDB Atlas Service
        mongodb_service = MongoDBService()
        await mongodb_service.initialize()
        
        # WebSocket Manager
        websocket_manager = WebSocketManager()
        
        # Pipeline Orchestrator
        pipeline_orchestrator = PipelineOrchestrator()
        await pipeline_orchestrator.initialize()
        
        # Chat Orchestrator
        chat_orchestrator = ChatOrchestrator(
            pipeline_orchestrator=pipeline_orchestrator,
            storage_service=storage_service
        )
        await chat_orchestrator.initialize()
        
        logger.info("✅ Tous les services initialisés avec succès")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        # Continuer avec les services disponibles
        
    yield
    
    logger.info("🛑 Arrêt de DEFENSEUR-IA Backend Complet")
    
    # Fermeture des services
    if mongodb_service:
        await mongodb_service.shutdown()
    if pinecone_service:
        await pinecone_service.shutdown()

# Création de l'application FastAPI
app = FastAPI(
    title="DEFENSEUR-IA Backend Complet",
    description="Backend FastAPI complet avec pipeline d'agents et vraies API",
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

# ===== ENDPOINTS MONGODB ATLAS =====

@app.get("/api/v1/mongodb/health")
async def mongodb_health_check():
    """Vérification de santé MongoDB Atlas"""
    try:
        if not mongodb_service:
            return {"success": False, "status": "not_initialized", "error": "Service non initialisé"}
        
        return {
            "success": True,
            "status": "connected" if mongodb_service.connected else "disconnected",
            "database": mongodb_service.database_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Erreur health check MongoDB: {e}")
        return {"success": False, "status": "error", "error": str(e)}

@app.get("/api/v1/mongodb/stats")
async def get_mongodb_stats():
    """Récupère les statistiques MongoDB Atlas"""
    try:
        if not mongodb_service:
            return {"success": False, "error": "Service MongoDB non initialisé"}
        
        stats = await mongodb_service.get_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Erreur récupération statistiques MongoDB: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/v1/mongodb/cases")
async def create_mongodb_case(case_data: Dict[str, Any]):
    """Crée un nouveau dossier dans MongoDB Atlas"""
    try:
        if not mongodb_service:
            raise HTTPException(status_code=503, detail="Service MongoDB non disponible")
        
        # Générer un ID unique si non fourni
        if 'dossier_id' not in case_data:
            import uuid
            case_data['dossier_id'] = f"dossier_{uuid.uuid4().hex[:8]}"
        
        # Ajouter les métadonnées
        case_data['status'] = case_data.get('status', 'nouveau')
        case_data['created_by'] = case_data.get('created_by', 'system')
        
        # Créer le dossier
        result_id = await mongodb_service.create_case(case_data)
        
        logger.info(f"✅ Dossier MongoDB créé: {case_data['dossier_id']}")
        
        return {
            "success": True,
            "dossier_id": case_data['dossier_id'],
            "mongodb_id": result_id,
            "message": "Dossier créé avec succès dans MongoDB Atlas"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur création dossier MongoDB: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur création dossier: {str(e)}")

@app.get("/api/v1/mongodb/cases")
async def list_mongodb_cases(skip: int = 0, limit: int = 10, status: str = None, created_by: str = None):
    """Liste les dossiers MongoDB Atlas avec pagination"""
    try:
        if not mongodb_service:
            raise HTTPException(status_code=503, detail="Service MongoDB non disponible")
        
        # Construire les filtres
        filters = {}
        if status:
            filters['status'] = status
        if created_by:
            filters['created_by'] = created_by
        
        # Récupérer les dossiers avec pagination
        cases = await mongodb_service.list_cases(skip=skip, limit=limit, filters=filters)
        
        logger.info(f"✅ Liste dossiers MongoDB: {len(cases)} résultats (skip={skip}, limit={limit})")
        
        return {
            "success": True,
            "cases": cases,
            "count": len(cases),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur liste dossiers MongoDB: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur liste dossiers: {str(e)}")

@app.get("/api/v1/mongodb/cases/{dossier_id}")
async def get_mongodb_case(dossier_id: str):
    """Récupère un dossier MongoDB par son ID"""
    try:
        if not mongodb_service:
            raise HTTPException(status_code=503, detail="Service MongoDB non disponible")
        
        case = await mongodb_service.get_case(dossier_id)
        
        if not case:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        
        return {
            "success": True,
            "case": case
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur récupération dossier MongoDB: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération dossier: {str(e)}")

@app.put("/api/v1/mongodb/cases/{dossier_id}")
async def update_mongodb_case(dossier_id: str, updates: Dict[str, Any]):
    """Met à jour un dossier MongoDB par son ID"""
    try:
        if not mongodb_service:
            raise HTTPException(status_code=503, detail="Service MongoDB non disponible")
        
        # Ajouter la date de modification
        updates['updated_at'] = datetime.now().isoformat()
        
        # Mettre à jour le dossier
        result = await mongodb_service.update_case(dossier_id, updates)
        
        if not result:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        
        logger.info(f"✅ Dossier MongoDB mis à jour: {dossier_id}")
        
        return {
            "success": True,
            "dossier_id": dossier_id,
            "message": "Dossier mis à jour avec succès dans MongoDB Atlas"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour dossier MongoDB: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour dossier: {str(e)}")

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
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        cases = await storage_service.get_all_cases()
        
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
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        # Créer le dossier
        case = await storage_service.create_case(
            nom_justiciable=case_data.nom_justiciable,
            type_contentieux=case_data.type_contentieux,
            description=case_data.description,
            urgence=case_data.urgence
        )
        
        logger.info(f"Nouveau dossier créé: {case['dossier_id']}")
        
        # Notifier via WebSocket
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "case_created",
                "data": case
            })
        
        return case
    except Exception as e:
        logger.error(f"Erreur création dossier: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/cases/{dossier_id}", response_model=CaseResponse)
async def get_case(dossier_id: str):
    """Récupérer un dossier spécifique"""
    try:
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        case = await storage_service.get_case(dossier_id)
        if not case:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération dossier {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/cases/{dossier_id}", response_model=CaseResponse)
async def update_case(dossier_id: str, updates: dict):
    """Mettre à jour un dossier"""
    try:
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        case = await storage_service.update_case(dossier_id, updates)
        if not case:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        
        # Notifier via WebSocket
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "case_updated",
                "data": case
            })
        
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour dossier {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/cases/{dossier_id}")
async def delete_case(dossier_id: str):
    """Supprimer un dossier"""
    try:
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        success = await storage_service.delete_case(dossier_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        
        # Notifier via WebSocket
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "case_deleted",
                "data": {"dossier_id": dossier_id}
            })
        
        return {"message": "Dossier supprimé"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression dossier {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS DOCUMENTS =====

@app.post("/api/v1/upload", response_model=List[DocumentResponse])
async def upload_documents(files: List[UploadFile] = File(...), dossier_id: str = ""):
    """Upload de documents avec analyse automatique"""
    try:
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        uploaded_docs = []
        
        for file in files:
            # Sauvegarder le fichier
            doc = await storage_service.save_document(
                file=file,
                dossier_id=dossier_id
            )
            uploaded_docs.append(doc)
            
            # Déclencher l'analyse automatique si le pipeline est disponible
            if pipeline_orchestrator:
                asyncio.create_task(
                    pipeline_orchestrator.analyze_document(doc["document_id"])
                )
        
        logger.info(f"Uploaded {len(files)} documents pour dossier {dossier_id}")
        
        # Notifier via WebSocket
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "documents_uploaded",
                "data": {
                    "dossier_id": dossier_id,
                    "documents": uploaded_docs
                }
            })
        
        return uploaded_docs
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents/{dossier_id}", response_model=List[DocumentResponse])
async def get_documents(dossier_id: str):
    """Récupérer les documents d'un dossier"""
    try:
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        docs = await storage_service.get_documents(dossier_id)
        return docs
    except Exception as e:
        logger.error(f"Erreur récupération documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS PIPELINE =====

@app.post("/api/v1/pipeline/{dossier_id}/start")
async def start_pipeline(dossier_id: str):
    """Démarrer le pipeline complet pour un dossier"""
    try:
        if not pipeline_orchestrator:
            raise HTTPException(status_code=503, detail="Pipeline non disponible")
        
        if not storage_service:
            raise HTTPException(status_code=503, detail="Service de stockage non disponible")
        
        # Vérifier que le dossier existe
        case = await storage_service.get_case(dossier_id)
        if not case:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        
        # Démarrer le pipeline
        execution_id = await pipeline_orchestrator.start_pipeline(dossier_id)
        
        logger.info(f"Pipeline démarré pour {dossier_id} (execution: {execution_id})")
        
        # Notifier via WebSocket
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "pipeline_started",
                "data": {
                    "dossier_id": dossier_id,
                    "execution_id": execution_id
                }
            })
        
        return {
            "message": "Pipeline démarré", 
            "dossier_id": dossier_id,
            "execution_id": execution_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur démarrage pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/pipeline/{dossier_id}/status", response_model=PipelineStatusResponse)
async def get_pipeline_status(dossier_id: str):
    """Récupérer le statut du pipeline"""
    try:
        if not pipeline_orchestrator:
            raise HTTPException(status_code=503, detail="Pipeline non disponible")
        
        status = await pipeline_orchestrator.get_status(dossier_id)
        if not status:
            raise HTTPException(status_code=404, detail="Statut pipeline non trouvé")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur statut pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/pipeline/{dossier_id}/pause")
async def pause_pipeline(dossier_id: str):
    """Mettre en pause le pipeline"""
    try:
        if not pipeline_orchestrator:
            raise HTTPException(status_code=503, detail="Pipeline non disponible")
        
        success = await pipeline_orchestrator.pause_pipeline(dossier_id)
        if not success:
            raise HTTPException(status_code=404, detail="Pipeline non trouvé")
        
        return {"message": "Pipeline mis en pause"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur pause pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/pipeline/{dossier_id}/resume")
async def resume_pipeline(dossier_id: str):
    """Reprendre le pipeline"""
    try:
        if not pipeline_orchestrator:
            raise HTTPException(status_code=503, detail="Pipeline non disponible")
        
        success = await pipeline_orchestrator.resume_pipeline(dossier_id)
        if not success:
            raise HTTPException(status_code=404, detail="Pipeline non trouvé")
        
        return {"message": "Pipeline repris"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur reprise pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS CHAT =====

@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(message: ChatMessage):
    """Endpoint pour les messages du chat avec ChatOrchestrator complet"""
    try:
        if not chat_orchestrator:
            raise HTTPException(status_code=503, detail="Chat non disponible")
        
        # Traiter le message avec le ChatOrchestrator
        response = await chat_orchestrator.process_message(
            message=message.message,
            attachments=message.attachments,
            session_id=message.session_id
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/sessions/{session_id}/history")
async def get_chat_history(session_id: str):
    """Récupérer l'historique d'une session de chat"""
    try:
        if not chat_orchestrator:
            raise HTTPException(status_code=503, detail="Chat non disponible")
        
        history = await chat_orchestrator.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Erreur historique chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS RECHERCHE JURIDIQUE =====

@app.post("/api/v1/legal/search", response_model=LegalSearchResponse)
async def legal_search(request: LegalSearchRequest):
    """Recherche juridique avancée avec Légifrance"""
    try:
        if not legifrance_service:
            raise HTTPException(status_code=503, detail="Service Légifrance non disponible")
        
        # Effectuer la recherche
        results = await legifrance_service.search(
            query=request.query,
            filters=request.filters,
            scope=request.scope
        )
        
        return results
    except Exception as e:
        logger.error(f"Erreur recherche juridique: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS EMBEDDINGS =====

@app.get("/api/v1/embeddings/stats")
async def get_embedding_stats():
    """Statistiques du service d'embeddings"""
    try:
        if not embedding_service:
            raise HTTPException(status_code=503, detail="Service embeddings non disponible")
        
        stats = await embedding_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur stats embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/embeddings/search")
async def semantic_search(query: str, limit: int = 10):
    """Recherche sémantique dans la base de connaissances"""
    try:
        if not embedding_service:
            raise HTTPException(status_code=503, detail="Service embeddings non disponible")
        
        results = await embedding_service.search(query, limit=limit)
        return {"query": query, "results": results}
    except Exception as e:
        logger.error(f"Erreur recherche sémantique: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS PINECONE =====

@app.get("/api/v1/pinecone/stats")
async def get_pinecone_stats():
    """Statistiques de la base vectorielle Pinecone"""
    try:
        if not pinecone_service:
            raise HTTPException(status_code=503, detail="Service Pinecone non disponible")
        
        stats = await pinecone_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur stats Pinecone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/pinecone/search")
async def pinecone_search(query: str, index_type: str = "legal_knowledge", limit: int = 10):
    """Recherche vectorielle dans Pinecone"""
    try:
        if not pinecone_service:
            raise HTTPException(status_code=503, detail="Service Pinecone non disponible")
        
        results = await pinecone_service.search(
            query=query,
            index_type=index_type,
            top_k=limit
        )
        return {
            "query": query,
            "index_type": index_type,
            "results": results
        }
    except Exception as e:
        logger.error(f"Erreur recherche Pinecone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/pinecone/store")
async def pinecone_store(text: str, metadata: dict, index_type: str = "legal_knowledge"):
    """Stocker un document dans Pinecone"""
    try:
        if not pinecone_service:
            raise HTTPException(status_code=503, detail="Service Pinecone non disponible")
        
        vector_id = await pinecone_service.store(
            text=text,
            metadata=metadata,
            index_type=index_type
        )
        return {
            "vector_id": vector_id,
            "index_type": index_type,
            "status": "stored"
        }
    except Exception as e:
        logger.error(f"Erreur stockage Pinecone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/pinecone/indexes")
async def get_pinecone_indexes():
    """Liste des index Pinecone disponibles"""
    try:
        if not pinecone_service:
            raise HTTPException(status_code=503, detail="Service Pinecone non disponible")
        
        indexes = await pinecone_service.list_indexes()
        return {"indexes": indexes}
    except Exception as e:
        logger.error(f"Erreur liste index Pinecone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS STATS =====

@app.get("/api/v1/stats/overview")
async def get_stats_overview():
    """Statistiques générales du système"""
    try:
        stats = {
            "system_status": "operational",
            "timestamp": datetime.now().isoformat()
        }
        
        if storage_service:
            storage_stats = await storage_service.get_stats()
            stats.update(storage_stats)
        
        if pipeline_orchestrator:
            pipeline_stats = await pipeline_orchestrator.get_stats()
            stats.update(pipeline_stats)
        
        if embedding_service:
            embedding_stats = await embedding_service.get_stats()
            stats["embeddings"] = embedding_stats
        
        return stats
    except Exception as e:
        logger.error(f"Erreur stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== WEBSOCKET =====

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour les mises à jour temps réel"""
    if not websocket_manager:
        await websocket.close(code=1011, reason="WebSocket service unavailable")
        return
    
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Maintenir la connexion active
            data = await websocket.receive_text()
            # Echo pour test de connexion
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)

# ===== ENDPOINT DE SANTÉ =====

@app.get("/health")
async def health_check():
    """Vérification de santé du service complet"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2024.12.01",
        "services": {}
    }
    
    # Vérifier chaque service
    health_status["services"]["storage"] = "available" if storage_service else "unavailable"
    health_status["services"]["pipeline"] = "available" if pipeline_orchestrator else "unavailable"
    health_status["services"]["chat"] = "available" if chat_orchestrator else "unavailable"
    health_status["services"]["embeddings"] = "available" if embedding_service else "unavailable"
    health_status["services"]["legifrance"] = "available" if legifrance_service else "unavailable"
    health_status["services"]["openai"] = "available" if openai_service else "unavailable"
    health_status["services"]["pinecone"] = "available" if pinecone_service else "unavailable"
    health_status["services"]["websocket"] = "available" if websocket_manager else "unavailable"
    
    # Déterminer le statut global
    unavailable_services = [k for k, v in health_status["services"].items() if v == "unavailable"]
    if len(unavailable_services) > 3:
        health_status["status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
