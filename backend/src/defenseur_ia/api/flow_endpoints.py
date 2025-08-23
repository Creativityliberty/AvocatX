"""
API Endpoints pour l'Orchestrateur de Flow DEFENSEUR-IA
Exposition REST et WebSocket pour le dashboard React
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime

from ..orchestrator.complete_flow_orchestrator import DefenseurFlowOrchestrator, FlowExecution, FlowStatus
from ..core.websocket_manager import WebSocketManager

# Router pour les endpoints de flow
flow_router = APIRouter(prefix="/flow", tags=["Flow Management"])

# Instance globale de l'orchestrateur
orchestrator = DefenseurFlowOrchestrator()
websocket_manager = WebSocketManager()

# Listener pour broadcaster les événements via WebSocket
async def flow_websocket_listener(event_type: str, data: Any):
    """Listener pour broadcaster les événements de flow via WebSocket"""
    message = {
        "type": "flow_event",
        "event": event_type,
        "data": serialize_flow_data(data),
        "timestamp": datetime.now().isoformat()
    }
    await websocket_manager.broadcast(json.dumps(message))

# Ajouter le listener à l'orchestrateur
orchestrator.add_flow_listener(flow_websocket_listener)


def serialize_flow_data(data: Any) -> Dict:
    """Sérialise les données de flow pour JSON"""
    if isinstance(data, FlowExecution):
        return {
            "id": data.id,
            "case_id": data.case_id,
            "status": data.status.value,
            "start_time": data.start_time,
            "end_time": data.end_time,
            "total_duration": data.total_duration,
            "steps": [
                {
                    "id": step.id,
                    "agent_name": step.agent_name,
                    "agent_class": step.agent_class,
                    "status": step.status.value,
                    "start_time": step.start_time,
                    "end_time": step.end_time,
                    "duration": step.duration,
                    "error": step.error,
                    "metrics": step.metrics
                }
                for step in data.steps
            ],
            "final_result": data.final_result,
            "error": data.error,
            "metrics": data.shared_context.get("metrics", {}) if data.shared_context else {}
        }
    elif isinstance(data, dict) and "flow" in data:
        return {
            "flow": serialize_flow_data(data["flow"]),
            "step": serialize_flow_data(data.get("step")),
            "error": str(data.get("error", "")) if data.get("error") else None
        }
    elif hasattr(data, 'id') and hasattr(data, 'agent_name'):  # FlowStep
        return {
            "id": data.id,
            "agent_name": data.agent_name,
            "agent_class": data.agent_class,
            "status": data.status.value,
            "start_time": data.start_time,
            "end_time": data.end_time,
            "duration": data.duration,
            "error": data.error,
            "metrics": data.metrics
        }
    else:
        return data if isinstance(data, (dict, list, str, int, float, bool)) else str(data)


@flow_router.post("/create")
async def create_flow(case_data: Dict[str, Any]) -> Dict[str, str]:
    """Crée un nouveau flow d'exécution"""
    try:
        # Normaliser les données en dict (compatible Pydantic / dict / objet)
        if hasattr(case_data, "model_dump"):
            case = case_data.model_dump()
        elif isinstance(case_data, dict):
            case = case_data
        else:
            case = getattr(case_data, "__dict__", {}) or {}

        # Assigner un identifiant si manquant
        if not any(k in case for k in ("id", "case_id", "dossier_id", "uuid")):
            case["id"] = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        flow_id = await orchestrator.create_flow(case)

        case_id_val = (
            case.get("id")
            or case.get("case_id")
            or case.get("dossier_id")
            or case.get("uuid")
            or "unknown_case"
        )

        return {
            "flow_id": flow_id,
            "status": "created",
            "message": f"Flow créé avec succès pour le dossier {case_id_val}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du flow: {str(e)}")


