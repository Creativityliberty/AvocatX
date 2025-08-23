"""
SharedStore - État global partagé entre les agents du pipeline DEFENSEUR-IA
"""

import json
import os
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SharedStore:
    """
    Store partagé pour maintenir l'état entre les différents agents du pipeline.
    Utilise un dictionnaire JSON pour la persistance et la sérialisation.
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.data = data or {}
        self._lock = asyncio.Lock()
        
        # Initialisation des métadonnées si pas présentes
        if "meta" not in self.data:
            self.data["meta"] = {
                "dossier_id": f"DOSSIER_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "version": 1,
                "langue": "fr"
            }
    
    async def initialize(self):
        """Initialise le SharedStore"""
        logger.info("✅ SharedStore initialisé")
        return True
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur du store de manière thread-safe"""
        async with self._lock:
            return self.data.get(key, default)
    
    async def set(self, key: str, value: Any) -> None:
        """Définit une valeur dans le store de manière thread-safe"""
        async with self._lock:
            self.data[key] = value
            logger.debug(f"SharedStore: set {key} = {type(value).__name__}")
    
    async def update(self, updates: Dict[str, Any]) -> None:
        """Met à jour plusieurs clés en une fois"""
        async with self._lock:
            self.data.update(updates)
            logger.debug(f"SharedStore: updated {len(updates)} keys")
    
    async def delete(self, key: str) -> bool:
        """Supprime une clé du store"""
        async with self._lock:
            if key in self.data:
                del self.data[key]
                logger.debug(f"SharedStore: deleted {key}")
                return True
            return False
    
    async def keys(self) -> list:
        """Retourne toutes les clés disponibles"""
        async with self._lock:
            return list(self.data.keys())
    
    async def to_dict(self) -> Dict[str, Any]:
        """Retourne une copie du store sous forme de dictionnaire"""
        async with self._lock:
            return self.data.copy()

    def get_config(self, key: str, default: Any = None) -> Any:
        """Récupère une configuration depuis le store, les settings ou les variables d'environnement.
        Ordre de résolution:
        1) self.data["config"][key] si présent
        2) defenseur_ia.config.settings.settings.<KEY> si défini
        3) variable d'environnement OS (ex: OPENAI_API_KEY)
        4) valeur par défaut
        """
        # 1) Config stockée en mémoire
        in_store = None
        try:
            in_store = self.data.get("config", {}).get(key)
        except Exception:
            in_store = None
        if in_store not in (None, ""):
            return in_store

        # 2) Settings Pydantic (lazy import pour éviter les cycles)
        try:
            from defenseur_ia.config.settings import settings  # type: ignore
            val = getattr(settings, key, None)
            if val not in (None, ""):
                return val
        except Exception:
            pass

        # 3) Variables d'environnement
        env_val = os.getenv(key)
        if env_val not in (None, ""):
            return env_val

        # 4) Par défaut
        return default
    
    async def save_to_file(self, filepath: str) -> None:
        """Sauvegarde le store dans un fichier JSON"""
        async with self._lock:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"SharedStore saved to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save SharedStore to {filepath}: {e}")
                raise
    
    @classmethod
    async def load_from_file(cls, filepath: str) -> 'SharedStore':
        """Charge un store depuis un fichier JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"SharedStore loaded from {filepath}")
            return cls(data)
        except Exception as e:
            logger.error(f"Failed to load SharedStore from {filepath}: {e}")
            raise
    
    def __str__(self) -> str:
        return f"SharedStore(keys={len(self.data)}, dossier_id={self.data.get('meta', {}).get('dossier_id', 'unknown')})"
    
    def __repr__(self) -> str:
        return self.__str__()
