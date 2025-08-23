"""
Schéma de raisonnement avancé RRLA pour les agents DEFENSEUR-IA
Reasoning, Reflection, Learning, Adaptation
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import json
from datetime import datetime


class ReasoningDepth(str, Enum):
    """Méthode de raisonnement"""
    ANALOGIE = "analogie"
    DIRECT = "direct"


class MemoryExperience(BaseModel):
    """Expérience mémorisée d'erreur/solution"""
    context: str = Field(..., description="Contexte de l'expérience")
    error: str = Field(..., description="Erreur rencontrée")
    solution: str = Field(..., description="Solution appliquée")
    validated: bool = Field(..., description="Solution validée ou non")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())


class TemporalAction(BaseModel):
    """Action horodatée"""
    timestamp: str = Field(..., description="Horodatage de l'action")
    action: str = Field(..., description="Description de l'action")


class Specialization(BaseModel):
    """Spécialisation par domaine"""
    domain: str = Field(..., description="Domaine maître de compétence")
    subdomains: List[str] = Field(..., description="Sous-domaines spécifiques")


class WorkingMemory(BaseModel):
    """Mémoire de travail - contexte et objectifs"""
    g: str = Field(..., description="Objectif principal du raisonnement")
    sg: str = Field(..., description="Objectif immédiat ou tâche en cours")
    pr: Dict[str, List[str]] = Field(..., description="Progression (completed, current)")
    ctx: str = Field(..., description="Contexte influençant la réflexion")


class KnowledgeTriplet(BaseModel):
    """Triplet de connaissance sémantique"""
    sub: str = Field(..., description="Sujet de la relation")
    pred: str = Field(..., description="Relation entre sujet et objet")
    obj: str = Field(..., description="Objet de la relation")


class LogicProposition(BaseModel):
    """Proposition logique avec représentation symbolique et naturelle"""
    symb: str = Field(..., description="Représentation symbolique")
    nl: str = Field(..., description="Représentation en langage naturel")


class ReasoningStep(BaseModel):
    """Étape de raisonnement dans la chaîne"""
    index: int = Field(..., description="Index de l'étape")
    depends_on: List[int] = Field(..., description="Étapes dont dépend cette étape")
    description: str = Field(..., description="Description de l'étape")
    prompt: str = Field(..., description="Prompt interne pour cette étape")


class RelationalNetwork(BaseModel):
    """Réseau relationnel entre concepts"""
    concept: str = Field(..., description="Concept principal")
    related_to: List[str] = Field(..., description="Concepts reliés")


class Adaptability(BaseModel):
    """Paramètres d'adaptation"""
    style: str = Field(..., description="Style d'adaptation")
    complexity: str = Field(..., description="Niveau de complexité")


class RRLAExtensions(BaseModel):
    """Extensions cognitives RRLA"""
    memory_experiential: List[MemoryExperience] = Field(default_factory=list)
    anti_recurrence: bool = Field(default=True, description="Contrôle anti-récurrence")
    temporal_memory: List[TemporalAction] = Field(default_factory=list)
    depth: ReasoningDepth = Field(default=ReasoningDepth.DIRECT)
    relational_networks: List[RelationalNetwork] = Field(default_factory=list)
    anticipation: List[str] = Field(default_factory=list, description="Erreurs/scénarios prédits")
    interaction: List[str] = Field(default_factory=list, description="Questions posées")
    adaptability: Optional[Adaptability] = None
    auto_documentation: bool = Field(default=True)
    explainability: str = Field(default="", description="Résumé explicatif des choix")


class LogicFramework(BaseModel):
    """Cadre logique de raisonnement"""
    propos: List[LogicProposition] = Field(default_factory=list, description="Propositions fondamentales")
    proofs: List[LogicProposition] = Field(default_factory=list, description="Éléments de preuve")
    crits: List[LogicProposition] = Field(default_factory=list, description="Contre-arguments")
    doubts: List[LogicProposition] = Field(default_factory=list, description="Incertitudes")


class ReasoningChain(BaseModel):
    """Chaîne de raisonnement structurée"""
    steps: List[ReasoningStep] = Field(..., description="Étapes de raisonnement")
    reflect: str = Field(default="", description="Analyse métacognitive")
    err: List[str] = Field(default_factory=list, description="Erreurs identifiées")
    note: List[str] = Field(default_factory=list, description="Notes techniques")
    warn: List[str] = Field(default_factory=list, description="Avertissements")


class KnowledgeGraph(BaseModel):
    """Graphe de connaissances"""
    tri: List[KnowledgeTriplet] = Field(default_factory=list, description="Triplets sémantiques")


