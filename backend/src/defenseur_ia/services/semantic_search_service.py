"""
Service de recherche sémantique avancée pour DEFENSEUR-IA
Inspiré des notebooks Pinecone pour la recherche sémantique et le RAG
Intègre la recherche dense, sparse et le reranking
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import json

from .unified_embedding_service import UnifiedEmbeddingService
from .gemini_embedding_service import GeminiEmbeddingService

logger = logging.getLogger(__name__)

class SemanticSearchService:
    """
    Service de recherche sémantique avancée avec support pour:
    - Recherche dense (embeddings sémantiques)
    - Recherche sparse (mots-clés)
    - Cascading retrieval (combinaison dense + sparse)
    - Reranking des résultats
    - RAG (Retrieval Augmented Generation)
    """
    
    def __init__(self):
        self.embedding_service = None
        self.document_store = {}  # Stockage des documents indexés
        self.dense_index = {}     # Index dense par agent
        self.sparse_index = {}    # Index sparse par agent
        self.stats = {
            "total_searches": 0,
            "avg_search_time": 0.0,
            "cache_hits": 0,
            "rerank_improvements": 0
        }
    
    async def initialize(self):
        """Initialise le service de recherche sémantique"""
        try:
            self.embedding_service = UnifiedEmbeddingService()
            await self.embedding_service.initialize()
            logger.info("✅ Service de recherche sémantique initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation service recherche: {e}")
            raise
    
    async def index_documents(
        self, 
        documents: List[Dict[str, Any]], 
        agent_id: str,
        context_type: str = "legal_knowledge"
    ) -> Dict[str, Any]:
        """
        Indexe une collection de documents pour la recherche
        
        Args:
            documents: Liste de documents avec 'id', 'title', 'content'
            agent_id: ID de l'agent pour la configuration d'embedding
            context_type: Type de contexte pour l'embedding
        """
        try:
            logger.info(f"🏗️ Indexation de {len(documents)} documents pour {agent_id}")
            
            # Préparation des textes pour l'embedding
            texts_to_embed = []
            doc_metadata = []
            
            for doc in documents:
                # Combinaison titre + contenu pour un meilleur contexte
                text = f"{doc.get('title', '')} {doc.get('content', '')}"
                texts_to_embed.append(text)
                
                # Métadonnées du document
                metadata = {
                    "id": doc.get("id"),
                    "title": doc.get("title", ""),
                    "content": doc.get("content", ""),
                    "source": doc.get("source", ""),
                    "timestamp": doc.get("timestamp", datetime.now().isoformat()),
                    "agent_id": agent_id,
                    "context_type": context_type
                }
                doc_metadata.append(metadata)
            
            # Génération des embeddings denses
            embeddings = await self.embedding_service.batch_embed_for_agent(
                agent_id=agent_id,
                texts=texts_to_embed,
                context_type=context_type
            )
            
            # Stockage dans l'index dense
            if agent_id not in self.dense_index:
                self.dense_index[agent_id] = {
                    "embeddings": [],
                    "metadata": [],
                    "dimension": len(embeddings[0]) if embeddings else 0
                }
            
            self.dense_index[agent_id]["embeddings"].extend(embeddings)
            self.dense_index[agent_id]["metadata"].extend(doc_metadata)
            
            # Stockage des documents
            for doc in documents:
                self.document_store[doc.get("id")] = doc
            
            # Création de l'index sparse (simulation basée sur mots-clés)
            await self._build_sparse_index(documents, agent_id)
            
            logger.info(f"✅ Indexation terminée: {len(documents)} documents indexés")
            
            return {
                "indexed_count": len(documents),
                "total_documents": len(self.dense_index[agent_id]["metadata"]),
                "embedding_dimension": self.dense_index[agent_id]["dimension"],
                "agent_id": agent_id,
                "context_type": context_type
            }
            
        except Exception as e:
            logger.error(f"Erreur indexation documents: {e}")
            raise
    
    async def _build_sparse_index(self, documents: List[Dict[str, Any]], agent_id: str):
        """Construit un index sparse basé sur les mots-clés"""
        try:
            if agent_id not in self.sparse_index:
                self.sparse_index[agent_id] = {}
            
            for doc in documents:
                doc_id = doc.get("id")
                content = f"{doc.get('title', '')} {doc.get('content', '')}".lower()
                
                # Extraction simple des mots-clés (à améliorer avec TF-IDF)
                words = content.split()
                word_freq = {}
                
                for word in words:
                    if len(word) > 3:  # Ignorer les mots trop courts
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                self.sparse_index[agent_id][doc_id] = word_freq
                
        except Exception as e:
            logger.error(f"Erreur construction index sparse: {e}")
    
    async def semantic_search(
        self,
        query: str,
        agent_id: str,
        top_k: int = 10,
        context_type: str = "legal_knowledge",
        search_type: str = "dense"  # "dense", "sparse", "cascading"
    ) -> List[Dict[str, Any]]:
        """
        Effectue une recherche sémantique
        
        Args:
            query: Requête de recherche
            agent_id: ID de l'agent
            top_k: Nombre de résultats à retourner
            context_type: Type de contexte
            search_type: Type de recherche ("dense", "sparse", "cascading")
        """
        try:
            start_time = datetime.now()
            logger.info(f"🔍 Recherche sémantique: '{query[:50]}...' ({search_type})")
            
            if search_type == "dense":
                results = await self._dense_search(query, agent_id, top_k, context_type)
            elif search_type == "sparse":
                results = await self._sparse_search(query, agent_id, top_k)
            elif search_type == "cascading":
                results = await self._cascading_search(query, agent_id, top_k, context_type)
            else:
                raise ValueError(f"Type de recherche non supporté: {search_type}")
            
            # Mise à jour des statistiques
            search_time = (datetime.now() - start_time).total_seconds()
            self.stats["total_searches"] += 1
            self.stats["avg_search_time"] = (
                (self.stats["avg_search_time"] * (self.stats["total_searches"] - 1) + search_time) /
                self.stats["total_searches"]
            )
            
            logger.info(f"✅ Recherche terminée: {len(results)} résultats en {search_time:.2f}s")
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche sémantique: {e}")
            raise
    
    async def _dense_search(
        self,
        query: str,
        agent_id: str,
        top_k: int,
        context_type: str
    ) -> List[Dict[str, Any]]:
        """Recherche dense basée sur les embeddings"""
        try:
            if agent_id not in self.dense_index:
                logger.warning(f"Aucun index dense pour l'agent {agent_id}")
                return []
            
            # Génération de l'embedding de la requête
            query_embedding = await self.embedding_service.embed_for_agent(
                agent_id=agent_id,
                text=query,
                context_type=context_type
            )
            
            # Calcul des similarités
            index_data = self.dense_index[agent_id]
            similarities = []
            
            for i, doc_embedding in enumerate(index_data["embeddings"]):
                similarity = await self.embedding_service.calculate_similarity(
                    query_embedding, doc_embedding
                )
                similarities.append((i, similarity, index_data["metadata"][i]))
            
            # Tri par similarité décroissante
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Sélection du top_k
            results = []
            for i, (idx, score, metadata) in enumerate(similarities[:top_k]):
                result = {
                    "rank": i + 1,
                    "score": float(score),
                    "document": metadata,
                    "search_type": "dense"
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche dense: {e}")
            return []
    
    async def _sparse_search(
        self,
        query: str,
        agent_id: str,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Recherche sparse basée sur les mots-clés"""
        try:
            if agent_id not in self.sparse_index:
                logger.warning(f"Aucun index sparse pour l'agent {agent_id}")
                return []
            
            query_words = query.lower().split()
            doc_scores = {}
            
            # Calcul des scores TF-IDF simplifiés
            for doc_id, word_freq in self.sparse_index[agent_id].items():
                score = 0.0
                for word in query_words:
                    if word in word_freq:
                        score += word_freq[word]
                
                if score > 0:
                    doc_scores[doc_id] = score
            
            # Tri par score décroissant
            sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Sélection du top_k
            results = []
            for i, (doc_id, score) in enumerate(sorted_docs[:top_k]):
                document = self.document_store.get(doc_id, {})
                result = {
                    "rank": i + 1,
                    "score": float(score),
                    "document": {
                        "id": doc_id,
                        "title": document.get("title", ""),
                        "content": document.get("content", ""),
                        "source": document.get("source", "")
                    },
                    "search_type": "sparse"
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur recherche sparse: {e}")
            return []
    
    async def _cascading_search(
        self,
        query: str,
        agent_id: str,
        top_k: int,
        context_type: str
    ) -> List[Dict[str, Any]]:
        """Recherche cascading (dense + sparse + reranking)"""
        try:
            # Recherche dense et sparse en parallèle
            dense_results, sparse_results = await asyncio.gather(
                self._dense_search(query, agent_id, top_k * 2, context_type),
                self._sparse_search(query, agent_id, top_k * 2)
            )
            
            # Déduplication et combinaison
            combined_results = self._deduplicate_results(dense_results, sparse_results)
            
            # Reranking (simulation d'un modèle de reranking)
            reranked_results = await self._rerank_results(query, combined_results, top_k)
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"Erreur recherche cascading: {e}")
            return []
    
    def _deduplicate_results(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Déduplique et combine les résultats dense et sparse"""
        try:
            seen_docs = {}
            combined = []
            
            # Ajout des résultats dense
            for result in dense_results:
                doc_id = result["document"].get("id")
                if doc_id and doc_id not in seen_docs:
                    seen_docs[doc_id] = True
                    result["sources"] = ["dense"]
                    combined.append(result)
            
            # Ajout des résultats sparse non dupliqués
            for result in sparse_results:
                doc_id = result["document"].get("id")
                if doc_id and doc_id not in seen_docs:
                    seen_docs[doc_id] = True
                    result["sources"] = ["sparse"]
                    combined.append(result)
                elif doc_id in seen_docs:
                    # Document déjà présent, on combine les sources
                    for existing in combined:
                        if existing["document"].get("id") == doc_id:
                            existing["sources"].append("sparse")
                            # Moyenne des scores
                            existing["score"] = (existing["score"] + result["score"]) / 2
                            break
            
            return combined
            
        except Exception as e:
            logger.error(f"Erreur déduplication: {e}")
            return dense_results + sparse_results
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Reranking des résultats (simulation)"""
        try:
            # Simulation d'un reranking basé sur la longueur du contenu et la présence de mots-clés
            query_words = set(query.lower().split())
            
            for result in results:
                content = result["document"].get("content", "").lower()
                title = result["document"].get("title", "").lower()
                
                # Bonus pour les mots-clés dans le titre
                title_matches = len(query_words.intersection(set(title.split())))
                title_bonus = title_matches * 0.2
                
                # Bonus pour les mots-clés dans le contenu
                content_matches = len(query_words.intersection(set(content.split())))
                content_bonus = content_matches * 0.1
                
                # Bonus pour les sources multiples
                source_bonus = 0.1 if len(result.get("sources", [])) > 1 else 0
                
                # Score de reranking
                rerank_score = result["score"] + title_bonus + content_bonus + source_bonus
                result["rerank_score"] = rerank_score
                result["original_score"] = result["score"]
                result["score"] = rerank_score
            
            # Tri par score de reranking
            results.sort(key=lambda x: x["rerank_score"], reverse=True)
            
            # Mise à jour des rangs
            for i, result in enumerate(results[:top_k]):
                result["rank"] = i + 1
                result["search_type"] = "cascading"
            
            self.stats["rerank_improvements"] += 1
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Erreur reranking: {e}")
            return results[:top_k]
    
    async def generate_rag_prompt(
        self,
        query: str,
        agent_id: str,
        top_k: int = 5,
        context_type: str = "legal_knowledge"
    ) -> str:
        """
        Génère un prompt RAG avec contexte récupéré
        """
        try:
            # Recherche des documents pertinents
            results = await self.semantic_search(
                query=query,
                agent_id=agent_id,
                top_k=top_k,
                context_type=context_type,
                search_type="cascading"
            )
            
            # Construction du prompt avec contexte
            prompt_start = (
                "Réponds à la question en te basant sur les documents juridiques suivants.\n\n"
                "Documents de référence:\n"
            )
            
            context_separator = "\n\n---\n\n"
            contexts = []
            
            for result in results:
                doc = result["document"]
                context = f"Document: {doc.get('title', 'Sans titre')}\n"
                context += f"Source: {doc.get('source', 'Non spécifiée')}\n"
                context += f"Contenu: {doc.get('content', '')[:1000]}..."
                context += f"\nScore de pertinence: {result['score']:.3f}"
                contexts.append(context)
            
            prompt_end = f"\n\nQuestion: {query}\nRéponse:"
            
            full_prompt = prompt_start + context_separator.join(contexts) + prompt_end
            
            logger.info(f"📝 Prompt RAG généré avec {len(results)} documents de contexte")
            return full_prompt
            
        except Exception as e:
            logger.error(f"Erreur génération prompt RAG: {e}")
            return f"Question: {query}\nRéponse:"
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de recherche"""
        return {
            "total_searches": self.stats["total_searches"],
            "avg_search_time": f"{self.stats['avg_search_time']:.3f}s",
            "cache_hits": self.stats["cache_hits"],
            "rerank_improvements": self.stats["rerank_improvements"],
            "indexed_agents": list(self.dense_index.keys()),
            "total_documents": sum(len(idx["metadata"]) for idx in self.dense_index.values()),
            "last_updated": datetime.now().isoformat()
        }
    
    async def clear_index(self, agent_id: Optional[str] = None):
        """Vide l'index pour un agent ou tous les agents"""
        try:
            if agent_id:
                if agent_id in self.dense_index:
                    del self.dense_index[agent_id]
                if agent_id in self.sparse_index:
                    del self.sparse_index[agent_id]
                logger.info(f"Index vidé pour l'agent {agent_id}")
            else:
                self.dense_index.clear()
                self.sparse_index.clear()
                self.document_store.clear()
                logger.info("Tous les index vidés")
        except Exception as e:
            logger.error(f"Erreur vidage index: {e}")
            raise
