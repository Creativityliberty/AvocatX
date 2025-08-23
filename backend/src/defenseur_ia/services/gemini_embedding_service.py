"""
Service d'embedding Gemini pour DEFENSEUR-IA
Intégration avec gemini-embedding-001 pour la mémoire sémantique des agents
"""

import asyncio
import os
import numpy as np
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import logging
from datetime import datetime
import json

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google GenAI non disponible - mode simulation activé")

logger = logging.getLogger(__name__)


class EmbeddingTaskType(Enum):
    """Types de tâches d'embedding supportés par Gemini"""
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
    CLASSIFICATION = "CLASSIFICATION"
    CLUSTERING = "CLUSTERING"
    RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY"
    CODE_RETRIEVAL_QUERY = "CODE_RETRIEVAL_QUERY"
    QUESTION_ANSWERING = "QUESTION_ANSWERING"
    FACT_VERIFICATION = "FACT_VERIFICATION"


class EmbeddingDimension(Enum):
    """Dimensions d'embedding supportées"""
    FULL = 3072  # Dimension complète
    LARGE = 1536  # Dimension large (recommandée)
    MEDIUM = 768  # Dimension moyenne (recommandée)


class GeminiEmbeddingService:
    """
    Service d'embedding utilisant Gemini embedding-001
    Optimisé pour les agents DEFENSEUR-IA avec cache et batch processing
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model_name = "gemini-embedding-001"
        self.cache = {}  # Cache simple pour éviter les appels répétés
        self.stats = {
            "total_embeddings": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "errors": 0
        }
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("✅ GeminiEmbeddingService initialisé avec API")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation Gemini: {e}")
                self.client = None
        else:
            logger.warning("⚠️ GeminiEmbeddingService en mode simulation")
    
    async def initialize(self):
        """Initialisation asynchrone du service"""
        if self.client:
            try:
                # Test de connexion avec un embedding simple
                test_result = await self.create_embedding(
                    "Test de connexion DEFENSEUR-IA",
                    task_type=EmbeddingTaskType.SEMANTIC_SIMILARITY
                )
                if test_result:
                    logger.info("✅ Service Gemini Embedding opérationnel")
                    return True
            except Exception as e:
                logger.error(f"❌ Test de connexion échoué: {e}")
        
        logger.warning("⚠️ Service en mode dégradé (simulation)")
        return False
    
    def _get_cache_key(self, text: str, task_type: EmbeddingTaskType, dimension: EmbeddingDimension) -> str:
        """Génère une clé de cache pour un embedding"""
        import hashlib
        content = f"{text}_{task_type.value}_{dimension.value}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _simulate_embedding(self, dimension: EmbeddingDimension) -> List[float]:
        """Simule un embedding pour les tests sans API"""
        np.random.seed(42)  # Pour la reproductibilité
        embedding = np.random.normal(0, 1, dimension.value)
        # Normaliser l'embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()
    
    async def create_embedding(
        self,
        text: str,
        task_type: EmbeddingTaskType = EmbeddingTaskType.SEMANTIC_SIMILARITY,
        dimension: EmbeddingDimension = EmbeddingDimension.LARGE,
        use_cache: bool = True
    ) -> Optional[List[float]]:
        """
        Crée un embedding pour un texte donné
        
        Args:
            text: Texte à embedder
            task_type: Type de tâche pour optimiser l'embedding
            dimension: Dimension de l'embedding de sortie
            use_cache: Utiliser le cache si disponible
        
        Returns:
            Liste de floats représentant l'embedding ou None si erreur
        """
        
        if not text or not text.strip():
            logger.warning("Texte vide fourni pour embedding")
            return None
        
        # Vérifier le cache
        cache_key = self._get_cache_key(text, task_type, dimension)
        if use_cache and cache_key in self.cache:
            self.stats["cache_hits"] += 1
            return self.cache[cache_key]
        
        try:
            if self.client and GEMINI_AVAILABLE:
                # Appel API réel
                config = types.EmbedContentConfig(
                    task_type=task_type.value,
                    output_dimensionality=dimension.value if dimension != EmbeddingDimension.FULL else None
                )
                
                result = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text,
                    config=config
                )
                
                if result.embeddings:
                    embedding = list(result.embeddings[0].values)
                    
                    # Normaliser si nécessaire (pour dimensions autres que 3072)
                    if dimension != EmbeddingDimension.FULL:
                        embedding_np = np.array(embedding)
                        norm = np.linalg.norm(embedding_np)
                        if norm > 0:
                            embedding = (embedding_np / norm).tolist()
                    
                    # Mettre en cache
                    if use_cache:
                        self.cache[cache_key] = embedding
                    
                    self.stats["api_calls"] += 1
                    self.stats["total_embeddings"] += 1
                    
                    return embedding
                else:
                    logger.error("Aucun embedding retourné par l'API")
                    self.stats["errors"] += 1
                    return None
            
            else:
                # Mode simulation
                embedding = self._simulate_embedding(dimension)
                if use_cache:
                    self.cache[cache_key] = embedding
                self.stats["total_embeddings"] += 1
                return embedding
                
        except Exception as e:
            logger.error(f"Erreur création embedding: {e}")
            self.stats["errors"] += 1
            return None
    
    async def create_embeddings_batch(
        self,
        texts: List[str],
        task_type: EmbeddingTaskType = EmbeddingTaskType.SEMANTIC_SIMILARITY,
        dimension: EmbeddingDimension = EmbeddingDimension.LARGE,
        use_cache: bool = True
    ) -> List[Optional[List[float]]]:
        """
        Crée des embeddings pour une liste de textes (batch processing)
        
        Args:
            texts: Liste de textes à embedder
            task_type: Type de tâche pour optimiser les embeddings
            dimension: Dimension des embeddings de sortie
            use_cache: Utiliser le cache si disponible
        
        Returns:
            Liste d'embeddings (ou None pour les erreurs)
        """
        
        if not texts:
            return []
        
        # Séparer les textes en cache et non-cache
        cached_results = {}
        texts_to_process = []
        
        if use_cache:
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text, task_type, dimension)
                if cache_key in self.cache:
                    cached_results[i] = self.cache[cache_key]
                    self.stats["cache_hits"] += 1
                else:
                    texts_to_process.append((i, text))
        else:
            texts_to_process = list(enumerate(texts))
        
        # Traiter les textes non-cachés
        results = [None] * len(texts)
        
        # Remplir les résultats cachés
        for i, embedding in cached_results.items():
            results[i] = embedding
        
        if texts_to_process:
            try:
                if self.client and GEMINI_AVAILABLE:
                    # Appel API batch réel
                    config = types.EmbedContentConfig(
                        task_type=task_type.value,
                        output_dimensionality=dimension.value if dimension != EmbeddingDimension.FULL else None
                    )
                    
                    batch_texts = [text for _, text in texts_to_process]
                    result = self.client.models.embed_content(
                        model=self.model_name,
                        contents=batch_texts,
                        config=config
                    )
                    
                    if result.embeddings:
                        for j, (i, text) in enumerate(texts_to_process):
                            if j < len(result.embeddings):
                                embedding = list(result.embeddings[j].values)
                                
                                # Normaliser si nécessaire
                                if dimension != EmbeddingDimension.FULL:
                                    embedding_np = np.array(embedding)
                                    norm = np.linalg.norm(embedding_np)
                                    if norm > 0:
                                        embedding = (embedding_np / norm).tolist()
                                
                                results[i] = embedding
                                
                                # Mettre en cache
                                if use_cache:
                                    cache_key = self._get_cache_key(text, task_type, dimension)
                                    self.cache[cache_key] = embedding
                    
                    self.stats["api_calls"] += 1
                    self.stats["total_embeddings"] += len(texts_to_process)
                
                else:
                    # Mode simulation batch
                    for i, text in texts_to_process:
                        embedding = self._simulate_embedding(dimension)
                        results[i] = embedding
                        
                        if use_cache:
                            cache_key = self._get_cache_key(text, task_type, dimension)
                            self.cache[cache_key] = embedding
                    
                    self.stats["total_embeddings"] += len(texts_to_process)
                        
            except Exception as e:
                logger.error(f"Erreur création embeddings batch: {e}")
                self.stats["errors"] += 1
        
        return results
    
    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings
        
        Args:
            embedding1: Premier embedding
            embedding2: Deuxième embedding
        
        Returns:
            Score de similarité entre -1 et 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Similarité cosinus
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Erreur calcul similarité: {e}")
            return 0.0
    
    async def find_most_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Trouve les embeddings les plus similaires à une requête
        
        Args:
            query_embedding: Embedding de la requête
            candidate_embeddings: Liste d'embeddings candidats
            top_k: Nombre de résultats à retourner
        
        Returns:
            Liste des résultats triés par similarité décroissante
        """
        
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            if candidate:  # Vérifier que l'embedding n'est pas None
                similarity = self.calculate_similarity(query_embedding, candidate)
                similarities.append({
                    "index": i,
                    "similarity": similarity,
                    "embedding": candidate
                })
        
        # Trier par similarité décroissante
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similarities[:top_k]
    
    async def create_agent_memory_embedding(
        self,
        agent_type: str,
        context: str,
        experience_data: Dict[str, Any]
    ) -> Optional[List[float]]:
        """
        Crée un embedding spécialisé pour la mémoire d'agent
        
        Args:
            agent_type: Type d'agent (ecouteur, cadreur_juridique, etc.)
            context: Contexte de l'expérience
            experience_data: Données d'expérience (erreur, solution, etc.)
        
        Returns:
            Embedding optimisé pour la mémoire d'agent
        """
        
        # Construire un texte enrichi pour l'embedding
        memory_text = f"""
        Agent: {agent_type}
        Contexte: {context}
        Erreur: {experience_data.get('error', 'Aucune')}
        Solution: {experience_data.get('solution', 'Non spécifiée')}
        Validé: {experience_data.get('validated', False)}
        """
        
        return await self.create_embedding(
            memory_text.strip(),
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT,
            dimension=EmbeddingDimension.LARGE
        )
    
    async def create_legal_knowledge_embedding(
        self,
        title: str,
        content: str,
        source: str,
        article_code: Optional[str] = None
    ) -> Optional[List[float]]:
        """
        Crée un embedding spécialisé pour les connaissances juridiques
        
        Args:
            title: Titre du document juridique
            content: Contenu du document
            source: Source du document
            article_code: Code d'article si applicable
        
        Returns:
            Embedding optimisé pour les connaissances juridiques
        """
        
        # Construire un texte enrichi pour l'embedding juridique
        legal_text = f"""
        Titre: {title}
        Source: {source}
        {f'Article: {article_code}' if article_code else ''}
        Contenu: {content}
        """
        
        return await self.create_embedding(
            legal_text.strip(),
            task_type=EmbeddingTaskType.RETRIEVAL_DOCUMENT,
            dimension=EmbeddingDimension.LARGE
        )
    
    async def create_case_embedding(
        self,
        case_type: str,
        narrative: str,
        metadata: Dict[str, Any]
    ) -> Optional[List[float]]:
        """
        Crée un embedding spécialisé pour les dossiers/cas
        
        Args:
            case_type: Type de dossier (OQTF, etc.)
            narrative: Récit du dossier
            metadata: Métadonnées du dossier
        
        Returns:
            Embedding optimisé pour les dossiers
        """
        
        # Construire un texte enrichi pour l'embedding de dossier
        case_text = f"""
        Type de dossier: {case_type}
        Récit: {narrative}
        Urgence: {metadata.get('urgency', 'normale')}
        Situation familiale: {metadata.get('family_situation', 'non spécifiée')}
        """
        
        return await self.create_embedding(
            case_text.strip(),
            task_type=EmbeddingTaskType.SEMANTIC_SIMILARITY,
            dimension=EmbeddingDimension.LARGE
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du service"""
        return {
            "service_type": "gemini_embedding",
            "model": self.model_name,
            "api_available": self.client is not None,
            "cache_size": len(self.cache),
            "stats": self.stats.copy()
        }
    
    def clear_cache(self):
        """Vide le cache d'embeddings"""
        self.cache.clear()
        logger.info("Cache d'embeddings vidé")
    
    async def export_embeddings_data(self, filename: Optional[str] = None) -> str:
        """Exporte les données d'embeddings pour analyse"""
        
        if not filename:
            filename = f"gemini_embeddings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "service_stats": self.get_stats(),
            "cache_entries": len(self.cache),
            "embeddings_sample": list(self.cache.keys())[:10]  # Échantillon des clés
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Données d'embeddings exportées: {filename}")
        return filename


# Instance globale du service
gemini_embedding_service = GeminiEmbeddingService()


# Fonctions utilitaires pour les agents
async def embed_agent_experience(
    agent_type: str,
    context: str,
    error: str,
    solution: str,
    validated: bool = False
) -> Optional[List[float]]:
    """Fonction utilitaire pour embedder une expérience d'agent"""
    
    experience_data = {
        "error": error,
        "solution": solution,
        "validated": validated
    }
    
    return await gemini_embedding_service.create_agent_memory_embedding(
        agent_type, context, experience_data
    )


async def embed_legal_document(
    title: str,
    content: str,
    source: str,
    article_code: Optional[str] = None
) -> Optional[List[float]]:
    """Fonction utilitaire pour embedder un document juridique"""
    
    return await gemini_embedding_service.create_legal_knowledge_embedding(
        title, content, source, article_code
    )


async def embed_case_narrative(
    case_type: str,
    narrative: str,
    urgency: str = "normale",
    family_situation: str = "non spécifiée"
) -> Optional[List[float]]:
    """Fonction utilitaire pour embedder un récit de dossier"""
    
    metadata = {
        "urgency": urgency,
        "family_situation": family_situation
    }
    
    return await gemini_embedding_service.create_case_embedding(
        case_type, narrative, metadata
    )


if __name__ == "__main__":
    # Test du service
    async def test_service():
        print("🧪 Test du service Gemini Embedding")
        
        # Initialiser le service
        await gemini_embedding_service.initialize()
        
        # Test embedding simple
        embedding = await gemini_embedding_service.create_embedding(
            "Test DEFENSEUR-IA avec Gemini",
            task_type=EmbeddingTaskType.SEMANTIC_SIMILARITY,
            dimension=EmbeddingDimension.MEDIUM
        )
        
        if embedding:
            print(f"✅ Embedding créé: {len(embedding)} dimensions")
            print(f"📊 Statistiques: {gemini_embedding_service.get_stats()}")
        else:
            print("❌ Échec création embedding")
    
    asyncio.run(test_service())
