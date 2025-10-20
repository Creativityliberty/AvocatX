"""
Service OpenAI Avancé pour DEFENSEUR-IA
Support GPT-4.1, Deep Research API et Web Search Preview
"""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from defenseur_ia.config.settings import settings

from openai import OpenAI, AsyncOpenAI
from openai.types.responses import Response

logger = logging.getLogger(__name__)


@dataclass
class OpenAIConfig:
    """Configuration pour le service OpenAI"""
    api_key: str
    model_gpt4: str = "gpt-4.1-2025-04-14"
    model_deep_research: str = "o3-deep-research-2025-06-26"
    model_deep_research_mini: str = "o4-mini-deep-research-2025-06-26"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 300


@dataclass
class ResearchQuery:
    """Requête de recherche structurée"""
    query: str
    context: Optional[str] = None
    domain: Optional[str] = None  # juridique, médical, technique, etc.
    language: str = "fr"
    max_results: int = 10
    include_citations: bool = True
    research_depth: str = "auto"  # auto, detailed, summary


@dataclass
class ResearchResult:
    """Résultat de recherche structuré"""
    query: str
    content: str
    citations: List[Dict[str, Any]]
    reasoning_steps: List[str]
    search_queries: List[str]
    execution_time: float
    model_used: str
    confidence_score: Optional[float] = None


@dataclass
class GPTResponse:
    """Réponse GPT structurée"""
    content: str
    model: str
    tokens_used: int
    execution_time: float
    finish_reason: str


