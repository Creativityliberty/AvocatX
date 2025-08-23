"""
Service de stockage pour DEFENSEUR-IA
Gère la persistance des données dans Redis et PostgreSQL
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import redis
import asyncpg
from defenseur_ia.config.settings import settings

logger = logging.getLogger(__name__)

class StorageService:
    """
    Service de stockage unifié pour Redis et PostgreSQL
    """
    
    def __init__(self):
        self.redis_client = None
        self.pg_pool = None
    
    async def initialize(self):
        """Initialise les connexions"""
        try:
            # Connexion Redis (optionnelle)
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True
                )
                # Test de connexion
                self.redis_client.ping()
                logger.info("✅ Redis connecté")
            except Exception as e:
                logger.warning(f"⚠️ Redis non disponible: {e}")
                self.redis_client = None
            
            # Connexion PostgreSQL (optionnelle)
            try:
                self.pg_pool = await asyncpg.create_pool(
                    host=settings.POSTGRES_HOST,
                    port=settings.POSTGRES_PORT,
                    database=settings.POSTGRES_DB,
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD
                )
                logger.info("✅ PostgreSQL connecté")
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL non disponible: {e}")
                self.pg_pool = None
            
            logger.info("✅ StorageService initialisé (mode développement)")
            
        except Exception as e:
            logger.error(f"❌ Erreur critique initialisation StorageService: {e}")
            # Ne pas lever d'exception pour permettre le démarrage en mode dev
            logger.warning("⚠️ Démarrage en mode dégradé sans base de données")
    
    async def shutdown(self):
        """Ferme les connexions"""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            self.redis_client.close()
    
    async def get_case(self, dossier_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un dossier"""
        try:
            # Mode JSON : lecture depuis fichier
            import os
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            case_file = os.path.join(data_dir, f"case_{dossier_id}.json")
            if os.path.exists(case_file):
                with open(case_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback Redis si disponible
            if self.redis_client:
                try:
                    case_data = self.redis_client.get(f"case:{dossier_id}")
                    if case_data:
                        return json.loads(case_data)
                except Exception as e:
                    logger.warning(f"Erreur Redis: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération case {dossier_id}: {e}")
            return None
    
    async def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau dossier"""
        try:
            dossier_id = case_data.get("dossier_id")
            
            # Mode JSON : sauvegarde dans fichier
            import os
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            case_data["created_at"] = datetime.now().isoformat()
            case_data["updated_at"] = datetime.now().isoformat()
            
            case_file = os.path.join(data_dir, f"case_{dossier_id}.json")
            with open(case_file, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2, ensure_ascii=False)
            
            # Fallback Redis si disponible
            if self.redis_client:
                try:
                    self.redis_client.setex(
                        f"case:{dossier_id}",
                        3600,  # 1 heure TTL
                        json.dumps(case_data)
                    )
                except Exception as e:
                    logger.warning(f"Erreur Redis: {e}")
            
            logger.info(f"✅ Dossier {dossier_id} sauvegardé en JSON")
            return case_data
            
        except Exception as e:
            logger.error(f"Erreur création case: {e}")
            raise
    
    async def update_case(self, dossier_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un dossier"""
        try:
            # Récupération actuelle
            current = await self.get_case(dossier_id)
            if not current:
                return False
            
            # Mise à jour
            updated = {**current, **updates}
            updated["updated_at"] = datetime.now().isoformat()
            
            # Mode JSON : sauvegarde dans fichier
            import os
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            case_file = os.path.join(data_dir, f"case_{dossier_id}.json")
            with open(case_file, 'w', encoding='utf-8') as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)
            
            # Fallback Redis si disponible
            if self.redis_client:
                try:
                    self.redis_client.setex(
                        f"case:{dossier_id}",
                        3600,
                        json.dumps(updated)
                    )
                except Exception as e:
                    logger.warning(f"Erreur Redis: {e}")
            
            logger.info(f"✅ Dossier {dossier_id} mis à jour en JSON")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour case {dossier_id}: {e}")
            return False
    
    async def get_cases(self, skip: int = 0, limit: int = 10, **filters) -> List[Dict[str, Any]]:
        """Récupère la liste des dossiers"""
        try:
            async with self.pg_pool.acquire() as conn:
                query = "SELECT * FROM cases"
                params = []
                
                if filters:
                    conditions = []
                    for key, value in filters.items():
                        if value is not None:
                            conditions.append(f"data->>'{key}' = ${len(params) + 1}")
                            params.append(value)
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                
                query += f" ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, skip])
                
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Erreur récupération cases: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales"""
        try:
            async with self.pg_pool.acquire() as conn:
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_cases,
                        COUNT(CASE WHEN data->>'status' = 'completed' THEN 1 END) as completed_cases,
                        COUNT(CASE WHEN data->>'status' = 'processing' THEN 1 END) as processing_cases,
                        COUNT(CASE WHEN data->>'status' = 'error' THEN 1 END) as error_cases
                    FROM cases
                """)
                return dict(stats)
                
        except Exception as e:
            logger.error(f"Erreur récupération stats: {e}")
            return {"total_cases": 0, "completed_cases": 0, "processing_cases": 0, "error_cases": 0}
