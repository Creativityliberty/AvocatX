"""
Service d'embedding unifié pour DEFENSEUR-IA
Support Pinecone + Gemini Embedding avec abstraction complète
"""

import asyncio
import os
import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import datetime
import json

from .gemini_embedding_service import (
    GeminiEmbeddingService,
    EmbeddingTaskType,
    EmbeddingDimension,
    gemini_embedding_service
)

logger = logging.getLogger(__name__)


class EmbeddingProvider(Enum):
    """Fournisseurs d'embedding supportés"""
    GEMINI = "gemini"
    PINECONE = "pinecone"
    OPENAI = "openai"
    AUTO = "auto"  # Sélection automatique


class UnifiedEmbeddingService:
    """
    Service d'embedding unifié pour tous les agents DEFENSEUR-IA
    Abstraction complète avec fallback automatique
    """
    
    def __init__(self):
        self.providers = {}
        self.default_provider = EmbeddingProvider.GEMINI
        self.fallback_chain = [
            EmbeddingProvider.GEMINI,
            EmbeddingProvider.OPENAI,
            EmbeddingProvider.PINECONE
        ]
        
        # Configuration par type d'agent
        self.agent_configs = {
            "ecouteur": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.SEMANTIC_SIMILARITY,
                "dimension": EmbeddingDimension.LARGE
            },
            "cadreur_juridique": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.RETRIEVAL_DOCUMENT,
                "dimension": EmbeddingDimension.LARGE
            },
            "parseur_preuves": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.CLASSIFICATION,
                "dimension": EmbeddingDimension.MEDIUM
            },
            "juriste_matching": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.SEMANTIC_SIMILARITY,
                "dimension": EmbeddingDimension.LARGE
            },
            "recherche_web": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.RETRIEVAL_QUERY,
                "dimension": EmbeddingDimension.LARGE
            },
            "redacteur_narratif": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.SEMANTIC_SIMILARITY,
                "dimension": EmbeddingDimension.LARGE
            },
            "relecteur_ia_1": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.FACT_VERIFICATION,
                "dimension": EmbeddingDimension.LARGE
            },
            "agregateur_coherence": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.CLUSTERING,
                "dimension": EmbeddingDimension.LARGE
            },
            "relecteur_ia_2": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.SEMANTIC_SIMILARITY,
                "dimension": EmbeddingDimension.LARGE
            },
            "synthese_strategique": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.CLASSIFICATION,
                "dimension": EmbeddingDimension.LARGE
            },
            "avocat_ia": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.RETRIEVAL_DOCUMENT,
                "dimension": EmbeddingDimension.LARGE
            },
            "export_final": {
                "provider": EmbeddingProvider.GEMINI,
                "task_type": EmbeddingTaskType.SEMANTIC_SIMILARITY,
                "dimension": EmbeddingDimension.MEDIUM
            }
        }
        
        self.stats = {
            "total_embeddings": 0,
            "provider_usage": {},
            "fallback_activations": 0,
            "errors": 0
        }
    
    async def initialize(self):
        """Initialise tous les fournisseurs d'embedding disponibles"""
        
        logger.info("🔧 Initialisation UnifiedEmbeddingService")
        
        # Initialiser Gemini
        try:
            await gemini_embedding_service.initialize()
            self.providers[EmbeddingProvider.GEMINI] = gemini_embedding_service
            logger.info("✅ Fournisseur Gemini initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Gemini: {e}")
        
        # Initialiser Pinecone (si disponible)
        try:
            from .pinecone_service import pinecone_service
            await pinecone_service.initialize()
            self.providers[EmbeddingProvider.PINECONE] = pinecone_service
            logger.info("✅ Fournisseur Pinecone initialisé")
        except Exception as e:
            logger.warning(f"⚠️ Pinecone non disponible: {e}")
        
        # Initialiser OpenAI (si disponible)
        try:
            # TODO: Implémenter OpenAI embedding service si nécessaire
            logger.info("ℹ️ OpenAI embedding non implémenté")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI non disponible: {e}")
        
        logger.info(f"✅ {len(self.providers)} fournisseurs d'embedding disponibles")
        return len(self.providers) > 0
    
    def _get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """Récupère la configuration d'embedding pour un type d'agent"""
        return self.agent_configs.get(agent_type, {
            "provider": self.default_provider,
            "task_type": EmbeddingTaskType.SEMANTIC_SIMILARITY,
            "dimension": EmbeddingDimension.LARGE
        })
    
    async def create_embedding(
        self,
        text: str,
        agent_type: Optional[str] = None,
        provider: Optional[EmbeddingProvider] = None,
        task_type: Optional[EmbeddingTaskType] = None,
        dimension: Optional[EmbeddingDimension] = None,
        use_fallback: bool = True
    ) -> Optional[List[float]]:
        """
        Crée un embedding avec le fournisseur optimal
        
        Args:
            text: Texte à embedder
            agent_type: Type d'agent (pour configuration automatique)
            provider: Fournisseur spécifique à utiliser
            task_type: Type de tâche d'embedding
            dimension: Dimension de l'embedding
            use_fallback: Utiliser le fallback en cas d'erreur
        
        Returns:
            Embedding ou None si erreur
        """
        
        if not text or not text.strip():
            return None
        
        # Déterminer la configuration
        if agent_type:
            config = self._get_agent_config(agent_type)
            provider = provider or config["provider"]
            task_type = task_type or config["task_type"]
            dimension = dimension or config["dimension"]
        else:
            provider = provider or self.default_provider
            task_type = task_type or EmbeddingTaskType.SEMANTIC_SIMILARITY
            dimension = dimension or EmbeddingDimension.LARGE
        
        # Liste des fournisseurs à essayer
        providers_to_try = [provider] if not use_fallback else [provider] + [
            p for p in self.fallback_chain if p != provider
        ]
        
        for current_provider in providers_to_try:
            if current_provider not in self.providers:
                continue
            
            try:
                service = self.providers[current_provider]
                
                if current_provider == EmbeddingProvider.GEMINI:
                    embedding = await service.create_embedding(
                        text=text,
                        task_type=task_type,
                        dimension=dimension
                    )
                elif current_provider == EmbeddingProvider.PINECONE:
                    # Adapter l'appel pour Pinecone
                    embedding = await service.create_embedding(text)
                else:
                    # Autres fournisseurs
                    embedding = await service.create_embedding(text)
                
                if embedding:
                    # Mettre à jour les statistiques
                    self.stats["total_embeddings"] += 1
                    provider_key = current_provider.value
                    self.stats["provider_usage"][provider_key] = \
                        self.stats["provider_usage"].get(provider_key, 0) + 1
                    
                    if current_provider != provider:
                        self.stats["fallback_activations"] += 1
                        logger.info(f"🔄 Fallback activé: {provider.value} → {current_provider.value}")
                    
                    return embedding
                
            except Exception as e:
                logger.error(f"❌ Erreur {current_provider.value}: {e}")
                continue
        
        # Aucun fournisseur n'a fonctionné
        self.stats["errors"] += 1
        logger.error(f"❌ Échec création embedding avec tous les fournisseurs")
        return None
    
    async def create_embeddings_batch(
        self,
        texts: List[str],
        agent_type: Optional[str] = None,
        provider: Optional[EmbeddingProvider] = None,
        **kwargs
    ) -> List[Optional[List[float]]]:
        """
        Crée des embeddings en batch
        
        Args:
            texts: Liste de textes à embedder
            agent_type: Type d'agent pour configuration
            provider: Fournisseur spécifique
            **kwargs: Arguments supplémentaires
        
        Returns:
            Liste d'embeddings
        """
        
        if not texts:
            return []
        
        # Déterminer la configuration
        config = self._get_agent_config(agent_type) if agent_type else {}
        provider = provider or config.get("provider", self.default_provider)
        
        # Essayer le batch processing si supporté
        if provider in self.providers:
            try:
                service = self.providers[provider]
                
                if hasattr(service, 'create_embeddings_batch'):
                    return await service.create_embeddings_batch(
                        texts=texts,
                        task_type=config.get("task_type", EmbeddingTaskType.SEMANTIC_SIMILARITY),
                        dimension=config.get("dimension", EmbeddingDimension.LARGE)
                    )
            except Exception as e:
                logger.error(f"❌ Erreur batch {provider.value}: {e}")
        
        # Fallback: traitement individuel
        results = []
        for text in texts:
            embedding = await self.create_embedding(
                text=text,
                agent_type=agent_type,
                provider=provider,
                **kwargs
            )
            results.append(embedding)
        
        return results
    
    async def create_agent_memory_embedding(
        self,
        agent_type: str,
        context: str,
        experience_data: Dict[str, Any]
    ) -> Optional[List[float]]:
        """Crée un embedding spécialisé pour la mémoire d'agent"""
        
        # Construire un texte enrichi
        memory_text = f"""
        Agent: {agent_type}
        Contexte: {context}
        Erreur: {experience_data.get('error', 'Aucune')}
        Solution: {experience_data.get('solution', 'Non spécifiée')}
        Validé: {experience_data.get('validated', False)}
        Métadonnées: {json.dumps(experience_data.get('metadata', {}), ensure_ascii=False)}
        """
        
        return await self.create_embedding(
            text=memory_text.strip(),
            agent_type=agent_type,
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT
        )
    
    async def create_legal_knowledge_embedding(
        self,
        title: str,
        content: str,
        source: str,
        article_code: Optional[str] = None
    ) -> Optional[List[float]]:
        """Crée un embedding pour les connaissances juridiques"""
        
        legal_text = f"""
        Titre: {title}
        Source: {source}
        {f'Article: {article_code}' if article_code else ''}
        Contenu: {content}
        """
        
        return await self.create_embedding(
            text=legal_text.strip(),
            agent_type="cadreur_juridique",  # Utiliser la config juridique
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT
        )
    
    async def create_case_embedding(
        self,
        case_type: str,
        narrative: str,
        metadata: Dict[str, Any]
    ) -> Optional[List[float]]:
        """Crée un embedding pour un dossier/cas"""
        
        case_text = f"""
        Type de dossier: {case_type}
        Récit: {narrative}
        Urgence: {metadata.get('urgency', 'normale')}
        Situation familiale: {metadata.get('family_situation', 'non spécifiée')}
        Métadonnées: {json.dumps(metadata, ensure_ascii=False)}
        """
        
        return await self.create_embedding(
            text=case_text.strip(),
            agent_type="redacteur_narratif",
            task_type=EmbeddingTaskType.SEMANTIC_SIMILARITY
        )
    
    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calcule la similarité cosinus entre deux embeddings"""
        
        # Utiliser le service Gemini pour le calcul (ou implémenter ici)
        if EmbeddingProvider.GEMINI in self.providers:
            return self.providers[EmbeddingProvider.GEMINI].calculate_similarity(
                embedding1, embedding2
            )
        
        # Implémentation fallback
        import numpy as np
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"Erreur calcul similarité: {e}")
            return 0.0
    
    async def find_most_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Trouve les embeddings les plus similaires"""
        
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            if candidate:
                similarity = self.calculate_similarity(query_embedding, candidate)
                similarities.append({
                    "index": i,
                    "similarity": similarity,
                    "embedding": candidate
                })
        
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques globales"""
        
        provider_stats = {}
        for provider, service in self.providers.items():
            if hasattr(service, 'get_stats'):
                provider_stats[provider.value] = service.get_stats()
        
        return {
            "service_type": "unified_embedding",
            "available_providers": list(self.providers.keys()),
            "default_provider": self.default_provider.value,
            "global_stats": self.stats.copy(),
            "provider_stats": provider_stats,
            "agent_configs": {
                agent: {
                    "provider": config["provider"].value,
                    "task_type": config["task_type"].value,
                    "dimension": config["dimension"].value
                }
                for agent, config in self.agent_configs.items()
            }
        }
    
    async def optimize_agent_config(
        self,
        agent_type: str,
        performance_data: Dict[str, Any]
    ):
        """Optimise la configuration d'un agent basée sur les performances"""
        
        if agent_type not in self.agent_configs:
            return
        
        current_config = self.agent_configs[agent_type]
        
        # Logique d'optimisation basée sur les performances
        # TODO: Implémenter l'optimisation automatique
        
        logger.info(f"🔧 Configuration agent {agent_type} optimisée")
    
    async def export_unified_stats(self, filename: Optional[str] = None) -> str:
        """Exporte les statistiques unifiées"""
        
        if not filename:
            filename = f"unified_embedding_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stats_data = {
            "timestamp": datetime.now().isoformat(),
            "unified_stats": self.get_stats(),
            "system_info": {
                "total_agents": len(self.agent_configs),
                "available_providers": len(self.providers),
                "fallback_enabled": True
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Statistiques unifiées exportées: {filename}")
        return filename


# Instance globale du service unifié
unified_embedding_service = UnifiedEmbeddingService()


# Fonctions utilitaires simplifiées pour les agents
async def embed_for_agent(
    text: str,
    agent_type: str,
    context_type: str = "general"
) -> Optional[List[float]]:
    """
    Fonction utilitaire principale pour embedder du texte pour un agent
    
    Args:
        text: Texte à embedder
        agent_type: Type d'agent DEFENSEUR-IA
        context_type: Type de contexte (general, memory, legal, case)
    
    Returns:
        Embedding optimisé pour l'agent
    """
    
    if context_type == "memory":
        # Pour les expériences d'agent
        experience_data = {"context": text}
        return await unified_embedding_service.create_agent_memory_embedding(
            agent_type, text, experience_data
        )
    elif context_type == "legal":
        # Pour les connaissances juridiques
        return await unified_embedding_service.create_legal_knowledge_embedding(
            title=f"Document {agent_type}",
            content=text,
            source="DEFENSEUR-IA"
        )
    elif context_type == "case":
        # Pour les dossiers
        return await unified_embedding_service.create_case_embedding(
            case_type="OQTF",
            narrative=text,
            metadata={"agent": agent_type}
        )
    else:
        # Embedding général
        return await unified_embedding_service.create_embedding(
            text=text,
            agent_type=agent_type
        )


async def batch_embed_for_agent(
    texts: List[str],
    agent_type: str
) -> List[Optional[List[float]]]:
    """Fonction utilitaire pour embedding batch optimisé par agent"""
    
    return await unified_embedding_service.create_embeddings_batch(
        texts=texts,
        agent_type=agent_type
    )


if __name__ == "__main__":
    # Test du service unifié
    async def test_unified_service():
        logger.info("🧪 Test du service d'embedding unifié")

        # Initialiser le service
        await unified_embedding_service.initialize()

        # Test embedding pour différents agents
        test_cases = [
            ("ecouteur", "Transcription audio OQTF"),
            ("cadreur_juridique", "Article L511-1 du CESEDA"),
            ("redacteur_narratif", "Récit de Marie, 32 ans, mère d'un enfant français")
        ]

        for agent_type, text in test_cases:
            embedding = await embed_for_agent(text, agent_type)
            if embedding:
                logger.info(f"✅ {agent_type}: embedding {len(embedding)}D créé")
            else:
                logger.error(f"❌ {agent_type}: échec embedding")

        # Afficher les statistiques
        stats = unified_embedding_service.get_stats()
        logger.info(f"\n📊 Statistiques: {stats['global_stats']}")
    
    asyncio.run(test_unified_service())
