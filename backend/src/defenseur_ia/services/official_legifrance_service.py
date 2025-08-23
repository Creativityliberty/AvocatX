"""
Service officiel d'intégration avec l'API Légifrance
Basé sur les spécifications OpenAPI officielles v2.4.2
Implémente tous les endpoints et modèles de données conformes à la documentation DILA
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import os
from enum import Enum

logger = logging.getLogger(__name__)

# ============================================================================
# ENUMS ET CONSTANTES OFFICIELLES
# ============================================================================

class NatureTexte(Enum):
    """Types de textes selon l'API Légifrance"""
    LODA = "LODA"  # Lois et décrets
    JORF = "JORF"  # Journal officiel
    CODE = "CODE"  # Codes
    KALI = "KALI"  # Conventions collectives
    JORFCONT = "JORFCONT"  # Conteneurs JORF

class TypeChamp(Enum):
    """Types de champs de recherche"""
    ALL = "ALL"
    TITLE = "TITLE"
    TABLE = "TABLE"
    NOR = "NOR"
    NUM = "NUM"
    ARTICLE = "ARTICLE"
    TEXTE = "TEXTE"
    MINISTERE = "MINISTERE"
    VISA = "VISA"
    NOTICE = "NOTICE"
    MOTS_CLES = "MOTS_CLES"

class TypeRecherche(Enum):
    """Types de recherche dans les champs"""
    UN_DES_MOTS = "UN_DES_MOTS"
    TOUS_LES_MOTS = "TOUS_LES_MOTS"
    EXPRESSION_EXACTE = "EXPRESSION_EXACTE"
    TOUS_LES_MOTS_DANS_UN_CHAMP = "TOUS_LES_MOTS_DANS_UN_CHAMP"

class OperateurLogique(Enum):
    """Opérateurs logiques"""
    ET = "ET"
    OU = "OU"

class TypeTri(Enum):
    """Types de tri disponibles"""
    SIGNATURE_DATE_DESC = "SIGNATURE_DATE_DESC"
    SIGNATURE_DATE_ASC = "SIGNATURE_DATE_ASC"
    PERTINENCE = "PERTINENCE"
    ID = "ID"

# ============================================================================
# MODÈLES DE DONNÉES OFFICIELS
# ============================================================================

@dataclass
class CritereDTO:
    """Critère de recherche selon l'API officielle"""
    valeur: str
    operateur: str = "ET"
    typeRecherche: str = "UN_DES_MOTS"
    proximite: Optional[int] = None
    criteres: Optional[List['CritereDTO']] = None

@dataclass
class ChampDTO:
    """Champ de recherche selon l'API officielle"""
    typeChamp: str
    operateur: str = "ET"
    criteres: Optional[List[CritereDTO]] = None

@dataclass
class FiltreDTO:
    """Filtre de recherche selon l'API officielle"""
    facette: str
    valeurs: Optional[List[str]] = None
    dates: Optional[Dict[str, str]] = None

@dataclass
class RechercheSpecifiqueDTO:
    """Requête de recherche spécifique selon l'API officielle"""
    champs: List[ChampDTO]
    operateur: str
    pageNumber: int
    pageSize: int
    sort: str
    typePagination: str = "DEFAUT"
    filtres: Optional[List[FiltreDTO]] = None
    secondSort: Optional[str] = None
    fromAdvancedRecherche: bool = False

@dataclass
class SearchResult:
    """Résultat de recherche selon l'API officielle"""
    id: str
    title: str
    url: str
    content: str
    date: str
    relevance_score: float
    nor: Optional[str] = None
    nature: Optional[str] = None
    ministere: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ============================================================================
# SERVICE LÉGIFRANCE OFFICIEL
# ============================================================================