class OpenAIService:
    """Service OpenAI avec support Deep Research et GPT-4.1"""
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        if config is None:
            # Préfère la configuration Pydantic, sinon variable d'environnement
            api_key = (getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY") or "").strip()
            config = OpenAIConfig(api_key=api_key)

        self.config = config
        self.simulation_mode = len(self.config.api_key or "") == 0
        if self.simulation_mode:
            self.client = None
            self.async_client = None
            logger.warning("OpenAIService running in SIMULATION mode (no OPENAI_API_KEY).")
        else:
            self.client = OpenAI(api_key=self.config.api_key)
            self.async_client = AsyncOpenAI(api_key=self.config.api_key)
        
        # Prompts spécialisés pour DEFENSEUR-IA
        self.legal_research_prompt = self._create_legal_research_prompt()
        self.clarifying_prompt = self._create_clarifying_prompt()
        self.rewriting_prompt = self._create_rewriting_prompt()

    def _create_legal_research_prompt(self) -> str:
        """Prompt spécialisé pour la recherche juridique"""
        return """
Vous êtes un assistant juridique spécialisé dans le droit des étrangers français, préparant un rapport structuré et basé sur des données pour une équipe juridique. Votre tâche est d'analyser la question juridique posée par l'utilisateur.

DIRECTIVES :
- Concentrez-vous sur des informations riches en données : incluez des chiffres spécifiques, des tendances, des statistiques et des résultats mesurables (ex: taux d'acceptation des demandes, délais de traitement, jurisprudence récente).
- Quand approprié, résumez les données de manière à pouvoir être transformées en graphiques ou tableaux, et mentionnez-le dans la réponse.
- Priorisez les sources fiables et à jour : jurisprudence, textes officiels (Légifrance, CESEDA), circulaires ministérielles, rapports d'organismes officiels.
- Incluez des citations en ligne et retournez toutes les métadonnées des sources.
- Structurez votre réponse avec des sections claires : Contexte juridique, Jurisprudence applicable, Procédures, Recommandations pratiques.

DOMAINES D'EXPERTISE :
- Titre de séjour (étudiant, salarié, vie privée et familiale, etc.)
- Regroupement familial
- Naturalisation et acquisition de nationalité
- Droit d'asile et protection subsidiaire
- OQTF et contentieux administratif
- Procédures préfectorales et recours

Soyez analytique, évitez les généralités, et assurez-vous que chaque section soutient un raisonnement basé sur des données qui pourrait informer une stratégie juridique ou une décision de politique publique.
"""

    def _create_clarifying_prompt(self) -> str:
        """Prompt pour poser des questions de clarification"""
        return """
Vous recevrez une demande de recherche juridique d'un utilisateur. Votre travail n'est PAS de compléter la tâche encore, mais plutôt de poser des questions de clarification qui aideraient à produire une réponse plus spécifique, efficace et pertinente.

DIRECTIVES :
1. **Maximiser la Pertinence**
- Posez des questions qui sont *directement nécessaires* pour délimiter la recherche.
- Considérez quelles informations changeraient la structure, la profondeur ou la direction de la réponse.

2. **Identifier les Dimensions Manquantes mais Critiques**
- Identifiez les attributs essentiels qui n'ont pas été spécifiés dans la demande de l'utilisateur (ex: nationalité, situation familiale, type de titre de séjour, délais).
- Demandez explicitement chacun d'eux, même si cela semble évident.

3. **Ne Pas Inventer de Préférences**
- Si l'utilisateur n'a pas mentionné une préférence, *ne l'assumez pas*. Demandez-le clairement et de manière neutre.

4. **Utiliser la Première Personne**
- Formulez vos questions du point de vue de l'assistant parlant à l'utilisateur (ex: "Pourriez-vous préciser..." ou "Avez-vous une préférence pour...")

5. **Utiliser une Liste à Puces si Plusieurs Questions**
- S'il y a plusieurs questions ouvertes, listez-les clairement en format puces pour la lisibilité.

6. **Éviter de Trop Demander**
- Priorisez les 3-6 questions qui réduiraient le plus l'ambiguïté. Vous n'avez pas besoin de tout demander, juste les inconnues les plus importantes.

7. **Inclure des Exemples Quand Utile**
- Si vous demandez des préférences (ex: type de procédure, urgence), listez brièvement des exemples pour aider l'utilisateur à répondre.

8. **Format Conversationnel**
- La sortie doit sembler utile et conversationnelle—pas comme un formulaire. Visez un ton naturel tout en restant précis.
"""

    def _create_rewriting_prompt(self) -> str:
        """Prompt pour réécrire les requêtes utilisateur"""
        return """
Vous recevrez une tâche de recherche juridique d'un utilisateur. Votre travail est de produire un ensemble d'instructions pour un chercheur qui complétera la tâche. NE complétez PAS la tâche vous-même, fournissez juste des instructions sur comment la compléter.

DIRECTIVES :
1. **Maximiser la Spécificité et le Détail**
- Incluez toutes les préférences utilisateur connues et listez explicitement les attributs clés ou dimensions à considérer.
- Il est de la plus haute importance que tous les détails de l'utilisateur soient inclus dans les instructions.

2. **Combler les Dimensions Non Déclarées mais Nécessaires**
- Si certains attributs sont essentiels pour une sortie significative mais que l'utilisateur ne les a pas fournis, déclarez explicitement qu'ils sont ouverts ou par défaut sans contrainte spécifique.

3. **Éviter les Suppositions Non Justifiées**
- Si l'utilisateur n'a pas fourni un détail particulier, ne l'inventez pas.
- Au lieu de cela, déclarez le manque de spécification et guidez le chercheur à le traiter comme flexible.

4. **Utiliser la Première Personne**
- Formulez la demande du point de vue de l'utilisateur.

5. **Tableaux**
- Si vous déterminez qu'inclure un tableau aiderait à illustrer, organiser ou améliorer l'information dans la sortie de recherche, vous devez explicitement demander que le chercheur les fournisse.

6. **En-têtes et Formatage**
- Vous devriez inclure le format de sortie attendu dans le prompt.
- Si l'utilisateur demande du contenu qui serait mieux retourné dans un format structuré (ex: rapport, plan), demandez au chercheur de formater comme un rapport avec les en-têtes appropriés.

7. **Langue**
- Si l'entrée utilisateur est dans une langue autre que le français, dites au chercheur de répondre dans cette langue.

8. **Sources**
- Si des sources spécifiques doivent être priorisées, spécifiez-les dans le prompt.
- Pour la recherche juridique, préférez les liens directs vers les sources officielles (Légifrance, sites gouvernementaux, jurisprudence) plutôt que les sites agrégateurs.
"""

    async def deep_research(self, query: ResearchQuery) -> ResearchResult:
        """Effectue une recherche approfondie avec Deep Research API"""
        start_time = datetime.now()
        
        if self.simulation_mode:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ResearchResult(
                query=query.query,
                content=(
                    f"[SIMULATION] Synthèse structurée (depth={query.research_depth}) pour: {query.query}\n"
                    f"Contexte: {query.context or 'N/A'}\n"
                    "- Textes applicables (CESEDA)\n"
                    "- Jurisprudence récente\n"
                    "- Procédures et délais\n"
                    "- Recommandations pratiques"
                ),
                citations=[{"title": "Légifrance - CESEDA", "url": "https://www.legifrance.gouv.fr", "start_index": 0, "end_index": 10}],
                reasoning_steps=["Compréhension du besoin", "Collecte de sources", "Analyse", "Synthèse"],
                search_queries=[query.query],
                execution_time=execution_time,
                model_used="simulation",
                confidence_score=0.8
            )
        
        try:
            # Choisir le modèle selon la profondeur demandée
            model = (self.config.model_deep_research if query.research_depth == "detailed" 
                    else self.config.model_deep_research_mini)
            
            # Construire le message système
            system_message = self.legal_research_prompt
            if query.domain:
                system_message += f"\n\nDOMAINE SPÉCIALISÉ : {query.domain}"
            if query.context:
                system_message += f"\n\nCONTEXTE ADDITIONNEL : {query.context}"
            
            # Appel à l'API Deep Research
            response = await self.async_client.responses.create(
                model=model,
                input=[
                    {
                        "role": "developer",
                        "content": [
                            {
                                "type": "input_text",
                                "text": system_message,
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": query.query,
                            }
                        ]
                    }
                ],
                reasoning={
                    "summary": query.research_depth
                },
                tools=[
                    {
                        "type": "web_search_preview"
                    },
                    {
                        "type": "code_interpreter",
                        "container": {
                            "type": "auto",
                            "file_ids": []
                        }
                    }
                ]
            )
            
            # Extraire le contenu principal
            main_content = response.output[-1].content[0].text
            
            # Extraire les citations
            citations = []
            if hasattr(response.output[-1].content[0], 'annotations'):
                for annotation in response.output[-1].content[0].annotations:
                    citations.append({
                        "title": annotation.title,
                        "url": annotation.url,
                        "start_index": annotation.start_index,
                        "end_index": annotation.end_index
                    })
            
            # Extraire les étapes de raisonnement
            reasoning_steps = []
            for item in response.output:
                if item.type == "reasoning":
                    for step in item.summary:
                        reasoning_steps.append(step.text)
            
            # Extraire les requêtes de recherche
            search_queries = []
            for item in response.output:
                if item.type == "web_search_call":
                    search_queries.append(item.action.get("query", ""))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ResearchResult(
                query=query.query,
                content=main_content,
                citations=citations,
                reasoning_steps=reasoning_steps,
                search_queries=search_queries,
                execution_time=execution_time,
                model_used=model
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche approfondie: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ResearchResult(
                query=query.query,
                content=f"Erreur lors de la recherche: {str(e)}",
                citations=[],
                reasoning_steps=[],
                search_queries=[],
                execution_time=execution_time,
                model_used=model,
                confidence_score=0.0
            )

    async def clarify_query(self, user_query: str) -> str:
        """Pose des questions de clarification pour une requête utilisateur"""
        if self.simulation_mode:
            return (
                "Pour affiner la recherche, pouvez-vous préciser:\n"
                "- La nationalité du client ?\n"
                "- Le type de procédure (première demande, renouvellement, recours) ?\n"
                "- La juridiction concernée ou la préfecture ?\n"
                "- Le degré d'urgence (normal/urgent) ?"
            )
        try:
            response = await self.async_client.responses.create(
                instructions=self.clarifying_prompt,
                model=self.config.model_gpt4,
                input=user_query
            )
            
            return response.output[0].content[0].text
            
        except Exception as e:
            logger.error(f"Erreur lors de la clarification: {e}")
            return f"Erreur lors de la clarification de la requête: {str(e)}"

    async def rewrite_query(self, user_input: str) -> str:
        """Réécrit une requête utilisateur pour optimiser la recherche"""
        if self.simulation_mode:
            return f"[SIMULATION] Instruction de recherche structurée basée sur le contexte fourni.\n\n{user_input}"
        try:
            response = await self.async_client.responses.create(
                instructions=self.rewriting_prompt,
                model=self.config.model_gpt4,
                input=user_input
            )
            
            return response.output[0].content[0].text
            
        except Exception as e:
            logger.error(f"Erreur lors de la réécriture: {e}")
            return user_input  # Retourner l'original en cas d'erreur

    async def gpt_completion(self, 
                           messages: List[Dict[str, str]], 
                           model: Optional[str] = None,
                           temperature: Optional[float] = None,
                           max_tokens: Optional[int] = None) -> GPTResponse:
        """Completion GPT standard avec gestion avancée"""
        start_time = datetime.now()
        
        if self.simulation_mode:
            execution_time = (datetime.now() - start_time).total_seconds()
            return GPTResponse(
                content="[SIMULATION] Réponse générée (mode dégradé).",
                model=model or self.config.model_gpt4,
                tokens_used=0,
                execution_time=execution_time,
                finish_reason="stop"
            )
        try:
            response = await self.async_client.chat.completions.create(
                model=model or self.config.model_gpt4,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return GPTResponse(
                content=response.choices[0].message.content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                execution_time=execution_time,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la completion GPT: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return GPTResponse(
                content=f"Erreur lors de la génération: {str(e)}",
                model=model or self.config.model_gpt4,
                tokens_used=0,
                execution_time=execution_time,
                finish_reason="error"
            )

    async def legal_analysis(self, case_description: str, legal_context: str = "") -> ResearchResult:
        """Analyse juridique spécialisée pour un dossier"""
        query = ResearchQuery(
            query=f"Analyse juridique détaillée : {case_description}",
            context=legal_context,
            domain="juridique",
            language="fr",
            research_depth="detailed",
            include_citations=True
        )
        
        return await self.deep_research(query)

    async def jurisprudence_search(self, legal_issue: str, jurisdiction: str = "") -> ResearchResult:
        """Recherche de jurisprudence spécialisée"""
        query_text = f"Recherche de jurisprudence sur : {legal_issue}"
        if jurisdiction:
            query_text += f" - Juridiction : {jurisdiction}"
        
        query = ResearchQuery(
            query=query_text,
            domain="jurisprudence",
            language="fr",
            research_depth="detailed",
            include_citations=True
        )
        
        return await self.deep_research(query)

    async def procedure_guidance(self, procedure_type: str, client_situation: str) -> ResearchResult:
        """Guide procédural personnalisé"""
        query = ResearchQuery(
            query=f"Guide procédural pour {procedure_type} - Situation : {client_situation}",
            domain="procédure",
            language="fr",
            research_depth="auto",
            include_citations=True
        )
        
        return await self.deep_research(query)

    def get_service_stats(self) -> Dict[str, Any]:
        """Statistiques du service OpenAI"""
        return {
            "service_name": "OpenAI Service",
            "models_available": {
                "gpt4": self.config.model_gpt4,
                "deep_research": self.config.model_deep_research,
                "deep_research_mini": self.config.model_deep_research_mini
            },
            "features": [
                "Deep Research API",
                "Web Search Preview",
                "Legal Analysis",
                "Jurisprudence Search",
                "Procedure Guidance",
                "Query Clarification",
                "Query Rewriting"
            ],
            "configuration": {
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "timeout": self.config.timeout
            }
        }


# Factory function pour créer le service
def create_openai_service(api_key: Optional[str] = None) -> OpenAIService:
    """Crée une instance du service OpenAI"""
    if api_key:
        config = OpenAIConfig(api_key=api_key)
    else:
        config = None
    
    return OpenAIService(config)


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation du service OpenAI"""
    service = create_openai_service()
    
    # Recherche approfondie
    query = ResearchQuery(
        query="Quelles sont les conditions pour obtenir un titre de séjour étudiant en France ?",
        domain="juridique",
        research_depth="detailed"
    )

    result = await service.deep_research(query)
    logger.info(f"Résultat: {result.content[:200]}...")
    logger.info(f"Citations: {len(result.citations)}")
    logger.info(f"Temps d'exécution: {result.execution_time}s")

    # Analyse juridique
    legal_result = await service.legal_analysis(
        "Demande de renouvellement de titre de séjour étudiant refusée",
        "Étudiant algérien en master, première demande de renouvellement"
    )
    logger.info(f"Analyse juridique: {legal_result.content[:200]}...")


if __name__ == "__main__":
    asyncio.run(example_usage())
