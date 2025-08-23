# enhanced_mongodb_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from typing import Optional, Dict, List, Any
import asyncio
from datetime import datetime, timedelta
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class EnhancedMongoDBService:
    """Service MongoDB optimisé pour DEFENSEUR-IA avec cache intelligent"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collections = {
            'dossiers': 'dossiers',
            'narrations': 'narrations', 
            'axes': 'axes_juridiques',
            'pieces': 'pieces_justificatives',
            'legal_corpus': 'legal_articles',
            'matches': 'piece_article_matches',
            'drafts': 'drafts_narratifs',
            'plans': 'plans_strategiques',
            'requetes': 'requetes_finales',
            'logs': 'execution_logs',
            'cache': 'api_cache',
            'embeddings': 'embeddings_cache',
            'agent_configs': 'agent_configurations',
            'flow_runs': 'flow_executions'
        }
        
        # Cache en mémoire pour les requêtes fréquentes
        self.memory_cache = {}
        self.cache_ttl = timedelta(minutes=30)
    
    async def connect(self, connection_string: str, database_name: str = "defenseur_ia"):
        """Connexion à MongoDB Atlas avec pool optimisé"""
        try:
            self.client = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000,
                retryWrites=True,
                w="majority"
            )
            self.db = self.client[database_name]
            
            # Test de connexion
            await self.client.admin.command('ping')
            logger.info("✅ Connexion MongoDB Atlas établie")
            
            # Création des index optimisés
            await self._create_optimized_indexes()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion MongoDB: {str(e)}")
            return False
    
    async def _create_optimized_indexes(self):
        """Création des index pour performance maximale"""
        
        index_definitions = {
            'dossiers': [
                ("dossier_id", 1),
                ("created_at", -1),
                ("meta.type_contentieux", 1),
                ("status", 1),
                ("completion_rate", -1),
                [("meta.client_name", "text"), ("meta.description", "text")]  # Index texte
            ],
            'pieces': [
                ("dossier_id", 1),
                ("id_piece", 1),
                ("type_piece", 1),
                ("hash_fichier", 1),
                ("is_virtual", 1),
                ("created_at", -1),
                [("titre", "text"), ("resume_automatique", "text")]
            ],
            'matches': [
                ("dossier_id", 1),
                ("piece_id", 1),
                ("article_cid", 1),
                ("similarite_score", -1),
                ("type_correspondance", 1),
                ("created_at", -1)
            ],
            'legal_corpus': [
                ("cid", 1),
                ("numero", 1),
                ("code_nom", 1),
                ("etat_juridique", 1),
                ("date_version", -1),
                [("titre", "text"), ("texte_brut", "text")]
            ],
            'embeddings': [
                ("content_hash", 1),
                ("model_type", 1),
                ("created_at", -1),
                ("expires_at", 1)
            ],
            'cache': [
                ("cache_key", 1),
                ("service", 1),
                ("expires_at", 1),
                ("created_at", -1)
            ],
            'flow_runs': [
                ("flow_id", 1),
                ("dossier_id", 1),
                ("status", 1),
                ("created_at", -1),
                ("agent_id", 1)
            ]
        }
        
        for collection_name, indexes in index_definitions.items():
            collection = self.db[self.collections[collection_name]]
            
            for index in indexes:
                try:
                    if isinstance(index, list):
                        # Index composé ou texte
                        await collection.create_index(index)
                    else:
                        # Index simple
                        await collection.create_index([index])
                except Exception as e:
                    logger.debug(f"Index déjà existant pour {collection_name}: {index}")
    
    # === OPERATIONS DOSSIERS OPTIMISÉES ===
    
    async def save_dossier_complete(self, dossier_data: Dict) -> str:
        """Sauvegarde complète d'un dossier avec transaction atomique"""
        
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                try:
                    dossier_id = dossier_data["meta"]["dossier_id"]
                    
                    # Enrichissement automatique des métadonnées
                    dossier_data["updated_at"] = datetime.utcnow().isoformat()
                    dossier_data["version"] = dossier_data.get("version", 1) + 1
                    
                    # Sauvegarde du dossier principal
                    await self.db[self.collections['dossiers']].replace_one(
                        {"dossier_id": dossier_id},
                        dossier_data,
                        upsert=True,
                        session=session
                    )
                    
                    # Sauvegarde des sous-collections
                    if "pieces" in dossier_data:
                        await self._save_pieces_batch(dossier_id, dossier_data["pieces"], session)
                    
                    if "matches" in dossier_data:
                        await self._save_matches_batch(dossier_id, dossier_data["matches"], session)
                    
                    if "axes" in dossier_data:
                        await self._save_axes_batch(dossier_id, dossier_data["axes"], session)
                    
                    # Log de l'opération
                    await self._log_operation("save_dossier", dossier_id, "success", session)
                    
                    await session.commit_transaction()
                    
                    # Invalidation du cache
                    self._invalidate_cache(f"dossier_{dossier_id}")
                    
                    logger.info(f"✅ Dossier {dossier_id} sauvegardé avec succès")
                    return dossier_id
                    
                except Exception as e:
                    await session.abort_transaction()
                    logger.error(f"❌ Erreur sauvegarde dossier {dossier_id}: {str(e)}")
                    raise Exception(f"Erreur sauvegarde dossier: {str(e)}")
    
    async def _save_pieces_batch(self, dossier_id: str, pieces: List[Dict], session):
        """Sauvegarde optimisée des pièces en batch"""
        if not pieces:
            return
        
        # Enrichissement des pièces
        for piece in pieces:
            piece["dossier_id"] = dossier_id
            piece["updated_at"] = datetime.utcnow().isoformat()
            if "hash_fichier" not in piece and "contenu" in piece:
                piece["hash_fichier"] = hashlib.md5(piece["contenu"].encode()).hexdigest()
        
        # Upsert en batch avec gestion d'erreurs
        operations = []
        for piece in pieces:
            operations.append({
                "replaceOne": {
                    "filter": {"dossier_id": dossier_id, "id_piece": piece["id_piece"]},
                    "replacement": piece,
                    "upsert": True
                }
            })
        
        if operations:
            result = await self.db[self.collections['pieces']].bulk_write(
                operations, 
                session=session,
                ordered=False  # Continue même si certaines opérations échouent
            )
            logger.debug(f"Pièces sauvegardées: {result.upserted_count + result.modified_count}")
    
    async def load_dossier_complete(self, dossier_id: str, include_relations: bool = True) -> Optional[Dict]:
        """Chargement complet d'un dossier avec cache intelligent"""
        
        # Vérification du cache mémoire
        cache_key = f"dossier_{dossier_id}_complete"
        if cache_key in self.memory_cache:
            cached_data, cached_time = self.memory_cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.debug(f"🎯 Cache hit pour dossier {dossier_id}")
                return cached_data
        
        try:
            # Dossier principal
            dossier = await self.db[self.collections['dossiers']].find_one(
                {"dossier_id": dossier_id}
            )
            
            if not dossier:
                return None
            
            if include_relations:
                # Chargement des relations en parallèle
                tasks = [
                    self._load_pieces(dossier_id),
                    self._load_matches(dossier_id),
                    self._load_axes(dossier_id),
                    self._load_recent_logs(dossier_id)
                ]
                
                pieces, matches, axes, logs = await asyncio.gather(*tasks)
                
                # Reconstruction du dossier complet
                if pieces:
                    dossier["pieces"] = pieces
                if matches:
                    dossier["matches"] = matches
                if axes:
                    dossier["axes"] = axes
                if logs:
                    dossier["logs"] = {"recent": logs}
            
            # Mise en cache
            self.memory_cache[cache_key] = (dossier, datetime.now())
            
            return dossier
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement dossier {dossier_id}: {str(e)}")
            return None
    
    async def _load_pieces(self, dossier_id: str) -> List[Dict]:
        """Chargement optimisé des pièces"""
        cursor = self.db[self.collections['pieces']].find(
            {"dossier_id": dossier_id}
        ).sort("annexe_numero", 1)
        return await cursor.to_list(None)
    
    async def _load_matches(self, dossier_id: str) -> List[Dict]:
        """Chargement optimisé des matches"""
        cursor = self.db[self.collections['matches']].find(
            {"dossier_id": dossier_id}
        ).sort("similarite_score", -1).limit(100)
        return await cursor.to_list(None)
    
    # === RECHERCHE ET ANALYTICS AVANCÉES ===
    
    async def search_dossiers_advanced(self, 
                                     filters: Dict = None, 
                                     text_search: str = None,
                                     limit: int = 50,
                                     skip: int = 0) -> Dict:
        """Recherche avancée avec filtres et texte"""
        
        query = {}
        
        # Filtres structurés
        if filters:
            if "type_contentieux" in filters:
                query["meta.type_contentieux"] = filters["type_contentieux"]
            if "status" in filters:
                query["status"] = filters["status"]
            if "date_debut" in filters and "date_fin" in filters:
                query["created_at"] = {
                    "$gte": filters["date_debut"],
                    "$lte": filters["date_fin"]
                }
            if "completion_min" in filters:
                query["completion_rate"] = {"$gte": filters["completion_min"]}
        
        # Recherche textuelle
        if text_search:
            query["$text"] = {"$search": text_search}
        
        # Exécution de la recherche
        cursor = self.db[self.collections['dossiers']].find(query)
        
        if text_search:
            cursor = cursor.sort([("score", {"$meta": "textScore"})])
        else:
            cursor = cursor.sort("created_at", -1)
        
        cursor = cursor.skip(skip).limit(limit)
        
        # Comptage total
        total_count = await self.db[self.collections['dossiers']].count_documents(query)
        
        results = await cursor.to_list(None)
        
        return {
            "dossiers": results,
            "total": total_count,
            "page": skip // limit + 1,
            "pages": (total_count + limit - 1) // limit
        }
    
    async def get_analytics_dashboard(self) -> Dict:
        """Analytics complètes pour le dashboard"""
        
        # Pipeline d'agrégation pour les statistiques
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "type": "$meta.type_contentieux",
                        "status": "$status"
                    },
                    "count": {"$sum": 1},
                    "avg_completion": {"$avg": "$completion_rate"},
                    "total_pieces": {"$sum": {"$size": {"$ifNull": ["$pieces", []]}}},
                    "avg_processing_time": {"$avg": "$processing_time_seconds"}
                }
            },
            {
                "$group": {
                    "_id": "$_id.type",
                    "stats_by_status": {
                        "$push": {
                            "status": "$_id.status",
                            "count": "$count",
                            "avg_completion": "$avg_completion",
                            "total_pieces": "$total_pieces",
                            "avg_processing_time": "$avg_processing_time"
                        }
                    },
                    "total_dossiers": {"$sum": "$count"}
                }
            }
        ]
        
        stats_by_type = await self.db[self.collections['dossiers']].aggregate(pipeline).to_list(None)
        
        # Statistiques globales
        total_dossiers = await self.db[self.collections['dossiers']].count_documents({})
        total_pieces = await self.db[self.collections['pieces']].count_documents({})
        total_matches = await self.db[self.collections['matches']].count_documents({})
        
        # Activité récente (dernières 24h)
        yesterday = datetime.now() - timedelta(days=1)
        recent_activity = await self.db[self.collections['dossiers']].count_documents({
            "created_at": {"$gte": yesterday.isoformat()}
        })
        
        # Performance des agents (dernière semaine)
        week_ago = datetime.now() - timedelta(days=7)
        agent_performance = await self.db[self.collections['logs']].aggregate([
            {"$match": {"timestamp": {"$gte": week_ago.isoformat()}, "level": "INFO"}},
            {"$group": {
                "_id": "$agent_id",
                "executions": {"$sum": 1},
                "avg_duration": {"$avg": "$duration_seconds"},
                "success_rate": {
                    "$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}
                }
            }},
            {"$sort": {"executions": -1}}
        ]).to_list(None)
        
        return {
            "totals": {
                "dossiers": total_dossiers,
                "pieces": total_pieces,
                "matches": total_matches,
                "recent_activity": recent_activity
            },
            "by_type": stats_by_type,
            "agent_performance": agent_performance,
            "database_size": await self._get_database_size(),
            "cache_stats": self._get_cache_stats()
        }
    
    # === GESTION DU CACHE ===
    
    def _invalidate_cache(self, pattern: str):
        """Invalidation du cache par pattern"""
        keys_to_remove = [key for key in self.memory_cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.memory_cache[key]
    
    def _get_cache_stats(self) -> Dict:
        """Statistiques du cache mémoire"""
        return {
            "entries": len(self.memory_cache),
            "memory_usage_mb": sum(
                len(str(data).encode()) for data, _ in self.memory_cache.values()
            ) / (1024 * 1024)
        }
    
    async def _get_database_size(self) -> Dict:
        """Taille de la base de données"""
        try:
            stats = await self.db.command("dbStats")
            return {
                "data_size_mb": stats.get("dataSize", 0) / (1024 * 1024),
                "storage_size_mb": stats.get("storageSize", 0) / (1024 * 1024),
                "index_size_mb": stats.get("indexSize", 0) / (1024 * 1024),
                "collections": stats.get("collections", 0)
            }
        except:
            return {"error": "Unable to get database stats"}
    
    async def _log_operation(self, operation: str, dossier_id: str, status: str, session=None):
        """Logging des opérations"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "dossier_id": dossier_id,
            "status": status,
            "service": "mongodb"
        }
        
        await self.db[self.collections['logs']].insert_one(log_entry, session=session)
    
    async def close(self):
        """Fermeture propre de la connexion"""
        if self.client:
            self.client.close()
            logger.info("🔌 Connexion MongoDB fermée")

# Instance globale
enhanced_mongodb_service = EnhancedMongoDBService()
