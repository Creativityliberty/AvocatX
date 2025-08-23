"""
Service d'intégration avancé avec l'API Légifrance et Judilibre
Basé sur la documentation officielle et les spécifications OpenAPI
Optimisé pour les agents DEFENSEUR-IA (cadreur_juridique, recherche_web, etc.)
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum
import json

from ..config.settings import settings

logger = logging.getLogger(__name__)

class JurisdictionType(Enum):
    """Types de juridictions Judilibre"""
    COUR_CASSATION = "cc"
    COUR_APPEL = "ca"
    TRIBUNAL_JUDICIAIRE = "tj"

class DecisionType(Enum):
    """Types de décisions Judilibre"""
    ARRET = "arret"
    QPC = "qpc"
    ORDONNANCE = "ordonnance"
    SAISIE = "saisie"

class PublicationLevel(Enum):
    """Niveaux de publication Judilibre"""
    BULLETIN = "b"
    RAPPORT = "r"
    LETTRE = "l"
    COMMUNIQUE = "c"

class SolutionType(Enum):
    """Types de solutions Judilibre"""
    ANNULATION = "annulation"
    AVIS = "avis"
    CASSATION = "cassation"
    DECHEANCE = "decheance"
    DESIGNATION = "designation"
    IRRECEVABILITE = "irrecevabilite"
    NONLIEU = "nonlieu"
    QPC = "qpc"
    RABAT = "rabat"

@dataclass
class LegalSearchResult:
    """Résultat de recherche juridique unifié"""
    id: str
    title: str
    content: str
    url: str
    source: str  # "legifrance" ou "judilibre"
    type: str
    jurisdiction: Optional[str] = None
    chamber: Optional[str] = None
    date: Optional[str] = None
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class SearchFilters:
    """Filtres de recherche pour Judilibre"""
    query: str
    jurisdiction: Optional[List[str]] = None
    type: Optional[List[str]] = None
    theme: Optional[List[str]] = None
    chamber: Optional[List[str]] = None
    formation: Optional[List[str]] = None
    location: Optional[List[str]] = None
    publication: Optional[List[str]] = None
    solution: Optional[List[str]] = None
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    field: Optional[List[str]] = None
    operator: str = "and"
    sort: str = "date"
    order: str = "desc"
    page_size: int = 10
    page: int = 0

class EnhancedLegifranceService:
    """Service d'accès unifié aux APIs Légifrance et Judilibre"""
    
    def __init__(self):
        self.legifrance_base_url = "https://api.aife.economie.gouv.fr"
        self.judilibre_base_url = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0"
        self.legifrance_token = None
        self.judilibre_token = None
        self.session = None
        self.taxonomies_cache = {}
        
    async def initialize(self):
        """Initialise le service avec authentification"""
        try:
            self.session = aiohttp.ClientSession()
            await self._authenticate_legifrance()
            await self._authenticate_judilibre()
            await self._load_taxonomies()
            logger.info("✅ Service Légifrance/Judilibre initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation service juridique: {e}")
            raise
    
    async def close(self):
        """Ferme la session HTTP"""
        if self.session:
            await self.session.close()
    
    async def _authenticate_legifrance(self):
        """Authentification OAuth2 Légifrance"""
        try:
            if not settings.LEGIFRANCE_API_KEY or not settings.LEGIFRANCE_API_SECRET:
                logger.warning("⚠️ Clés API Légifrance manquantes, utilisation du mode mock")
                return
            
            auth_url = f"{self.legifrance_base_url}/oauth/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": settings.LEGIFRANCE_API_KEY,
                "client_secret": settings.LEGIFRANCE_API_SECRET,
                "scope": "openid"
            }
            
            async with self.session.post(auth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.legifrance_token = token_data.get("access_token")
                    logger.info("✅ Authentification Légifrance réussie")
                else:
                    logger.warning(f"⚠️ Échec authentification Légifrance: {response.status}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur authentification Légifrance: {e}")
    
    async def _authenticate_judilibre(self):
        """Authentification Judilibre (API Key ou OAuth)"""
        try:
            # Pour Judilibre, l'authentification se fait via headers
            # Pas de token à récupérer, juste validation des clés
            if not hasattr(settings, 'JUDILIBRE_API_KEY'):
                logger.warning("⚠️ Clé API Judilibre manquante, utilisation du mode mock")
                return
            
            # Test de connectivité avec endpoint stats
            test_url = f"{self.judilibre_base_url}/stats"
            headers = {
                "X-API-KEY": getattr(settings, 'JUDILIBRE_API_KEY', ''),
                "Accept": "application/json"
            }
            
            async with self.session.get(test_url, headers=headers) as response:
                if response.status == 200:
                    logger.info("✅ Connexion Judilibre validée")
                else:
                    logger.warning(f"⚠️ Échec connexion Judilibre: {response.status}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur connexion Judilibre: {e}")
    
    async def _load_taxonomies(self):
        """Charge les taxonomies Judilibre pour les filtres"""
        try:
            taxonomy_url = f"{self.judilibre_base_url}/taxonomy"
            headers = {
                "X-API-KEY": getattr(settings, 'JUDILIBRE_API_KEY', ''),
                "Accept": "application/json"
            }
            
            # Chargement des principales taxonomies
            taxonomies_to_load = [
                "type", "jurisdiction", "chamber", "formation", 
                "publication", "theme", "solution", "field"
            ]
            
            for taxonomy_id in taxonomies_to_load:
                try:
                    url = f"{taxonomy_url}?id={taxonomy_id}"
                    async with self.session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.taxonomies_cache[taxonomy_id] = data.get("result", [])
                            logger.debug(f"Taxonomie {taxonomy_id} chargée: {len(self.taxonomies_cache[taxonomy_id])} entrées")
                except Exception as e:
                    logger.warning(f"Erreur chargement taxonomie {taxonomy_id}: {e}")
            
            logger.info(f"✅ {len(self.taxonomies_cache)} taxonomies Judilibre chargées")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement taxonomies: {e}")
    
    async def search_legal_articles(
        self,
        query: str,
        code_name: str = "CESEDA",
        max_results: int = 10
    ) -> List[LegalSearchResult]:
        """
        Recherche d'articles de loi via Légifrance
        Optimisé pour les besoins DEFENSEUR-IA (OQTF, droit des étrangers)
        """
        try:
            logger.info(f"🔍 Recherche articles Légifrance: '{query}' dans {code_name}")
            
            if not self.legifrance_token:
                return self._mock_legifrance_search(query, code_name, max_results)
            
            search_url = f"{self.legifrance_base_url}/dila/legifrance/lf-engine-app/search"
            headers = {
                "Authorization": f"Bearer {self.legifrance_token}",
                "Content-Type": "application/json"
            }
            
            # Paramètres de recherche optimisés pour le droit des étrangers
            search_params = {
                "query": query,
                "searchType": "code",
                "codeName": code_name,
                "pageSize": max_results,
                "sort": "PERTINENCE",
                "filters": {
                    "themes": ["droit des étrangers", "OQTF", "reconduite à la frontière"],
                    "types": ["article", "section"]
                }
            }
            
            async with self.session.post(search_url, headers=headers, json=search_params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = self._parse_legifrance_results(data, "legifrance")
                    logger.info(f"✅ {len(results)} articles trouvés sur Légifrance")
                    return results
                else:
                    logger.warning(f"⚠️ Erreur recherche Légifrance: {response.status}")
                    return self._mock_legifrance_search(query, code_name, max_results)
                    
        except Exception as e:
            logger.error(f"Erreur recherche articles Légifrance: {e}")
            return self._mock_legifrance_search(query, code_name, max_results)
    
    async def search_jurisprudence(
        self,
        filters: SearchFilters
    ) -> List[LegalSearchResult]:
        """
        Recherche de jurisprudence via Judilibre
        Avec filtres avancés selon la documentation OpenAPI
        """
        try:
            logger.info(f"🔍 Recherche jurisprudence Judilibre: '{filters.query}'")
            
            if not hasattr(settings, 'JUDILIBRE_API_KEY'):
                return self._mock_judilibre_search(filters)
            
            search_url = f"{self.judilibre_base_url}/search"
            headers = {
                "X-API-KEY": getattr(settings, 'JUDILIBRE_API_KEY', ''),
                "Accept": "application/json"
            }
            
            # Construction des paramètres selon l'API Judilibre
            params = {
                "query": filters.query,
                "operator": filters.operator,
                "sort": filters.sort,
                "order": filters.order,
                "page_size": filters.page_size,
                "page": filters.page
            }
            
            # Ajout des filtres optionnels
            if filters.jurisdiction:
                params["jurisdiction"] = filters.jurisdiction
            if filters.type:
                params["type"] = filters.type
            if filters.theme:
                params["theme"] = filters.theme
            if filters.chamber:
                params["chamber"] = filters.chamber
            if filters.formation:
                params["formation"] = filters.formation
            if filters.location:
                params["location"] = filters.location
            if filters.publication:
                params["publication"] = filters.publication
            if filters.solution:
                params["solution"] = filters.solution
            if filters.date_start:
                params["date_start"] = filters.date_start.isoformat()
            if filters.date_end:
                params["date_end"] = filters.date_end.isoformat()
            if filters.field:
                params["field"] = filters.field
            
            async with self.session.get(search_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = self._parse_judilibre_results(data)
                    logger.info(f"✅ {len(results)} décisions trouvées sur Judilibre")
                    return results
                else:
                    logger.warning(f"⚠️ Erreur recherche Judilibre: {response.status}")
                    return self._mock_judilibre_search(filters)
                    
        except Exception as e:
            logger.error(f"Erreur recherche jurisprudence Judilibre: {e}")
            return self._mock_judilibre_search(filters)
    
    async def get_judilibre_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques Judilibre"""
        try:
            stats_url = f"{self.judilibre_base_url}/stats"
            headers = {
                "X-API-KEY": getattr(settings, 'JUDILIBRE_API_KEY', ''),
                "Accept": "application/json"
            }
            
            async with self.session.get(stats_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Status {response.status}"}
                    
        except Exception as e:
            logger.error(f"Erreur récupération stats Judilibre: {e}")
            return {"error": str(e)}
    
    def get_taxonomy(self, taxonomy_id: str, key: str = None) -> Union[List[Dict], str, None]:
        """Récupère une taxonomie ou une valeur spécifique"""
        taxonomy = self.taxonomies_cache.get(taxonomy_id, [])
        
        if key:
            # Recherche d'une clé spécifique
            for item in taxonomy:
                if item.get("key") == key:
                    return item.get("value")
            return None
        
        return taxonomy
    
    def _parse_legifrance_results(self, data: Dict[str, Any], source: str) -> List[LegalSearchResult]:
        """Parse les résultats Légifrance"""
        results = []
        
        for item in data.get("results", []):
            result = LegalSearchResult(
                id=item.get("id", ""),
                title=item.get("title", ""),
                content=item.get("content", "")[:1000] + "...",
                url=item.get("url", ""),
                source=source,
                type=item.get("type", "article"),
                date=item.get("date"),
                relevance_score=item.get("score", 0.0),
                metadata=item.get("metadata", {})
            )
            results.append(result)
        
        return results
    
    def _parse_judilibre_results(self, data: Dict[str, Any]) -> List[LegalSearchResult]:
        """Parse les résultats Judilibre"""
        results = []
        
        for item in data.get("results", []):
            result = LegalSearchResult(
                id=item.get("id", ""),
                title=item.get("title", ""),
                content=item.get("summary", "")[:1000] + "...",
                url=item.get("url", ""),
                source="judilibre",
                type=item.get("type", "arret"),
                jurisdiction=item.get("jurisdiction"),
                chamber=item.get("chamber"),
                date=item.get("date"),
                relevance_score=item.get("score", 0.0),
                metadata={
                    "formation": item.get("formation"),
                    "publication": item.get("publication"),
                    "solution": item.get("solution"),
                    "themes": item.get("themes", [])
                }
            )
            results.append(result)
        
        return results
    
    def _mock_legifrance_search(self, query: str, code_name: str, max_results: int) -> List[LegalSearchResult]:
        """Résultats mock Légifrance pour développement"""
        mock_results = []
        
        if "OQTF" in query.upper() or "reconduite" in query.lower():
            mock_results.append(LegalSearchResult(
                id="LEGIARTI000006335204",
                title="Article L511-1 du CESEDA",
                content="L'autorité administrative peut prononcer par arrêté motivé l'obligation pour un étranger de quitter le territoire français...",
                url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335204",
                source="legifrance_mock",
                type="article",
                date="2024-01-01",
                relevance_score=0.95
            ))
            
            mock_results.append(LegalSearchResult(
                id="LEGIARTI000006335206",
                title="Article L511-3 du CESEDA",
                content="L'obligation de quitter le territoire français peut être assortie d'une interdiction de retour...",
                url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335206",
                source="legifrance_mock",
                type="article",
                date="2024-01-01",
                relevance_score=0.88
            ))
        
        return mock_results[:max_results]
    
    def _mock_judilibre_search(self, filters: SearchFilters) -> List[LegalSearchResult]:
        """Résultats mock Judilibre pour développement"""
        mock_results = []
        
        if "OQTF" in filters.query.upper() or "étranger" in filters.query.lower():
            mock_results.append(LegalSearchResult(
                id="CETATEXT000047123456",
                title="CE, 1ère et 6ème sous-sections réunies, 15/04/2024, n°123456",
                content="Considérant que l'obligation de quitter le territoire français prononcée à l'encontre du requérant...",
                url="https://www.legifrance.gouv.fr/ceta/id/CETATEXT000047123456",
                source="judilibre_mock",
                type="arret",
                jurisdiction="ce",
                chamber="1ere_6eme_ssr",
                date="2024-04-15",
                relevance_score=0.92,
                metadata={
                    "formation": "sous_sections_reunies",
                    "publication": "r",
                    "solution": "annulation",
                    "themes": ["droit des étrangers", "OQTF"]
                }
            ))
        
        return mock_results

# Configuration spécialisée pour les agents DEFENSEUR-IA
AGENT_SEARCH_CONFIGS = {
    "cadreur_juridique": {
        "legifrance_codes": ["CESEDA", "CJA", "CPCE"],
        "judilibre_filters": {
            "jurisdiction": ["cc", "ce"],
            "theme": ["droit des étrangers", "contentieux administratif"],
            "publication": ["b", "r"],  # Bulletin et Rapport
            "field": ["title", "summary", "text"]
        },
        "max_results": 15
    },
    "recherche_web": {
        "legifrance_codes": ["CESEDA"],
        "judilibre_filters": {
            "jurisdiction": ["cc", "ce", "ca"],
            "type": ["arret", "ordonnance"],
            "publication": ["b", "r", "l"],
            "field": ["title", "summary"]
        },
        "max_results": 10
    },
    "juriste_matching": {
        "legifrance_codes": ["CESEDA", "CJA"],
        "judilibre_filters": {
            "jurisdiction": ["cc", "ce"],
            "solution": ["cassation", "annulation", "irrecevabilite"],
            "field": ["title", "summary", "text"]
        },
        "max_results": 20
    }
}
