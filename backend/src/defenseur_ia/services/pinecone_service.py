"""
Service Pinecone pour la base de données vectorielle DEFENSEUR-IA
Gestion de la mémoire sémantique et de l'apprentissage multi-agents
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

# Mock imports pour éviter les dépendances manquantes
try:
    from pinecone.grpc import PineconeGRPC as Pinecone
    from pinecone import ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Pinecone non disponible - mode simulation activé")
    Pinecone = None
    ServerlessSpec = None
    PINECONE_AVAILABLE = False

import numpy as np
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from ..core.config import settings
except ImportError:
    # Configuration par défaut en mode simulation
    class MockSettings:
        PINECONE_API_KEY = "mock_key"
        PINECONE_ENVIRONMENT = "mock_env"
    settings = MockSettings()

try:
    from .mock_pinecone_methods import MockPineconeMethods
except ImportError:
    MockPineconeMethods = None

logger = logging.getLogger(__name__)


class PineconeService:
    """
    Service de gestion de la base de données vectorielle Pinecone
    pour la mémoire sémantique des agents DEFENSEUR-IA
    """
    
    def __init__(self):
        self.pc = None
        self.openai_client = None
        self.indexes = {}
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small
        self.simulation_mode = False  # Forcer l'utilisation de la vraie API
        
        if self.simulation_mode:
            logger.warning("⚠️ PineconeService en mode simulation")
            # Données simulées pour les tests
            self.mock_data = {}
            self.mock_stats = {
                "total_vectors": 0,
                "indexes_count": 0,
                "queries_count": 0,
                "upserts_count": 0
            }
            # Ajouter les méthodes mock
            if MockPineconeMethods:
                mock_methods = MockPineconeMethods()
                mock_methods.add_mock_methods(self)
        
        # Configuration des index par type de données
        self.index_configs = {
            "agent_experiences": {
                "name": "defenseur-ia-experiences",
                "dimension": self.embedding_dimension,
                "metric": "cosine",
                "description": "Expériences et apprentissages des agents"
            },
            "legal_knowledge": {
                "name": "defenseur-ia-legal-kb",
                "dimension": self.embedding_dimension,
                "metric": "cosine",
                "description": "Base de connaissances juridiques"
            },
            "case_contexts": {
                "name": "defenseur-ia-cases",
                "dimension": self.embedding_dimension,
                "metric": "cosine",
                "description": "Contextes et historiques de dossiers"
            },
            "reasoning_patterns": {
                "name": "defenseur-ia-reasoning",
                "dimension": self.embedding_dimension,
                "metric": "cosine",
                "description": "Patterns de raisonnement et solutions"
            }
        }
        
        logger.info("🔧 PineconeService initialisé")
    
    async def initialize(self):
        """Initialise la connexion Pinecone et les index"""
        if self.simulation_mode:
            logger.info("🔧 PineconeService en mode simulation - initialisation mock")
            # Initialiser les données simulées
            for index_type, config in self.index_configs.items():
                self.mock_data[config['name']] = []
                self.mock_stats['indexes_count'] += 1
            logger.info("✅ PineconeService simulé initialisé avec succès")
            return
            
        try:
            # Initialiser Pinecone réel
            api_key = getattr(settings, 'PINECONE_API_KEY', None)
            if not api_key:
                logger.warning("⚠️ PINECONE_API_KEY non définie - basculement en mode simulation")
                self.simulation_mode = True
                await self.initialize()  # Réinitialiser en mode simulation
                return
            self.pc = Pinecone(api_key=api_key)
            
            # Initialiser OpenAI pour les embeddings
            if OpenAI:
                openai_key = getattr(settings, 'OPENAI_API_KEY', None)
                if openai_key:
                    self.openai_client = OpenAI(api_key=openai_key)
                else:
                    logger.warning("⚠️ OPENAI_API_KEY non définie - embeddings désactivés")
            
            # Créer ou vérifier les index
            await self._ensure_indexes_exist()
            
            logger.info("✅ PineconeService initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation PineconeService: {e}")
            # Basculer en mode simulation
            self.simulation_mode = True
            self.pc = None
            await self.initialize()  # Réinitialiser en mode simulation
            logger.warning("⚠️ Fonctionnement en mode dégradé sans Pinecone")
    
    async def _ensure_indexes_exist(self):
        """Crée les index Pinecone s'ils n'existent pas"""
        if not self.pc:
            return
        
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            for index_type, config in self.index_configs.items():
                index_name = config["name"]
                
                if index_name not in existing_indexes:
                    logger.info(f"🔨 Création de l'index {index_name}...")
                    
                    self.pc.create_index(
                        name=index_name,
                        dimension=config["dimension"],
                        metric=config["metric"],
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        ),
                        deletion_protection="disabled"
                    )
                    
                    logger.info(f"✅ Index {index_name} créé")
                else:
                    logger.info(f"✅ Index {index_name} existe déjà")
                
                # Stocker la référence à l'index
                self.indexes[index_type] = self.pc.Index(name=index_name)
            
        except Exception as e:
            logger.error(f"❌ Erreur création des index: {e}")
    
    async def create_embedding(self, text: str) -> List[float]:
        """Crée un embedding vectoriel pour un texte"""
        if not self.openai_client:
            # Retourner un embedding factice en mode dégradé
            return [0.0] * self.embedding_dimension
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Erreur création embedding: {e}")
            return [0.0] * self.embedding_dimension
    
    async def store_agent_experience(
        self, 
        agent_id: str, 
        agent_type: str,
        context: str, 
        error: str, 
        solution: str, 
        validated: bool = False,
        metadata: Optional[Dict] = None
    ) -> str:
        """Stocke une expérience d'agent dans Pinecone"""
        
        if not self.pc or "agent_experiences" not in self.indexes:
            logger.warning("⚠️ Pinecone non disponible - expérience non stockée")
            return "local_storage"
        
        try:
            # Créer le texte à embedder
            experience_text = f"""
            Agent: {agent_type}
            Contexte: {context}
            Erreur: {error}
            Solution: {solution}
            Validé: {validated}
            """
            
            # Créer l'embedding
            embedding = await self.create_embedding(experience_text.strip())
            
            # Générer un ID unique
            experience_id = hashlib.md5(
                f"{agent_id}_{context}_{error}_{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Métadonnées complètes
            full_metadata = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "context": context,
                "error": error,
                "solution": solution,
                "validated": validated,
                "timestamp": datetime.now().isoformat(),
                "type": "agent_experience"
            }
            
            if metadata:
                full_metadata.update(metadata)
            
            # Stocker dans Pinecone
            index = self.indexes["agent_experiences"]
            index.upsert(
                vectors=[{
                    "id": experience_id,
                    "values": embedding,
                    "metadata": full_metadata
                }],
                namespace=f"agent_{agent_type}"
            )
            
            logger.info(f"✅ Expérience stockée: {experience_id} pour agent {agent_type}")
            return experience_id
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage expérience: {e}")
            return "error"
    
    async def search_similar_experiences(
        self, 
        agent_type: str,
        query_context: str, 
        top_k: int = 5,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Recherche des expériences similaires pour un agent"""
        
        if not self.pc or "agent_experiences" not in self.indexes:
            logger.warning("⚠️ Pinecone non disponible - recherche locale")
            return []
        
        try:
            # Créer l'embedding de la requête
            query_embedding = await self.create_embedding(query_context)
            
            # Rechercher dans Pinecone
            index = self.indexes["agent_experiences"]
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=f"agent_{agent_type}",
                filter={"validated": True}  # Seulement les expériences validées
            )
            
            # Filtrer par score de similarité
            similar_experiences = []
            for match in results.matches:
                if match.score >= min_score:
                    similar_experiences.append({
                        "id": match.id,
                        "score": match.score,
                        "context": match.metadata.get("context", ""),
                        "error": match.metadata.get("error", ""),
                        "solution": match.metadata.get("solution", ""),
                        "validated": match.metadata.get("validated", False),
                        "timestamp": match.metadata.get("timestamp", ""),
                        "metadata": match.metadata
                    })
            
            logger.info(f"🔍 Trouvé {len(similar_experiences)} expériences similaires pour {agent_type}")
            return similar_experiences
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche expériences: {e}")
            return []
    
    async def store_legal_knowledge(
        self, 
        title: str, 
        content: str, 
        source: str,
        article_code: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Stocke une connaissance juridique dans Pinecone"""
        
        if not self.pc or "legal_knowledge" not in self.indexes:
            logger.warning("⚠️ Pinecone non disponible - connaissance non stockée")
            return "local_storage"
        
        try:
            # Créer le texte à embedder
            knowledge_text = f"""
            Titre: {title}
            Contenu: {content}
            Source: {source}
            Article: {article_code or 'N/A'}
            """
            
            # Créer l'embedding
            embedding = await self.create_embedding(knowledge_text.strip())
            
            # Générer un ID unique
            knowledge_id = hashlib.md5(
                f"{title}_{source}_{article_code}".encode()
            ).hexdigest()
            
            # Métadonnées complètes
            full_metadata = {
                "title": title,
                "content": content[:1000],  # Limiter la taille
                "source": source,
                "article_code": article_code,
                "timestamp": datetime.now().isoformat(),
                "type": "legal_knowledge"
            }
            
            if metadata:
                full_metadata.update(metadata)
            
            # Stocker dans Pinecone
            index = self.indexes["legal_knowledge"]
            index.upsert(
                vectors=[{
                    "id": knowledge_id,
                    "values": embedding,
                    "metadata": full_metadata
                }],
                namespace="legal_kb"
            )
            
            logger.info(f"✅ Connaissance juridique stockée: {knowledge_id}")
            return knowledge_id
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage connaissance: {e}")
            return "error"
    
    async def search_legal_knowledge(
        self, 
        query: str, 
        top_k: int = 10,
        min_score: float = 0.6
    ) -> List[Dict[str, Any]]:
        """Recherche dans la base de connaissances juridiques"""
        
        if not self.pc or "legal_knowledge" not in self.indexes:
            logger.warning("⚠️ Pinecone non disponible - recherche locale")
            return []
        
        try:
            # Créer l'embedding de la requête
            query_embedding = await self.create_embedding(query)
            
            # Rechercher dans Pinecone
            index = self.indexes["legal_knowledge"]
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace="legal_kb"
            )
            
            # Filtrer par score de similarité
            legal_knowledge = []
            for match in results.matches:
                if match.score >= min_score:
                    legal_knowledge.append({
                        "id": match.id,
                        "score": match.score,
                        "title": match.metadata.get("title", ""),
                        "content": match.metadata.get("content", ""),
                        "source": match.metadata.get("source", ""),
                        "article_code": match.metadata.get("article_code", ""),
                        "metadata": match.metadata
                    })
            
            logger.info(f"🔍 Trouvé {len(legal_knowledge)} connaissances juridiques")
            return legal_knowledge
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche connaissances: {e}")
            return []
    
    async def store_case_context(
        self, 
        case_id: str, 
        case_type: str,
        narrative: str, 
        legal_axes: List[str],
        outcome: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """Stocke le contexte d'un dossier dans Pinecone"""
        
        if not self.pc or "case_contexts" not in self.indexes:
            logger.warning("⚠️ Pinecone non disponible - contexte non stocké")
            return "local_storage"
        
        try:
            # Créer le texte à embedder
            case_text = f"""
            Type: {case_type}
            Récit: {narrative}
            Axes juridiques: {', '.join(legal_axes)}
            Résultat: {outcome or 'En cours'}
            """
            
            # Créer l'embedding
            embedding = await self.create_embedding(case_text.strip())
            
            # Métadonnées complètes
            full_metadata = {
                "case_id": case_id,
                "case_type": case_type,
                "narrative": narrative[:1000],  # Limiter la taille
                "legal_axes": legal_axes,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat(),
                "type": "case_context"
            }
            
            if metadata:
                full_metadata.update(metadata)
            
            # Stocker dans Pinecone
            index = self.indexes["case_contexts"]
            index.upsert(
                vectors=[{
                    "id": case_id,
                    "values": embedding,
                    "metadata": full_metadata
                }],
                namespace=f"cases_{case_type}"
            )
            
            logger.info(f"✅ Contexte dossier stocké: {case_id}")
            return case_id
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage contexte: {e}")
            return "error"
    
    async def search_similar_cases(
        self, 
        case_type: str,
        narrative: str, 
        top_k: int = 5,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Recherche des dossiers similaires"""
        
        if not self.pc or "case_contexts" not in self.indexes:
            logger.warning("⚠️ Pinecone non disponible - recherche locale")
            return []
        
        try:
            # Créer l'embedding de la requête
            query_embedding = await self.create_embedding(narrative)
            
            # Rechercher dans Pinecone
            index = self.indexes["case_contexts"]
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=f"cases_{case_type}"
            )
            
            # Filtrer par score de similarité
            similar_cases = []
            for match in results.matches:
                if match.score >= min_score:
                    similar_cases.append({
                        "id": match.id,
                        "score": match.score,
                        "case_id": match.metadata.get("case_id", ""),
                        "case_type": match.metadata.get("case_type", ""),
                        "narrative": match.metadata.get("narrative", ""),
                        "legal_axes": match.metadata.get("legal_axes", []),
                        "outcome": match.metadata.get("outcome", ""),
                        "metadata": match.metadata
                    })
            
            logger.info(f"🔍 Trouvé {len(similar_cases)} dossiers similaires")
            return similar_cases
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche dossiers: {e}")
            return []
    
    async def store_reasoning_pattern(
        self, 
        agent_type: str,
        pattern_name: str, 
        reasoning_steps: List[Dict],
        success_rate: float,
        context_tags: List[str],
        metadata: Optional[Dict] = None
    ) -> str:
        """Stocke un pattern de raisonnement réussi"""
        
        if not self.pc or "reasoning_patterns" not in self.indexes:
            logger.warning("⚠️ Pinecone non disponible - pattern non stocké")
            return "local_storage"
        
        try:
            # Créer le texte à embedder
            pattern_text = f"""
            Agent: {agent_type}
            Pattern: {pattern_name}
            Étapes: {json.dumps(reasoning_steps, ensure_ascii=False)}
            Taux de succès: {success_rate}
            Contexte: {', '.join(context_tags)}
            """
            
            # Créer l'embedding
            embedding = await self.create_embedding(pattern_text.strip())
            
            # Générer un ID unique
            pattern_id = hashlib.md5(
                f"{agent_type}_{pattern_name}_{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Métadonnées complètes
            full_metadata = {
                "agent_type": agent_type,
                "pattern_name": pattern_name,
                "reasoning_steps": reasoning_steps,
                "success_rate": success_rate,
                "context_tags": context_tags,
                "timestamp": datetime.now().isoformat(),
                "type": "reasoning_pattern"
            }
            
            if metadata:
                full_metadata.update(metadata)
            
            # Stocker dans Pinecone
            index = self.indexes["reasoning_patterns"]
            index.upsert(
                vectors=[{
                    "id": pattern_id,
                    "values": embedding,
                    "metadata": full_metadata
                }],
                namespace=f"patterns_{agent_type}"
            )
            
            logger.info(f"✅ Pattern de raisonnement stocké: {pattern_id}")
            return pattern_id
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage pattern: {e}")
            return "error"
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des index Pinecone"""
        
        if not self.pc:
            return {"status": "disabled", "indexes": {}}
        
        try:
            stats = {
                "status": "active",
                "indexes": {}
            }
            
            for index_type, index in self.indexes.items():
                try:
                    index_stats = index.describe_index_stats()
                    stats["indexes"][index_type] = {
                        "total_vectors": index_stats.total_vector_count,
                        "namespaces": dict(index_stats.namespaces) if index_stats.namespaces else {},
                        "dimension": index_stats.dimension
                    }
                except Exception as e:
                    stats["indexes"][index_type] = {"error": str(e)}
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération stats: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cleanup_old_data(self, days_old: int = 30):
        """Nettoie les anciennes données (optionnel)"""
        
        if not self.pc:
            logger.warning("⚠️ Pinecone non disponible - nettoyage ignoré")
            return
        
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            # Pour chaque index, supprimer les vecteurs anciens
            # (implémentation simplifiée - en production, utiliser des filtres plus sophistiqués)
            
            logger.info(f"🧹 Nettoyage des données > {days_old} jours")
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage: {e}")
    
    async def shutdown(self):
        """Ferme les connexions Pinecone"""
        try:
            if self.pc:
                # Fermer les connexions aux index
                self.indexes.clear()
                self.pc = None
                logger.info("🛑 Connexions Pinecone fermées")
            else:
                logger.info("🛑 Pinecone déjà fermé")
        except Exception as e:
            logger.error(f"❌ Erreur fermeture Pinecone: {e}")


# Instance globale du service
pinecone_service = PineconeService()
