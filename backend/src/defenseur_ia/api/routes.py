"""
Routes API REST pour DEFENSEUR-IA
Conformes aux spécifications exactes lues dans les docs
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from defenseur_ia.models import (
    CaseStatus, CaseCreateRequest, CaseUpdateRequest, 
    DocumentUploadRequest, PipelineStatus
)
from defenseur_ia.core.pipeline import PipelineOrchestrator
from defenseur_ia.services.storage_service import StorageService
from defenseur_ia.services.document_service import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter()
pipeline_manager = PipelineOrchestrator()
storage_service = StorageService()
document_service = DocumentService()

# Routes Cases
@router.get("/cases", response_model=List[CaseStatus])
async def get_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    type_contentieux: Optional[str] = None
):
    """Récupérer la liste des dossiers"""
    try:
        cases = await storage_service.get_cases(
            skip=skip, 
            limit=limit, 
            status=status,
            type_contentieux=type_contentieux
        )
        return cases
    except Exception as e:
        logger.error(f"Erreur récupération dossiers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cases/{dossier_id}", response_model=CaseStatus)
async def get_case(dossier_id: str):
    """Récupérer un dossier spécifique"""
    try:
        case = await storage_service.get_case(dossier_id)
        if not case:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        return case
    except Exception as e:
        logger.error(f"Erreur récupération dossier {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cases", response_model=CaseStatus)
async def create_case(request: CaseCreateRequest):
    """Créer un nouveau dossier"""
    try:
        case = await storage_service.create_case(request.dict())
        
        # Démarrer automatiquement le pipeline
        await pipeline_manager.start_pipeline(case.dossier_id)
        
        return case
    except Exception as e:
        logger.error(f"Erreur création dossier: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/cases/{dossier_id}", response_model=CaseStatus)
async def update_case(dossier_id: str, request: CaseUpdateRequest):
    """Mettre à jour un dossier"""
    try:
        case = await storage_service.update_case(dossier_id, request.dict(exclude_unset=True))
        if not case:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        return case
    except Exception as e:
        logger.error(f"Erreur mise à jour dossier {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cases/{dossier_id}")
async def delete_case(dossier_id: str):
    """Supprimer un dossier"""
    try:
        success = await storage_service.delete_case(dossier_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        return {"message": "Dossier supprimé avec succès"}
    except Exception as e:
        logger.error(f"Erreur suppression dossier {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes Documents
@router.post("/cases/{dossier_id}/documents")
async def upload_document(
    dossier_id: str,
    file: UploadFile = File(...),
    type_document: str = Query(...),
    description: Optional[str] = None
):
    """Uploader un document pour un dossier"""
    try:
        document = await document_service.upload_document(
            dossier_id=dossier_id,
            file=file,
            type_document=type_document,
            description=description
        )
        return document
    except Exception as e:
        logger.error(f"Erreur upload document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cases/{dossier_id}/documents")
async def get_documents(dossier_id: str):
    """Récupérer les documents d'un dossier"""
    try:
        documents = await storage_service.get_documents(dossier_id)
        return documents
    except Exception as e:
        logger.error(f"Erreur récupération documents {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Récupérer un document spécifique"""
    try:
        document = await storage_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document non trouvé")
        return document
    except Exception as e:
        logger.error(f"Erreur récupération document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes Pipeline
@router.get("/cases/{dossier_id}/status", response_model=PipelineStatus)
async def get_pipeline_status(dossier_id: str):
    """Récupérer le statut du pipeline pour un dossier"""
    try:
        status = await pipeline_manager.get_status(dossier_id)
        if not status:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        return status
    except Exception as e:
        logger.error(f"Erreur récupération statut pipeline {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cases/{dossier_id}/pipeline/start")
async def start_pipeline(dossier_id: str):
    """Démarrer le pipeline pour un dossier"""
    try:
        success = await pipeline_manager.start_pipeline(dossier_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        return {"message": "Pipeline démarré avec succès"}
    except Exception as e:
        logger.error(f"Erreur démarrage pipeline {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cases/{dossier_id}/pipeline/stop")
async def stop_pipeline(dossier_id: str):
    """Arrêter le pipeline pour un dossier"""
    try:
        success = await pipeline_manager.stop_pipeline(dossier_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dossier non trouvé")
        return {"message": "Pipeline arrêté avec succès"}
    except Exception as e:
        logger.error(f"Erreur arrêt pipeline {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes Statistiques
@router.get("/stats")
async def get_stats():
    """Récupérer les statistiques globales"""
    try:
        stats = await storage_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/daily")
async def get_daily_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Récupérer les statistiques quotidiennes"""
    try:
        stats = await storage_service.get_daily_stats(start_date, end_date)
        return stats
    except Exception as e:
        logger.error(f"Erreur récupération statistiques quotidiennes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes Clients
@router.get("/clients")
async def get_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Récupérer la liste des clients"""
    try:
        clients = await storage_service.get_clients(skip=skip, limit=limit)
        return clients
    except Exception as e:
        logger.error(f"Erreur récupération clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clients")
async def create_client(client_data: Dict[str, Any]):
    """Créer un nouveau client"""
    try:
        client = await storage_service.create_client(client_data)
        return client
    except Exception as e:
        logger.error(f"Erreur création client: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients/{client_id}")
async def get_client(client_id: str):
    """Récupérer un client spécifique"""
    try:
        client = await storage_service.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client non trouvé")
        return client
    except Exception as e:
        logger.error(f"Erreur récupération client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes Rendez-vous
@router.get("/appointments")
async def get_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    client_id: Optional[str] = None
):
    """Récupérer la liste des rendez-vous"""
    try:
        appointments = await storage_service.get_appointments(
            skip=skip, 
            limit=limit, 
            client_id=client_id
        )
        return appointments
    except Exception as e:
        logger.error(f"Erreur récupération rendez-vous: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/appointments")
async def create_appointment(appointment_data: Dict[str, Any]):
    """Créer un nouveau rendez-vous"""
    try:
        appointment = await storage_service.create_appointment(appointment_data)
        return appointment
    except Exception as e:
        logger.error(f"Erreur création rendez-vous: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes Recherche
@router.get("/search")
async def search(
    query: str = Query(..., min_length=2),
    type_filter: Optional[str] = None
):
    """Recherche globale multi-critères"""
    try:
        results = await storage_service.search(
            query=query,
            type_filter=type_filter
        )
        return results
    except Exception as e:
        logger.error(f"Erreur recherche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Routes WebSocket
@router.websocket("/ws/{dossier_id}")
async def websocket_endpoint(websocket: WebSocket, dossier_id: str):
    """WebSocket pour monitoring temps réel"""
    from defenseur_ia.core.websocket_manager import WebSocketManager
    
    ws_manager = WebSocketManager()
    await ws_manager.connect(websocket, dossier_id)
    
    try:
        while True:
            # Récupération du statut
            status = await pipeline_manager.get_status(dossier_id)
            await websocket.send_json(status)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        ws_manager.disconnect(dossier_id)
    except Exception as e:
        logger.error(f"Erreur WebSocket {dossier_id}: {e}")
        await websocket.close()
