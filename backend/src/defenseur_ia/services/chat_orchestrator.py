"""
ChatOrchestrator - Module d'orchestration des interactions utilisateur avec le pipeline DEFENSEUR-IA.

Ce module fournit une interface conversationnelle pour interagir avec le pipeline d'agents existant
tout en préservant l'architecture actuelle.
"""
from typing import Dict, Any, Optional, List, Union
import logging
from enum import Enum
import json
import uuid
from datetime import datetime
import asyncio

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandType(str, Enum):
    """Types de commandes supportées par le ChatOrchestrator."""
    STATUS = "status"
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    UPLOAD = "upload"
    ANALYSE = "analyse"
    RESULTATS = "resultats"
    HISTORIQUE = "historique"
    CONFIG = "config"
    HELP = "help"
    UNKNOWN = "unknown"

class DocumentType(str, Enum):
    """Types de documents supportés."""
    PDF = "pdf"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    EMAIL = "email"

class ChatOrchestrator:
    """
    Orchestrateur des interactions utilisateur avec le pipeline DEFENSEUR-IA.
    
    Gère les commandes utilisateur et les traduit en actions sur le pipeline existant.
    Phase 2: Gestion des documents et commandes avancées.
    """
    
    def __init__(self, pipeline_orchestrator: Any):
        """
        Initialise le ChatOrchestrator avec une référence au pipeline existant.
        
        Args:
            pipeline_orchestrator: Instance du pipeline d'orchestration existant
        """
        self.pipeline = pipeline_orchestrator
        self.active_flows: Dict[str, Dict] = {}
        self.user_sessions: Dict[str, Dict] = {}
        self.document_store: Dict[str, List[Dict]] = {}
        
    async def handle_message(self, message: str, user_id: str, attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Traite un message utilisateur et retourne une réponse.
        
        Args:
            message: Message texte de l'utilisateur
            user_id: Identifiant unique de l'utilisateur
            attachments: Liste des fichiers attachés (optionnel)
            
        Returns:
            Dict contenant la réponse et des métadonnées
        """
        try:
            # Initialisation de la session utilisateur si nécessaire
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    "created_at": datetime.now().isoformat(),
                    "last_activity": datetime.now().isoformat(),
                    "context": {}
                }
            
            # Mise à jour de l'activité
            self.user_sessions[user_id]["last_activity"] = datetime.now().isoformat()
            
            # Gestion des attachments
            if attachments:
                upload_result = await self._handle_document_upload(user_id, attachments)
                if upload_result["status"] == "error":
                    return upload_result
            
            # Détection de l'intention/commande
            command_type, args = self._parse_command(message)
            
            # Traitement de la commande
            if command_type == CommandType.STATUS:
                return await self._handle_status(user_id, args)
            elif command_type == CommandType.START:
                return await self._handle_start(user_id, args)
            elif command_type == CommandType.PAUSE:
                return await self._handle_pause(user_id, args)
            elif command_type == CommandType.RESUME:
                return await self._handle_resume(user_id, args)
            elif command_type == CommandType.CANCEL:
                return await self._handle_cancel(user_id, args)
            elif command_type == CommandType.UPLOAD:
                return await self._handle_upload_command(user_id, args)
            elif command_type == CommandType.ANALYSE:
                return await self._handle_analyse(user_id, args)
            elif command_type == CommandType.RESULTATS:
                return await self._handle_resultats(user_id, args)
            elif command_type == CommandType.HISTORIQUE:
                return await self._handle_historique(user_id, args)
            elif command_type == CommandType.CONFIG:
                return await self._handle_config(user_id, args)
            elif command_type == CommandType.HELP:
                return self._get_help()
            else:
                # Analyse d'intention pour messages non-commandes
                return await self._handle_natural_language(user_id, message)
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message: {str(e)}", exc_info=True)
            return {
                "response": "Une erreur est survenue lors du traitement de votre demande.",
                "status": "error",
                "error": str(e)
            }
    
    def _parse_command(self, message: str) -> tuple[CommandType, List[str]]:
        """
        Analyse le message pour en extraire la commande et ses arguments.
        
        Args:
            message: Message utilisateur à analyser
            
        Returns:
            Tuple (type de commande, arguments)
        """
        if not message.startswith('/'):
            return CommandType.UNKNOWN, []
            
        parts = message[1:].split()
        if not parts:
            return CommandType.UNKNOWN, []
            
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            return CommandType(command), args
        except ValueError:
            return CommandType.UNKNOWN, args
    
    async def _handle_document_upload(self, user_id: str, attachments: List[Dict]) -> Dict[str, Any]:
        """Gère l'upload de documents."""
        try:
            if user_id not in self.document_store:
                self.document_store[user_id] = []
            
            uploaded_docs = []
            for attachment in attachments:
                doc_id = str(uuid.uuid4())
                doc_info = {
                    "id": doc_id,
                    "name": attachment.get("name", "document_sans_nom"),
                    "type": self._detect_document_type(attachment),
                    "size": attachment.get("size", 0),
                    "uploaded_at": datetime.now().isoformat(),
                    "status": "uploaded",
                    "path": attachment.get("path", "")
                }
                
                self.document_store[user_id].append(doc_info)
                uploaded_docs.append(doc_info)
            
            return {
                "response": f"{len(uploaded_docs)} document(s) téléchargé(s) avec succès.",
                "status": "success",
                "documents": uploaded_docs
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'upload: {str(e)}")
            return {
                "response": "Erreur lors du téléchargement des documents.",
                "status": "error",
                "error": str(e)
            }
    
    def _detect_document_type(self, attachment: Dict) -> DocumentType:
        """Détecte le type de document basé sur l'extension."""
        name = attachment.get("name", "").lower()
        if name.endswith(('.pdf',)):
            return DocumentType.PDF
        elif name.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
            return DocumentType.AUDIO
        elif name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            return DocumentType.IMAGE
        elif name.endswith(('.txt', '.doc', '.docx')):
            return DocumentType.TEXT
        elif name.endswith(('.eml', '.msg')):
            return DocumentType.EMAIL
        else:
            return DocumentType.TEXT  # Par défaut
    
    async def _handle_analyse(self, user_id: str, args: List[str]) -> Dict[str, Any]:
        """Gère la commande /analyse."""
        try:
            # Vérifier qu'il y a des documents
            user_docs = self.document_store.get(user_id, [])
            if not user_docs:
                return {
                    "response": "Aucun document trouvé. Veuillez d'abord télécharger des documents avec /upload ou en les attachant à votre message.",
                    "status": "error"
                }
            
            # Créer et démarrer un nouveau flux
            flow_id = self.pipeline.create_flow()
            
            # Configuration du flux avec les documents
            flow_config = {
                "user_id": user_id,
                "documents": user_docs,
                "created_at": datetime.now().isoformat(),
                "status": "analyzing"
            }
            
            self.active_flows[flow_id] = flow_config
            
            # Démarrage asynchrone de l'analyse
            asyncio.create_task(self._run_analysis_flow(flow_id, user_docs))
            
            return {
                "response": f"Analyse démarrée pour {len(user_docs)} document(s). ID du flux: {flow_id}",
                "status": "success",
                "flow_id": flow_id,
                "documents_count": len(user_docs)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de l'analyse: {str(e)}")
            return {
                "response": "Impossible de démarrer l'analyse.",
                "status": "error",
                "error": str(e)
            }
    
    async def _run_analysis_flow(self, flow_id: str, documents: List[Dict]):
        """Exécute le flux d'analyse en arrière-plan."""
        try:
            # Mise à jour du statut
            self.active_flows[flow_id]["status"] = "running"
            
            # Exécution du pipeline avec les documents
            await self.pipeline.execute_flow(flow_id, {"documents": documents})
            
            # Mise à jour du statut final
            self.active_flows[flow_id]["status"] = "completed"
            self.active_flows[flow_id]["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Erreur dans le flux d'analyse {flow_id}: {str(e)}")
            self.active_flows[flow_id]["status"] = "error"
            self.active_flows[flow_id]["error"] = str(e)
    
    async def _handle_resultats(self, user_id: str, args: List[str]) -> Dict[str, Any]:
        """Gère la commande /resultats."""
        if not args:
            # Afficher les résultats des flux récents
            user_flows = {fid: flow for fid, flow in self.active_flows.items() 
                         if flow.get("user_id") == user_id}
            
            if not user_flows:
                return {
                    "response": "Aucun flux trouvé pour cet utilisateur.",
                    "status": "error"
                }
            
            results_summary = []
            for flow_id, flow in user_flows.items():
                results_summary.append(f"• {flow_id}: {flow.get('status', 'inconnu')}")
            
            return {
                "response": f"Résultats disponibles:\n" + "\n".join(results_summary),
                "status": "success",
                "flows": user_flows
            }
        else:
            # Afficher les résultats d'un flux spécifique
            flow_id = args[0]
            if flow_id in self.active_flows:
                flow = self.active_flows[flow_id]
                if flow.get("user_id") != user_id:
                    return {
                        "response": "Accès non autorisé à ce flux.",
                        "status": "error"
                    }
                
                # Récupérer les résultats détaillés du pipeline
                # results = await self.pipeline.get_flow_results(flow_id)
                
                return {
                    "response": f"Résultats du flux {flow_id}:\nStatut: {flow.get('status')}\nDocuments traités: {len(flow.get('documents', []))}",
                    "status": "success",
                    "flow_details": flow
                }
            else:
                return {
                    "response": f"Flux {flow_id} non trouvé.",
                    "status": "error"
                }
    
    async def _handle_historique(self, user_id: str, args: List[str]) -> Dict[str, Any]:
        """Gère la commande /historique."""
        user_flows = {fid: flow for fid, flow in self.active_flows.items() 
                     if flow.get("user_id") == user_id}
        
        if not user_flows:
            return {
                "response": "Aucun historique trouvé.",
                "status": "success"
            }
        
        history_lines = []
        for flow_id, flow in sorted(user_flows.items(), 
                                  key=lambda x: x[1].get("created_at", ""), 
                                  reverse=True):
            created = flow.get("created_at", "")[:19]  # Format: YYYY-MM-DDTHH:MM:SS
            status = flow.get("status", "inconnu")
            doc_count = len(flow.get("documents", []))
            
            history_lines.append(f"• {created} - {flow_id[:8]}... - {status} ({doc_count} docs)")
        
        return {
            "response": f"Historique des analyses:\n" + "\n".join(history_lines),
            "status": "success",
            "history": user_flows
        }
    
    async def _handle_config(self, user_id: str, args: List[str]) -> Dict[str, Any]:
        """Gère la commande /config."""
        if not args:
            # Afficher la configuration actuelle
            session = self.user_sessions.get(user_id, {})
            config = session.get("context", {})
            
            return {
                "response": f"Configuration actuelle:\n{json.dumps(config, indent=2, ensure_ascii=False)}",
                "status": "success",
                "config": config
            }
        else:
            # Modifier la configuration
            # Format: /config key value
            if len(args) >= 2:
                key, value = args[0], " ".join(args[1:])
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = {"context": {}}
                
                self.user_sessions[user_id]["context"][key] = value
                
                return {
                    "response": f"Configuration mise à jour: {key} = {value}",
                    "status": "success"
                }
            else:
                return {
                    "response": "Usage: /config [clé] [valeur]",
                    "status": "error"
                }
    
    async def _handle_natural_language(self, user_id: str, message: str) -> Dict[str, Any]:
        """Gère les messages en langage naturel (analyse d'intention)."""
        message_lower = message.lower()
        
        # Intentions simples basées sur des mots-clés
        if any(word in message_lower for word in ["analyser", "analyse", "traiter", "commencer"]):
            return await self._handle_analyse(user_id, [])
        elif any(word in message_lower for word in ["résultat", "résultats", "voir", "afficher"]):
            return await self._handle_resultats(user_id, [])
        elif any(word in message_lower for word in ["historique", "histoire", "précédent"]):
            return await self._handle_historique(user_id, [])
        elif any(word in message_lower for word in ["aide", "help", "comment"]):
            return self._get_help()
        else:
            return {
                "response": "Je n'ai pas compris votre demande. Tapez /help pour voir les commandes disponibles ou utilisez des mots-clés comme 'analyser', 'résultats', 'historique'.",
                "status": "info"
            }
    
    async def _handle_resume(self, user_id: str, args: List[str]) -> Dict[str, Any]:
        """Gère la commande /resume."""
        if not args:
            return {
                "response": "Veuillez spécifier l'ID du flux à reprendre.",
                "status": "error"
            }
            
        flow_id = args[0]
        if flow_id in self.active_flows:
            flow = self.active_flows[flow_id]
            if flow.get("user_id") != user_id:
                return {
                    "response": "Accès non autorisé à ce flux.",
                    "status": "error"
                }
            
            # Implémenter la logique de reprise dans le pipeline
            # await self.pipeline.resume_flow(flow_id)
            self.active_flows[flow_id]["status"] = "running"
            return {
                "response": f"Flux {flow_id} repris.",
                "status": "success"
            }
        else:
            return {
                "response": f"Aucun flux trouvé avec l'ID {flow_id}.",
                "status": "error"
            }
    
    async def _handle_cancel(self, user_id: str, args: List[str]) -> Dict[str, Any]:
        """Gère la commande /cancel."""
        if not args:
            return {
                "response": "Veuillez spécifier l'ID du flux à annuler.",
                "status": "error"
            }
            
        flow_id = args[0]
        if flow_id in self.active_flows:
            flow = self.active_flows[flow_id]
            if flow.get("user_id") != user_id:
                return {
                    "response": "Accès non autorisé à ce flux.",
                    "status": "error"
                }
            
            # Implémenter la logique d'annulation dans le pipeline
            # await self.pipeline.cancel_flow(flow_id)
            self.active_flows[flow_id]["status"] = "cancelled"
            return {
                "response": f"Flux {flow_id} annulé.",
                "status": "success"
            }
        else:
            return {
                "response": f"Aucun flux trouvé avec l'ID {flow_id}.",
                "status": "error"
            }
    
    async def _handle_upload_command(self, user_id: str, args: List[str]) -> Dict[str, Any]:
        """Gère la commande /upload."""
        return {
            "response": "Pour télécharger des documents, attachez-les directement à votre message ou utilisez la fonction d'upload de l'interface.",
            "status": "info"
        }

    def _get_help(self) -> Dict[str, Any]:
        """Retourne l'aide sur les commandes disponibles."""
        help_text = """
Commandes disponibles:
  /status [flow_id]    - Affiche le statut du système ou d'un flux spécifique
  /start               - Démarre un nouveau flux de traitement
  /pause <flow_id>     - Met en pause un flux en cours
  /resume <flow_id>    - Reprend un flux en pause
  /cancel <flow_id>    - Annule un flux
  /analyse             - Démarre l'analyse des documents téléchargés
  /resultats [flow_id] - Affiche les résultats d'analyse
  /historique          - Affiche l'historique des analyses
  /config [clé] [val]  - Gère la configuration utilisateur
  /upload              - Informations sur l'upload de documents
  /help                - Affiche cette aide

Vous pouvez aussi utiliser le langage naturel:
  "Analyser mes documents"
  "Voir les résultats"
  "Afficher l'historique"
"""
        return {
            "response": help_text.strip(),
            "status": "success"
        }
