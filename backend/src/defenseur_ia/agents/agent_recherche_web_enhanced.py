"""
Agent de Recherche Web Amélioré pour DEFENSEUR-IA
Utilise OpenAI Deep Research API et GPT-4.1 pour des recherches juridiques avancées
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from urllib.parse import urlparse

from .enhanced_agent_base import EnhancedAgentBase
from ..models import AgentResult
from ..core.base import NodeContext
from ..services.openai_service import OpenAIService, ResearchQuery, ResearchResult
from ..config.legifrance_config import LegifranceConfigManager
from ..services.unified_embedding_service import UnifiedEmbeddingService

logger = logging.getLogger(__name__)


@dataclass
class WebResearchConfig:
    """Configuration pour l'agent de recherche web"""
    use_deep_research: bool = True
    use_clarification: bool = True
    use_query_rewriting: bool = True
    max_research_depth: str = "detailed"  # auto, detailed, summary
    include_jurisprudence: bool = True
    include_procedures: bool = True
    fallback_to_traditional: bool = True


@dataclass
class ResearchContext:
    """Contexte de recherche pour l'agent"""
    case_data: Dict[str, Any]
    legal_domain: str
    client_nationality: Optional[str] = None
    procedure_type: Optional[str] = None
    urgency_level: str = "normal"  # low, normal, high, urgent
    previous_research: List[str] = None

    def __post_init__(self):
        if self.previous_research is None:
            self.previous_research = []


