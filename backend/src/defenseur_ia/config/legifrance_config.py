"""
Configuration centralisée pour l'intégration du service Légifrance officiel
Gère les paramètres OAuth2, les scopes et la configuration par agent
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from ..services.official_legifrance_service import NatureTexte, TypeChamp, TypeTri


class LegifranceEnvironment(Enum):
    """Environnements disponibles pour l'API Légifrance"""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


@dataclass
class OAuth2Config:
    """Configuration OAuth2 pour l'API Légifrance"""
    client_id: str
    client_secret: str
    scopes: List[str]
    environment: LegifranceEnvironment
    
    @property
    def base_url(self) -> str:
        if self.environment == LegifranceEnvironment.PRODUCTION:
            return "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app"
        return "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app"
    
    @property
    def oauth_url(self) -> str:
        if self.environment == LegifranceEnvironment.PRODUCTION:
            return "https://oauth.piste.gouv.fr/api/oauth"
        return "https://sandbox-oauth.piste.gouv.fr/api/oauth"


@dataclass
class AgentSearchConfig:
    """Configuration de recherche spécialisée par agent"""
    agent_id: str
    nature_textes_prioritaires: List[NatureTexte]
    champs_recherche: List[TypeChamp]
    tri_par_defaut: TypeTri
    max_results_per_query: int
    date_limite: Optional[str] = None
    filtres_specialises: Optional[Dict[str, any]] = None


class LegifranceConfigManager:
    """Gestionnaire de configuration centralisé pour Légifrance"""
    
    def __init__(self):
        self.oauth_config = self._load_oauth_config()
        self.agent_configs = self._load_agent_configs()
    
    def _load_oauth_config(self) -> OAuth2Config:
        """Charge la configuration OAuth2 depuis les variables d'environnement"""
        
        # Configuration par défaut fournie par l'utilisateur
        default_client_id = "contact@isais.fr"
        default_client_secret = "L@banane2025+"
        default_scopes = ["openid"]  # Scope sélectionné par défaut
        
        return OAuth2Config(
            client_id=os.getenv("LEGIFRANCE_CLIENT_ID", default_client_id),
            client_secret=os.getenv("LEGIFRANCE_CLIENT_SECRET", default_client_secret),
            scopes=os.getenv("LEGIFRANCE_SCOPES", ",".join(default_scopes)).split(","),
            environment=LegifranceEnvironment(
                os.getenv("LEGIFRANCE_ENVIRONMENT", "sandbox")
            )
        )
    
    def _load_agent_configs(self) -> Dict[str, AgentSearchConfig]:
        """Charge les configurations spécialisées par agent"""
        
        configs = {
            # Agent 1 - Cadreur Juridique
            "cadreur_juridique": AgentSearchConfig(
                agent_id="cadreur_juridique",
                nature_textes_prioritaires=[NatureTexte.CODE, NatureTexte.LODA],
                champs_recherche=[TypeChamp.ALL, TypeChamp.TEXTE],
                tri_par_defaut=TypeTri.PERTINENCE,
                max_results_per_query=15,
                date_limite="2020-01-01",
                filtres_specialises={
                    "codes_prioritaires": ["CESEDA", "CN", "CCiv"],
                    "focus_immigration": True
                }
            ),
            
            # Agent 4 - Recherche Web
            "recherche_web": AgentSearchConfig(
                agent_id="recherche_web",
                nature_textes_prioritaires=[NatureTexte.LODA, NatureTexte.JORF, NatureTexte.CODE],
                champs_recherche=[TypeChamp.ALL, TypeChamp.TEXTE, TypeChamp.TITLE],
                tri_par_defaut=TypeTri.PERTINENCE,
                max_results_per_query=10,
                date_limite="2020-01-01",
                filtres_specialises={
                    "recherche_etendue": True,
                    "include_jurisprudence": True
                }
            ),
            
            # Agent 7 - Relecteur IA #1
            "relecteur_ia_1": AgentSearchConfig(
                agent_id="relecteur_ia_1",
                nature_textes_prioritaires=[NatureTexte.CODE, NatureTexte.LODA],
                champs_recherche=[TypeChamp.ALL],
                tri_par_defaut=TypeTri.PERTINENCE,
                max_results_per_query=5,
                filtres_specialises={
                    "validation_references": True,
                    "precision_maximale": True
                }
            ),
            
            # Agent 10 - Synthèse Stratégique
            "synthese_strategique": AgentSearchConfig(
                agent_id="synthese_strategique",
                nature_textes_prioritaires=[NatureTexte.CODE, NatureTexte.LODA],
                champs_recherche=[TypeChamp.ALL, TypeChamp.TEXTE],
                tri_par_defaut=TypeTri.PERTINENCE,
                max_results_per_query=8,
                filtres_specialises={
                    "scoring_arguments": True,
                    "validation_juridique": True
                }
            ),
            
            # Agent 11 - Avocat IA (peut aussi bénéficier de la validation)
            "avocat_ia": AgentSearchConfig(
                agent_id="avocat_ia",
                nature_textes_prioritaires=[NatureTexte.CODE, NatureTexte.LODA, NatureTexte.JORF],
                champs_recherche=[TypeChamp.ALL, TypeChamp.TEXTE],
                tri_par_defaut=TypeTri.PERTINENCE,
                max_results_per_query=12,
                filtres_specialises={
                    "redaction_finale": True,
                    "precision_juridique": True
                }
            )
        }
        
        return configs
    
    def get_oauth_config(self) -> OAuth2Config:
        """Retourne la configuration OAuth2"""
        return self.oauth_config
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentSearchConfig]:
        """Retourne la configuration d'un agent spécifique"""
        return self.agent_configs.get(agent_id)
    
    def get_all_agent_configs(self) -> Dict[str, AgentSearchConfig]:
        """Retourne toutes les configurations d'agents"""
        return self.agent_configs
    
    def is_agent_enabled(self, agent_id: str) -> bool:
        """Vérifie si un agent est configuré pour utiliser Légifrance"""
        return agent_id in self.agent_configs
    
    def get_environment_info(self) -> Dict[str, str]:
        """Retourne les informations sur l'environnement configuré"""
        return {
            "environment": self.oauth_config.environment.value,
            "base_url": self.oauth_config.base_url,
            "oauth_url": self.oauth_config.oauth_url,
            "client_id": self.oauth_config.client_id,
            "scopes": ",".join(self.oauth_config.scopes)
        }
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Valide la configuration complète"""
        validation = {
            "oauth_valid": bool(self.oauth_config.client_id and self.oauth_config.client_secret),
            "scopes_valid": bool(self.oauth_config.scopes),
            "agents_configured": len(self.agent_configs) > 0,
            "environment_valid": self.oauth_config.environment in LegifranceEnvironment
        }
        
        validation["overall_valid"] = all(validation.values())
        return validation


# Instance globale du gestionnaire de configuration
legifrance_config = LegifranceConfigManager()


def get_legifrance_config() -> LegifranceConfigManager:
    """Fonction utilitaire pour accéder à la configuration"""
    return legifrance_config


def get_oauth_config() -> OAuth2Config:
    """Fonction utilitaire pour accéder à la config OAuth2"""
    return legifrance_config.get_oauth_config()


def get_agent_config(agent_id: str) -> Optional[AgentSearchConfig]:
    """Fonction utilitaire pour accéder à la config d'un agent"""
    return legifrance_config.get_agent_config(agent_id)