class AgentReasoning(BaseModel):
    """Schéma complet de raisonnement pour un agent DEFENSEUR-IA"""
    
    # Compétences et spécialisations
    exp: List[str] = Field(..., description="Compétences techniques principales")
    se: List[Specialization] = Field(..., description="Spécialisations par domaines")
    
    # Mémoire de travail et contexte
    wm: WorkingMemory = Field(..., description="Cadre de mission et contexte")
    
    # Base de connaissances
    kg: KnowledgeGraph = Field(default_factory=KnowledgeGraph)
    
    # Logique de raisonnement
    logic: LogicFramework = Field(default_factory=LogicFramework)
    
    # Chaîne de raisonnement
    chain: ReasoningChain = Field(..., description="Chaîne logique de raisonnement")
    
    # Extensions RRLA
    rrla_ext: RRLAExtensions = Field(default_factory=RRLAExtensions)
    
    # Métadonnées
    agent_id: str = Field(..., description="Identifiant de l'agent")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dag_representation(self) -> Dict[str, Any]:
        """Convertit le raisonnement en représentation DAG"""
        nodes = []
        edges = []
        
        # Créer les nœuds pour chaque étape
        for step in self.chain.steps:
            nodes.append({
                "id": f"step_{step.index}",
                "label": step.description,
                "type": "reasoning_step",
                "data": {
                    "prompt": step.prompt,
                    "index": step.index
                }
            })
            
            # Créer les arêtes basées sur les dépendances
            for dep in step.depends_on:
                edges.append({
                    "from": f"step_{dep}",
                    "to": f"step_{step.index}",
                    "type": "dependency"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "agent_id": self.agent_id,
                "goal": self.wm.g,
                "subgoal": self.wm.sg,
                "context": self.wm.ctx
            }
        }
    
    def add_experience(self, context: str, error: str, solution: str, validated: bool = False):
        """Ajoute une expérience à la mémoire"""
        experience = MemoryExperience(
            context=context,
            error=error,
            solution=solution,
            validated=validated
        )
        self.rrla_ext.memory_experiential.append(experience)
    
    def add_temporal_action(self, action: str):
        """Ajoute une action à la mémoire temporelle"""
        temporal_action = TemporalAction(
            timestamp=datetime.now().isoformat(),
            action=action
        )
        self.rrla_ext.temporal_memory.append(temporal_action)
    
    def get_relevant_experiences(self, context_keywords: List[str]) -> List[MemoryExperience]:
        """Récupère les expériences pertinentes basées sur des mots-clés"""
        relevant = []
        for exp in self.rrla_ext.memory_experiential:
            if any(keyword.lower() in exp.context.lower() for keyword in context_keywords):
                relevant.append(exp)
        return relevant
    
    def update_explainability(self, explanation: str):
        """Met à jour l'explication du raisonnement"""
        self.rrla_ext.explainability = explanation
        
    def to_json(self) -> str:
        """Export JSON du raisonnement"""
        return self.model_dump_json(indent=2)


class ReasoningDAGVisualizer:
    """Visualiseur DAG pour le raisonnement"""
    
    @staticmethod
    def generate_mermaid_diagram(reasoning: AgentReasoning) -> str:
        """Génère un diagramme Mermaid du DAG de raisonnement"""
        dag = reasoning.to_dag_representation()
        
        mermaid = ["graph TD"]
        
        # Ajouter les nœuds
        for node in dag["nodes"]:
            mermaid.append(f'    {node["id"]}["{node["label"]}"]')
        
        # Ajouter les arêtes
        for edge in dag["edges"]:
            mermaid.append(f'    {edge["from"]} --> {edge["to"]}')
        
        return "\n".join(mermaid)
    
    @staticmethod
    def generate_ascii_diagram(reasoning: AgentReasoning) -> str:
        """Génère un diagramme ASCII du raisonnement"""
        steps = reasoning.chain.steps
        if not steps:
            return "Aucune étape de raisonnement"
        
        diagram = ["╔═══════════════════════════════════════════════════════════════╗"]
        diagram.append(f"║ AGENT: {reasoning.agent_id:<50} ║")
        diagram.append(f"║ OBJECTIF: {reasoning.wm.g:<46} ║")
        diagram.append("╠═══════════════════════════════════════════════════════════════╣")
        
        for i, step in enumerate(sorted(steps, key=lambda x: x.index)):
            prefix = "├─" if i < len(steps) - 1 else "└─"
            diagram.append(f"║ {prefix} [{step.index}] {step.description:<50} ║")
            
            if step.depends_on:
                deps = ", ".join(map(str, step.depends_on))
                diagram.append(f"║ │    └─ Dépend de: {deps:<40} ║")
        
        diagram.append("╚═══════════════════════════════════════════════════════════════╝")
        
        return "\n".join(diagram)


