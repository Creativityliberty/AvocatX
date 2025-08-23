"""
Agent de base amélioré avec capacités de raisonnement RRLA
Pour tous les agents DEFENSEUR-IA
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..core.reasoning_schema import (
    AgentReasoning, 
    create_agent_reasoning,
    ReasoningDAGVisualizer,
    MemoryExperience,
    LogicProposition
)
from ..core.shared_store import SharedStore

logger = logging.getLogger(__name__)


class EnhancedAgentBase:
    """
    Agent de base avec capacités de raisonnement avancées RRLA
    """
    
    def __init__(self, agent_type: str, agent_id: str = None):
        self.agent_type = agent_type
        self.agent_id = agent_id or f"agent_{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialiser le schéma de raisonnement
        self.reasoning: AgentReasoning = create_agent_reasoning(agent_type)
        self.reasoning.agent_id = self.agent_id
        
        # État de l'agent
        self.is_active = False
        self.current_step = 0
        self.execution_log = []
        
        logger.info(f"✅ Agent {self.agent_id} initialisé avec raisonnement RRLA")
    
    async def process(self, shared_store: SharedStore, **kwargs) -> Dict[str, Any]:
        """
        Traitement principal avec raisonnement RRLA
        """
        self.is_active = True
        start_time = datetime.now()
        
        try:
            # 1. Initialiser le contexte de raisonnement
            await self._initialize_reasoning_context(shared_store, **kwargs)
            
            # 2. Exécuter la chaîne de raisonnement
            result = await self._execute_reasoning_chain(shared_store, **kwargs)
            
            # 3. Métacognition et apprentissage
            await self._perform_metacognition(shared_store, result)
            
            # 4. Mise à jour de la mémoire
            await self._update_memory(shared_store, result, success=True)
            
            # 5. Documentation automatique
            if self.reasoning.rrla_ext.auto_documentation:
                await self._auto_document_reasoning()
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Agent {self.agent_id} terminé en {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            # Gestion d'erreur avec apprentissage
            await self._handle_error(shared_store, str(e), **kwargs)
            raise
        finally:
            self.is_active = False
    
    async def _initialize_reasoning_context(self, shared_store: SharedStore, **kwargs):
        """Initialise le contexte de raisonnement"""
        
        # Mettre à jour l'objectif immédiat
        self.reasoning.wm.sg = kwargs.get("immediate_goal", "Traitement en cours")
        meta_info = await shared_store.get('meta_info', {})
        self.reasoning.wm.ctx = f"Dossier: {meta_info.get('dossier_id', 'unknown')}"
        
        # Récupérer les expériences pertinentes
        context_keywords = await self._extract_context_keywords(shared_store)
        relevant_experiences = self.reasoning.get_relevant_experiences(context_keywords)
        
        if relevant_experiences:
            logger.info(f"🧠 {len(relevant_experiences)} expériences pertinentes trouvées")
            
            # Activer l'anti-récurrence si des erreurs similaires ont été rencontrées
            if any(exp.error for exp in relevant_experiences):
                self.reasoning.rrla_ext.anti_recurrence = True
                logger.warning("⚠️ Anti-récurrence activée (erreurs similaires détectées)")
        
        # Ajouter l'action d'initialisation
        self.reasoning.add_temporal_action(f"Initialisation contexte - {self.agent_type}")
    
    async def _execute_reasoning_chain(self, shared_store: SharedStore, **kwargs) -> Dict[str, Any]:
        """Exécute la chaîne de raisonnement étape par étape"""
        
        results = {}
        
        # Trier les étapes par index
        sorted_steps = sorted(self.reasoning.chain.steps, key=lambda x: x.index)
        
        for step in sorted_steps:
            # Vérifier les dépendances
            if not self._check_dependencies(step.depends_on, results):
                error_msg = f"Dépendances non satisfaites pour l'étape {step.index}: {step.depends_on}"
                self.reasoning.chain.err.append(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"🔄 Exécution étape {step.index}: {step.description}")
            
            # Marquer l'étape comme en cours
            self.current_step = step.index
            if step.description not in self.reasoning.wm.pr["current"]:
                self.reasoning.wm.pr["current"].append(step.description)
            
            try:
                # Exécuter l'étape spécifique
                step_result = await self._execute_step(step, shared_store, results, **kwargs)
                results[f"step_{step.index}"] = step_result
                
                # Marquer comme terminée
                self.reasoning.wm.pr["completed"].append(step.description)
                if step.description in self.reasoning.wm.pr["current"]:
                    self.reasoning.wm.pr["current"].remove(step.description)
                
                # Ajouter à la mémoire temporelle
                self.reasoning.add_temporal_action(f"Étape {step.index} terminée: {step.description}")
                
                logger.info(f"✅ Étape {step.index} terminée avec succès")
                
            except Exception as e:
                error_msg = f"Erreur étape {step.index}: {str(e)}"
                self.reasoning.chain.err.append(error_msg)
                logger.error(f"❌ {error_msg}")
                raise
        
        return results
    
    async def _execute_step(self, step, shared_store: SharedStore, previous_results: Dict, **kwargs) -> Any:
        """
        Exécute une étape spécifique - à surcharger par les agents concrets
        """
        # Implémentation par défaut - les agents concrets doivent surcharger cette méthode
        return {"step_index": step.index, "description": step.description, "status": "completed"}
    
    def _check_dependencies(self, dependencies: List[int], results: Dict) -> bool:
        """Vérifie que toutes les dépendances sont satisfaites"""
        for dep in dependencies:
            if f"step_{dep}" not in results:
                return False
        return True
    
    async def _extract_context_keywords(self, shared_store: SharedStore) -> List[str]:
        """Extrait les mots-clés du contexte pour la recherche d'expériences"""
        keywords = []
        
        # Mots-clés du type d'agent
        keywords.append(self.agent_type)
        
        # Mots-clés du dossier
        meta_info = await shared_store.get("meta_info", {})
        if "type_contentieux" in meta_info:
            keywords.append(meta_info["type_contentieux"])
        
        # Mots-clés de la narration
        narration = await shared_store.get("narration", {})
        if isinstance(narration, dict) and "segments" in narration:
            for segment in narration["segments"][:3]:  # Premiers segments seulement
                if "contenu" in segment:
                    # Extraire quelques mots-clés du contenu
                    words = segment["contenu"].split()[:5]
                    keywords.extend(words)
        
        return keywords
    
    async def _perform_metacognition(self, shared_store: SharedStore, result: Dict[str, Any]):
        """Effectue l'analyse métacognitive du raisonnement"""
        
        # Analyser la qualité du raisonnement
        total_steps = len(self.reasoning.chain.steps)
        completed_steps = len(self.reasoning.wm.pr["completed"])
        error_count = len(self.reasoning.chain.err)
        
        reflection = f"""
        Analyse métacognitive - Agent {self.agent_id}:
        - Étapes prévues: {total_steps}
        - Étapes complétées: {completed_steps}
        - Erreurs rencontrées: {error_count}
        - Efficacité: {(completed_steps/total_steps)*100:.1f}%
        """
        
        if error_count > 0:
            reflection += f"\n- Erreurs: {', '.join(self.reasoning.chain.err)}"
        
        # Identifier les améliorations possibles
        if error_count > 0:
            self.reasoning.chain.warn.append("Erreurs détectées - révision du processus recommandée")
        
        if completed_steps < total_steps:
            self.reasoning.chain.warn.append("Processus incomplet - vérifier les dépendances")
        
        self.reasoning.chain.reflect = reflection
        
        # Générer l'explication
        explainability = f"Agent {self.agent_type}: {completed_steps}/{total_steps} étapes complétées"
        if result:
            explainability += f", résultat principal: {list(result.keys())}"
        
        self.reasoning.update_explainability(explainability)
        
        logger.info(f"🧠 Métacognition terminée: {explainability}")
    
    async def _update_memory(self, shared_store: SharedStore, result: Dict[str, Any], success: bool = True):
        """Met à jour la mémoire expérientielle"""
        
        meta_info = await shared_store.get('meta_info', {})
        context = f"Agent {self.agent_type} - Dossier {meta_info.get('dossier_id', 'unknown')}"
        
        if success:
            # Enregistrer le succès
            solution = f"Processus complété avec succès: {len(self.reasoning.wm.pr['completed'])} étapes"
            self.reasoning.add_experience(
                context=context,
                error="Aucune",
                solution=solution,
                validated=True
            )
        else:
            # Enregistrer l'échec pour apprentissage
            errors = "; ".join(self.reasoning.chain.err) if self.reasoning.chain.err else "Erreur inconnue"
            self.reasoning.add_experience(
                context=context,
                error=errors,
                solution="À déterminer",
                validated=False
            )
    
    async def _handle_error(self, shared_store: SharedStore, error_message: str, **kwargs):
        """Gestion d'erreur avec apprentissage"""
        
        logger.error(f"❌ Erreur dans {self.agent_id}: {error_message}")
        
        # Enregistrer l'erreur
        self.reasoning.chain.err.append(error_message)
        
        # Ajouter à la mémoire expérientielle
        await self._update_memory(shared_store, {}, success=False)
        
        # Ajouter à la mémoire temporelle
        self.reasoning.add_temporal_action(f"ERREUR: {error_message}")
    
    async def _auto_document_reasoning(self):
        """Documentation automatique du raisonnement"""
        
        # Générer le diagramme ASCII
        ascii_diagram = ReasoningDAGVisualizer.generate_ascii_diagram(self.reasoning)
        
        # Générer le diagramme Mermaid
        mermaid_diagram = ReasoningDAGVisualizer.generate_mermaid_diagram(self.reasoning)
        
        # Sauvegarder la documentation
        doc_data = {
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "reasoning_json": json.loads(self.reasoning.to_json()),
            "ascii_diagram": ascii_diagram,
            "mermaid_diagram": mermaid_diagram
        }
        
        # Sauvegarder dans un fichier (optionnel)
        doc_filename = f"./data/reasoning_docs/{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import os
            os.makedirs(os.path.dirname(doc_filename), exist_ok=True)
            with open(doc_filename, 'w', encoding='utf-8') as f:
                json.dump(doc_data, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Documentation sauvegardée: {doc_filename}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de sauvegarder la documentation: {e}")
    
    def get_reasoning_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel du raisonnement"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "is_active": self.is_active,
            "current_step": self.current_step,
            "total_steps": len(self.reasoning.chain.steps),
            "completed_steps": len(self.reasoning.wm.pr["completed"]),
            "current_tasks": self.reasoning.wm.pr["current"],
            "errors": self.reasoning.chain.err,
            "warnings": self.reasoning.chain.warn,
            "goal": self.reasoning.wm.g,
            "subgoal": self.reasoning.wm.sg,
            "explainability": self.reasoning.rrla_ext.explainability
        }
    
    def get_dag_visualization(self) -> str:
        """Retourne la visualisation DAG ASCII"""
        return ReasoningDAGVisualizer.generate_ascii_diagram(self.reasoning)
    
    def get_mermaid_diagram(self) -> str:
        """Retourne le diagramme Mermaid"""
        return ReasoningDAGVisualizer.generate_mermaid_diagram(self.reasoning)
    
    def export_reasoning(self) -> Dict[str, Any]:
        """Exporte le raisonnement complet"""
        return {
            "reasoning": json.loads(self.reasoning.to_json()),
            "status": self.get_reasoning_status(),
            "dag_ascii": self.get_dag_visualization(),
            "dag_mermaid": self.get_mermaid_diagram()
        }
