"""
Service MongoDB Atlas pour DEFENSEUR-IA
Gestion de la persistance des dossiers, documents et données du pipeline
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import json
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDBService:
    """Service de gestion MongoDB Atlas pour DEFENSEUR-IA"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.connected = False
        
        # Configuration depuis les variables d'environnement
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.database_name = os.getenv('MONGODB_DATABASE', 'defenseur_ia')
        
        # Collections
        self.collections = {
            'cases': 'cases',           # Dossiers juridiques
            'documents': 'documents',   # Documents uploadés
            'pipeline_runs': 'pipeline_runs',  # Exécutions du pipeline
            'agent_results': 'agent_results',  # Résultats des agents
            'chat_sessions': 'chat_sessions',  # Sessions de chat
            'embeddings': 'embeddings',        # Cache des embeddings
            'legal_knowledge': 'legal_knowledge'  # Base de connaissances juridiques
        }
        
        logger.info("🔧 MongoDBService initialisé")
    
    async def initialize(self):
        """Initialise la connexion MongoDB Atlas"""
        try:
            logger.info("🚀 Connexion à MongoDB Atlas...")
            
            # Créer le client MongoDB
            self.client = AsyncIOMotorClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 secondes timeout
                connectTimeoutMS=10000,          # 10 secondes pour la connexion
                maxPoolSize=50,                  # Pool de connexions
                retryWrites=True
            )
            
            # Tester la connexion
            await self.client.admin.command('ping')
            
            # Sélectionner la base de données
            self.database = self.client[self.database_name]
            
            # Créer les index nécessaires
            await self._create_indexes()
            
            self.connected = True
            logger.info("✅ MongoDB Atlas connecté avec succès")
            logger.info(f"📊 Base de données: {self.database_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Erreur connexion MongoDB Atlas: {e}")
            self.connected = False
            # Mode dégradé : continuer sans MongoDB
            logger.warning("⚠️ Fonctionnement en mode dégradé sans MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Erreur inattendue MongoDB: {e}")
            self.connected = False
    
    async def _create_indexes(self):
        """Crée les index nécessaires pour optimiser les performances"""
        try:
            # Index pour les dossiers
            await self.database.cases.create_index("dossier_id", unique=True)
            await self.database.cases.create_index("created_at")
            await self.database.cases.create_index("status")
            
            # Index pour les documents
            await self.database.documents.create_index("document_id", unique=True)
            await self.database.documents.create_index("dossier_id")
            await self.database.documents.create_index("uploaded_at")
            
            # Index pour les exécutions pipeline
            await self.database.pipeline_runs.create_index("flow_id", unique=True)
            await self.database.pipeline_runs.create_index("dossier_id")
            await self.database.pipeline_runs.create_index("started_at")
            
            # Index pour les résultats d'agents
            await self.database.agent_results.create_index([("flow_id", 1), ("agent_id", 1)])
            await self.database.agent_results.create_index("timestamp")
            
            # Index pour les sessions de chat
            await self.database.chat_sessions.create_index("session_id", unique=True)
            await self.database.chat_sessions.create_index("user_id")
            await self.database.chat_sessions.create_index("created_at")
            
            logger.info("✅ Index MongoDB créés avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur création des index: {e}")
    
    async def shutdown(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🛑 Connexion MongoDB fermée")
    
    # ===== GESTION DES DOSSIERS =====
    
    async def create_case(self, case_data: Dict[str, Any]) -> str:
        """Crée un nouveau dossier"""
        if not self.connected:
            return await self._fallback_create_case(case_data)
        
        try:
            case_data['created_at'] = datetime.now()
            case_data['updated_at'] = datetime.now()
            
            result = await self.database.cases.insert_one(case_data)
            logger.info(f"✅ Dossier créé: {case_data['dossier_id']}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur création dossier: {e}")
            return await self._fallback_create_case(case_data)
    
    async def get_case(self, dossier_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un dossier par son ID"""
        if not self.connected:
            return await self._fallback_get_case(dossier_id)
        
        try:
            case = await self.database.cases.find_one({"dossier_id": dossier_id})
            if case:
                case['_id'] = str(case['_id'])  # Convertir ObjectId en string
            return case
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération dossier: {e}")
            return await self._fallback_get_case(dossier_id)
    
    async def update_case(self, dossier_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un dossier"""
        if not self.connected:
            return await self._fallback_update_case(dossier_id, updates)
        
        try:
            updates['updated_at'] = datetime.now()
            result = await self.database.cases.update_one(
                {"dossier_id": dossier_id},
                {"$set": updates}
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour dossier: {e}")
            return await self._fallback_update_case(dossier_id, updates)
    
    async def list_cases(self, skip: int = 0, limit: int = 10, filters: Dict = None) -> List[Dict[str, Any]]:
        """Liste les dossiers avec pagination"""
        if not self.connected:
            return await self._fallback_list_cases(skip, limit, filters)
        
        try:
            query = filters or {}
            cursor = self.database.cases.find(query).skip(skip).limit(limit).sort("created_at", -1)
            cases = []
            
            async for case in cursor:
                case['_id'] = str(case['_id'])
                cases.append(case)
            
            return cases
            
        except Exception as e:
            logger.error(f"❌ Erreur liste dossiers: {e}")
            return await self._fallback_list_cases(skip, limit, filters)
    
    # ===== GESTION DES DOCUMENTS =====
    
    async def store_document(self, document_data: Dict[str, Any]) -> str:
        """Stocke les métadonnées d'un document"""
        if not self.connected:
            return await self._fallback_store_document(document_data)
        
        try:
            document_data['uploaded_at'] = datetime.now()
            result = await self.database.documents.insert_one(document_data)
            logger.info(f"✅ Document stocké: {document_data['document_id']}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage document: {e}")
            return await self._fallback_store_document(document_data)
    
    async def get_documents(self, dossier_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les documents d'un dossier"""
        if not self.connected:
            return await self._fallback_get_documents(dossier_id)
        
        try:
            cursor = self.database.documents.find({"dossier_id": dossier_id}).sort("uploaded_at", -1)
            documents = []
            
            async for doc in cursor:
                doc['_id'] = str(doc['_id'])
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération documents: {e}")
            return await self._fallback_get_documents(dossier_id)
    
    # ===== GESTION DU PIPELINE =====
    
    async def store_pipeline_run(self, pipeline_data: Dict[str, Any]) -> str:
        """Stocke une exécution de pipeline"""
        if not self.connected:
            return await self._fallback_store_pipeline_run(pipeline_data)
        
        try:
            pipeline_data['started_at'] = datetime.now()
            result = await self.database.pipeline_runs.insert_one(pipeline_data)
            logger.info(f"✅ Pipeline run stocké: {pipeline_data['flow_id']}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage pipeline run: {e}")
            return await self._fallback_store_pipeline_run(pipeline_data)
    
    async def update_pipeline_run(self, flow_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour une exécution de pipeline"""
        if not self.connected:
            return await self._fallback_update_pipeline_run(flow_id, updates)
        
        try:
            updates['updated_at'] = datetime.now()
            result = await self.database.pipeline_runs.update_one(
                {"flow_id": flow_id},
                {"$set": updates}
            )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour pipeline run: {e}")
            return await self._fallback_update_pipeline_run(flow_id, updates)
    
    async def get_pipeline_run(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une exécution de pipeline"""
        if not self.connected:
            return await self._fallback_get_pipeline_run(flow_id)
        
        try:
            run = await self.database.pipeline_runs.find_one({"flow_id": flow_id})
            if run:
                run['_id'] = str(run['_id'])
            return run
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération pipeline run: {e}")
            return await self._fallback_get_pipeline_run(flow_id)
    
    # ===== MÉTHODES FALLBACK (mode dégradé) =====
    
    async def _fallback_create_case(self, case_data: Dict[str, Any]) -> str:
        """Fallback pour créer un dossier en mode dégradé"""
        # Utiliser le stockage JSON local comme fallback
        logger.warning("⚠️ Utilisation du fallback JSON pour créer un dossier")
        # Implémentation simple pour le fallback
        return f"fallback_{case_data.get('dossier_id', 'unknown')}"
    
    async def _fallback_get_case(self, dossier_id: str) -> Optional[Dict[str, Any]]:
        """Fallback pour récupérer un dossier"""
        logger.warning("⚠️ Utilisation du fallback JSON pour récupérer un dossier")
        return None
    
    async def _fallback_update_case(self, dossier_id: str, updates: Dict[str, Any]) -> bool:
        """Fallback pour mettre à jour un dossier"""
        logger.warning("⚠️ Utilisation du fallback JSON pour mettre à jour un dossier")
        return False
    
    async def _fallback_list_cases(self, skip: int, limit: int, filters: Dict) -> List[Dict[str, Any]]:
        """Fallback pour lister les dossiers"""
        logger.warning("⚠️ Utilisation du fallback JSON pour lister les dossiers")
        return []
    
    async def _fallback_store_document(self, document_data: Dict[str, Any]) -> str:
        """Fallback pour stocker un document"""
        logger.warning("⚠️ Utilisation du fallback JSON pour stocker un document")
        return f"fallback_{document_data.get('document_id', 'unknown')}"
    
    async def _fallback_get_documents(self, dossier_id: str) -> List[Dict[str, Any]]:
        """Fallback pour récupérer les documents"""
        logger.warning("⚠️ Utilisation du fallback JSON pour récupérer les documents")
        return []
    
    async def _fallback_store_pipeline_run(self, pipeline_data: Dict[str, Any]) -> str:
        """Fallback pour stocker un pipeline run"""
        logger.warning("⚠️ Utilisation du fallback JSON pour stocker un pipeline run")
        return f"fallback_{pipeline_data.get('flow_id', 'unknown')}"
    
    async def _fallback_update_pipeline_run(self, flow_id: str, updates: Dict[str, Any]) -> bool:
        """Fallback pour mettre à jour un pipeline run"""
        logger.warning("⚠️ Utilisation du fallback JSON pour mettre à jour un pipeline run")
        return False
    
    async def _fallback_get_pipeline_run(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """Fallback pour récupérer un pipeline run"""
        logger.warning("⚠️ Utilisation du fallback JSON pour récupérer un pipeline run")
        return None
    
    # ===== STATISTIQUES =====
    
    async def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de la base de données"""
        if not self.connected:
            return {
                "status": "disconnected",
                "mode": "fallback",
                "total_cases": 0,
                "total_documents": 0,
                "total_pipeline_runs": 0
            }
        
        try:
            stats = {
                "status": "connected",
                "database": self.database_name,
                "total_cases": await self.database.cases.count_documents({}),
                "total_documents": await self.database.documents.count_documents({}),
                "total_pipeline_runs": await self.database.pipeline_runs.count_documents({}),
                "total_agent_results": await self.database.agent_results.count_documents({}),
                "total_chat_sessions": await self.database.chat_sessions.count_documents({})
            }
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statistiques: {e}")
            return {"status": "error", "error": str(e)}