# Templates prédéfinis pour les agents DEFENSEUR-IA
AGENT_REASONING_TEMPLATES = {
    "ecouteur": {
        "exp": ["transcription_audio", "detection_emotion", "segmentation_narrative"],
        "specializations": [
            {"domain": "Speech-to-Text", "subdomains": ["Whisper", "Gemini Live", "français juridique"]},
            {"domain": "Analyse émotionnelle", "subdomains": ["détresse", "urgence", "cohérence"]}
        ],
        "goal": "Transcrire et analyser le témoignage audio du justiciable",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Analyser la qualité audio", "prompt": "Évaluer la clarté et la qualité de l'enregistrement"},
            {"index": 1, "depends_on": [0], "description": "Transcription initiale", "prompt": "Transcrire l'audio en texte avec Whisper"},
            {"index": 2, "depends_on": [1], "description": "Détection émotionnelle", "prompt": "Analyser les émotions et le stress dans la voix"},
            {"index": 3, "depends_on": [1, 2], "description": "Segmentation narrative", "prompt": "Découper le récit en segments logiques"}
        ]
    },
    
    "cadreur_juridique": {
        "exp": ["recherche_legifrance", "analyse_juridique", "classification_contentieux"],
        "specializations": [
            {"domain": "Droit des étrangers", "subdomains": ["OQTF", "recours", "aide juridictionnelle"]},
            {"domain": "API Légifrance", "subdomains": ["codes", "jurisprudence", "circulaires"]}
        ],
        "goal": "Identifier les axes juridiques pertinents et rechercher la législation applicable",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Analyse du témoignage", "prompt": "Extraire les éléments juridiques du récit"},
            {"index": 1, "depends_on": [0], "description": "Classification contentieux", "prompt": "Déterminer le type de contentieux"},
            {"index": 2, "depends_on": [1], "description": "Recherche Légifrance", "prompt": "Interroger l'API pour les textes pertinents"},
            {"index": 3, "depends_on": [2], "description": "Synthèse juridique", "prompt": "Synthétiser les axes juridiques identifiés"}
        ]
    },
    
    "redacteur_narratif": {
        "exp": ["redaction_juridique", "storytelling", "argumentation"],
        "specializations": [
            {"domain": "Rédaction juridique", "subdomains": ["récit factuel", "chronologie", "empathie"]},
            {"domain": "Argumentation", "subdomains": ["preuves", "références légales", "cohérence"]}
        ],
        "goal": "Rédiger un récit structuré et argumenté pour le recours",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Analyse des éléments", "prompt": "Compiler narration, preuves et axes juridiques"},
            {"index": 1, "depends_on": [0], "description": "Structure narrative", "prompt": "Organiser chronologiquement les faits"},
            {"index": 2, "depends_on": [1], "description": "Intégration juridique", "prompt": "Intégrer les références légales pertinentes"},
            {"index": 3, "depends_on": [2], "description": "Rédaction empathique", "prompt": "Rédiger avec empathie et professionnalisme"}
        ]
    },

    "recherche_web_enhanced": {
        "exp": [
            "deep_research",
            "query_clarification",
            "query_rewriting",
            "jurisprudence_search",
            "procedure_search",
            "synthesis"
        ],
        "specializations": [
            {"domain": "Recherche web juridique", "subdomains": ["Deep Research", "GPT-4.1", "français juridique"]},
            {"domain": "Jurisprudence et procédures", "subdomains": ["Légifrance", "circulaires", "procédures"]}
        ],
        "goal": "Mener une recherche web juridique approfondie et synthétiser des résultats fiables",
        "reasoning_steps": [
            {"index": 0, "depends_on": [], "description": "Clarification de la requête", "prompt": "Identifier les zones d'ambiguïté et les clarifier"},
            {"index": 1, "depends_on": [0], "description": "Réécriture de la requête", "prompt": "Optimiser la requête pour la recherche juridique"},
            {"index": 2, "depends_on": [1], "description": "Recherche approfondie (Deep Research)", "prompt": "Utiliser l'API Deep Research pour collecter des informations pertinentes"},
            {"index": 3, "depends_on": [2], "description": "Recherche de jurisprudence", "prompt": "Interroger les sources officielles pour la jurisprudence pertinente"},
            {"index": 4, "depends_on": [2], "description": "Recherche de procédures", "prompt": "Identifier les procédures administratives applicables"},
            {"index": 5, "depends_on": [2, 3, 4], "description": "Synthèse des résultats", "prompt": "Synthétiser et évaluer la fiabilité des sources"}
        ]
    }
}


def create_agent_reasoning(agent_type: str, **kwargs) -> AgentReasoning:
    """Factory pour créer un schéma de raisonnement pour un agent"""
    if agent_type not in AGENT_REASONING_TEMPLATES:
        raise ValueError(f"Type d'agent inconnu: {agent_type}")
    
    template = AGENT_REASONING_TEMPLATES[agent_type]
    
    # Créer les spécialisations
    specializations = [
        Specialization(domain=spec["domain"], subdomains=spec["subdomains"])
        for spec in template["specializations"]
    ]
    
    # Créer la mémoire de travail
    working_memory = WorkingMemory(
        g=template["goal"],
        sg=kwargs.get("subgoal", "Étape en cours"),
        pr={"completed": [], "current": []},
        ctx=kwargs.get("context", "Traitement d'un dossier DEFENSEUR-IA")
    )
    
    # Créer les étapes de raisonnement
    reasoning_steps = [
        ReasoningStep(**step) for step in template["reasoning_steps"]
    ]
    
    # Créer la chaîne de raisonnement
    reasoning_chain = ReasoningChain(
        steps=reasoning_steps,
        reflect="Analyse métacognitive en cours..."
    )
    
    return AgentReasoning(
        agent_id=f"defenseur_ia_{agent_type}",
        exp=template["exp"],
        se=specializations,
        wm=working_memory,
        chain=reasoning_chain
    )
