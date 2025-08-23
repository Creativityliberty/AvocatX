"""
WebSocket Manager pour le monitoring temps réel du pipeline DEFENSEUR-IA
"""

import asyncio
import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Gestionnaire des connexions WebSocket pour le monitoring temps réel
    du pipeline DEFENSEUR-IA.
    """
    
    def __init__(self):
        # Dictionnaire: dossier_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, dossier_id: str) -> None:
        """Accepte une nouvelle connexion WebSocket pour un dossier"""
        await websocket.accept()
        
        async with self._lock:
            if dossier_id not in self.active_connections:
                self.active_connections[dossier_id] = set()
            self.active_connections[dossier_id].add(websocket)
        
        logger.info(f"WebSocket connected for dossier {dossier_id}")
        
        # Envoyer un message de bienvenue
        await self.send_to_dossier(dossier_id, {
            "type": "connection_established",
            "dossier_id": dossier_id,
            "message": "Connexion établie pour le monitoring du pipeline"
        })
    
    async def disconnect(self, websocket: WebSocket, dossier_id: str) -> None:
        """Déconnecte un WebSocket d'un dossier"""
        async with self._lock:
            if dossier_id in self.active_connections:
                self.active_connections[dossier_id].discard(websocket)
                
                # Nettoyer si plus de connexions pour ce dossier
                if not self.active_connections[dossier_id]:
                    del self.active_connections[dossier_id]
        
        logger.info(f"WebSocket disconnected for dossier {dossier_id}")
    
    async def send_to_dossier(self, dossier_id: str, message: dict) -> None:
        """Envoie un message à toutes les connexions d'un dossier"""
        async with self._lock:
            if dossier_id not in self.active_connections:
                return
            
            connections = self.active_connections[dossier_id].copy()
        
        # Envoyer le message à toutes les connexions actives
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(message, default=str))
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Nettoyer les connexions fermées
        if disconnected:
            async with self._lock:
                if dossier_id in self.active_connections:
                    for ws in disconnected:
                        self.active_connections[dossier_id].discard(ws)
    
    async def broadcast_pipeline_update(self, dossier_id: str, agent_id: str, 
                                      status: str, message: str = "", 
                                      progress: float = 0.0, **kwargs) -> None:
        """
        Diffuse une mise à jour du pipeline à toutes les connexions d'un dossier
        
        Args:
            dossier_id: ID du dossier
            agent_id: ID de l'agent en cours
            status: Statut (started, progress, completed, error)
            message: Message descriptif
            progress: Progression (0.0 à 1.0)
            **kwargs: Données additionnelles
        """
        update_message = {
            "type": "pipeline_update",
            "dossier_id": dossier_id,
            "agent_id": agent_id,
            "status": status,
            "message": message,
            "progress": progress,
            "timestamp": asyncio.get_event_loop().time(),
            **kwargs
        }
        
        await self.send_to_dossier(dossier_id, update_message)
        logger.debug(f"Pipeline update sent for {dossier_id}: {agent_id} - {status}")
    
    async def send_error(self, dossier_id: str, error_message: str, 
                        agent_id: str = None) -> None:
        """Envoie un message d'erreur"""
        error_msg = {
            "type": "error",
            "dossier_id": dossier_id,
            "agent_id": agent_id,
            "error": error_message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.send_to_dossier(dossier_id, error_msg)
    
    async def send_completion(self, dossier_id: str, result_data: dict = None) -> None:
        """Envoie un message de completion du pipeline"""
        completion_msg = {
            "type": "pipeline_completed",
            "dossier_id": dossier_id,
            "result": result_data or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.send_to_dossier(dossier_id, completion_msg)
    
    def get_active_connections_count(self, dossier_id: str = None) -> int:
        """Retourne le nombre de connexions actives"""
        if dossier_id:
            return len(self.active_connections.get(dossier_id, set()))
        else:
            return sum(len(connections) for connections in self.active_connections.values())
    
    def get_active_dossiers(self) -> List[str]:
        """Retourne la liste des dossiers avec des connexions actives"""
        return list(self.active_connections.keys())
