"""
Classes de base pour le pipeline DEFENSEUR-IA
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from defenseur_ia.core.shared_store import SharedStore

logger = logging.getLogger(__name__)


class NodeContext:
    """
    Contexte d'exécution pour un agent du pipeline.
    Contient le SharedStore, les métadonnées d'exécution et des infos dossier.
    """
    
    def __init__(self, shared: SharedStore, node_id: Optional[str] = None,
                 dossier_id: Optional[str] = None, storage: Optional[Any] = None):
        # Store partagé (API moderne)
        self.shared = shared
        # Alias rétrocompatibilité: plusieurs agents utilisent encore `shared_store`
        # Propriété exposée plus bas
        self.node_id = node_id
        # Contexte dossier (attendu par l'orchestrateur)
        self.dossier_id = dossier_id
        self.storage = storage
        # Métadonnées d'exécution
        self.start_time = datetime.now()
        self.metadata: Dict[str, Any] = {}
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Définit une métadonnée pour ce contexte d'exécution"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Récupère une métadonnée de ce contexte"""
        return self.metadata.get(key, default)
    
    @property
    def execution_time(self) -> float:
        """Temps d'exécution en secondes depuis le début"""
        return (datetime.now() - self.start_time).total_seconds()

    # Alias rétrocompatibilité: certains agents référencent `context.shared_store`
    @property
    def shared_store(self) -> SharedStore:
        return self.shared


class BaseNode(ABC):
    """
    Classe de base pour tous les agents du pipeline DEFENSEUR-IA.
    Chaque agent doit hériter de cette classe et implémenter la méthode exec().
    """
    
    id: str = "base_node"
    name: str = "Base Node"
    description: str = "Nœud de base du pipeline"
    
    def __init__(self, node_id: Optional[str] = None, name: Optional[str] = None):
        # Compatibilité ascendante: certains agents passent (id, name) ici
        if node_id:
            self.id = node_id
        if name:
            self.name = name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def exec(self, ctx: NodeContext) -> None:
        """
        Méthode principale d'exécution de l'agent.
        
        Args:
            ctx: Contexte d'exécution contenant le SharedStore
        
        Raises:
            NotImplementedError: Si la méthode n'est pas implémentée
        """
        raise NotImplementedError(f"Agent {self.id} must implement exec() method")
    
    async def pre_exec(self, ctx: NodeContext) -> None:
        """
        Hook appelé avant l'exécution principale.
        Peut être surchargé pour des initialisations spécifiques.
        """
        self.logger.info(f"Starting execution of {self.id}")
        ctx.set_metadata("start_time", datetime.now().isoformat())
    
    async def post_exec(self, ctx: NodeContext) -> None:
        """
        Hook appelé après l'exécution principale.
        Peut être surchargé pour des nettoyages ou logs spécifiques.
        """
        execution_time = ctx.execution_time
        self.logger.info(f"Completed execution of {self.id} in {execution_time:.2f}s")
        ctx.set_metadata("end_time", datetime.now().isoformat())
        ctx.set_metadata("execution_time_seconds", execution_time)
    
    async def run(self, ctx: NodeContext) -> None:
        """
        Méthode d'exécution complète avec hooks pre/post.
        Cette méthode ne doit généralement pas être surchargée.
        """
        try:
            await self.pre_exec(ctx)
            await self.exec(ctx)
            await self.post_exec(ctx)
        except Exception as e:
            self.logger.error(f"Error in {self.id}: {str(e)}")
            ctx.set_metadata("error", str(e))
            ctx.set_metadata("status", "failed")
            raise
        else:
            ctx.set_metadata("status", "completed")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __repr__(self) -> str:
        return self.__str__()


class DefenseurIAException(Exception):
    """Exception de base pour le système DEFENSEUR-IA"""
    pass


class NodeExecutionError(DefenseurIAException):
    """Erreur lors de l'exécution d'un agent"""
    
    def __init__(self, node_id: str, message: str, original_error: Optional[Exception] = None):
        self.node_id = node_id
        self.original_error = original_error
        super().__init__(f"Error in node {node_id}: {message}")


class PipelineError(DefenseurIAException):
    """Erreur au niveau du pipeline"""
    pass


class ValidationError(DefenseurIAException):
    """Erreur de validation des données"""
    pass
