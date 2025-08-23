"""
AGENT 3 - Juriste Matching
Établit des correspondances entre les pièces justificatives et les articles de loi
Utilise le service d'embedding unifié (Gemini/Pinecone) pour le matching sémantique
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from ..core.base import BaseNode, NodeContext
from ..models import MatchPieceArticle, CodeArticle, PieceParsed
from ..services.unified_embedding_service import UnifiedEmbeddingService

logger = logging.getLogger(__name__)

class JuristeMatchingNode(BaseNode):
    """
    Agent responsable du matching sémantique entre pièces et articles de loi
    
    Inputs: pieces_parsed, corpus_legal
    Output: matches (correspondances pièces ↔ articles)
    """
    
    def __init__(self):
        super().__init__("juriste_matching", "Juriste Matching")
        self.embedding_service = None
        self.articles_cache = []
        self.articles_embeddings = []
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Effectue le matching sémantique entre pièces et corpus légal
        """
        try:
            logger.info("🔗 Début du matching juridique sémantique avec embedding unifié")
            
            # Récupération des données
            pieces_parsed = context.shared_store.get("pieces_parsed", [])
            corpus_legal = context.shared_store.get("corpus_legal", [])
            
            if not pieces_parsed:
                logger.warning("Aucune pièce parsée disponible")
                return {"matches": []}
                
            if not corpus_legal:
                logger.warning("Aucun corpus légal disponible")
                return {"matches": []}

            # Initialisation du service d'embedding
            await self._initialize_embedding_service()
            
            # Construction de l'index d'embeddings
            await self._build_embedding_index(corpus_legal)
            
            # Matching pour chaque pièce
            all_matches = []
            for piece in pieces_parsed:
                matches = await self._match_piece_to_articles(piece)
                all_matches.extend(matches)
            
            logger.info(f"✅ Matching terminé: {len(all_matches)} correspondances trouvées")
            
            return {
                "matches": all_matches,
                "stats": {
                    "total_pieces": len(pieces_parsed),
                    "total_articles": len(corpus_legal),
                    "total_matches": len(all_matches)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dans le matching juridique: {e}")
            return {"matches": [], "error": str(e)}
    
    async def _initialize_embedding_service(self):
        """Initialise le service d'embedding unifié"""
        try:
            if self.embedding_service is None:
                self.embedding_service = UnifiedEmbeddingService()
                await self.embedding_service.initialize()
                logger.info("✅ Service d'embedding unifié initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation service embedding: {e}")
            raise

    async def _build_embedding_index(self, corpus_legal: List[Dict[str, Any]]):
        """Construit l'index d'embeddings pour la recherche vectorielle"""
        try:
            logger.info("🏗️ Construction de l'index d'embeddings...")
            
            # Préparation des textes à encoder
            texts_to_encode = []
            self.articles_cache = []
            
            for article in corpus_legal:
                # Combinaison titre + contenu pour un meilleur matching
                text = f"{article.get('titre', '')} {article.get('contenu', '')}"
                texts_to_encode.append(text)
                self.articles_cache.append(article)
            
            if not texts_to_encode:
                logger.warning("Aucun texte à encoder dans le corpus légal")
                return
            
            # Génération des embeddings via le service unifié
            self.articles_embeddings = await self.embedding_service.batch_embed_for_agent(
                agent_id="juriste_matching",
                texts=texts_to_encode,
                context_type="legal_knowledge"
            )
            
            logger.info(f"✅ Index d'embeddings construit: {len(texts_to_encode)} articles indexés")
            
        except Exception as e:
            logger.error(f"Erreur construction index embeddings: {e}")
            raise
    
    async def _match_piece_to_articles(self, piece: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Trouve les articles les plus pertinents pour une pièce"""
        try:
            # Préparation du texte de la pièce
            contenu_piece = piece.get('contenu_brut', '')
            filename = piece.get('filename', 'unknown')
            
            if not contenu_piece.strip():
                logger.warning(f"Contenu vide pour {filename}")
                return []
            
            # Génération de l'embedding de la pièce
            piece_embedding = await self.embedding_service.embed_for_agent(
                agent_id="juriste_matching",
                text=contenu_piece,
                context_type="case_document"
            )
            
            # Calcul des similarités avec tous les articles
            similarities = []
            for i, article_embedding in enumerate(self.articles_embeddings):
                similarity = await self.embedding_service.calculate_similarity(
                    piece_embedding, article_embedding
                )
                similarities.append((i, similarity))
            
            # Tri par similarité décroissante et sélection du top 10
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_matches = similarities[:10]
            
            matches = []
            for idx, score in top_matches:
                if score > 0.3:  # Seuil de pertinence
                    article = self.articles_cache[idx]
                    
                    match = MatchPieceArticle(
                        piece_id=piece.get('id', filename),
                        article_id=article.get('id', f"art_{idx}"),
                        score_pertinence=float(score),
                        justification=f"Similarité sémantique: {score:.3f}",
                        piece_filename=filename,
                        article_titre=article.get('titre', 'Sans titre'),
                        article_contenu=article.get('contenu', '')[:500] + "..." if len(article.get('contenu', '')) > 500 else article.get('contenu', '')
                    )
                    
                    matches.append(match.dict())
                    
            logger.info(f"📄 {filename}: {len(matches)} correspondances trouvées")
            return matches
            
        except Exception as e:
            logger.error(f"Erreur matching pièce {piece.get('filename', 'unknown')}: {e}")
            return []