# Configuration par défaut pour les nouveaux agents
DEFAULT_AGENT_CONFIG = AgentSearchConfig(
    agent_id="default",
    nature_textes_prioritaires=[NatureTexte.CODE, NatureTexte.LODA],
    champs_recherche=[TypeChamp.ALL],
    tri_par_defaut=TypeTri.PERTINENCE,
    max_results_per_query=10,
    filtres_specialises={}
)


# Mapping des domaines juridiques vers les configurations optimales
DOMAIN_SPECIFIC_CONFIGS = {
    "oqtf": {
        "nature_textes": [NatureTexte.CODE, NatureTexte.LODA],
        "codes_prioritaires": ["CESEDA"],
        "articles_cles": ["L511-1", "L511-2", "L511-3", "L511-4"],
        "mots_cles_optimaux": ["OQTF", "éloignement", "reconduite", "frontière"]
    },
    "titre_sejour": {
        "nature_textes": [NatureTexte.CODE, NatureTexte.LODA],
        "codes_prioritaires": ["CESEDA"],
        "articles_cles": ["L313-1", "L313-2", "L313-3", "L313-4"],
        "mots_cles_optimaux": ["titre", "séjour", "renouvellement", "carte"]
    },
    "regroupement_familial": {
        "nature_textes": [NatureTexte.CODE, NatureTexte.LODA],
        "codes_prioritaires": ["CESEDA"],
        "articles_cles": ["L411-1", "L411-2", "L411-3"],
        "mots_cles_optimaux": ["regroupement", "familial", "conjoint", "famille"]
    },
    "naturalisation": {
        "nature_textes": [NatureTexte.CODE],
        "codes_prioritaires": ["CN"],
        "articles_cles": ["21-1", "21-2", "21-3", "21-4"],
        "mots_cles_optimaux": ["naturalisation", "nationalité", "assimilation"]
    },
    "asile": {
        "nature_textes": [NatureTexte.CODE, NatureTexte.LODA],
        "codes_prioritaires": ["CESEDA"],
        "articles_cles": ["L741-1", "L741-2", "L741-3"],
        "mots_cles_optimaux": ["asile", "réfugié", "protection", "OFPRA"]
    }
}


def get_domain_config(domain: str) -> Optional[Dict[str, any]]:
    """Retourne la configuration optimale pour un domaine juridique"""
    return DOMAIN_SPECIFIC_CONFIGS.get(domain.lower())


def create_agent_service_factory(agent_id: str):
    """Factory pour créer un service Légifrance configuré pour un agent"""
    from ..services.official_legifrance_service import OfficialLegifranceService
    
    oauth_config = get_oauth_config()
    
    return OfficialLegifranceService(
        client_id=oauth_config.client_id,
        client_secret=oauth_config.client_secret,
        use_production=(oauth_config.environment == LegifranceEnvironment.PRODUCTION)
    )
