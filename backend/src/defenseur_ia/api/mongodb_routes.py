"""
Endpoints API pour MongoDB Atlas - DEFENSEUR-IA
Routes pour la gestion des dossiers, documents et données via MongoDB Atlas
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

# Import du service MongoDB
from ..services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)

# Router pour les endpoints MongoDB
router = APIRouter(prefix="/api/v1/mongodb", tags=["MongoDB Atlas"])

# Dépendance pour obtenir le service MongoDB
async def get_mongodb_service() -> MongoDBService:
    """Dépendance pour obtenir le service MongoDB"""
    try:
        from ..main_complete import mongodb_service
        if mongodb_service is None:
            raise HTTPException(status_code=503, detail="Service MongoDB non initialisé")
        if not mongodb_service.connected:
            raise HTTPException(status_code=503, detail="Service MongoDB non connecté")
        return mongodb_service
    except ImportError as e:
        logger.error(f"❌ Erreur import service MongoDB: {e}")
        raise HTTPException(status_code=503, detail="Service MongoDB non disponible")

# ===== ENDPOINTS DOSSIERS =====

@router.post("/cases", response_model=Dict[str, Any])
async def create_case(
    case_data: Dict[str, Any],
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Crée un nouveau dossier juridique"""
    try:
        # Générer un ID unique si non fourni
        if 'dossier_id' not in case_data:
            case_data['dossier_id'] = f"dossier_{uuid.uuid4().hex[:8]}"
        
        # Ajouter les métadonnées
        case_data['status'] = case_data.get('status', 'nouveau')
        case_data['created_by'] = case_data.get('created_by', 'system')
        
        # Créer le dossier
        result_id = await mongodb_service.create_case(case_data)
        
        logger.info(f"✅ Dossier créé: {case_data['dossier_id']}")
        
        return {
            "success": True,
            "dossier_id": case_data['dossier_id'],
            "mongodb_id": result_id,
            "message": "Dossier créé avec succès"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur création dossier: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur création dossier: {str(e)}")

@router.get("/cases/{dossier_id}", response_model=Dict[str, Any])
async def get_case(
    dossier_id: str,
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Récupère un dossier par son ID"""
    try:
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
        logger.error(f"❌ Erreur récupération dossier: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération dossier: {str(e)}")

@router.put("/cases/{dossier_id}", response_model=Dict[str, Any])
async def update_case(
    dossier_id: str,
    updates: Dict[str, Any],
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Met à jour un dossier"""
    try:
        # Ajouter les métadonnées de mise à jour
        updates['updated_by'] = updates.get('updated_by', 'system')
        
        success = await mongodb_service.update_case(dossier_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Dossier non trouvé ou non modifié")
        
        return {
            "success": True,
            "dossier_id": dossier_id,
            "message": "Dossier mis à jour avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour dossier: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour dossier: {str(e)}")

@router.get("/cases", response_model=Dict[str, Any])
async def list_cases(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(10, ge=1, le=100, description="Nombre d'éléments à retourner"),
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    created_by: Optional[str] = Query(None, description="Filtrer par créateur"),
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Liste les dossiers avec pagination et filtres"""
    try:
        # Construire les filtres
        filters = {}
        if status:
            filters['status'] = status
        if created_by:
            filters['created_by'] = created_by
        
        cases = await mongodb_service.list_cases(skip=skip, limit=limit, filters=filters)
        
        return {
            "success": True,
            "cases": cases,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "count": len(cases)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur liste dossiers: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur liste dossiers: {str(e)}")

# ===== ENDPOINTS DOCUMENTS =====

@router.post("/documents", response_model=Dict[str, Any])
async def store_document(
    document_data: Dict[str, Any],
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Stocke les métadonnées d'un document"""
    try:
        # Générer un ID unique si non fourni
        if 'document_id' not in document_data:
            document_data['document_id'] = f"doc_{uuid.uuid4().hex[:8]}"
        
        # Ajouter les métadonnées
        document_data['uploaded_by'] = document_data.get('uploaded_by', 'system')
        
        result_id = await mongodb_service.store_document(document_data)
        
        logger.info(f"✅ Document stocké: {document_data['document_id']}")
        
        return {
            "success": True,
            "document_id": document_data['document_id'],
            "mongodb_id": result_id,
            "message": "Document stocké avec succès"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur stockage document: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur stockage document: {str(e)}")

@router.get("/documents/{dossier_id}", response_model=Dict[str, Any])
async def get_documents(
    dossier_id: str,
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Récupère tous les documents d'un dossier"""
    try:
        documents = await mongodb_service.get_documents(dossier_id)
        
        return {
            "success": True,
            "dossier_id": dossier_id,
            "documents": documents,
            "count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération documents: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération documents: {str(e)}")

# ===== ENDPOINTS PIPELINE =====

@router.post("/pipeline/runs", response_model=Dict[str, Any])
async def store_pipeline_run(
    pipeline_data: Dict[str, Any],
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Stocke une exécution de pipeline"""
    try:
        # Générer un ID unique si non fourni
        if 'flow_id' not in pipeline_data:
            pipeline_data['flow_id'] = f"flow_{uuid.uuid4().hex[:8]}"
        
        # Ajouter les métadonnées
        pipeline_data['status'] = pipeline_data.get('status', 'started')
        pipeline_data['started_by'] = pipeline_data.get('started_by', 'system')
        
        result_id = await mongodb_service.store_pipeline_run(pipeline_data)
        
        logger.info(f"✅ Pipeline run stocké: {pipeline_data['flow_id']}")
        
        return {
            "success": True,
            "flow_id": pipeline_data['flow_id'],
            "mongodb_id": result_id,
            "message": "Pipeline run stocké avec succès"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur stockage pipeline run: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur stockage pipeline run: {str(e)}")

@router.get("/pipeline/runs/{flow_id}", response_model=Dict[str, Any])
async def get_pipeline_run(
    flow_id: str,
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Récupère une exécution de pipeline"""
    try:
        run = await mongodb_service.get_pipeline_run(flow_id)
        
        if not run:
            raise HTTPException(status_code=404, detail="Pipeline run non trouvé")
        
        return {
            "success": True,
            "pipeline_run": run
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur récupération pipeline run: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération pipeline run: {str(e)}")

@router.put("/pipeline/runs/{flow_id}", response_model=Dict[str, Any])
async def update_pipeline_run(
    flow_id: str,
    updates: Dict[str, Any],
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Met à jour une exécution de pipeline"""
    try:
        success = await mongodb_service.update_pipeline_run(flow_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Pipeline run non trouvé ou non modifié")
        
        return {
            "success": True,
            "flow_id": flow_id,
            "message": "Pipeline run mis à jour avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour pipeline run: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur mise à jour pipeline run: {str(e)}")

# ===== ENDPOINTS STATISTIQUES =====

@router.get("/stats", response_model=Dict[str, Any])
async def get_mongodb_stats(
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Récupère les statistiques MongoDB Atlas"""
    try:
        stats = await mongodb_service.get_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur récupération statistiques: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération statistiques: {str(e)}")

@router.get("/health", response_model=Dict[str, Any])
async def mongodb_health_check(
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Vérification de santé MongoDB Atlas"""
    try:
        return {
            "success": True,
            "status": "connected" if mongodb_service.connected else "disconnected",
            "database": mongodb_service.database_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur health check MongoDB: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur health check: {str(e)}")
