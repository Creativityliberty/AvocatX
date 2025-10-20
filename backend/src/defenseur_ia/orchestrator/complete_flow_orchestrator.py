"""
Orchestrateur de Flow Complet DEFENSEUR-IA
Inspiré de PocketFlow - Gestion du pipeline complet du premier au dernier agent
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

from ..models import PipelineStatus
from ..agents import *
from ..services.unified_embedding_service import UnifiedEmbeddingService
from ..config.legifrance_config import LegifranceConfigManager
from ..core.shared_store import SharedStore
from ..core.base import NodeContext


class FlowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class FlowStep:
    """Représente une étape du flow"""
    id: str
    agent_name: str
    agent_class: str
    status: FlowStatus
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None
    error: Optional[str] = None
    metrics: Optional[Dict] = None


@dataclass
class FlowExecution:
    """Représente une exécution complète du flow"""
    id: str
    case_id: str
    status: FlowStatus
    start_time: str
    end_time: Optional[str] = None
    total_duration: Optional[float] = None
    steps: List[FlowStep] = None
    shared_context: Dict = None
    final_result: Optional[Dict] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.shared_context is None:
            self.shared_context = {}


class DefenseurFlowOrchestrator:
    """
    Orchestrateur principal du flow DEFENSEUR-IA
    Inspiré du pattern Workflow de PocketFlow
    """
    
    def __init__(self):
        self.embedding_service = UnifiedEmbeddingService()
        self.legifrance_config = LegifranceConfigManager()
        self.active_flows: Dict[str, FlowExecution] = {}
        self.flow_listeners: List[Callable] = []
        
        # Configuration des agents dans l'ordre d'exécution
        import os
        use_enhanced = os.getenv("USE_ENHANCED_WEB_RESEARCH", "1").lower() in ("1", "true", "yes")
        self.agent_pipeline = [
            {"name": "ecouteur", "class": AgentEcouteur, "description": "Écoute et analyse la demande initiale"},
            {"name": "cadreur_juridique", "class": AgentCadreurJuridique, "description": "Cadrage juridique et identification des enjeux"},
            {"name": "parseur_preuves", "class": AgentParseurPreuves, "description": "Analyse et extraction des preuves"},
            {"name": "juriste_matching", "class": AgentJuristeMatching, "description": "Matching avec jurisprudence similaire"},
            {"name": "recherche_web", "class": (AgentRechercheWebEnhanced if use_enhanced else AgentRechercheWeb), "description": "Recherche d'informations complémentaires"},
            {"name": "redacteur_narratif", "class": AgentRedacteurNarratif, "description": "Rédaction du narratif factuel"},
            {"name": "relecteur_ia_1", "class": AgentRelecteurIA1, "description": "Première relecture et corrections"},
            {"name": "synthese_strategique", "class": AgentSyntheseStrategique, "description": "Synthèse stratégique et recommandations"},
            {"name": "relecteur_ia_2", "class": AgentRelecteurIA2, "description": "Seconde relecture et finalisation"},
            {"name": "avocat_ia", "class": AgentAvocatIA, "description": "Validation finale et conseils juridiques"},
            # Étapes optionnelles à réactiver lorsqu'elles seront implémentées :
            # {"name": "generateur_documents", "class": AgentGenerateurDocuments, "description": "Génération des documents finaux"},
            # {"name": "archiveur", "class": AgentArchiveur, "description": "Archivage et sauvegarde"}
        ]

    async def create_flow(self, case_data: Any) -> str:
        """Crée un nouveau flow d'exécution"""
        flow_id = str(uuid.uuid4())
        
        # Sérialiser case_data de manière robuste (Pydantic / dict / dataclass)
        if hasattr(case_data, "model_dump"):
            serialized_case = case_data.model_dump()
        elif isinstance(case_data, dict):
            serialized_case = case_data
        else:
            try:
                serialized_case = asdict(case_data)
            except Exception:
                serialized_case = case_data.__dict__ if hasattr(case_data, "__dict__") else {}
        case_id_val = (
            serialized_case.get("id")
            or serialized_case.get("case_id")
            or serialized_case.get("dossier_id")
            or serialized_case.get("uuid")
            or "unknown_case"
        )
        
        flow_execution = FlowExecution(
            id=flow_id,
            case_id=str(case_id_val),
            status=FlowStatus.PENDING,
            start_time=datetime.now().isoformat(),
            shared_context={
                "case_data": serialized_case,
                "flow_id": flow_id,
                "agent_results": {},
                "inter_agent_messages": asyncio.Queue(),
                "global_context": {},
                "metrics": {
                    "total_agents": len(self.agent_pipeline),
                    "completed_agents": 0,
                    "failed_agents": 0,
                    "api_calls": 0,
                    "embedding_calls": 0,
                    "legifrance_calls": 0
                }
            }
        )
        
        # Initialiser les étapes
        for i, agent_config in enumerate(self.agent_pipeline):
            step = FlowStep(
                id=f"{flow_id}_step_{i}",
                agent_name=agent_config["name"],
                agent_class=agent_config["class"].__name__,
                status=FlowStatus.PENDING
            )
            flow_execution.steps.append(step)
        
        self.active_flows[flow_id] = flow_execution
        await self._notify_listeners("flow_created", flow_execution)
        
        return flow_id

    async def execute_flow(self, flow_id: str) -> FlowExecution:
        """Exécute un flow complet"""
        if flow_id not in self.active_flows:
            raise ValueError(f"Flow {flow_id} not found")
        
        flow = self.active_flows[flow_id]
        flow.status = FlowStatus.RUNNING
        
        try:
            await self._notify_listeners("flow_started", flow)
            
            # Créer un SharedStore pour ce flow en enveloppant le contexte partagé existant
            shared_store = SharedStore(flow.shared_context)
            await shared_store.initialize()
            # Semer quelques métadonnées globales utiles
            await shared_store.set("flow_id", flow.id)
            await shared_store.set("case_id", flow.case_id)
            
            # Exécution séquentielle des agents
            for i, (step, agent_config) in enumerate(zip(flow.steps, self.agent_pipeline)):
                await self._execute_step(flow, step, agent_config, i, shared_store)
                
                # Vérifier si le flow doit être interrompu
                if flow.status == FlowStatus.FAILED:
                    break
            
            # Finaliser le flow
            if flow.status != FlowStatus.FAILED:
                flow.status = FlowStatus.COMPLETED
                flow.end_time = datetime.now().isoformat()
                flow.total_duration = self._calculate_duration(flow.start_time, flow.end_time)
                
                # Créer le résultat final
                flow.final_result = await self._create_final_result(flow)
            
            await self._notify_listeners("flow_completed", flow)
            
        except Exception as e:
            flow.status = FlowStatus.FAILED
            flow.error = str(e)
            flow.end_time = datetime.now().isoformat()
            await self._notify_listeners("flow_failed", flow)
            raise
        
        return flow

    async def _execute_step(self, flow: FlowExecution, step: FlowStep, agent_config: Dict, step_index: int, shared_store: SharedStore):
        """Exécute une étape individuelle du flow"""
        step.status = FlowStatus.RUNNING
        step.start_time = datetime.now().isoformat()
        
        await self._notify_listeners("step_started", {"flow": flow, "step": step})
        
        try:
            # Instancier l'agent
            agent_class = agent_config["class"]
            agent = agent_class()
            
            # Capture des clés avant exécution pour extraire les nouveautés
            keys_before = set(await shared_store.keys())

            # Construire le contexte d'exécution NodeContext
            dossier_id_val = flow.case_id
            ctx = NodeContext(
                shared=shared_store,
                node_id=agent_config.get("name"),
                dossier_id=str(dossier_id_val),
                storage=None,
            )

            # Semer l'entrée initiale pour le premier agent si nécessaire
            if step_index == 0 and step.agent_name == "ecouteur":
                existing_input = await shared_store.get("input_blob")
                if existing_input in (None, ""):
                    await self._seed_first_step_input(flow, shared_store)

            # Exécuter l'agent avec le contexte standardisé (inclut pre/post hooks)
            await agent.run(ctx)

            # Fin de l'étape: mesurer la durée et produire un résumé de sortie
            keys_after = set(await shared_store.keys())
            new_keys = sorted(list(keys_after - keys_before))
            step.output_data = {
                "status": ctx.get_metadata("status", "completed"),
                "new_keys": new_keys,
            }

            # Fin de l'étape: mesurer la durée
            step.end_time = datetime.now().isoformat()
            step.duration = self._calculate_duration(step.start_time, step.end_time)

            # Déterminer le statut via le contexte d'exécution
            status_str = step.output_data.get("status", "completed")

            # Mettre à jour le contexte partagé (résumé par agent)
            flow.shared_context["agent_results"][agent_config["name"]] = step.output_data

            # Collecter les métriques
            step.metrics = await self._collect_step_metrics(agent, ctx)

            if status_str != "success":
                # Échec logique renvoyé par l'agent
                step.status = FlowStatus.FAILED
                errors_list = step.output_data.get("errors", []) if isinstance(step.output_data, dict) else []
                step.error = "; ".join(errors_list[:5]) if errors_list else "Agent returned non-success status"
                flow.shared_context["metrics"]["failed_agents"] += 1
                await self._notify_listeners("step_failed", {"flow": flow, "step": step, "error": step.error})

                # Arrêt si agent critique
                if self._is_critical_agent(agent_config["name"]):
                    flow.status = FlowStatus.FAILED
                    flow.error = f"Critical agent {agent_config['name']} returned error status"
            else:
                step.status = FlowStatus.COMPLETED
                flow.shared_context["metrics"]["completed_agents"] += 1
                await self._notify_listeners("step_completed", {"flow": flow, "step": step})
            
        except Exception as e:
            step.status = FlowStatus.FAILED
            step.error = str(e)
            step.end_time = datetime.now().isoformat()
            flow.shared_context["metrics"]["failed_agents"] += 1
            
            await self._notify_listeners("step_failed", {"flow": flow, "step": step, "error": e})
            
            # Décider si continuer ou arrêter le flow
            if self._is_critical_agent(agent_config["name"]):
                flow.status = FlowStatus.FAILED
                flow.error = f"Critical agent {agent_config['name']} failed: {str(e)}"

    async def _prepare_agent_input(self, flow: FlowExecution, step: FlowStep, step_index: int) -> Dict:
        """Prépare les données d'entrée pour un agent"""
        base_input = {
            "case_data": flow.shared_context["case_data"],
            "flow_id": flow.id,
            "step_index": step_index,
            "previous_results": flow.shared_context["agent_results"],
            "global_context": flow.shared_context["global_context"]
        }
        
        # Ajouter des données spécifiques selon l'agent
        agent_name = step.agent_name
        
        if agent_name == "ecouteur":
            # Premier agent - données initiales uniquement
            pass
        elif agent_name == "cadreur_juridique":
            # Utiliser le résultat de l'écouteur
            if "ecouteur" in flow.shared_context["agent_results"]:
                base_input["initial_analysis"] = flow.shared_context["agent_results"]["ecouteur"]
        elif agent_name == "parseur_preuves":
            # Utiliser le cadrage juridique
            if "cadreur_juridique" in flow.shared_context["agent_results"]:
                base_input["legal_framework"] = flow.shared_context["agent_results"]["cadreur_juridique"]
        # ... etc pour chaque agent
        
        return base_input

    async def _collect_step_metrics(self, agent: Any, result: Any) -> Dict:
        """Collecte les métriques d'une étape"""
        # Cas NodeContext: utiliser les métadonnées post_exec
        try:
            if isinstance(result, NodeContext):
                exec_time = result.get_metadata("execution_time_seconds", None)
                if exec_time is None:
                    # fallback sur le calcul direct
                    exec_time = result.execution_time
                metrics = {
                    "execution_time": exec_time
                }
                return {k: v for k, v in metrics.items() if v is not None}
        except Exception:
            pass

        # Extraire la confiance moyenne depuis le payload imbriqué du nouvel AgentResult
        avg_conf = None
        try:
            if hasattr(result, 'result') and isinstance(result.result, dict):
                avg_conf = (result.result.get('metrics', {}) or {}).get('average_confidence')
            elif isinstance(result, dict):
                avg_conf = ((result.get('result', {}) or {}).get('metrics', {}) or {}).get('average_confidence')
        except Exception:
            avg_conf = None

        metrics = {
            "execution_time": getattr(result, 'execution_time', None),
            "api_calls": getattr(result, 'api_calls', 0),
            "embedding_calls": getattr(result, 'embedding_calls', 0),
            "legifrance_calls": getattr(result, 'legifrance_calls', 0),
            "tokens_used": getattr(result, 'tokens_used', 0),
            "average_confidence": avg_conf,
            "quality_score": getattr(result, 'quality_score', None)
        }
        
        return {k: v for k, v in metrics.items() if v is not None}

    async def _seed_first_step_input(self, flow: FlowExecution, shared: SharedStore) -> None:
        """Sème l'entrée initiale attendue par l'agent 0 (écouteur) si présente dans case_data."""
        try:
            case_data = flow.shared_context.get("case_data", {}) or {}

            # Déjà fourni explicitement
            if "input_blob" in case_data:
                await shared.set("input_blob", case_data.get("input_blob"))
                return

            # Variantes textuelles communes
            for key in ("input", "text", "message", "prompt"):
                if key in case_data and case_data.get(key):
                    await shared.set("input_blob", str(case_data.get(key)))
                    return

            # Variantes audio communes
            audio_path = case_data.get("audio_file") or case_data.get("audio_path") or None
            audio_data = case_data.get("audio_data")
            if audio_path or audio_data:
                await shared.set("input_blob", {
                    "type": "audio",
                    "file_path": audio_path,
                    "audio_data": audio_data,
                })
                return
        except Exception:
            # Ne pas bloquer l'exécution si rien n'est détecté
            pass

    async def _create_final_result(self, flow: FlowExecution) -> Dict:
        """Crée le résultat final du flow"""
        return {
            "flow_id": flow.id,
            "case_id": flow.case_id,
            "status": flow.status.value,
            "total_duration": flow.total_duration,
            "agents_executed": len([s for s in flow.steps if s.status == FlowStatus.COMPLETED]),
            "final_documents": flow.shared_context["agent_results"].get("generateur_documents", {}),
            "legal_analysis": flow.shared_context["agent_results"].get("avocat_ia", {}),
            "strategic_summary": flow.shared_context["agent_results"].get("synthese_strategique", {}),
            "archive_location": flow.shared_context["agent_results"].get("archiveur", {}),
            "overall_metrics": flow.shared_context["metrics"]
        }

    def _is_critical_agent(self, agent_name: str) -> bool:
        """Détermine si un agent est critique pour la continuation du flow"""
        critical_agents = ["ecouteur", "cadreur_juridique", "avocat_ia"]
        return agent_name in critical_agents

    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calcule la durée entre deux timestamps"""
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return (end - start).total_seconds()

    async def _notify_listeners(self, event_type: str, data: Any):
        """Notifie les listeners d'événements du flow"""
        for listener in self.flow_listeners:
            try:
                await listener(event_type, data)
            except Exception as e:
                logger.error(f"Error in flow listener: {e}")

    def add_flow_listener(self, listener: Callable):
        """Ajoute un listener d'événements du flow"""
        self.flow_listeners.append(listener)

    def get_flow_status(self, flow_id: str) -> Optional[FlowExecution]:
        """Récupère le statut d'un flow"""
        return self.active_flows.get(flow_id)

    def get_all_flows(self) -> List[FlowExecution]:
        """Récupère tous les flows actifs"""
        return list(self.active_flows.values())

    async def pause_flow(self, flow_id: str):
        """Met en pause un flow"""
        if flow_id in self.active_flows:
            self.active_flows[flow_id].status = FlowStatus.PAUSED
            await self._notify_listeners("flow_paused", self.active_flows[flow_id])

    async def resume_flow(self, flow_id: str):
        """Reprend un flow en pause"""
        if flow_id in self.active_flows:
            flow = self.active_flows[flow_id]
            if flow.status == FlowStatus.PAUSED:
                flow.status = FlowStatus.RUNNING
                await self._notify_listeners("flow_resumed", flow)

    async def cancel_flow(self, flow_id: str):
        """Annule un flow"""
        if flow_id in self.active_flows:
            flow = self.active_flows[flow_id]
            flow.status = FlowStatus.FAILED
            flow.error = "Flow cancelled by user"
            flow.end_time = datetime.now().isoformat()
            await self._notify_listeners("flow_cancelled", flow)


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation de l'orchestrateur"""
    orchestrator = DefenseurFlowOrchestrator()
    
    # Ajouter un listener pour le monitoring
    async def flow_monitor(event_type: str, data: Any):
        logger.info(f"Flow Event: {event_type}")
        if event_type == "step_completed":
            step = data["step"]
            logger.info(f"  - Agent {step.agent_name} completed in {step.duration}s")
    
    orchestrator.add_flow_listener(flow_monitor)
    
    # Créer des données de test (dict normalisé)
    case_data = {
        "id": "test_case_001",
        "title": "Demande de titre de séjour",
        "description": "Renouvellement de titre de séjour étudiant",
        "client_info": {"name": "Test Client", "nationality": "Algérienne"},
        "documents": [],
        "priority": "normal"
    }
    
    # Créer et exécuter le flow
    flow_id = await orchestrator.create_flow(case_data)
    logger.info(f"Flow créé: {flow_id}")
    
    result = await orchestrator.execute_flow(flow_id)
    logger.info(f"Flow terminé: {result.status}")
    logger.info(f"Durée totale: {result.total_duration}s")


if __name__ == "__main__":
    asyncio.run(example_usage())