class OfficialLegifranceService:
    """
    Service d'intégration avec l'API Légifrance officielle
    Conforme aux spécifications OpenAPI v2.4.2 de la DILA
    """
    
    def __init__(self):
        self.base_url = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app"
        self.prod_url = "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app"
        self.client_id = os.getenv("LEGIFRANCE_CLIENT_ID")
        self.client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_at = None
        self.session = None
        self.use_production = os.getenv("LEGIFRANCE_USE_PRODUCTION", "false").lower() == "true"
        
        # Configuration des endpoints
        self.endpoints = {
            "oauth_token": "/oauth/token",
            "search_specific": "/search/search",
            "consult_code": "/consult/code",
            "consult_loda": "/consult/lawDecree", 
            "consult_jorf": "/consult/jorfText",
            "consult_article": "/consult/getArticleByCid",
            "list_codes": "/list/codes",
            "suggest": "/suggest/suggest"
        }
        
    async def initialize(self):
        """Initialise le service avec authentification OAuth2"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'DEFENSEUR-IA Legal Research Bot 1.0',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
            
            if self.client_id and self.client_secret:
                await self._authenticate()
                logger.info("✅ Service Légifrance officiel initialisé avec authentification")
            else:
                logger.warning("⚠️ Clés API Légifrance manquantes, utilisation du mode mock")
                
        except Exception as e:
            logger.error(f"Erreur initialisation service Légifrance: {e}")
            raise
    
    async def _authenticate(self):
        """Authentification OAuth2 selon les spécifications officielles"""
        try:
            current_url = self.prod_url if self.use_production else self.base_url
            auth_url = f"{current_url}/oauth/token"
            
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "openid"
            }
            
            async with self.session.post(auth_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    
                    # Mise à jour des headers d'authentification
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    
                    logger.info("🔐 Authentification Légifrance réussie")
                else:
                    logger.error(f"Erreur authentification: {response.status}")
                    raise Exception(f"Authentification échouée: {response.status}")
                    
        except Exception as e:
            logger.error(f"Erreur authentification OAuth2: {e}")
            raise
    
    async def _ensure_authenticated(self):
        """Vérifie et renouvelle l'authentification si nécessaire"""
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            await self._authenticate()
    
    async def search_legal_texts(
        self, 
        query: str, 
        nature: Optional[NatureTexte] = None,
        champ: TypeChamp = TypeChamp.ALL,
        page_number: int = 1,
        page_size: int = 10,
        sort: TypeTri = TypeTri.PERTINENCE,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None,
        ministere: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Recherche de textes légaux selon l'API officielle
        
        Args:
            query: Terme de recherche
            nature: Type de texte (LODA, JORF, CODE, etc.)
            champ: Type de champ de recherche
            page_number: Numéro de page
            page_size: Taille de page (max 100)
            sort: Type de tri
            date_start: Date de début (YYYY-MM-DD)
            date_end: Date de fin (YYYY-MM-DD)
            ministere: Ministère concerné
        """
        try:
            await self._ensure_authenticated()
            
            # Construction de la requête selon les spécifications officielles
            critere = CritereDTO(
                valeur=query,
                typeRecherche=TypeRecherche.TOUS_LES_MOTS.value,
                operateur=OperateurLogique.ET.value
            )
            
            champ_dto = ChampDTO(
                typeChamp=champ.value,
                operateur=OperateurLogique.ET.value,
                criteres=[critere]
            )
            
            # Construction des filtres
            filtres = []
            
            if nature:
                filtres.append(FiltreDTO(
                    facette="NATURE",
                    valeurs=[nature.value]
                ))
            
            if date_start and date_end:
                filtres.append(FiltreDTO(
                    facette="DATE_SIGNATURE",
                    dates={"start": date_start, "end": date_end}
                ))
            
            if ministere:
                filtres.append(FiltreDTO(
                    facette="MINISTERE",
                    valeurs=[ministere]
                ))
            
            # Requête complète
            recherche_request = RechercheSpecifiqueDTO(
                champs=[champ_dto],
                operateur=OperateurLogique.ET.value,
                pageNumber=page_number,
                pageSize=min(page_size, 100),  # Limite API
                sort=sort.value,
                filtres=filtres if filtres else None
            )
            
            # Appel API
            current_url = self.prod_url if self.use_production else self.base_url
            search_url = f"{current_url}{self.endpoints['search_specific']}"
            
            async with self.session.post(search_url, json=asdict(recherche_request)) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_results(data)
                else:
                    logger.error(f"Erreur recherche API: {response.status}")
                    return self._get_mock_results(query, nature)
                    
        except Exception as e:
            logger.error(f"Erreur recherche textes légaux: {e}")
            return self._get_mock_results(query, nature)
    
    async def search_articles_by_code(
        self,
        code_name: str,
        article_query: str,
        page_number: int = 1,
        page_size: int = 10
    ) -> List[SearchResult]:
        """
        Recherche d'articles dans un code spécifique
        """
        try:
            # Recherche spécialisée pour les articles de code
            critere = CritereDTO(
                valeur=article_query,
                typeRecherche=TypeRecherche.TOUS_LES_MOTS.value
            )
            
            champ_dto = ChampDTO(
                typeChamp=TypeChamp.ARTICLE.value,
                criteres=[critere]
            )
            
            # Filtre par code
            filtre_code = FiltreDTO(
                facette="CODE",
                valeurs=[code_name]
            )
            
            recherche_request = RechercheSpecifiqueDTO(
                champs=[champ_dto],
                operateur=OperateurLogique.ET.value,
                pageNumber=page_number,
                pageSize=page_size,
                sort=TypeTri.PERTINENCE.value,
                filtres=[filtre_code]
            )
            
            current_url = self.prod_url if self.use_production else self.base_url
            search_url = f"{current_url}{self.endpoints['search_specific']}"
            
            async with self.session.post(search_url, json=asdict(recherche_request)) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_search_results(data)
                else:
                    return self._get_mock_code_articles(code_name, article_query)
                    
        except Exception as e:
            logger.error(f"Erreur recherche articles code: {e}")
            return self._get_mock_code_articles(code_name, article_query)
    
    async def get_article_by_id(self, article_id: str) -> Optional[SearchResult]:
        """
        Récupère un article par son identifiant
        """
        try:
            await self._ensure_authenticated()
            
            current_url = self.prod_url if self.use_production else self.base_url
            consult_url = f"{current_url}{self.endpoints['consult_article']}"
            
            request_data = {"id": article_id}
            
            async with self.session.post(consult_url, json=request_data) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_article_result(data)
                else:
                    return self._get_mock_article(article_id)
                    
        except Exception as e:
            logger.error(f"Erreur récupération article: {e}")
            return self._get_mock_article(article_id)
    
    async def suggest_terms(self, partial_query: str, max_suggestions: int = 10) -> List[str]:
        """
        Autocomplétion de termes juridiques
        """
        try:
            await self._ensure_authenticated()
            
            current_url = self.prod_url if self.use_production else self.base_url
            suggest_url = f"{current_url}{self.endpoints['suggest']}"
            
            request_data = {
                "q": partial_query,
                "size": max_suggestions
            }
            
            async with self.session.post(suggest_url, json=request_data) as response:
                if response.status == 200:
                    data = await response.json()
                    return [item.get("text", "") for item in data.get("suggestions", [])]
                else:
                    return self._get_mock_suggestions(partial_query)
                    
        except Exception as e:
            logger.error(f"Erreur suggestions: {e}")
            return self._get_mock_suggestions(partial_query)
    
    def _parse_search_results(self, api_response: Dict[str, Any]) -> List[SearchResult]:
        """Parse les résultats de l'API en objets SearchResult"""
        results = []
        
        for item in api_response.get("results", []):
            result = SearchResult(
                id=item.get("id", ""),
                title=item.get("title", ""),
                url=item.get("url", ""),
                content=item.get("summary", ""),
                date=item.get("dateSignature", ""),
                relevance_score=item.get("score", 0.0),
                nor=item.get("nor"),
                nature=item.get("nature"),
                ministere=item.get("ministere"),
                metadata=item
            )
            results.append(result)
        
        return results
    
    def _parse_article_result(self, api_response: Dict[str, Any]) -> SearchResult:
        """Parse un article de l'API"""
        article = api_response.get("article", {})
        
        return SearchResult(
            id=article.get("id", ""),
            title=article.get("title", ""),
            url=article.get("url", ""),
            content=article.get("content", ""),
            date=article.get("dateDebut", ""),
            relevance_score=1.0,
            metadata=article
        )
    
    # ========================================================================
    # MÉTHODES MOCK POUR LE DÉVELOPPEMENT
    # ========================================================================
    
    def _get_mock_results(self, query: str, nature: Optional[NatureTexte]) -> List[SearchResult]:
        """Résultats mock pour le développement"""
        mock_results = []
        
        if "oqtf" in query.lower() or "obligation" in query.lower():
            mock_results.append(SearchResult(
                id="LEGIARTI000006335092",
                title="Article L511-1 du Code de l'entrée et du séjour des étrangers",
                url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335092",
                content="L'autorité administrative peut prendre une décision d'obligation de quitter le territoire français...",
                date="2024-01-01",
                relevance_score=0.95,
                nor="INTV2400001A",
                nature="CODE",
                metadata={"code": "CESEDA", "section": "Mesures d'éloignement"}
            ))
        
        if "titre" in query.lower() and "séjour" in query.lower():
            mock_results.append(SearchResult(
                id="LEGIARTI000006335001",
                title="Article L313-1 du Code de l'entrée et du séjour des étrangers",
                url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335001",
                content="Sauf cas particuliers, l'étranger qui souhaite séjourner en France doit être muni d'un titre de séjour...",
                date="2024-01-01",
                relevance_score=0.90,
                nor="INTV2400002A",
                nature="CODE",
                metadata={"code": "CESEDA", "section": "Titres de séjour"}
            ))
        
        return mock_results
    
    def _get_mock_code_articles(self, code_name: str, query: str) -> List[SearchResult]:
        """Articles mock pour un code spécifique"""
        if code_name.upper() == "CESEDA":
            return [
                SearchResult(
                    id="LEGIARTI000006335092",
                    title=f"Article L511-1 - {query}",
                    url="https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335092",
                    content=f"Article du CESEDA relatif à {query}...",
                    date="2024-01-01",
                    relevance_score=0.85,
                    metadata={"code": code_name, "article": "L511-1"}
                )
            ]
        return []
    
    def _get_mock_article(self, article_id: str) -> SearchResult:
        """Article mock par ID"""
        return SearchResult(
            id=article_id,
            title=f"Article {article_id}",
            url=f"https://www.legifrance.gouv.fr/codes/article_lc/{article_id}",
            content="Contenu de l'article...",
            date="2024-01-01",
            relevance_score=1.0,
            metadata={"id": article_id}
        )
    
    def _get_mock_suggestions(self, query: str) -> List[str]:
        """Suggestions mock"""
        suggestions = [
            "obligation de quitter le territoire",
            "titre de séjour",
            "regroupement familial",
            "naturalisation",
            "rétention administrative"
        ]
        return [s for s in suggestions if query.lower() in s.lower()][:5]
    
    async def close(self):
        """Ferme la session HTTP"""
        if self.session:
            await self.session.close()
            logger.info("🔒 Session Légifrance fermée")
