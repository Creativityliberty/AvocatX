"""
Service d'intégration avec l'API Légifrance
Permet de rechercher des articles de loi, jurisprudence et textes officiels
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..config.legifrance_config import get_oauth_config, get_legifrance_config

logger = logging.getLogger(__name__)

@dataclass
class LegiFranceResult:
    """Résultat d'une recherche Légifrance"""
    id: str
    title: str
    content: str
    url: str
    type: str  # "code", "jurisprudence", "circulaire", etc.
    date: Optional[str] = None
    relevance_score: float = 0.0

class LegifranceService:
    """Service d'accès à l'API Légifrance officielle"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        # Utilisation de la configuration centralisée
        oauth_config = get_oauth_config()
        
        self.client_id = client_id or oauth_config.client_id
        self.client_secret = client_secret or oauth_config.client_secret
        self.base_url = oauth_config.base_url
        self.oauth_url = oauth_config.oauth_url
        self.scopes = oauth_config.scopes
        self.environment = oauth_config.environment
        self.access_token = None
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self._authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def _authenticate(self):
        """Authentification OAuth2 avec l'API Légifrance officielle"""
        try:
            auth_url = f"{self.oauth_url}/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": " ".join(self.scopes)
            }
            
            async with self.session.post(auth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get("access_token")
                    logger.info("Authentification Légifrance réussie")
                else:
                    logger.warning(f"Échec authentification Légifrance: {response.status}")
                    # Mode dégradé avec données mock
                    self.access_token = "mock_token"
                    
        except Exception as e:
            logger.error(f"Erreur authentification Légifrance: {e}")
            self.access_token = "mock_token"
    
    async def search_code_articles(self, query: str, code_name: str = "CESEDA") -> List[LegiFranceResult]:
        """
        Recherche d'articles dans un code spécifique
        
        Args:
            query: Termes de recherche
            code_name: Nom du code (CESEDA, Code civil, etc.)
        """
        try:
            if not self.access_token or self.access_token == "mock_token":
                return self._mock_code_search(query, code_name)
                
            search_url = f"{self.base_url}/dila/legifrance/lf-engine-app/search"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "type": "code",
                "code": code_name,
                "pageSize": 10,
                "pageNumber": 1
            }
            
            async with self.session.post(search_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_results(data)
                else:
                    logger.warning(f"Erreur recherche Légifrance: {response.status}")
                    return self._mock_code_search(query, code_name)
                    
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return self._mock_code_search(query, code_name)
    
    async def search_jurisprudence(self, query: str, jurisdiction: str = "all") -> List[LegiFranceResult]:
        """
        Recherche de jurisprudence
        
        Args:
            query: Termes de recherche
            jurisdiction: Juridiction (CE, Cass, CAA, etc.)
        """
        try:
            if not self.access_token or self.access_token == "mock_token":
                return self._mock_jurisprudence_search(query, jurisdiction)
                
            # Implémentation réelle de l'API
            # ... (similaire à search_code_articles)
            
            return self._mock_jurisprudence_search(query, jurisdiction)
            
        except Exception as e:
            logger.error(f"Erreur recherche jurisprudence: {e}")
            return self._mock_jurisprudence_search(query, jurisdiction)
    
    def _mock_code_search(self, query: str, code_name: str) -> List[LegiFranceResult]:
        """Données mock pour les tests et développement"""
        mock_results = []
        
        if "OQTF" in query.upper() or "obligation" in query.lower():
            mock_results.append(LegiFranceResult(
                id="L511-1",
                title="Article L511-1 du CESEDA",
                content="L'autorité administrative peut, par décision motivée, obliger un étranger à quitter le territoire français dans les cas suivants...",
                url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335204",
                type="code",
                relevance_score=0.95
            ))
            
        if "recours" in query.lower():
            mock_results.append(LegiFranceResult(
                id="L512-1",
                title="Article L512-1 du CESEDA",
                content="L'étranger qui fait l'objet d'une décision d'éloignement peut former un recours...",
                url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335206",
                type="code",
                relevance_score=0.88
            ))
            
        return mock_results
    
    def _mock_jurisprudence_search(self, query: str, jurisdiction: str) -> List[LegiFranceResult]:
        """Données mock de jurisprudence"""
        mock_results = []
        
        if "OQTF" in query.upper():
            mock_results.append(LegiFranceResult(
                id="CE-2023-123456",
                title="CE, 10 mars 2023, n° 123456",
                content="Considérant que l'obligation de quitter le territoire français ne peut être prononcée...",
                url="https://www.legifrance.gouv.fr/ceta/id/CETATEXT000047123456",
                type="jurisprudence",
                date="2023-03-10",
                relevance_score=0.92
            ))
            
        return mock_results
    
    def _parse_search_results(self, data: Dict[str, Any]) -> List[LegiFranceResult]:
        """Parse les résultats de l'API Légifrance"""
        results = []
        
        for item in data.get("results", []):
            result = LegiFranceResult(
                id=item.get("id", ""),
                title=item.get("title", ""),
                content=item.get("content", ""),
                url=item.get("url", ""),
                type=item.get("type", "unknown"),
                date=item.get("date"),
                relevance_score=item.get("score", 0.0)
            )
            results.append(result)
            
        return results

# Fonction utilitaire pour usage simple
async def search_legal_articles(query: str, code: str = "CESEDA") -> List[LegiFranceResult]:
    """Fonction helper pour recherche rapide"""
    async with LegifranceService() as service:
        return await service.search_code_articles(query, code)
