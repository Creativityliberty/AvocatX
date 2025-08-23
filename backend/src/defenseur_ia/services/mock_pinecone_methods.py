"""
Méthodes mock pour PineconeService en mode simulation
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import random

logger = logging.getLogger(__name__)

class MockPineconeMethods:
    """Méthodes mock pour simuler Pinecone"""
    
    def add_mock_methods(self, pinecone_service):
        """Ajoute les méthodes mock au service Pinecone"""
        
        async def mock_query(self, index_name: str, vector: List[float], 
                           top_k: int = 10, namespace: str = "", 
                           filter_dict: Dict = None, include_metadata: bool = True):
            """Query mock simulé"""
            if not self.simulation_mode:
                return await self._real_query(index_name, vector, top_k, namespace, filter_dict, include_metadata)
                
            self.mock_stats['queries_count'] += 1
            
            # Simulation de résultats
            mock_results = []
            for i in range(min(top_k, 3)):  # Simuler 3 résultats max
                mock_results.append({
                    "id": f"mock_result_{i}",
                    "score": random.uniform(0.7, 0.95),
                    "metadata": {
                        "text": f"Résultat simulé {i}",
                        "type": "mock_data",
                        "timestamp": datetime.now().isoformat()
                    } if include_metadata else {}
                })
            
            return {"matches": mock_results}
        
        async def mock_upsert(self, index_name: str, vectors: List[Dict], namespace: str = ""):
            """Upsert mock simulé"""
            if not self.simulation_mode:
                return await self._real_upsert(index_name, vectors, namespace)
                
            self.mock_stats['upserts_count'] += len(vectors)
            self.mock_stats['total_vectors'] += len(vectors)
            
            # Stocker dans les données mock
            if index_name not in self.mock_data:
                self.mock_data[index_name] = []
            
            for vector in vectors:
                self.mock_data[index_name].append({
                    "id": vector.get("id", f"mock_{len(self.mock_data[index_name])}"),
                    "values": vector.get("values", [0.0] * self.embedding_dimension),
                    "metadata": vector.get("metadata", {}),
                    "namespace": namespace,
                    "timestamp": datetime.now().isoformat()
                })
            
            logger.info(f"✅ Mock upsert: {len(vectors)} vecteurs dans {index_name}")
            return {"upserted_count": len(vectors)}
        
        async def mock_get_stats(self):
            """Statistiques mock"""
            if not self.simulation_mode:
                return await self._real_get_stats()
                
            return {
                "status": "simulation",
                "total_vectors": self.mock_stats['total_vectors'],
                "indexes": list(self.mock_data.keys()),
                "indexes_count": self.mock_stats['indexes_count'],
                "queries_count": self.mock_stats['queries_count'],
                "upserts_count": self.mock_stats['upserts_count'],
                "simulation_mode": True
            }
        
        async def mock_list_indexes(self):
            """Liste des index mock"""
            if not self.simulation_mode:
                return await self._real_list_indexes()
                
            return [{"name": name, "dimension": self.embedding_dimension, "metric": "cosine"} 
                   for name in self.mock_data.keys()]
        
        async def mock_create_embedding(self, text: str):
            """Embedding mock simulé"""
            if not self.simulation_mode and self.openai_client:
                return await self._real_create_embedding(text)
                
            # Simuler un embedding avec des valeurs aléatoires normalisées
            import numpy as np
            embedding = np.random.normal(0, 1, self.embedding_dimension)
            embedding = embedding / np.linalg.norm(embedding)  # Normaliser
            return embedding.tolist()
        
        # Attacher les méthodes au service
        pinecone_service.query = mock_query.__get__(pinecone_service, type(pinecone_service))
        pinecone_service.upsert = mock_upsert.__get__(pinecone_service, type(pinecone_service))
        pinecone_service.get_stats = mock_get_stats.__get__(pinecone_service, type(pinecone_service))
        pinecone_service.list_indexes = mock_list_indexes.__get__(pinecone_service, type(pinecone_service))
        pinecone_service.create_embedding = mock_create_embedding.__get__(pinecone_service, type(pinecone_service))
        
        logger.info("🔧 Méthodes mock ajoutées au PineconeService")