class AgentRechercheWebEnhanced(EnhancedAgentBase):
    """
    Agent de recherche web amélioré avec Deep Research API
    Spécialisé dans la recherche juridique approfondie
    """
    
    def __init__(self, config: Optional[WebResearchConfig] = None):
        super().__init__("recherche_web_enhanced")
        self.agent_name = "recherche_web_enhanced"
        self.agent_description = "Agent de recherche web avancé avec Deep Research API"
        
        self.config = config or WebResearchConfig()
        self.openai_service = OpenAIService()
        self.legifrance_config = LegifranceConfigManager()
        self.embedding_service = UnifiedEmbeddingService()
        
        # Métriques de performance
        self.research_stats = {
            "total_queries": 0,
            "deep_research_calls": 0,
            "traditional_searches": 0,
            "clarifications_requested": 0,
            "queries_rewritten": 0,
            "average_response_time": 0.0,
            "success_rate": 0.0
        }

    async def exec(self, ctx: NodeContext) -> None:
        """Exécution asynchrone intégrée au pipeline DEFENSEUR-IA.
 
         - Récupère l'entrée depuis le SharedStore (`query`, `case_data`, `urgency`/`urgence`).
         - Appelle `process_async` pour la recherche avancée.
         - Transforme les citations en `web_corpus` (format legacy `RessourceWeb`).
         - Stocke les résultats dans le SharedStore et met à jour les métadonnées.
         - Gère les erreurs de manière robuste.
         """
        start_time = datetime.now()
        ctx.set_metadata("agent", self.agent_name)
        ctx.set_metadata("start_time", start_time.isoformat())
 
        try:
            # 1) Récupération des entrées depuis le SharedStore (avec fallbacks)
            query = await ctx.shared.get("query")
            case_data = await ctx.shared.get("case_data")
            urgency = await ctx.shared.get("urgency")
            if urgency is None:
                urgency = await ctx.shared.get("urgence")
 
            # Fallback: extraire depuis l'input_blob si présent
            if not query or case_data is None or urgency is None:
                input_blob = await ctx.shared.get("input_blob", {})
                if not query:
                    query = input_blob.get("query")
                if case_data is None:
                    case_data = input_blob.get("case_data")
                if urgency is None:
                    urgency = input_blob.get("urgency") or input_blob.get("urgence")
 
            input_data: Dict[str, Any] = {
                "query": query or "",
                "case_data": case_data or {},
                "urgency": urgency or "normal",
            }
 
            # 2) Appel du traitement principal
            agent_result: AgentResult = await self.process_async(input_data)
 
            # 3) Conversion AgentResult -> dict (compatibilité Pydantic v1/v2)
            if hasattr(agent_result, "model_dump"):
                agent_result_dict = agent_result.model_dump()
            else:
                agent_result_dict = agent_result.dict()  # type: ignore[attr-defined]
 
            payload = agent_result_dict.get("result", {}) or {}
            citations = payload.get("citations", []) or []
            metrics = payload.get("metrics", {}) or {}
 
            # 4) Transformer les citations en web_corpus (format legacy attendu en aval)
            avg_conf = metrics.get("average_confidence")
            try:
                default_score = float(avg_conf) if avg_conf is not None else 0.7
            except Exception:
                default_score = 0.7
            default_score = max(0.0, min(1.0, default_score))
 
            web_corpus: List[Dict[str, Any]] = []
            now_iso = datetime.now().isoformat()
            for c in citations:
                url = c.get("url") or c.get("link") or ""
                title = c.get("title") or c.get("titre") or url
                snippet = c.get("snippet") or c.get("description") or c.get("summary") or ""
                domain = ""
                try:
                    domain = urlparse(url).netloc
                except Exception:
                    domain = ""
 
                item = {
                    "url": url,
                    "titre": title,
                    "description": snippet,
                    "contenu": snippet,
                    "source": domain or "web",
                    "pertinence": default_score,
                    "date_acces": now_iso,
                }
                web_corpus.append(item)
 
            # 5) Stockage des résultats dans le SharedStore
            await ctx.shared.set("recherche_web_enhanced", agent_result_dict)
            await ctx.shared.set("web_corpus", web_corpus)
 
            # Agrégation des résultats d'agents
            aggregated = await ctx.shared.get("agent_results", [])
            if not isinstance(aggregated, list):
                aggregated = []
            aggregated.append(agent_result_dict)
            await ctx.shared.set("agent_results", aggregated)
 
            # 6) Mise à jour des métadonnées d'exécution
            execution_time = (datetime.now() - start_time).total_seconds()
            models_used = metrics.get("models_used")
            if not models_used:
                # fallback: extraire depuis research_results
                rr = payload.get("research_results") or []
                models_used = list({r.get("model_used") for r in rr if isinstance(r, dict) and r.get("model_used")})
 
            ctx.set_metadata("status", "completed")
            ctx.set_metadata("execution_time_seconds", execution_time)
            if models_used:
                ctx.set_metadata("models_used", models_used)
            ctx.set_metadata("citations_count", len(citations))
 
        except Exception as e:
            # 7) Gestion d'erreur robuste
            logger.error(f"Erreur dans exec() {self.agent_name}: {e}")
            error_info = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            try:
                await ctx.shared.set("recherche_web_enhanced_error", error_info)
            except Exception:
                pass
            ctx.set_metadata("status", "error")
            ctx.set_metadata("error", str(e))
            ctx.set_metadata("execution_time_seconds", (datetime.now() - start_time).total_seconds())
            raise

    async def process_async(self, input_data: Dict[str, Any]) -> AgentResult:
        """Traitement principal de l'agent"""
        start_time = datetime.now()
        
        try:
            # Extraire les données d'entrée
            research_context = self._extract_research_context(input_data)
            user_query = input_data.get("query", "")
            
            if not user_query:
                return self._create_error_result("Aucune requête de recherche fournie")
            
            # Étape 1: Clarification si nécessaire
            clarified_query = user_query
            if self.config.use_clarification and self._needs_clarification(user_query):
                clarification = await self._request_clarification(user_query)
                if clarification:
                    # En production, on pourrait demander à l'utilisateur
                    # Ici on utilise la clarification pour améliorer la requête
                    clarified_query = f"{user_query}\n\nClarifications nécessaires: {clarification}"
                    self.research_stats["clarifications_requested"] += 1
            
            # Étape 2: Réécriture de la requête
            optimized_query = clarified_query
            if self.config.use_query_rewriting:
                optimized_query = await self._rewrite_query(clarified_query, research_context)
                self.research_stats["queries_rewritten"] += 1
            
            # Étape 3: Recherche principale
            research_results = []
            
            if self.config.use_deep_research:
                # Recherche approfondie avec Deep Research API
                deep_result = await self._deep_research(optimized_query, research_context)
                research_results.append(deep_result)
                self.research_stats["deep_research_calls"] += 1
            
            # Étape 4: Recherches spécialisées complémentaires
            if self.config.include_jurisprudence:
                jurisprudence_result = await self._search_jurisprudence(optimized_query, research_context)
                if jurisprudence_result:
                    research_results.append(jurisprudence_result)
            
            if self.config.include_procedures:
                procedure_result = await self._search_procedures(optimized_query, research_context)
                if procedure_result:
                    research_results.append(procedure_result)
            
            # Étape 5: Recherche traditionnelle en fallback si nécessaire
            if self.config.fallback_to_traditional and not research_results:
                traditional_result = await self._traditional_search(optimized_query, research_context)
                if traditional_result:
                    research_results.append(traditional_result)
                    self.research_stats["traditional_searches"] += 1
            
            # Étape 6: Synthèse des résultats
            final_result = await self._synthesize_results(research_results, research_context)
            
            # Mise à jour des statistiques
            execution_time = (datetime.now() - start_time).total_seconds()
            self.research_stats["total_queries"] += 1
            self.research_stats["average_response_time"] = (
                (self.research_stats["average_response_time"] * (self.research_stats["total_queries"] - 1) + execution_time) /
                self.research_stats["total_queries"]
            )
            
            if getattr(final_result, "status", "") == "success":
                success_count = self.research_stats["total_queries"] * self.research_stats["success_rate"] / 100 + 1
                self.research_stats["success_rate"] = (success_count / self.research_stats["total_queries"]) * 100
            
            return final_result
            
        except Exception as e:
            logger.error(f"Erreur dans l'agent de recherche web: {e}")
            return self._create_error_result(f"Erreur lors de la recherche: {str(e)}")

    def _extract_research_context(self, input_data: Dict[str, Any]) -> ResearchContext:
        """Extrait le contexte de recherche des données d'entrée"""
        raw_case = input_data.get("case_data") or {}
        # Normaliser en dict, sans imposer le schéma CaseData
        if hasattr(raw_case, "model_dump"):
            case_data = raw_case.model_dump()
        elif isinstance(raw_case, dict):
            case_data = raw_case
        else:
            try:
                case_data = asdict(raw_case)
            except Exception:
                case_data = getattr(raw_case, "__dict__", {}) or {}
        
        # Déterminer le domaine juridique
        legal_domain = self._determine_legal_domain(input_data)
        
        # Extraire la nationalité du client
        client_nationality = None
        if isinstance(case_data, dict):
            ci = case_data.get("client_info")
            if isinstance(ci, dict):
                client_nationality = ci.get("nationality")
        
        # Déterminer le type de procédure
        procedure_type = self._determine_procedure_type(input_data)
        
        # Niveau d'urgence
        urgency_level = input_data.get("urgency", "normal")
        
        return ResearchContext(
            case_data=case_data,
            legal_domain=legal_domain,
            client_nationality=client_nationality,
            procedure_type=procedure_type,
            urgency_level=urgency_level,
            previous_research=input_data.get("previous_results", {}).get("recherche_web", [])
        )

    def _determine_legal_domain(self, input_data: Dict[str, Any]) -> str:
        """Détermine le domaine juridique principal"""
        # Analyse du titre et de la description du dossier
        case_data = input_data.get("case_data", {})
        title = case_data.get("title", "").lower()
        description = case_data.get("description", "").lower()
        
        keywords_mapping = {
            "titre_sejour": ["titre", "séjour", "étudiant", "salarié", "vie privée"],
            "regroupement_familial": ["regroupement", "familial", "conjoint", "enfant"],
            "naturalisation": ["naturalisation", "nationalité", "française"],
            "asile": ["asile", "réfugié", "protection", "subsidiaire"],
            "oqtf": ["oqtf", "expulsion", "reconduite", "frontière"],
            "contentieux": ["recours", "tribunal", "administratif", "contentieux"]
        }
        
        text_to_analyze = f"{title} {description}"
        
        for domain, keywords in keywords_mapping.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                return domain
        
        return "general"

    def _determine_procedure_type(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Détermine le type de procédure"""
        case_data = input_data.get("case_data", {})
        description = case_data.get("description", "").lower()
        
        if "première demande" in description:
            return "premiere_demande"
        elif "renouvellement" in description:
            return "renouvellement"
        elif "recours" in description:
            return "recours"
        elif "naturalisation" in description:
            return "naturalisation"
        
        return None

    def _needs_clarification(self, query: str) -> bool:
        """Détermine si une requête a besoin de clarification"""
        # Critères simples pour déterminer si clarification nécessaire
        clarification_indicators = [
            len(query.split()) < 5,  # Requête très courte
            "?" not in query and len(query.split()) < 10,  # Pas de question claire
            any(word in query.lower() for word in ["aide", "comment", "que faire", "problème"])
        ]
        
        return any(clarification_indicators)

    async def _request_clarification(self, query: str) -> Optional[str]:
        """Demande des clarifications pour une requête"""
        try:
            clarification = await self.openai_service.clarify_query(query)
            return clarification
        except Exception as e:
            logger.error(f"Erreur lors de la clarification: {e}")
            return None

    async def _rewrite_query(self, query: str, context: ResearchContext) -> str:
        """Réécrit une requête pour optimiser la recherche"""
        try:
            # Ajouter le contexte à la requête
            context_info = f"""
Contexte du dossier:
- Domaine juridique: {context.legal_domain}
- Nationalité du client: {context.client_nationality or 'Non spécifiée'}
- Type de procédure: {context.procedure_type or 'Non spécifié'}
- Niveau d'urgence: {context.urgency_level}

Requête originale: {query}
"""
            
            rewritten = await self.openai_service.rewrite_query(context_info)
            return rewritten
        except Exception as e:
            logger.error(f"Erreur lors de la réécriture: {e}")
            return query

    async def _deep_research(self, query: str, context: ResearchContext) -> ResearchResult:
        """Effectue une recherche approfondie avec Deep Research API"""
        research_query = ResearchQuery(
            query=query,
            context=f"Domaine: {context.legal_domain}, Nationalité: {context.client_nationality}",
            domain="juridique",
            language="fr",
            research_depth=self.config.max_research_depth,
            include_citations=True
        )
        
        return await self.openai_service.deep_research(research_query)

    async def _search_jurisprudence(self, query: str, context: ResearchContext) -> Optional[ResearchResult]:
        """Recherche de jurisprudence spécialisée"""
        try:
            jurisprudence_query = f"Jurisprudence {context.legal_domain}: {query}"
            if context.client_nationality:
                jurisprudence_query += f" - Nationalité: {context.client_nationality}"
            
            return await self.openai_service.jurisprudence_search(
                jurisprudence_query,
                jurisdiction="Conseil d'État, Cour administrative d'appel"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de jurisprudence: {e}")
            return None

    async def _search_procedures(self, query: str, context: ResearchContext) -> Optional[ResearchResult]:
        """Recherche de guides procéduraux"""
        try:
            if not context.procedure_type:
                return None
            
            client_situation = f"Nationalité: {context.client_nationality}, Domaine: {context.legal_domain}"
            
            return await self.openai_service.procedure_guidance(
                context.procedure_type,
                client_situation
            )
        except Exception as e:
            logger.error(f"Erreur lors de la recherche procédurale: {e}")
            return None

    async def _traditional_search(self, query: str, context: ResearchContext) -> Optional[ResearchResult]:
        """Recherche traditionnelle en fallback"""
        try:
            # Utiliser GPT-4.1 pour une recherche structurée
            messages = [
                {
                    "role": "system",
                    "content": f"""Vous êtes un assistant juridique spécialisé en droit des étrangers.
                    Effectuez une recherche structurée sur: {query}
                    
                    Contexte:
                    - Domaine: {context.legal_domain}
                    - Nationalité: {context.client_nationality}
                    - Procédure: {context.procedure_type}
                    
                    Fournissez une réponse structurée avec sources."""
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            gpt_response = await self.openai_service.gpt_completion(messages)
            
            return ResearchResult(
                query=query,
                content=gpt_response.content,
                citations=[],
                reasoning_steps=["Recherche traditionnelle GPT-4.1"],
                search_queries=[query],
                execution_time=gpt_response.execution_time,
                model_used=gpt_response.model,
                confidence_score=0.7
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche traditionnelle: {e}")
            return None

    async def _synthesize_results(self, results: List[ResearchResult], context: ResearchContext) -> AgentResult:
        """Synthétise les résultats de recherche"""
        if not results:
            return self._create_error_result("Aucun résultat de recherche obtenu")
        
        # Combiner tous les contenus
        combined_content = []
        all_citations = []
        all_reasoning_steps = []
        all_search_queries = []
        total_execution_time = 0
        
        for i, result in enumerate(results):
            combined_content.append(f"## Résultat {i+1} ({result.model_used})\n{result.content}")
            all_citations.extend(result.citations)
            all_reasoning_steps.extend(result.reasoning_steps)
            all_search_queries.extend(result.search_queries)
            total_execution_time += result.execution_time
        
        # Créer une synthèse finale
        synthesis_content = "\n\n".join(combined_content)
        
        # Métriques détaillées
        confs = [r.confidence_score for r in results if getattr(r, "confidence_score", None) is not None]
        avg_conf = (sum(confs) / len(confs)) if confs else None
        metrics = {
            "total_results": len(results),
            "total_citations": len(all_citations),
            "total_execution_time": total_execution_time,
            "models_used": list(set(r.model_used for r in results)),
            "search_queries_count": len(all_search_queries),
            "reasoning_steps_count": len(all_reasoning_steps),
            "research_depth": self.config.max_research_depth,
            "legal_domain": context.legal_domain,
            "agent_stats": self.research_stats,
            "average_confidence": avg_conf
        }
        
        # Construire le payload de résultat conforme aux modèles Pydantic
        result_payload: Dict[str, Any] = {
            "content": synthesis_content,
            "citations": all_citations,
            "reasoning_steps": all_reasoning_steps,
            "search_queries": all_search_queries,
            "research_context": asdict(context),
            "metrics": metrics,
            "research_results": [asdict(r) for r in results],
        }
        
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="success",
            result=result_payload,
            execution_time=total_execution_time,
            timestamp=datetime.now(),
            errors=[]
        )

    def _create_error_result(self, error_message: str) -> AgentResult:
        """Crée un résultat d'erreur"""
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status="error",
            result={"error": error_message},
            execution_time=0.0,
            timestamp=datetime.now(),
            errors=[error_message]
        )

    def get_agent_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'agent"""
        return {
            "agent_name": self.agent_name,
            "agent_description": self.agent_description,
            "configuration": asdict(self.config),
            "performance_stats": self.research_stats,
            "capabilities": [
                "Deep Research API",
                "Query Clarification",
                "Query Rewriting",
                "Jurisprudence Search",
                "Procedure Guidance",
                "Traditional Fallback",
                "Multi-source Synthesis"
            ]
        }

    async def test_capabilities(self) -> Dict[str, Any]:
        """Test des capacités de l'agent"""
        test_results = {}
        
        # Test de recherche simple
        try:
            simple_query = "Conditions pour obtenir un titre de séjour étudiant"
            test_input = {
                "query": simple_query,
                "case_data": {
                    "id": "test_001",
                    "title": "Demande titre de séjour étudiant",
                    "description": "Première demande de titre de séjour pour études",
                    "client_info": {"nationality": "Algérienne"}
                }
            }
            
            result = await self.process_async(test_input)
            test_results["simple_research"] = {
                "success": (getattr(result, "status", "error") == "success"),
                "execution_time": getattr(result, "execution_time", 0.0),
                "content_length": len(getattr(result, "result", {}).get("content", ""))
            }
            
        except Exception as e:
            test_results["simple_research"] = {"error": str(e)}
        
        # Test des services
        test_results["openai_service"] = self.openai_service.get_service_stats()
        test_results["agent_stats"] = self.get_agent_stats()
        
        return test_results


