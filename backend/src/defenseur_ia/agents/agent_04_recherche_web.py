"""
AGENT 4 - Recherche Web
Recherche complémentaire d'informations juridiques et jurisprudentielles
Utilise les APIs Légifrance/Judilibre et la recherche sémantique avancée
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import re
from urllib.parse import quote

from ..core.base import BaseNode, NodeContext
from ..models import HypotheseRecherche, CodeArticle, RessourceWeb
from ..services.enhanced_legifrance_service import (
    EnhancedLegifranceService, 
    SearchFilters, 
    AGENT_SEARCH_CONFIGS
)
from ..services.unified_embedding_service import UnifiedEmbeddingService
from ..services.semantic_search_service import SemanticSearchService

logger = logging.getLogger(__name__)

class RechercheWebNode(BaseNode):
    """
    Agent responsable de la recherche web complémentaire
    
    Inputs: axes_juridiques, corpus_legal
    Output: web_corpus (ressources web pertinentes)
    """
    
    def __init__(self):
        super().__init__("recherche_web", "Recherche Web")
        self.legal_service = None
        self.embedding_service = None
        self.semantic_search = None
        self.session = None
        self.agent_config = AGENT_SEARCH_CONFIGS["recherche_web"]
        
        # Sources web spécialisées en droit des étrangers
        self.specialized_sources = {
            "forums": [
                "https://www.village-justice.com",
                "https://www.net-iris.fr",
                "https://www.juristudiant.com"
            ],
            "associations": [
                "https://www.gisti.org",
                "https://www.lacimade.org",
                "https://www.anafe.org"
            ],
            "institutions": [
                "https://www.service-public.fr",
                "https://www.immigration.interieur.gouv.fr",
                "https://www.ofii.fr"
            ]
        }
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Recherche web complémentaire basée sur les axes juridiques
        """
        try:
            logger.info("🌐 Début de la recherche web complémentaire")
            
            # Récupération des données d'entrée
            axes_juridiques = context.shared_store.get("axes_juridiques", [])
            corpus_legal = context.shared_store.get("corpus_legal", [])
            
            if not axes_juridiques:
                logger.warning("Aucun axe juridique disponible pour la recherche web")
                return {"web_corpus": []}
            
            # Initialisation des services
            await self._initialize_services()
            
            # Recherche jurisprudentielle approfondie
            jurisprudence_results = await self._deep_jurisprudence_search(axes_juridiques)
            
            # Recherche dans les sources spécialisées
            specialized_results = await self._search_specialized_sources(axes_juridiques)
            
            # Recherche sémantique dans les bases existantes
            semantic_results = await self._semantic_web_search(axes_juridiques, corpus_legal)
            
            # Recherche de précédents similaires
            precedent_results = await self._search_similar_precedents(axes_juridiques)
            
            # Consolidation des résultats
            web_corpus = jurisprudence_results + specialized_results + semantic_results + precedent_results
            
            # Déduplication et scoring
            unique_corpus = await self._deduplicate_and_score(web_corpus)
            
            # Sauvegarde dans le store partagé
            context.shared_store.set("web_corpus", unique_corpus)
            
            logger.info(f"✅ Recherche web terminée: {len(unique_corpus)} ressources trouvées")
            
            return {
                "web_corpus": [resource.dict() for resource in unique_corpus],
                "stats": {
                    "total_sources": len(web_corpus),
                    "unique_resources": len(unique_corpus),
                    "jurisprudence": len(jurisprudence_results),
                    "specialized": len(specialized_results),
                    "semantic": len(semantic_results),
                    "precedents": len(precedent_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dans la recherche web: {e}")
            return {"web_corpus": [], "error": str(e)}
    
    async def _initialize_services(self):
        """Initialise les services de recherche"""
        try:
            if self.legal_service is None:
                self.legal_service = EnhancedLegifranceService()
                await self.legal_service.initialize()
                
            if self.embedding_service is None:
                self.embedding_service = UnifiedEmbeddingService()
                await self.embedding_service.initialize()
                
            if self.semantic_search is None:
                self.semantic_search = SemanticSearchService(self.embedding_service)
                await self.semantic_search.initialize()
                
            if self.session is None:
                self.session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={'User-Agent': 'DEFENSEUR-IA Legal Research Bot 1.0'}
                )
                
            logger.info("✅ Services de recherche initialisés")
        except Exception as e:
            logger.error(f"Erreur initialisation services: {e}")
            raise
    
    async def _deep_jurisprudence_search(self, axes: List[Dict[str, Any]]) -> List[RessourceWeb]:
        """
        Recherche jurisprudentielle approfondie via Judilibre
        """
        try:
            jurisprudence_resources = []
            config = self.agent_config["judilibre_filters"]
            
            for axe in axes:
                # Construction de requêtes multiples pour chaque axe
                queries = self._build_jurisprudence_queries(axe)
                
                for query in queries:
                    # Filtres spécialisés pour la recherche web
                    filters = SearchFilters(
                        query=query,
                        jurisdiction=config["jurisdiction"],
                        theme=config.get("theme", []),
                        publication=config["publication"],
                        field=config["field"],
                        page_size=10,  # Plus de résultats pour la recherche web
                        sort="pertinence",
                        order="desc",
                        date_start="2020-01-01",  # Jurisprudence récente
                        date_end=datetime.now().strftime("%Y-%m-%d")
                    )
                    
                    # Recherche via Judilibre
                    results = await self.legal_service.search_jurisprudence(filters)
                    
                    # Conversion en RessourceWeb
                    for result in results:
                        resource = RessourceWeb(
                            id=f"juris_{result.id}",
                            titre=result.title,
                            url=result.url,
                            source="Judilibre",
                            type_contenu="jurisprudence",
                            contenu=result.content,
                            date_publication=result.date,
                            pertinence=result.relevance_score,
                            mots_cles=axe.get("mots_cles", []),
                            axe_juridique_id=axe.get("id"),
                            metadata={
                                "jurisdiction": result.jurisdiction,
                                "chamber": result.chamber,
                                "decision_type": result.type,
                                "query_used": query
                            }
                        )
                        jurisprudence_resources.append(resource)
            
            logger.info(f"⚖️ {len(jurisprudence_resources)} décisions jurisprudentielles trouvées")
            return jurisprudence_resources
            
        except Exception as e:
            logger.error(f"Erreur recherche jurisprudentielle: {e}")
            return []
    
    def _build_jurisprudence_queries(self, axe: Dict[str, Any]) -> List[str]:
        """Construit des requêtes spécialisées pour la jurisprudence"""
        base_keywords = axe.get("mots_cles", [])
        domain = axe.get("domaine_juridique", "")
        subdomain = axe.get("sous_domaine", "")
        
        queries = []
        
        # Requête principale
        main_query = " ".join(base_keywords[:3])  # Limite à 3 mots-clés principaux
        queries.append(main_query)
        
        # Requêtes spécialisées selon le domaine
        if "OQTF" in main_query.upper():
            queries.extend([
                "OQTF reconduite frontière délai",
                "obligation quitter territoire motifs",
                "OQTF vie privée familiale article 8"
            ])
        elif "titre de séjour" in main_query.lower():
            queries.extend([
                "titre séjour renouvellement refus",
                "carte résident conditions",
                "régularisation situation administrative"
            ])
        elif "regroupement familial" in main_query.lower():
            queries.extend([
                "regroupement familial conditions ressources",
                "visa famille conjoint",
                "vie privée familiale CEDH"
            ])
        
        return queries[:5]  # Limite à 5 requêtes par axe
    
    async def _search_specialized_sources(self, axes: List[Dict[str, Any]]) -> List[RessourceWeb]:
        """
        Recherche dans les sources spécialisées (associations, forums)
        """
        try:
            specialized_resources = []
            
            for axe in axes:
                keywords = axe.get("mots_cles", [])
                search_terms = " ".join(keywords[:2])  # 2 mots-clés principaux
                
                # Recherche dans chaque type de source
                for source_type, urls in self.specialized_sources.items():
                    for base_url in urls:
                        try:
                            # Construction de l'URL de recherche (approximative)
                            search_url = f"{base_url}/search?q={quote(search_terms)}"
                            
                            # Simulation de recherche (en production, utiliser des APIs spécifiques)
                            resource = await self._simulate_specialized_search(
                                base_url, search_terms, source_type, axe
                            )
                            
                            if resource:
                                specialized_resources.append(resource)
                                
                        except Exception as e:
                            logger.warning(f"Erreur recherche {base_url}: {e}")
                            continue
            
            logger.info(f"🔍 {len(specialized_resources)} ressources spécialisées trouvées")
            return specialized_resources
            
        except Exception as e:
            logger.error(f"Erreur recherche sources spécialisées: {e}")
            return []
    
    async def _simulate_specialized_search(self, base_url: str, terms: str, source_type: str, axe: Dict[str, Any]) -> Optional[RessourceWeb]:
        """
        Simule une recherche dans une source spécialisée
        (En production, remplacer par de vraies requêtes HTTP ou APIs)
        """
        try:
            # Données simulées basées sur la source
            if "gisti.org" in base_url:
                return RessourceWeb(
                    id=f"gisti_{hash(terms)}",
                    titre=f"Guide GISTI: {terms}",
                    url=f"{base_url}/spip.php?article123",
                    source="GISTI",
                    type_contenu="guide_pratique",
                    contenu=f"Guide pratique sur {terms} - Informations détaillées sur les droits et procédures.",
                    date_publication=datetime.now().strftime("%Y-%m-%d"),
                    pertinence=0.8,
                    mots_cles=axe.get("mots_cles", []),
                    axe_juridique_id=axe.get("id"),
                    metadata={"source_type": source_type, "organization": "GISTI"}
                )
            elif "lacimade.org" in base_url:
                return RessourceWeb(
                    id=f"cimade_{hash(terms)}",
                    titre=f"Fiche pratique La Cimade: {terms}",
                    url=f"{base_url}/nos-actions/fiche-pratique-{terms.replace(' ', '-')}",
                    source="La Cimade",
                    type_contenu="fiche_pratique",
                    contenu=f"Fiche pratique détaillée sur {terms} avec conseils et démarches.",
                    date_publication=datetime.now().strftime("%Y-%m-%d"),
                    pertinence=0.75,
                    mots_cles=axe.get("mots_cles", []),
                    axe_juridique_id=axe.get("id"),
                    metadata={"source_type": source_type, "organization": "La Cimade"}
                )
            elif "service-public.fr" in base_url:
                return RessourceWeb(
                    id=f"servicepublic_{hash(terms)}",
                    titre=f"Service-public.fr: {terms}",
                    url=f"{base_url}/particuliers/vosdroits/F123",
                    source="Service-public.fr",
                    type_contenu="information_officielle",
                    contenu=f"Information officielle sur {terms} - Démarches et conditions.",
                    date_publication=datetime.now().strftime("%Y-%m-%d"),
                    pertinence=0.9,
                    mots_cles=axe.get("mots_cles", []),
                    axe_juridique_id=axe.get("id"),
                    metadata={"source_type": source_type, "official": True}
                )
            
            return None
            
        except Exception as e:
            logger.warning(f"Erreur simulation recherche {base_url}: {e}")
            return None
    
    async def _semantic_web_search(self, axes: List[Dict[str, Any]], corpus_legal: List[Dict[str, Any]]) -> List[RessourceWeb]:
        """
        Recherche sémantique dans les bases de connaissances existantes
        """
        try:
            semantic_resources = []
            
            # Construction d'un index sémantique des articles existants
            documents = []
            for article in corpus_legal:
                doc_text = f"{article.get('titre', '')} {article.get('contenu', '')}"
                documents.append({
                    "id": article.get("id"),
                    "text": doc_text,
                    "metadata": article
                })
            
            # Indexation des documents
            if documents:
                await self.semantic_search.index_documents(documents, "legal_corpus")
            
            # Recherche sémantique pour chaque axe
            for axe in axes:
                query = " ".join(axe.get("mots_cles", []))
                
                # Recherche dense (embeddings)
                dense_results = await self.semantic_search.dense_search(
                    query=query,
                    index_name="legal_corpus",
                    top_k=5
                )
                
                # Recherche sparse (mots-clés)
                sparse_results = await self.semantic_search.sparse_search(
                    query=query,
                    index_name="legal_corpus",
                    top_k=5
                )
                
                # Recherche cascading (combinée)
                cascading_results = await self.semantic_search.cascading_search(
                    query=query,
                    index_name="legal_corpus",
                    top_k=3
                )
                
                # Conversion des résultats en RessourceWeb
                all_results = dense_results + sparse_results + cascading_results
                for result in all_results:
                    resource = RessourceWeb(
                        id=f"semantic_{result['id']}",
                        titre=f"Analyse sémantique: {result['metadata'].get('titre', 'Document')}",
                        url=result['metadata'].get('url_legifrance', '#'),
                        source="Analyse sémantique",
                        type_contenu="analyse_semantique",
                        contenu=result['text'][:500] + "...",
                        date_publication=datetime.now().strftime("%Y-%m-%d"),
                        pertinence=result['score'],
                        mots_cles=axe.get("mots_cles", []),
                        axe_juridique_id=axe.get("id"),
                        metadata={
                            "search_type": result.get("search_type", "unknown"),
                            "original_article_id": result['metadata'].get('id')
                        }
                    )
                    semantic_resources.append(resource)
            
            logger.info(f"🧠 {len(semantic_resources)} ressources sémantiques trouvées")
            return semantic_resources
            
        except Exception as e:
            logger.error(f"Erreur recherche sémantique: {e}")
            return []
    
    async def _search_similar_precedents(self, axes: List[Dict[str, Any]]) -> List[RessourceWeb]:
        """
        Recherche de précédents similaires via embeddings
        """
        try:
            precedent_resources = []
            
            for axe in axes:
                # Construction de la requête de précédents
                precedent_query = self._build_precedent_query(axe)
                
                # Embedding de la requête
                query_embedding = await self.embedding_service.embed_for_agent(
                    agent_id="recherche_web",
                    text=precedent_query,
                    context_type="case_search"
                )
                
                # Recherche de cas similaires (simulation avec des cas types)
                similar_cases = await self._find_similar_cases(query_embedding, axe)
                
                # Conversion en ressources web
                for case in similar_cases:
                    resource = RessourceWeb(
                        id=f"precedent_{case['id']}",
                        titre=f"Précédent similaire: {case['title']}",
                        url=case.get('url', '#'),
                        source="Base de précédents",
                        type_contenu="precedent",
                        contenu=case['description'],
                        date_publication=case.get('date', datetime.now().strftime("%Y-%m-%d")),
                        pertinence=case['similarity_score'],
                        mots_cles=axe.get("mots_cles", []),
                        axe_juridique_id=axe.get("id"),
                        metadata={
                            "case_type": case.get('type'),
                            "outcome": case.get('outcome'),
                            "similarity_score": case['similarity_score']
                        }
                    )
                    precedent_resources.append(resource)
            
            logger.info(f"📚 {len(precedent_resources)} précédents similaires trouvés")
            return precedent_resources
            
        except Exception as e:
            logger.error(f"Erreur recherche précédents: {e}")
            return []
    
    def _build_precedent_query(self, axe: Dict[str, Any]) -> str:
        """Construit une requête pour rechercher des précédents"""
        domain = axe.get("domaine_juridique", "")
        subdomain = axe.get("sous_domaine", "")
        keywords = axe.get("mots_cles", [])
        
        return f"{domain} {subdomain} {' '.join(keywords[:3])}"
    
    async def _find_similar_cases(self, query_embedding: List[float], axe: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Trouve des cas similaires (simulation avec base de cas types)
        """
        # Cas types pour simulation (en production, utiliser une vraie base de données)
        case_templates = [
            {
                "id": "case_oqtf_001",
                "title": "OQTF avec vie privée et familiale",
                "description": "Cas d'OQTF contestée pour motif de vie privée et familiale, présence d'enfants français",
                "type": "OQTF",
                "outcome": "Annulation partielle",
                "keywords": ["OQTF", "vie privée", "enfants", "français"]
            },
            {
                "id": "case_titre_001", 
                "title": "Refus de renouvellement titre de séjour",
                "description": "Refus de renouvellement d'un titre de séjour pour insuffisance de ressources",
                "type": "Titre de séjour",
                "outcome": "Rejet confirmé",
                "keywords": ["titre", "séjour", "ressources", "renouvellement"]
            },
            {
                "id": "case_regroupement_001",
                "title": "Regroupement familial refusé",
                "description": "Demande de regroupement familial refusée pour conditions de logement",
                "type": "Regroupement familial",
                "outcome": "Annulation",
                "keywords": ["regroupement", "familial", "logement", "conditions"]
            }
        ]
        
        similar_cases = []
        axe_keywords = set(kw.lower() for kw in axe.get("mots_cles", []))
        
        for case in case_templates:
            case_keywords = set(kw.lower() for kw in case["keywords"])
            
            # Calcul de similarité simple basé sur les mots-clés communs
            common_keywords = axe_keywords.intersection(case_keywords)
            similarity_score = len(common_keywords) / max(len(axe_keywords), len(case_keywords), 1)
            
            if similarity_score > 0.3:  # Seuil de pertinence
                case["similarity_score"] = similarity_score
                similar_cases.append(case)
        
        # Tri par score de similarité
        similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_cases[:3]  # Top 3
    
    async def _deduplicate_and_score(self, resources: List[RessourceWeb]) -> List[RessourceWeb]:
        """
        Déduplique et score les ressources trouvées
        """
        try:
            # Déduplication par URL et titre
            seen = set()
            unique_resources = []
            
            for resource in resources:
                key = (resource.url, resource.titre)
                if key not in seen:
                    seen.add(key)
                    unique_resources.append(resource)
            
            # Scoring final basé sur la source et le type
            for resource in unique_resources:
                base_score = resource.pertinence
                
                # Bonus selon la source
                if resource.source in ["Judilibre", "Légifrance"]:
                    base_score += 0.2
                elif resource.source in ["Service-public.fr"]:
                    base_score += 0.15
                elif resource.source in ["GISTI", "La Cimade"]:
                    base_score += 0.1
                
                # Bonus selon le type de contenu
                if resource.type_contenu in ["jurisprudence", "information_officielle"]:
                    base_score += 0.1
                elif resource.type_contenu in ["guide_pratique", "fiche_pratique"]:
                    base_score += 0.05
                
                resource.pertinence = min(base_score, 1.0)  # Cap à 1.0
            
            # Tri par pertinence décroissante
            unique_resources.sort(key=lambda x: x.pertinence, reverse=True)
            
            # Limite le nombre de ressources
            max_resources = self.agent_config.get("max_results", 20)
            return unique_resources[:max_resources]
            
        except Exception as e:
            logger.error(f"Erreur déduplication/scoring: {e}")
            return resources
    
    async def close(self):
        """Ferme les services et sessions"""
        if self.legal_service:
            await self.legal_service.close()
        if self.session:
            await self.session.close()
