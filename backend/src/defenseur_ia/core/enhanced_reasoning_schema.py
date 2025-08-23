"""
Schéma de raisonnement RRLA amélioré avec Pinecone
Version multi-agents avec mémoire sémantique partagée
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
from datetime import datetime
import asyncio

from .reasoning_schema import (
    AgentReasoning, 
    MemoryExperience, 
    ReasoningDAGVisualizer,
    AGENT_REASONING_TEMPLATES
)
from ..services.pinecone_service import pinecone_service


class EnhancedAgentReasoning(AgentReasoning):
    """
    Schéma de raisonnement RRLA amélioré avec Pinecone
    Mémoire sémantique partagée entre agents
    """
    
    # Nouvelles capacités Pinecone
    pinecone_enabled: bool = Field(default=True, description="Pinecone activé")
    semantic_memory_ids: List[str] = Field(default_factory=list, description="IDs des mémoires stockées")
    shared_knowledge_access: bool = Field(default=True, description="Accès aux connaissances partagées")
    cross_agent_learning: bool = Field(default=True, description="Apprentissage inter-agents")
    
    async def store_experience_to_pinecone(
        self, 
        context: str, 
        error: str, 
        solution: str, 
        validated: bool = False
    ) -> str:
        """Stocke une expérience dans Pinecone pour partage inter-agents"""
        
        if not self.pinecone_enabled:
            return "pinecone_disabled"
        
        try:
            # Extraire le type d'agent depuis l'ID
            agent_type = self.agent_id.split('_')[-1] if '_' in self.agent_id else "unknown"
            
            experience_id = await pinecone_service.store_agent_experience(
                agent_id=self.agent_id,
                agent_type=agent_type,
                context=context,
                error=error,
                solution=solution,
                validated=validated,
                metadata={
                    "reasoning_goal": self.wm.g,
                    "competencies": self.exp,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Ajouter à la liste des mémoires
            if experience_id not in self.semantic_memory_ids:
                self.semantic_memory_ids.append(experience_id)
            
            return experience_id
            
        except Exception as e:
            print(f"❌ Erreur stockage expérience Pinecone: {e}")
            return "error"
    
    async def search_similar_experiences_from_pinecone(
        self, 
        context_query: str, 
        top_k: int = 5,
        include_other_agents: bool = True
    ) -> List[Dict[str, Any]]:
        """Recherche des expériences similaires dans Pinecone"""
        
        if not self.pinecone_enabled:
            return []
        
        try:
            # Extraire le type d'agent
            agent_type = self.agent_id.split('_')[-1] if '_' in self.agent_id else "unknown"
            
            # Rechercher les expériences similaires
            experiences = await pinecone_service.search_similar_experiences(
                agent_type=agent_type,
                query_context=context_query,
                top_k=top_k,
                min_score=0.7
            )
            
            # Si activé, rechercher aussi dans les autres types d'agents
            if include_other_agents and self.cross_agent_learning:
                other_agent_types = ["ecouteur", "cadreur_juridique", "redacteur_narratif", 
                                   "parseur_preuves", "juriste_matching", "recherche_web"]
                
                for other_type in other_agent_types:
                    if other_type != agent_type:
                        other_experiences = await pinecone_service.search_similar_experiences(
                            agent_type=other_type,
                            query_context=context_query,
                            top_k=2,  # Moins d'expériences des autres agents
                            min_score=0.8  # Score plus élevé pour les autres agents
                        )
                        experiences.extend(other_experiences)
            
            return experiences
            
        except Exception as e:
            print(f"❌ Erreur recherche expériences Pinecone: {e}")
            return []
    
    async def search_legal_knowledge(
        self, 
        query: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Recherche dans la base de connaissances juridiques"""
        
        if not self.pinecone_enabled or not self.shared_knowledge_access:
            return []
        
        try:
            return await pinecone_service.search_legal_knowledge(
                query=query,
                top_k=top_k,
                min_score=0.6
            )
            
        except Exception as e:
            print(f"❌ Erreur recherche connaissances juridiques: {e}")
            return []
    
    async def search_similar_cases(
        self, 
        case_type: str,
        narrative: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Recherche des dossiers similaires"""
        
        if not self.pinecone_enabled:
            return []
        
        try:
            return await pinecone_service.search_similar_cases(
                case_type=case_type,
                narrative=narrative,
                top_k=top_k,
                min_score=0.7
            )
            
        except Exception as e:
            print(f"❌ Erreur recherche dossiers similaires: {e}")
            return []
    
    async def store_successful_reasoning_pattern(
        self, 
        pattern_name: str,
        success_rate: float = 1.0,
        context_tags: Optional[List[str]] = None
    ) -> str:
        """Stocke un pattern de raisonnement réussi"""
        
        if not self.pinecone_enabled:
            return "pinecone_disabled"
        
        try:
            agent_type = self.agent_id.split('_')[-1] if '_' in self.agent_id else "unknown"
            
            # Convertir les étapes de raisonnement en format stockable
            reasoning_steps = []
            for step in self.chain.steps:
                reasoning_steps.append({
                    "index": step.index,
                    "description": step.description,
                    "depends_on": step.depends_on,
                    "prompt": step.prompt
                })
            
            pattern_id = await pinecone_service.store_reasoning_pattern(
                agent_type=agent_type,
                pattern_name=pattern_name,
                reasoning_steps=reasoning_steps,
                success_rate=success_rate,
                context_tags=context_tags or [],
                metadata={
                    "agent_id": self.agent_id,
                    "goal": self.wm.g,
                    "completed_steps": len(self.wm.pr["completed"]),
                    "total_steps": len(self.chain.steps)
                }
            )
            
            return pattern_id
            
        except Exception as e:
            print(f"❌ Erreur stockage pattern raisonnement: {e}")
            return "error"
    
    async def enhance_with_semantic_memory(self, context_query: str) -> Dict[str, Any]:
        """Enrichit le raisonnement avec la mémoire sémantique"""
        
        enhancement_data = {
            "similar_experiences": [],
            "legal_knowledge": [],
            "similar_cases": [],
            "enhancement_applied": False
        }
        
        if not self.pinecone_enabled:
            return enhancement_data
        
        try:
            # Rechercher des expériences similaires
            similar_experiences = await self.search_similar_experiences_from_pinecone(
                context_query=context_query,
                top_k=3,
                include_other_agents=True
            )
            
            # Rechercher des connaissances juridiques pertinentes
            legal_knowledge = await self.search_legal_knowledge(
                query=context_query,
                top_k=5
            )
            
            # Si c'est un contexte de dossier, rechercher des cas similaires
            similar_cases = []
            if "OQTF" in context_query or "contentieux" in context_query:
                similar_cases = await self.search_similar_cases(
                    case_type="OQTF",
                    narrative=context_query,
                    top_k=3
                )
            
            # Appliquer les améliorations au raisonnement
            if similar_experiences:
                for exp in similar_experiences:
                    if exp["validated"]:
                        # Ajouter l'expérience à la mémoire locale
                        memory_exp = MemoryExperience(
                            context=exp["context"],
                            error=exp["error"],
                            solution=exp["solution"],
                            validated=exp["validated"]
                        )
                        self.rrla_ext.memory_experiential.append(memory_exp)
                        
                        # Ajouter des anticipations basées sur l'expérience
                        if exp["error"] not in self.rrla_ext.anticipation:
                            self.rrla_ext.anticipation.append(f"Éviter: {exp['error']}")
            
            if legal_knowledge:
                # Enrichir la base de connaissances
                for knowledge in legal_knowledge:
                    self.kg.tri.append({
                        "sub": knowledge["title"],
                        "pred": "source_juridique",
                        "obj": knowledge["source"]
                    })
            
            enhancement_data.update({
                "similar_experiences": similar_experiences,
                "legal_knowledge": legal_knowledge,
                "similar_cases": similar_cases,
                "enhancement_applied": True
            })
            
            # Mettre à jour l'explication
            enhancement_summary = f"""
            Enrichissement sémantique appliqué:
            - {len(similar_experiences)} expériences similaires trouvées
            - {len(legal_knowledge)} connaissances juridiques pertinentes
            - {len(similar_cases)} dossiers similaires identifiés
            """
            
            self.rrla_ext.explainability += enhancement_summary
            
            return enhancement_data
            
        except Exception as e:
            print(f"❌ Erreur enrichissement sémantique: {e}")
            return enhancement_data


# Templates étendus pour tous les agents DEFENSEUR-IA
ENHANCED_AGENT_TEMPLATES = {
    **AGENT_REASONING_TEMPLATES,  # Inclure les templates existants
    
    "parseur_preuves": {
        "exp": ["ocr_tesseract", "extraction_pdf", "analyse_emails", "classification_documents"],
        "specializations": [
            {"domain": "OCR et extraction", "subdomains": ["PDF", "images", "documents scannés"]},
            {"domain": "Classification", "subdomains": ["preuves", "correspondances", "documents officiels"]}
        ],
        "goal": "Extraire et analyser les pièces justificatives du dossier",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Identifier le type de document", "prompt": "Analyser le format et la nature du document"},
            {"index": 1, "depends_on": [0], "description": "Extraction OCR/texte", "prompt": "Extraire le contenu textuel avec Tesseract"},
            {"index": 2, "depends_on": [1], "description": "Classification du contenu", "prompt": "Classer le document par type et importance"},
            {"index": 3, "depends_on": [2], "description": "Validation et structuration", "prompt": "Valider l'extraction et structurer les données"}
        ]
    },
    
    "juriste_matching": {
        "exp": ["embedding_faiss", "matching_semantique", "analyse_juridique", "scoring_pertinence"],
        "specializations": [
            {"domain": "Matching sémantique", "subdomains": ["FAISS", "embeddings", "similarité"]},
            {"domain": "Analyse juridique", "subdomains": ["correspondance texte-loi", "pertinence", "scoring"]}
        ],
        "goal": "Faire correspondre les preuves avec les articles de loi pertinents",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Embedding des preuves", "prompt": "Créer les embeddings vectoriels des pièces"},
            {"index": 1, "depends_on": [0], "description": "Recherche FAISS", "prompt": "Rechercher les articles de loi similaires"},
            {"index": 2, "depends_on": [1], "description": "Scoring de pertinence", "prompt": "Évaluer la pertinence des correspondances"},
            {"index": 3, "depends_on": [2], "description": "Validation juridique", "prompt": "Valider la cohérence juridique des matches"}
        ]
    },
    
    "recherche_web": {
        "exp": ["scraping_web", "recherche_jurisprudence", "forums_juridiques", "associations"],
        "specializations": [
            {"domain": "Recherche web", "subdomains": ["jurisprudence", "forums", "associations"]},
            {"domain": "Validation sources", "subdomains": ["fiabilité", "pertinence", "actualité"]}
        ],
        "goal": "Rechercher des informations complémentaires sur le web",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Définir stratégie de recherche", "prompt": "Identifier les mots-clés et sources pertinentes"},
            {"index": 1, "depends_on": [0], "description": "Recherche jurisprudence", "prompt": "Rechercher dans les bases de jurisprudence"},
            {"index": 2, "depends_on": [0], "description": "Recherche forums/associations", "prompt": "Rechercher dans les forums et sites d'associations"},
            {"index": 3, "depends_on": [1, 2], "description": "Validation et synthèse", "prompt": "Valider les sources et synthétiser les informations"}
        ]
    },
    
    "relecteur_ia_1": {
        "exp": ["relecture_technique", "verification_coherence", "correction_erreurs", "validation_qa"],
        "specializations": [
            {"domain": "Relecture technique", "subdomains": ["cohérence", "logique", "erreurs factuelles"]},
            {"domain": "Assurance qualité", "subdomains": ["validation", "correction", "amélioration"]}
        ],
        "goal": "Relire et corriger le premier brouillon narratif",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Analyse de cohérence", "prompt": "Vérifier la cohérence logique du récit"},
            {"index": 1, "depends_on": [0], "description": "Vérification factuelle", "prompt": "Vérifier l'exactitude des faits et références"},
            {"index": 2, "depends_on": [1], "description": "Correction des erreurs", "prompt": "Corriger les erreurs identifiées"},
            {"index": 3, "depends_on": [2], "description": "Validation finale", "prompt": "Valider la qualité du texte corrigé"}
        ]
    },
    
    "agregateur_coherence": {
        "exp": ["synthese_donnees", "agregation_coherence", "resolution_conflits", "harmonisation"],
        "specializations": [
            {"domain": "Synthèse", "subdomains": ["agrégation", "cohérence", "harmonisation"]},
            {"domain": "Résolution conflits", "subdomains": ["contradictions", "priorités", "validation"]}
        ],
        "goal": "Agréger et harmoniser toutes les informations collectées",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Collecte des données", "prompt": "Rassembler toutes les informations des agents précédents"},
            {"index": 1, "depends_on": [0], "description": "Détection des conflits", "prompt": "Identifier les contradictions et incohérences"},
            {"index": 2, "depends_on": [1], "description": "Résolution et priorisation", "prompt": "Résoudre les conflits et prioriser les informations"},
            {"index": 3, "depends_on": [2], "description": "Synthèse harmonisée", "prompt": "Créer une synthèse cohérente et complète"}
        ]
    },
    
    "relecteur_ia_2": {
        "exp": ["relecture_stylistique", "amelioration_empathie", "optimisation_narrative", "polish_final"],
        "specializations": [
            {"domain": "Style et empathie", "subdomains": ["ton", "empathie", "clarté", "impact"]},
            {"domain": "Optimisation narrative", "subdomains": ["fluidité", "persuasion", "émotion"]}
        ],
        "goal": "Peaufiner le style et l'empathie du récit final",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Analyse stylistique", "prompt": "Analyser le style et le ton du récit"},
            {"index": 1, "depends_on": [0], "description": "Amélioration empathique", "prompt": "Renforcer l'empathie et l'impact émotionnel"},
            {"index": 2, "depends_on": [1], "description": "Optimisation narrative", "prompt": "Optimiser la fluidité et la persuasion"},
            {"index": 3, "depends_on": [2], "description": "Polish final", "prompt": "Finaliser le style et la présentation"}
        ]
    },
    
    "synthese_strategique": {
        "exp": ["analyse_strategique", "scoring_arguments", "plan_action", "evaluation_chances"],
        "specializations": [
            {"domain": "Stratégie juridique", "subdomains": ["analyse", "scoring", "recommandations"]},
            {"domain": "Évaluation", "subdomains": ["chances de succès", "risques", "alternatives"]}
        ],
        "goal": "Créer une synthèse stratégique et un plan d'action",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Analyse des arguments", "prompt": "Analyser la force des arguments juridiques"},
            {"index": 1, "depends_on": [0], "description": "Scoring et priorisation", "prompt": "Scorer et prioriser les arguments"},
            {"index": 2, "depends_on": [1], "description": "Évaluation des chances", "prompt": "Évaluer les chances de succès du recours"},
            {"index": 3, "depends_on": [2], "description": "Plan d'action", "prompt": "Élaborer un plan d'action stratégique"}
        ]
    },
    
    "avocat_ia": {
        "exp": ["redaction_juridique_finale", "style_professionnel", "argumentation_avancee", "references_jurisprudence"],
        "specializations": [
            {"domain": "Rédaction juridique", "subdomains": ["style professionnel", "argumentation", "structure"]},
            {"domain": "Références", "subdomains": ["jurisprudence", "doctrine", "textes de loi"]}
        ],
        "goal": "Rédiger la requête finale dans un style juridique professionnel",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Structure juridique", "prompt": "Structurer la requête selon les standards juridiques"},
            {"index": 1, "depends_on": [0], "description": "Argumentation professionnelle", "prompt": "Développer l'argumentation avec style professionnel"},
            {"index": 2, "depends_on": [1], "description": "Intégration références", "prompt": "Intégrer les références jurisprudentielles"},
            {"index": 3, "depends_on": [2], "description": "Finalisation requête", "prompt": "Finaliser la requête pour soumission"}
        ]
    },
    
    "export_final": {
        "exp": ["generation_pdf", "creation_annexes", "packaging_dossier", "validation_format"],
        "specializations": [
            {"domain": "Export et packaging", "subdomains": ["PDF", "ZIP", "annexes", "formatage"]},
            {"domain": "Validation", "subdomains": ["format", "complétude", "qualité"]}
        ],
        "goal": "Exporter le dossier final en PDF professionnel avec annexes",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Préparation export", "prompt": "Préparer tous les éléments pour l'export"},
            {"index": 1, "depends_on": [0], "description": "Génération PDF", "prompt": "Générer le PDF principal avec mise en forme"},
            {"index": 2, "depends_on": [1], "description": "Création annexes", "prompt": "Créer et organiser les annexes"},
            {"index": 3, "depends_on": [2], "description": "Package final", "prompt": "Créer le package ZIP final avec tous les documents"}
        ]
    }
}


async def create_enhanced_agent_reasoning(agent_type: str, **kwargs) -> EnhancedAgentReasoning:
    """Factory pour créer un schéma de raisonnement RRLA amélioré avec Pinecone"""
    
    if agent_type not in ENHANCED_AGENT_TEMPLATES:
        raise ValueError(f"Type d'agent inconnu: {agent_type}")
    
    # Créer le raisonnement de base
    base_reasoning = create_agent_reasoning(agent_type, **kwargs)
    
    # Convertir en version améliorée
    enhanced_reasoning = EnhancedAgentReasoning(
        agent_id=f"defenseur_ia_{agent_type}_enhanced",
        exp=base_reasoning.exp,
        se=base_reasoning.se,
        wm=base_reasoning.wm,
        kg=base_reasoning.kg,
        logic=base_reasoning.logic,
        chain=base_reasoning.chain,
        rrla_ext=base_reasoning.rrla_ext,
        pinecone_enabled=True,
        shared_knowledge_access=True,
        cross_agent_learning=True
    )
    
    return enhanced_reasoning


class MultiAgentRRLAOrchestrator:
    """
    Orchestrateur pour coordonner les agents RRLA avec Pinecone
    """
    
    def __init__(self):
        self.agents = {}
        self.execution_history = []
        self.shared_context = {}
    
    async def initialize_all_agents(self):
        """Initialise tous les agents DEFENSEUR-IA avec RRLA"""
        
        agent_types = list(ENHANCED_AGENT_TEMPLATES.keys())
        
        for agent_type in agent_types:
            try:
                agent_reasoning = await create_enhanced_agent_reasoning(agent_type)
                self.agents[agent_type] = agent_reasoning
                print(f"✅ Agent {agent_type} initialisé avec RRLA+Pinecone")
            except Exception as e:
                print(f"❌ Erreur initialisation agent {agent_type}: {e}")
    
    async def execute_pipeline_with_rrla(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute le pipeline complet avec raisonnement RRLA"""
        
        pipeline_results = {}
        
        # Ordre d'exécution des agents
        execution_order = [
            "ecouteur", "cadreur_juridique", "parseur_preuves", 
            "juriste_matching", "recherche_web", "redacteur_narratif",
            "relecteur_ia_1", "agregateur_coherence", "relecteur_ia_2",
            "synthese_strategique", "avocat_ia", "export_final"
        ]
        
        for agent_type in execution_order:
            if agent_type in self.agents:
                agent = self.agents[agent_type]
                
                # Enrichir avec la mémoire sémantique
                context_query = f"Dossier {case_data.get('type', 'OQTF')} - {case_data.get('narrative', '')}"
                enhancement = await agent.enhance_with_semantic_memory(context_query)
                
                # Simuler l'exécution (en production: appel réel à l'agent)
                result = {
                    "agent_type": agent_type,
                    "status": "completed",
                    "enhancement_data": enhancement,
                    "reasoning_summary": agent.rrla_ext.explainability
                }
                
                pipeline_results[agent_type] = result
                
                # Stocker l'expérience de succès
                await agent.store_experience_to_pinecone(
                    context=context_query,
                    error="Aucune",
                    solution=f"Pipeline {agent_type} exécuté avec succès",
                    validated=True
                )
        
        return pipeline_results
    
    async def get_collective_intelligence_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'intelligence collective"""
        
        stats = {
            "total_agents": len(self.agents),
            "pinecone_stats": await pinecone_service.get_stats(),
            "agents_status": {}
        }
        
        for agent_type, agent in self.agents.items():
            stats["agents_status"][agent_type] = {
                "pinecone_enabled": agent.pinecone_enabled,
                "cross_agent_learning": agent.cross_agent_learning,
                "semantic_memories": len(agent.semantic_memory_ids),
                "local_experiences": len(agent.rrla_ext.memory_experiential)
            }
        
        return stats


# Instance globale de l'orchestrateur
multi_agent_orchestrator = MultiAgentRRLAOrchestrator()