@flow_router.post("/execute/{flow_id}")
async def execute_flow(flow_id: str) -> Dict[str, Any]:
    """Lance l'exécution d'un flow"""
    try:
        # Exécuter le flow de manière asynchrone
        asyncio.create_task(orchestrator.execute_flow(flow_id))
        
        return {
            "flow_id": flow_id,
            "status": "started",
            "message": "Exécution du flow démarrée"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution du flow: {str(e)}")


@flow_router.get("/status/{flow_id}")
async def get_flow_status(flow_id: str) -> Dict[str, Any]:
    """Récupère le statut détaillé d'un flow"""
    try:
        flow = orchestrator.get_flow_status(flow_id)
        
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} non trouvé")
        
        return serialize_flow_data(flow)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")


@flow_router.get("/list")
async def list_flows() -> Dict[str, Any]:
    """Liste tous les flows actifs"""
    try:
        flows = orchestrator.get_all_flows()
        
        return {
            "flows": [serialize_flow_data(flow) for flow in flows],
            "total": len(flows),
            "active": len([f for f in flows if f.status == FlowStatus.RUNNING]),
            "completed": len([f for f in flows if f.status == FlowStatus.COMPLETED]),
            "failed": len([f for f in flows if f.status == FlowStatus.FAILED])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des flows: {str(e)}")


@flow_router.post("/pause/{flow_id}")
async def pause_flow(flow_id: str) -> Dict[str, str]:
    """Met en pause un flow"""
    try:
        await orchestrator.pause_flow(flow_id)
        
        return {
            "flow_id": flow_id,
            "status": "paused",
            "message": "Flow mis en pause"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise en pause: {str(e)}")


@flow_router.post("/resume/{flow_id}")
async def resume_flow(flow_id: str) -> Dict[str, str]:
    """Reprend un flow en pause"""
    try:
        await orchestrator.resume_flow(flow_id)
        
        return {
            "flow_id": flow_id,
            "status": "resumed",
            "message": "Flow repris"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la reprise: {str(e)}")


@flow_router.post("/cancel/{flow_id}")
async def cancel_flow(flow_id: str) -> Dict[str, str]:
    """Annule un flow"""
    try:
        await orchestrator.cancel_flow(flow_id)
        
        return {
            "flow_id": flow_id,
            "status": "cancelled",
            "message": "Flow annulé"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'annulation: {str(e)}")


@flow_router.get("/metrics")
async def get_flow_metrics() -> Dict[str, Any]:
    """Récupère les métriques globales des flows"""
    try:
        flows = orchestrator.get_all_flows()
        
        total_flows = len(flows)
        if total_flows == 0:
            return {
                "total_flows": 0,
                "avg_duration": 0,
                "success_rate": 0,
                "agent_performance": {},
                "status_distribution": {}
            }
        
        # Calculer les métriques
        completed_flows = [f for f in flows if f.status == FlowStatus.COMPLETED]
        avg_duration = sum(f.total_duration or 0 for f in completed_flows) / len(completed_flows) if completed_flows else 0
        success_rate = len(completed_flows) / total_flows * 100
        
        # Distribution des statuts
        status_distribution = {}
        for status in FlowStatus:
            count = len([f for f in flows if f.status == status])
            status_distribution[status.value] = count
        
        # Performance par agent
        agent_performance = {}
        for flow in completed_flows:
            for step in flow.steps:
                if step.status == FlowStatus.COMPLETED:
                    if step.agent_name not in agent_performance:
                        agent_performance[step.agent_name] = {
                            "total_executions": 0,
                            "avg_duration": 0,
                            "success_rate": 100,
                            "total_duration": 0
                        }
                    
                    agent_performance[step.agent_name]["total_executions"] += 1
                    agent_performance[step.agent_name]["total_duration"] += step.duration or 0
                    agent_performance[step.agent_name]["avg_duration"] = (
                        agent_performance[step.agent_name]["total_duration"] / 
                        agent_performance[step.agent_name]["total_executions"]
                    )
        
        return {
            "total_flows": total_flows,
            "avg_duration": round(avg_duration, 2),
            "success_rate": round(success_rate, 2),
            "agent_performance": agent_performance,
            "status_distribution": status_distribution,
            "active_flows": len([f for f in flows if f.status == FlowStatus.RUNNING])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques: {str(e)}")


@flow_router.get("/pipeline-config")
async def get_pipeline_config() -> Dict[str, Any]:
    """Récupère la configuration du pipeline d'agents"""
    try:
        return {
            "agents": [
                {
                    "name": agent["name"],
                    "class": agent["class"].__name__,
                    "description": agent["description"],
                    "order": i
                }
                for i, agent in enumerate(orchestrator.agent_pipeline)
            ],
            "total_agents": len(orchestrator.agent_pipeline)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la configuration: {str(e)}")


# WebSocket pour le monitoring temps réel
@flow_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket pour le monitoring temps réel des flows"""
    await websocket_manager.connect(websocket)
    
    try:
        # Envoyer l'état initial
        flows = orchestrator.get_all_flows()
        initial_data = {
            "type": "initial_state",
            "data": {
                "flows": [serialize_flow_data(flow) for flow in flows],
                "metrics": await get_flow_metrics()
            },
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(initial_data))
        
        # Maintenir la connexion
        while True:
            try:
                # Ping périodique pour maintenir la connexion
                await asyncio.sleep(30)
                ping_data = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(ping_data))
                
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket)


# Endpoint pour créer et exécuter un flow en une seule fois
@flow_router.post("/create-and-execute")
async def create_and_execute_flow(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crée et lance immédiatement l'exécution d'un flow"""
    try:
        # Créer le flow avec données normalisées
        if hasattr(case_data, "model_dump"):
            case = case_data.model_dump()
        elif isinstance(case_data, dict):
            case = case_data
        else:
            case = getattr(case_data, "__dict__", {}) or {}

        if not any(k in case for k in ("id", "case_id", "dossier_id", "uuid")):
            case["id"] = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        flow_id = await orchestrator.create_flow(case)

        case_id_val = (
            case.get("id")
            or case.get("case_id")
            or case.get("dossier_id")
            or case.get("uuid")
            or "unknown_case"
        )

        # Lancer l'exécution de manière asynchrone
        asyncio.create_task(orchestrator.execute_flow(flow_id))
        
        return {
            "flow_id": flow_id,
            "case_id": case_id_val,
            "status": "created_and_started",
            "message": "Flow créé et exécution démarrée"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création et exécution du flow: {str(e)}")


# Endpoint pour obtenir les logs détaillés d'un flow
@flow_router.get("/logs/{flow_id}")
async def get_flow_logs(flow_id: str) -> Dict[str, Any]:
    """Récupère les logs détaillés d'un flow"""
    try:
        flow = orchestrator.get_flow_status(flow_id)
        
        if not flow:
            raise HTTPException(status_code=404, detail=f"Flow {flow_id} non trouvé")
        
        logs = []
        
        # Log de création du flow
        logs.append({
            "timestamp": flow.start_time,
            "level": "INFO",
            "message": f"Flow créé pour le dossier {flow.case_id}",
            "agent": "system",
            "step_id": None
        })
        
        # Logs des étapes
        for step in flow.steps:
            if step.start_time:
                logs.append({
                    "timestamp": step.start_time,
                    "level": "INFO",
                    "message": f"Début de l'agent {step.agent_name}",
                    "agent": step.agent_name,
                    "step_id": step.id
                })
            
            if step.end_time:
                level = "ERROR" if step.status == FlowStatus.FAILED else "INFO"
                message = f"Agent {step.agent_name} terminé"
                if step.error:
                    message += f" avec erreur: {step.error}"
                elif step.duration:
                    message += f" en {step.duration:.2f}s"
                
                logs.append({
                    "timestamp": step.end_time,
                    "level": level,
                    "message": message,
                    "agent": step.agent_name,
                    "step_id": step.id,
                    "duration": step.duration,
                    "error": step.error
                })
        
        # Log de fin de flow
        if flow.end_time:
            level = "ERROR" if flow.status == FlowStatus.FAILED else "INFO"
            message = f"Flow terminé avec le statut {flow.status.value}"
            if flow.error:
                message += f": {flow.error}"
            
            logs.append({
                "timestamp": flow.end_time,
                "level": level,
                "message": message,
                "agent": "system",
                "step_id": None,
                "total_duration": flow.total_duration
            })
        
        return {
            "flow_id": flow_id,
            "logs": sorted(logs, key=lambda x: x["timestamp"]),
            "total_logs": len(logs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des logs: {str(e)}")
