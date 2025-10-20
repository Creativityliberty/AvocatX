"""
Configuration OpenAI pour DEFENSEUR-IA
Gestion sécurisée des clés API et paramètres OpenAI
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class OpenAIConfig:
    """Configuration pour les services OpenAI"""
    api_key: str
    organization: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3
    
    # Modèles disponibles
    gpt_model: str = "gpt-4-1106-preview"  # GPT-4.1
    deep_research_model: str = "o3-deep-research"
    deep_research_mini_model: str = "o4-mini-deep-research"
    
    # Paramètres par défaut
    default_temperature: float = 0.7
    default_max_tokens: int = 4000
    
    # Outils disponibles
    available_tools: list = None
    
    def __post_init__(self):
        if self.available_tools is None:
            self.available_tools = [
                "web_search_preview",
                "code_interpreter"
            ]


class OpenAIConfigManager:
    """Gestionnaire de configuration OpenAI"""
    
    def __init__(self):
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration OpenAI"""
        try:
            # Priorité 1: Variable d'environnement
            api_key = os.getenv("OPENAI_API_KEY")
            
            # Priorité 2: Clé fournie par l'utilisateur
            if not api_key:
                api_key = "AIzaSyDFhEDxV6y2wrW5bmL7xMptDb4Z44G5esk"
                logger.info("Utilisation de la clé API OpenAI fournie par l'utilisateur")
            else:
                logger.info("Utilisation de la clé API OpenAI depuis les variables d'environnement")
            
            if not api_key:
                raise ValueError("Aucune clé API OpenAI trouvée")
            
            # Configuration complète
            self._config = OpenAIConfig(
                api_key=api_key,
                organization=os.getenv("OPENAI_ORGANIZATION"),
                base_url=os.getenv("OPENAI_BASE_URL"),
                timeout=int(os.getenv("OPENAI_TIMEOUT", "60")),
                max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
                gpt_model=os.getenv("OPENAI_GPT_MODEL", "gpt-4-1106-preview"),
                deep_research_model=os.getenv("OPENAI_DEEP_RESEARCH_MODEL", "o3-deep-research"),
                deep_research_mini_model=os.getenv("OPENAI_DEEP_RESEARCH_MINI_MODEL", "o4-mini-deep-research"),
                default_temperature=float(os.getenv("OPENAI_DEFAULT_TEMPERATURE", "0.7")),
                default_max_tokens=int(os.getenv("OPENAI_DEFAULT_MAX_TOKENS", "4000"))
            )
            
            logger.info("Configuration OpenAI chargée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration OpenAI: {e}")
            raise
    
    @property
    def config(self) -> OpenAIConfig:
        """Retourne la configuration OpenAI"""
        if not self._config:
            self._load_config()
        return self._config
    
    def get_client_config(self) -> Dict[str, Any]:
        """Retourne la configuration pour le client OpenAI"""
        return {
            "api_key": self._config.api_key,
            "organization": self._config.organization,
            "base_url": self._config.base_url,
            "timeout": self._config.timeout,
            "max_retries": self._config.max_retries
        }
    
    def get_model_config(self, model_type: str = "gpt") -> Dict[str, Any]:
        """Retourne la configuration pour un modèle spécifique"""
        model_mapping = {
            "gpt": self._config.gpt_model,
            "deep_research": self._config.deep_research_model,
            "deep_research_mini": self._config.deep_research_mini_model
        }
        
        return {
            "model": model_mapping.get(model_type, self._config.gpt_model),
            "temperature": self._config.default_temperature,
            "max_tokens": self._config.default_max_tokens
        }
    
    def get_tools_config(self) -> list:
        """Retourne la configuration des outils disponibles"""
        return [
            {
                "type": "web_search_preview",
                "web_search_preview": {
                    "enabled": True,
                    "max_results": 10
                }
            },
            {
                "type": "code_interpreter",
                "code_interpreter": {
                    "enabled": True
                }
            }
        ]
    
    def validate_config(self) -> bool:
        """Valide la configuration OpenAI"""
        try:
            if not self._config.api_key:
                logger.error("Clé API OpenAI manquante")
                return False
            
            if len(self._config.api_key) < 20:
                logger.error("Clé API OpenAI invalide (trop courte)")
                return False
            
            logger.info("Configuration OpenAI validée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la configuration: {e}")
            return False
    
    def update_config(self, **kwargs):
        """Met à jour la configuration OpenAI"""
        try:
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)
                    logger.info(f"Configuration OpenAI mise à jour: {key} = {value}")
                else:
                    logger.warning(f"Paramètre de configuration inconnu: {key}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la configuration: {e}")
            raise
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation (placeholder)"""
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens_used": 0,
            "average_response_time": 0.0,
            "models_used": {
                "gpt": 0,
                "deep_research": 0,
                "deep_research_mini": 0
            }
        }


# Instance globale du gestionnaire de configuration
openai_config_manager = OpenAIConfigManager()


def get_openai_config() -> OpenAIConfig:
    """Fonction utilitaire pour obtenir la configuration OpenAI"""
    return openai_config_manager.config


def get_openai_client_config() -> Dict[str, Any]:
    """Fonction utilitaire pour obtenir la configuration du client OpenAI"""
    return openai_config_manager.get_client_config()


def validate_openai_setup() -> bool:
    """Fonction utilitaire pour valider la configuration OpenAI"""
    return openai_config_manager.validate_config()


# Test de la configuration au chargement du module
if __name__ == "__main__":
    try:
        config = get_openai_config()
        logger.info("Configuration OpenAI chargée:")
        logger.info(f"- Modèle GPT: {config.gpt_model}")
        logger.info(f"- Modèle Deep Research: {config.deep_research_model}")
        logger.info(f"- Outils disponibles: {config.available_tools}")
        logger.info(f"- Validation: {'✅ OK' if validate_openai_setup() else '❌ Erreur'}")

    except Exception as e:
        logger.error(f"❌ Erreur lors du test de configuration: {e}")
