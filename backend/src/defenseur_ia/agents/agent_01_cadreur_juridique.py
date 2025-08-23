"""
AGENT 1 - Cadreur Juridique
Analyse la narration et identifie les axes juridiques pertinents
Utilise les APIs Légifrance et Judilibre avec configuration avancée
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..core.base import BaseNode, NodeContext
from ..models import HypotheseRecherche, CodeArticle, NarrationJusticiable
from ..services.enhanced_legifrance_service import (
    EnhancedLegifranceService, 
    SearchFilters, 
    AGENT_SEARCH_CONFIGS
)
from ..services.unified_embedding_service import UnifiedEmbeddingService

logger = logging.getLogger(__name__)

class CadreurJuridiqueNode(BaseNode):
    """
    Agent responsable du cadrage juridique initial
    
    Inputs: narration (témoignage du justiciable)
    Output: axes_juridiques, corpus_legal (articles de loi pertinents)
    """
    
    def __init__(self):
        super().__init__("cadreur_juridique", "Cadreur Juridique")
        self.legal_service = None
        self.embedding_service = None
        self.agent_config = AGENT_SEARCH_CONFIGS["cadreur_juridique"]
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Analyse la narration et identifie les axes juridiques
        """
        try:
            logger.info("⚖️ Début du cadrage juridique avec APIs avancées")
            
            # Récupération de la narration
            narration = context.shared_store.get("narration", {})
            if not narration:
                logger.warning("Aucune narration disponible pour le cadrage")
                return {"axes_juridiques": [], "corpus_legal": []}
            
            # Initialisation des services
            await self._initialize_services()
            
            # Analyse de la narration pour identifier les problématiques
            axes_juridiques = await self._analyze_legal_issues(narration)
            
            # Recherche des articles de loi pertinents
            corpus_legal = await self._build_legal_corpus(axes_juridiques)
            
            # Enrichissement avec la jurisprudence
            jurisprudence = await self._search_relevant_jurisprudence(axes_juridiques)
            
            # Fusion du corpus légal et jurisprudentiel
            complete_corpus = corpus_legal + jurisprudence
            
            # Sauvegarde dans le store partagé
            context.shared_store.set("axes_juridiques", axes_juridiques)
            context.shared_store.set("corpus_legal", complete_corpus)
            
            logger.info(f"✅ Cadrage terminé: {len(axes_juridiques)} axes, {len(complete_corpus)} références")
            
            return {
                "axes_juridiques": [axe.dict() for axe in axes_juridiques],
                "corpus_legal": [article.dict() for article in complete_corpus],
                "stats": {
                    "total_axes": len(axes_juridiques),
                    "articles_legifrance": len(corpus_legal),
                    "decisions_judilibre": len(jurisprudence),
                    "total_references": len(complete_corpus)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dans le cadrage juridique: {e}")
            return {"axes_juridiques": [], "corpus_legal": [], "error": str(e)}
    
    async def _initialize_services(self):
        """Initialise les services juridiques et d'embedding"""
        try:
            if self.legal_service is None:
                self.legal_service = EnhancedLegifranceService()
                await self.legal_service.initialize()
                
            if self.embedding_service is None:
                self.embedding_service = UnifiedEmbeddingService()
                await self.embedding_service.initialize()
                
            logger.info("✅ Services juridiques initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation services: {e}")
            raise
    
    async def _analyze_legal_issues(self, narration: Dict[str, Any]) -> List[HypotheseRecherche]:
        """
        Analyse la narration pour identifier les problématiques juridiques
        """
        try:
            axes_juridiques = []
            
            # Extraction du contenu de la narration
            segments = narration.get("segments", [])
            full_text = " ".join([seg.get("contenu", "") for seg in segments])
            
            # Mots-clés spécifiques au droit des étrangers
            legal_keywords = {
                "OQTF": {
                    "domaine": "Droit des étrangers",
                    "sous_domaine": "Obligation de quitter le territoire",
                    "urgence": "haute",
                    "codes": ["CESEDA"]
                },
                "reconduite": {
                    "domaine": "Droit des étrangers", 
                    "sous_domaine": "Mesures d'éloignement",
                    "urgence": "haute",
                    "codes": ["CESEDA"]
                },
                "titre de séjour": {
                    "domaine": "Droit des étrangers",
                    "sous_domaine": "Autorisation de séjour",
                    "urgence": "moyenne",
                    "codes": ["CESEDA"]
                },
                "regroupement familial": {
                    "domaine": "Droit des étrangers",
                    "sous_domaine": "Vie privée et familiale",
                    "urgence": "moyenne",
                    "codes": ["CESEDA"]
                },
                "naturalisation": {
                    "domaine": "Droit des étrangers",
                    "sous_domaine": "Acquisition de nationalité",
                    "urgence": "faible",
                    "codes": ["CESEDA", "Code civil"]
                },
                "rétention": {
                    "domaine": "Droit des étrangers",
                    "sous_domaine": "Mesures privatives de liberté",
                    "urgence": "très haute",
                    "codes": ["CESEDA", "CJA"]
                }
            }
            
            # Détection des problématiques dans le texte
            detected_issues = []
            for keyword, config in legal_keywords.items():
                if keyword.lower() in full_text.lower():
                    detected_issues.append((keyword, config))
            
            # Si aucun mot-clé spécifique détecté, analyse sémantique
            if not detected_issues:
                detected_issues = await self._semantic_legal_analysis(full_text)
            
            # Création des axes juridiques
            for i, (issue, config) in enumerate(detected_issues):
                axe = HypotheseRecherche(
                    id=f"axe_{i+1}",
                    domaine_juridique=config["domaine"],
                    sous_domaine=config["sous_domaine"],
                    mots_cles=[issue] + self._extract_related_keywords(full_text, issue),
                    niveau_urgence=config["urgence"],
                    codes_applicables=config["codes"],
                    articles_potentiels=[],
                    score_pertinence=0.9 if issue.lower() in full_text.lower() else 0.7
                )
                axes_juridiques.append(axe)
            
            logger.info(f"📋 {len(axes_juridiques)} axes juridiques identifiés")
            return axes_juridiques
            
        except Exception as e:
            logger.error(f"Erreur analyse problématiques juridiques: {e}")
            return []
    
    async def _semantic_legal_analysis(self, text: str) -> List[tuple]:
        """Analyse sémantique pour détecter les problématiques juridiques"""
        try:
            # Utilisation des embeddings pour une analyse sémantique
            text_embedding = await self.embedding_service.embed_for_agent(
                agent_id="cadreur_juridique",
                text=text,
                context_type="case_narrative"
            )
            
            # Références juridiques types pour comparaison
            legal_references = [
                "Obligation de quitter le territoire français OQTF reconduite frontière",
                "Titre de séjour autorisation séjour régularisation",
                "Regroupement familial vie privée familiale article 8 CEDH",
                "Rétention administrative centre rétention liberté",
                "Naturalisation acquisition nationalité française intégration"
            ]
            
            # Calcul des similarités
            similarities = []
            for ref in legal_references:
                ref_embedding = await self.embedding_service.embed_for_agent(
                    agent_id="cadreur_juridique",
                    text=ref,
                    context_type="legal_knowledge"
                )
                
                similarity = await self.embedding_service.calculate_similarity(
                    text_embedding, ref_embedding
                )
                similarities.append((ref, similarity))
            
            # Sélection des références les plus similaires
            similarities.sort(key=lambda x: x[1], reverse=True)
            detected_issues = []
            
            for ref, score in similarities[:3]:  # Top 3
                if score > 0.6:  # Seuil de pertinence
                    if "OQTF" in ref:
                        detected_issues.append(("OQTF", {
                            "domaine": "Droit des étrangers",
                            "sous_domaine": "Obligation de quitter le territoire",
                            "urgence": "haute",
                            "codes": ["CESEDA"]
                        }))
                    elif "titre de séjour" in ref.lower():
                        detected_issues.append(("titre de séjour", {
                            "domaine": "Droit des étrangers",
                            "sous_domaine": "Autorisation de séjour", 
                            "urgence": "moyenne",
                            "codes": ["CESEDA"]
                        }))
            
            return detected_issues
            
        except Exception as e:
            logger.error(f"Erreur analyse sémantique: {e}")
            return []
    
    def _extract_related_keywords(self, text: str, main_keyword: str) -> List[str]:
        """Extrait les mots-clés connexes du texte"""
        related_keywords = []
        
        # Dictionnaire de mots-clés connexes
        keyword_relations = {
            "OQTF": ["reconduite", "frontière", "éloignement", "préfecture", "délai"],
            "reconduite": ["OQTF", "frontière", "escorte", "vol", "pays origine"],
            "titre de séjour": ["carte", "récépissé", "renouvellement", "préfecture"],
            "regroupement familial": ["conjoint", "enfant", "famille", "visa"],
            "rétention": ["centre", "CRA", "liberté", "juge", "48h"]
        }
        
        # Recherche des mots connexes dans le texte
        for keyword in keyword_relations.get(main_keyword, []):
            if keyword.lower() in text.lower():
                related_keywords.append(keyword)
        
        return related_keywords[:5]  # Limite à 5 mots-clés
    
    async def _build_legal_corpus(self, axes: List[HypotheseRecherche]) -> List[CodeArticle]:
        """
        Construit le corpus légal en recherchant les articles pertinents
        """
        try:
            corpus_legal = []
            
            for axe in axes:
                # Recherche pour chaque code applicable
                for code_name in axe.codes_applicables:
                    # Construction de la requête de recherche
                    query = " ".join(axe.mots_cles)
                    
                    # Recherche via Légifrance
                    results = await self.legal_service.search_legal_articles(
                        query=query,
                        code_name=code_name,
                        max_results=self.agent_config["max_results"]
                    )
                    
                    # Conversion en CodeArticle
                    for result in results:
                        article = CodeArticle(
                            id=result.id,
                            code=code_name,
                            numero=self._extract_article_number(result.title),
                            titre=result.title,
                            contenu=result.content,
                            url_legifrance=result.url,
                            date_version=result.date,
                            pertinence=result.relevance_score,
                            axe_juridique_id=axe.id
                        )
                        corpus_legal.append(article)
            
            # Déduplication par ID
            seen_ids = set()
            unique_corpus = []
            for article in corpus_legal:
                if article.id not in seen_ids:
                    seen_ids.add(article.id)
                    unique_corpus.append(article)
            
            logger.info(f"📚 {len(unique_corpus)} articles uniques trouvés")
            return unique_corpus
            
        except Exception as e:
            logger.error(f"Erreur construction corpus légal: {e}")
            return []
    
    async def _search_relevant_jurisprudence(self, axes: List[HypotheseRecherche]) -> List[CodeArticle]:
        """
        Recherche la jurisprudence pertinente via Judilibre
        """
        try:
            jurisprudence = []
            config = self.agent_config["judilibre_filters"]
            
            for axe in axes:
                # Construction des filtres de recherche
                filters = SearchFilters(
                    query=" ".join(axe.mots_cles),
                    jurisdiction=config["jurisdiction"],
                    theme=config.get("theme", []),
                    publication=config["publication"],
                    field=config["field"],
                    page_size=5,  # Limite pour éviter la surcharge
                    sort="pertinence",
                    order="desc"
                )
                
                # Recherche via Judilibre
                results = await self.legal_service.search_jurisprudence(filters)
                
                # Conversion en CodeArticle (réutilisation du modèle)
                for result in results:
                    decision = CodeArticle(
                        id=result.id,
                        code="JURISPRUDENCE",
                        numero=result.id,
                        titre=result.title,
                        contenu=result.content,
                        url_legifrance=result.url,
                        date_version=result.date,
                        pertinence=result.relevance_score,
                        axe_juridique_id=axe.id,
                        metadata={
                            "source": result.source,
                            "jurisdiction": result.jurisdiction,
                            "chamber": result.chamber,
                            "type": result.type,
                            "metadata": result.metadata
                        }
                    )
                    jurisprudence.append(decision)
            
            logger.info(f"⚖️ {len(jurisprudence)} décisions jurisprudentielles trouvées")
            return jurisprudence
            
        except Exception as e:
            logger.error(f"Erreur recherche jurisprudence: {e}")
            return []
    
    def _extract_article_number(self, title: str) -> str:
        """Extrait le numéro d'article du titre"""
        import re
        
        # Recherche de patterns comme "Article L511-1", "Art. R123-4", etc.
        patterns = [
            r"Article\s+([LRD]?\d+(?:-\d+)*)",
            r"Art\.\s+([LRD]?\d+(?:-\d+)*)",
            r"([LRD]?\d+(?:-\d+)*)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "N/A"
    
    async def close(self):
        """Ferme les services"""
        if self.legal_service:
            await self.legal_service.close()
