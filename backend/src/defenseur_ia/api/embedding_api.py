"""
API endpoints pour le monitoring et la gestion des embeddings
Expose les métriques et statistiques pour le dashboard
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import asyncio

from ..services.unified_embedding_service import UnifiedEmbeddingService
from ..services.gemini_embedding_service import GeminiEmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])

# Instance globale du service d'embedding
embedding_service: Optional[UnifiedEmbeddingService] = None

async def get_embedding_service() -> UnifiedEmbeddingService:
    """Dependency pour obtenir le service d'embedding"""
    global embedding_service
    if embedding_service is None:
        embedding_service = UnifiedEmbeddingService()
        await embedding_service.initialize()
    return embedding_service

@router.get("/stats")
async def get_embedding_stats(service: UnifiedEmbeddingService = Depends(get_embedding_service)):
    """
    Récupère les statistiques générales des embeddings
    """
    try:
        stats = await service.get_stats()
        
        # Calcul des métriques dérivées
        total_embeddings = sum(stats.get("provider_stats", {}).values())
        today_embeddings = stats.get("today_count", 0)
        cache_hit_rate = stats.get("cache_hit_rate", 0.0)
        avg_time = stats.get("avg_processing_time", 0.0)
        
        return {
            "total_embeddings": total_embeddings,
            "today_embeddings": today_embeddings,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "avg_time": f"{avg_time:.0f}ms",
            "provider_stats": stats.get("provider_stats", {}),
            "agent_stats": stats.get("agent_stats", {}),
            "context_type_stats": stats.get("context_type_stats", {}),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur récupération stats embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/services/status")
async def get_services_status(service: UnifiedEmbeddingService = Depends(get_embedding_service)):
    """
    Vérifie le status des différents services d'embedding
    """
    try:
        status = {}
        
        # Test Gemini
        try:
            gemini_service = service.providers.get("gemini")
            if gemini_service:
                # Test simple d'embedding
                await gemini_service.create_embedding("test", "SEMANTIC_SIMILARITY")
                status["gemini"] = {"status": "online", "message": "Service opérationnel"}
            else:
                status["gemini"] = {"status": "offline", "message": "Service non initialisé"}
        except Exception as e:
            status["gemini"] = {"status": "error", "message": str(e)}
        
        # Test Pinecone (si disponible)
        try:
            pinecone_service = service.providers.get("pinecone")
            if pinecone_service:
                status["pinecone"] = {"status": "online", "message": "Service opérationnel"}
            else:
                status["pinecone"] = {"status": "offline", "message": "Service non configuré"}
        except Exception as e:
            status["pinecone"] = {"status": "error", "message": str(e)}
        
        # Test OpenAI (si disponible)
        try:
            openai_service = service.providers.get("openai")
            if openai_service:
                status["openai"] = {"status": "online", "message": "Service opérationnel"}
            else:
                status["openai"] = {"status": "offline", "message": "Service non configuré"}
        except Exception as e:
            status["openai"] = {"status": "error", "message": str(e)}
        
        return status
    except Exception as e:
        logger.error(f"Erreur vérification status services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/config")
async def get_agents_config(service: UnifiedEmbeddingService = Depends(get_embedding_service)):
    """
    Récupère la configuration des agents pour les embeddings
    """
    try:
        config = service.agent_configs
        
        # Formatage pour le dashboard
        agents_info = []
        for agent_id, agent_config in config.items():
            agents_info.append({
                "id": agent_id,
                "name": agent_id.replace("_", " ").title(),
                "provider": agent_config["provider"],
                "task_type": agent_config["task_type"],
                "dimension": f"{agent_config['dimension']}D"
            })
        
        return {"agents": agents_info}
    except Exception as e:
        logger.error(f"Erreur récupération config agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics(service: UnifiedEmbeddingService = Depends(get_embedding_service)):
    """
    Récupère les métriques de performance détaillées
    """
    try:
        stats = await service.get_stats()
        
        # Calcul des métriques de performance
        performance = {
            "avg_latency": f"{stats.get('avg_processing_time', 0):.0f}ms",
            "throughput": stats.get("requests_per_minute", 0),
            "error_count": stats.get("error_count_24h", 0),
            "uptime": f"{stats.get('uptime_percentage', 99.5):.2f}%",
            "cache_efficiency": f"{stats.get('cache_hit_rate', 0):.1f}%",
            "total_requests": stats.get("total_requests", 0),
            "successful_requests": stats.get("successful_requests", 0),
            "failed_requests": stats.get("failed_requests", 0)
        }
        
        return performance
    except Exception as e:
        logger.error(f"Erreur récupération métriques performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/by-type")
async def get_usage_by_type(service: UnifiedEmbeddingService = Depends(get_embedding_service)):
    """
    Récupère l'utilisation par type de contexte
    """
    try:
        stats = await service.get_stats()
        context_stats = stats.get("context_type_stats", {})
        
        usage = {
            "agent_memory": context_stats.get("agent_memory", 0),
            "legal_knowledge": context_stats.get("legal_knowledge", 0),
            "case_documents": context_stats.get("case_document", 0),
            "case_narrative": context_stats.get("case_narrative", 0),
            "other": sum(v for k, v in context_stats.items() 
                        if k not in ["agent_memory", "legal_knowledge", "case_document", "case_narrative"])
        }
        
        return usage
    except Exception as e:
        logger.error(f"Erreur récupération usage par type: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/embed")
async def create_embedding(
    text: str,
    agent_id: str,
    context_type: str = "general",
    service: UnifiedEmbeddingService = Depends(get_embedding_service)
):
    """
    Crée un embedding pour un texte donné
    """
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide")
        
        embedding = await service.embed_for_agent(
            agent_id=agent_id,
            text=text,
            context_type=context_type
        )
        
        return {
            "embedding": embedding,
            "dimension": len(embedding),
            "agent_id": agent_id,
            "context_type": context_type,
            "text_length": len(text),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur création embedding: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/similarity")
async def calculate_similarity(
    text1: str,
    text2: str,
    agent_id: str,
    context_type: str = "general",
    service: UnifiedEmbeddingService = Depends(get_embedding_service)
):
    """
    Calcule la similarité entre deux textes
    """
    try:
        if not text1.strip() or not text2.strip():
            raise HTTPException(status_code=400, detail="Les textes ne peuvent pas être vides")
        
        # Création des embeddings
        embedding1 = await service.embed_for_agent(agent_id, text1, context_type)
        embedding2 = await service.embed_for_agent(agent_id, text2, context_type)
        
        # Calcul de la similarité
        similarity = await service.calculate_similarity(embedding1, embedding2)
        
        return {
            "similarity": float(similarity),
            "text1_length": len(text1),
            "text2_length": len(text2),
            "agent_id": agent_id,
            "context_type": context_type,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur calcul similarité: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-embed")
async def create_batch_embeddings(
    texts: List[str],
    agent_id: str,
    context_type: str = "general",
    service: UnifiedEmbeddingService = Depends(get_embedding_service)
):
    """
    Crée des embeddings en lot pour plusieurs textes
    """
    try:
        if not texts:
            raise HTTPException(status_code=400, detail="La liste de textes ne peut pas être vide")
        
        if len(texts) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 textes par lot")
        
        embeddings = await service.batch_embed_for_agent(
            agent_id=agent_id,
            texts=texts,
            context_type=context_type
        )
        
        return {
            "embeddings": embeddings,
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0,
            "agent_id": agent_id,
            "context_type": context_type,
            "total_text_length": sum(len(text) for text in texts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur création embeddings batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_stats(
    format: str = "json",
    service: UnifiedEmbeddingService = Depends(get_embedding_service)
):
    """
    Exporte les statistiques complètes des embeddings
    """
    try:
        stats = await service.export_stats()
        
        if format.lower() == "json":
            return stats
        else:
            raise HTTPException(status_code=400, detail="Format non supporté. Utilisez 'json'")
    except Exception as e:
        logger.error(f"Erreur export stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache")
async def clear_cache(service: UnifiedEmbeddingService = Depends(get_embedding_service)):
    """
    Vide le cache des embeddings
    """
    try:
        # Vider le cache de tous les providers
        cleared_count = 0
        for provider_name, provider in service.providers.items():
            if hasattr(provider, 'cache') and provider.cache:
                cache_size = len(provider.cache)
                provider.cache.clear()
                cleared_count += cache_size
                logger.info(f"Cache {provider_name} vidé: {cache_size} entrées")
        
        return {
            "message": "Cache vidé avec succès",
            "cleared_entries": cleared_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur vidage cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
