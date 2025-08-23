"""
Orchestrateur principal du pipeline DEFENSEUR-IA
Gère l'exécution des 12 agents en séquence avec monitoring temps réel
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from defenseur_ia.core.shared_store import SharedStore
from defenseur_ia.core.base import NodeContext
from defenseur_ia.agents.agent_00_ecouteur import EcouteurNode
from defenseur_ia.agents.agent_01_cadreur_juridique import CadreurJuridiqueNode
from defenseur_ia.services.storage_service import StorageService

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """
    Orchestrateur principal qui gère l'exécution des 12 agents du pipeline
    """
    
    def __init__(self):
        self.shared_store = SharedStore()
        self.storage_service = StorageService()
        self.agents = self._initialize_agents()
        self.running_pipelines = {}  # dossier_id -> task
        
    def _initialize_agents(self) -> List:
        """Initialise tous les agents du pipeline"""
        from ..agents.agent_02_parseur_preuves import ParseurPreuvesNode
        from ..agents.agent_03_juriste_matching import JuristeMatchingNode
        from ..agents.agent_recherche_web_enhanced_node import RechercheWebEnhancedNode
        from ..agents.agent_06_redacteur_narratif import RedacteurNarratifNode
        from ..agents.agent_07_relecteur_ia_1 import RelecteurIA1Node
        from ..agents.agent_08_agregateur_coherence import AgregateurCoherenceNode
        from ..agents.agent_09_relecteur_ia_2 import RelecteurIA2Node
        from ..agents.agent_10_synthese_strategique import SyntheseStrategiqueNode
        from ..agents.agent_11_avocat_ia import AvocatIANode
        
        return [
            EcouteurNode(),              # Agent 0
            CadreurJuridiqueNode(),      # Agent 1
            ParseurPreuvesNode(),        # Agent 2
            JuristeMatchingNode(),       # Agent 3
            RechercheWebEnhancedNode(),  # Agent 4 (enhanced)
            RedacteurNarratifNode(),     # Agent 6
            RelecteurIA1Node(),          # Agent 7
            AgregateurCoherenceNode(),   # Agent 8
            RelecteurIA2Node(),          # Agent 9
            SyntheseStrategiqueNode(),   # Agent 10
            AvocatIANode(),              # Agent 11
        ]
    
    async def initialize(self):
        """Initialise l'orchestrateur"""
        logger.info("🚀 Initialisation de l'orchestrateur pipeline")
        await self.shared_store.initialize()
        await self.storage_service.initialize()
    
    async def shutdown(self):
        """Arrête l'orchestrateur"""
        logger.info("🛑 Arrêt de l'orchestrateur pipeline")
        
        # Arrêt des pipelines en cours
        for dossier_id, task in self.running_pipelines.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        await self.shared_store.shutdown()
        await self.storage_service.shutdown()
    
    async def start_pipeline(self, dossier_id: str, input_data: Dict[str, Any] = None) -> bool:
        """
        Démarre le pipeline pour un dossier
        """
        try:
            # Vérifier si le pipeline est déjà en cours
            if dossier_id in self.running_pipelines and not self.running_pipelines[dossier_id].done():
                logger.warning(f"Pipeline déjà en cours pour {dossier_id}")
                return False
            
            # Créer le contexte
            ctx = NodeContext(
                dossier_id=dossier_id,
                shared=self.shared_store,
                storage=self.storage_service
            )
            
            # Stocker les données d'entrée
            if input_data:
                await ctx.shared.set("input_blob", input_data)
            
            # Démarrer l'exécution asynchrone
            task = asyncio.create_task(self._execute_pipeline(ctx))
            self.running_pipelines[dossier_id] = task
            
            logger.info(f"✅ Pipeline démarré pour {dossier_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage pipeline {dossier_id}: {e}")
            return False
    
    async def stop_pipeline(self, dossier_id: str) -> bool:
        """
        Arrête le pipeline pour un dossier
        """
        if dossier_id in self.running_pipelines:
            task = self.running_pipelines[dossier_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            del self.running_pipelines[dossier_id]
            logger.info(f"✅ Pipeline arrêté pour {dossier_id}")
            return True
        
        return False
    
    async def _execute_pipeline(self, ctx: NodeContext):
        """
        Exécute le pipeline complet pour un dossier
        """
        dossier_id = ctx.dossier_id
        
        try:
            logger.info(f"🚀 Démarrage pipeline pour {dossier_id}")
            
            # Initialisation du statut
            await self._update_pipeline_status(ctx, 0, "started")
            
            # Exécution séquentielle des agents
            for agent_index, agent in enumerate(self.agents):
                try:
                    logger.info(f"🔍 Agent {agent_index} - {agent.name} démarré")
                    
                    # Mise à jour du statut
                    await self._update_pipeline_status(ctx, agent_index, "processing")
                    
                    # Exécution de l'agent
                    await agent.exec(ctx)
                    
                    # Mise à jour du statut
                    await self._update_pipeline_status(ctx, agent_index, "completed")
                    
                    logger.info(f"✅ Agent {agent_index} - {agent.name} terminé")
                    
                except Exception as e:
                    logger.error(f"❌ Erreur Agent {agent_index} - {agent.name}: {e}")
                    await self._update_pipeline_status(ctx, agent_index, "error", str(e))
                    raise
            
            # Pipeline terminé avec succès
            await self._update_pipeline_status(ctx, len(self.agents), "completed")
            logger.info(f"✅ Pipeline terminé avec succès pour {dossier_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur pipeline {dossier_id}: {e}")
            await self._update_pipeline_status(ctx, -1, "failed", str(e))
            raise
    
    async def _update_pipeline_status(self, ctx: NodeContext, step: int, status: str, error: str = None):
        """
        Met à jour le statut du pipeline
        """
        try:
            pipeline_status = {
                "dossier_id": ctx.dossier_id,
                "current_step": step,
                "status": status,
                "error": error,
                "timestamp": datetime.now().isoformat(),
                "progress": (step / len(self.agents)) * 100 if step >= 0 else 0
            }
            
            # Sauvegarde dans le SharedStore
            await ctx.shared.set("pipeline_status", pipeline_status)
            
            # Notification WebSocket
            await self._notify_websocket(ctx.dossier_id, pipeline_status)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour statut: {e}")
    
    async def _notify_websocket(self, dossier_id: str, status: Dict[str, Any]):
        """
        Notifie les clients WebSocket du changement de statut
        """
        try:
            from defenseur_ia.core.websocket_manager import WebSocketManager
            ws_manager = WebSocketManager()
            await ws_manager.broadcast(dossier_id, status)
        except Exception as e:
            logger.error(f"Erreur notification WebSocket: {e}")
    
    async def get_status(self, dossier_id: str) -> Dict[str, Any]:
        """
        Récupère le statut actuel du pipeline
        """
        try:
            # Récupération depuis le SharedStore
            status = await self.shared_store.get(f"pipeline_status_{dossier_id}")
            
            if not status:
                # Vérifier si le dossier existe
                case = await self.storage_service.get_case(dossier_id)
                if not case:
                    return None
                
                # Retourner un statut par défaut
                status = {
                    "dossier_id": dossier_id,
                    "current_step": 0,
                    "status": "pending",
                    "progress": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Erreur récupération statut {dossier_id}: {e}")
            return None
    
    async def get_cases(self, skip: int = 0, limit: int = 10, **filters) -> List[Dict[str, Any]]:
        """
        Récupère la liste des dossiers
        """
        try:
            return await self.storage_service.get_cases(skip=skip, limit=limit, **filters)
        except Exception as e:
            logger.error(f"Erreur récupération dossiers: {e}")
            return []
    
    async def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nouveau dossier
        """
        try:
            dossier_id = str(uuid.uuid4())
            case_data["dossier_id"] = dossier_id
            case_data["created_at"] = datetime.now().isoformat()
            
            # Sauvegarde du dossier
            await self.storage_service.create_case(case_data)
            
            # Initialisation dans le SharedStore
            await self.shared_store.set(f"case_{dossier_id}", case_data)
            
            return {
                "dossier_id": dossier_id,
                "status": "created",
                "message": "Dossier créé avec succès"
            }
            
        except Exception as e:
            logger.error(f"Erreur création dossier: {e}")
            raise