# Factory function
def create_enhanced_web_research_agent(config: Optional[WebResearchConfig] = None) -> AgentRechercheWebEnhanced:
    """Crée une instance de l'agent de recherche web amélioré"""
    return AgentRechercheWebEnhanced(config)


# Exemple d'utilisation
async def example_usage():
    """Exemple d'utilisation de l'agent"""
    agent = create_enhanced_web_research_agent()
    
    # Test avec un cas réel
    test_input = {
        "query": "Mon client algérien étudiant en master a vu sa demande de renouvellement de titre de séjour refusée. Quels sont les recours possibles ?",
        "case_data": {
            "id": "case_001",
            "title": "Refus renouvellement titre séjour étudiant",
            "description": "Étudiant algérien en master 2, première demande de renouvellement refusée par la préfecture",
            "client_info": {
                "name": "Ahmed Benali",
                "nationality": "Algérienne"
            }
        },
        "urgency": "high"
    }
    
    result = await agent.process_async(test_input)
    
    print(f"Statut: {getattr(result, 'status', 'unknown')}")
    print(f"Temps d'exécution: {getattr(result, 'execution_time', 0.0)}s")
    content = getattr(result, "result", {}).get("content", "")
    print(f"Contenu (extrait): {content[:300]}...")
    
    payload = getattr(result, "result", {})
    metrics = payload.get("metrics", {})
    print(f"Confiance moyenne: {metrics.get('average_confidence')}")
    print(f"Citations: {len(payload.get('citations', []))}")
    print(f"Requêtes de recherche: {payload.get('search_queries', [])}")
    
    # Afficher les statistiques
    stats = agent.get_agent_stats()
    print(f"Statistiques agent: {stats['performance_stats']}")


if __name__ == "__main__":
    asyncio.run(example_usage())
