"""
AGENT 10 - Synthèse Stratégique
Plan d'action et scoring des arguments pour optimiser les chances de succès
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from ..services.openai_service import OpenAIService, create_openai_service
from datetime import datetime

from ..core.base import BaseNode, NodeContext
from ..services.official_legifrance_service import OfficialLegifranceService, NatureTexte, TypeChamp

logger = logging.getLogger(__name__)

class SyntheseStrategiqueNode(BaseNode):
    """
    Agent responsable de la synthèse stratégique et du plan d'action
    
    Inputs: draft.v2, coherence_report, review_reports
    Output: strategic_synthesis (plan d'action et scoring)
    """
    
    def __init__(self):
        super().__init__("synthese_strategique", "Synthèse Stratégique")
        self.openai: Optional[OpenAIService] = create_openai_service()
        self.official_legal_service = None
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Effectue la synthèse stratégique du dossier
        """
        try:
            logger.info("🎯 Début de la synthèse stratégique")
            
            # Récupération des données
            draft_data = await context.shared.get("draft", {})
            draft_v2 = draft_data.get("v2")
            coherence_report = await context.shared.get("coherence_report", {})
            review_report_v1 = await context.shared.get("review_report_v1", {})
            review_report_v2 = await context.shared.get("review_report_v2", {})
            axes_juridiques = await context.shared.get("axes_juridiques", [])
            matches = await context.shared.get("matches", [])
            pieces_parsed = await context.shared.get("pieces_parsed", [])
            meta_info = await context.shared.get("meta_info", {})
            
            if not draft_v2:
                logger.error("Aucun brouillon v2 disponible pour la synthèse")
                raise ValueError("Brouillon v2 manquant")
            
            # Initialisation du client OpenAI
            await self._init_openai_client(context)
            
            # Analyse des forces et faiblesses
            strengths_weaknesses = self._analyze_strengths_weaknesses(
                draft_v2, axes_juridiques, matches, pieces_parsed, coherence_report
            )
            
            # Scoring des arguments
            argument_scoring = await self._score_arguments(
                draft_v2, context
            )
            
            # Évaluation des chances de succès
            success_probability = self._evaluate_success_probability(
                strengths_weaknesses, argument_scoring, coherence_report
            )
            
            # Plan d'action stratégique
            action_plan = await self._generate_action_plan(
                strengths_weaknesses, argument_scoring, success_probability, context
            )
            
            # Recommandations finales
            final_recommendations = await self._generate_final_recommendations(
                draft_v2, strengths_weaknesses, action_plan, context
            )
            
            # Synthèse stratégique complète
            strategic_synthesis = {
                "case_overview": {
                    "type_procedure": meta_info.get('type_procedure', 'Recours administratif'),
                    "complexity_level": self._assess_case_complexity(axes_juridiques, pieces_parsed),
                    "urgency_level": self._assess_urgency(meta_info),
                    "success_probability": success_probability
                },
                "strengths_weaknesses": strengths_weaknesses,
                "argument_scoring": argument_scoring,
                "action_plan": action_plan,
                "final_recommendations": final_recommendations,
                "quality_metrics": {
                    "coherence_score": coherence_report.get('global_quality_score', 0),
                    "empathy_score": review_report_v2.get('stats', {}).get('empathy_score', 0),
                    "legal_coverage": coherence_report.get('analysis_details', {}).get('coverage', {}).get('legal_covered', 0)
                },
                "generated_at": datetime.now().isoformat(),
                "agent_version": "1.0"
            }
            
            # Sauvegarde dans le store
            await context.shared.set("strategic_synthesis", strategic_synthesis)
            
            logger.info(f"✅ Synthèse stratégique terminée (Probabilité succès: {success_probability:.1f}%)")
            
            return {
                "strategic_synthesis": strategic_synthesis,
                "stats": {
                    "success_probability": success_probability,
                    "strong_arguments": len([a for a in argument_scoring.get('arguments', []) if a.get('score', 0) > 80]),
                    "weak_arguments": len([a for a in argument_scoring.get('arguments', []) if a.get('score', 0) < 50]),
                    "action_items": len(action_plan.get('immediate_actions', []))
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans la synthèse stratégique: {e}")
            raise
    
    async def _init_openai_client(self, context: NodeContext):
        """Initialise le service OpenAI"""
        try:
            self.openai = create_openai_service()
            if self.openai and self.openai.simulation_mode:
                logger.warning("Clé API OpenAI manquante, utilisation du mode simulation")
            else:
                logger.info("✅ OpenAIService initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation OpenAI: {e}")
            self.openai = None
    
    def _analyze_strengths_weaknesses(self, draft_v2: Dict[str, Any], axes_juridiques: List[Dict],
                                     matches: List[Dict], pieces_parsed: List[Dict],
                                     coherence_report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les forces et faiblesses du dossier"""
        
        strengths = []
        weaknesses = []
        
        # Analyse des forces
        
        # 1. Qualité des arguments juridiques
        high_quality_matches = [m for m in matches if m.get('score_matching', 0) > 0.8]
        if len(high_quality_matches) >= 3:
            strengths.append({
                "category": "legal",
                "description": f"{len(high_quality_matches)} arguments juridiques solides",
                "impact": "high",
                "confidence": 0.9
            })
        
        # 2. Qualité des pièces justificatives
        key_pieces = [p for p in pieces_parsed if p.get('type_piece') in [
            'decision_administrative', 'piece_identite', 'document_travail'
        ]]
        if len(key_pieces) >= 3:
            strengths.append({
                "category": "evidence",
                "description": f"{len(key_pieces)} pièces justificatives importantes",
                "impact": "high",
                "confidence": 0.85
            })
        
        # 3. Cohérence globale
        coherence_score = coherence_report.get('global_quality_score', 0)
        if coherence_score > 75:
            strengths.append({
                "category": "coherence",
                "description": f"Dossier cohérent (score: {coherence_score:.1f}/100)",
                "impact": "medium",
                "confidence": 0.8
            })
        
        # 4. Diversité des axes juridiques
        if len(axes_juridiques) >= 2:
            strengths.append({
                "category": "strategy",
                "description": f"{len(axes_juridiques)} axes juridiques développés",
                "impact": "medium",
                "confidence": 0.75
            })
        
        # Analyse des faiblesses
        
        # 1. Lacunes identifiées
        gaps = coherence_report.get('analysis_details', {}).get('gaps', {}).get('gaps', [])
        high_priority_gaps = [g for g in gaps if g.get('priority') == 'high']
        
        if high_priority_gaps:
            weaknesses.append({
                "category": "gaps",
                "description": f"{len(high_priority_gaps)} lacunes prioritaires identifiées",
                "impact": "high",
                "confidence": 0.9
            })
        
        # 2. Faible couverture
        coverage_score = coherence_report.get('coverage_score', 0)
        if coverage_score < 60:
            weaknesses.append({
                "category": "coverage",
                "description": f"Couverture insuffisante (score: {coverage_score:.1f}/100)",
                "impact": "high",
                "confidence": 0.85
            })
        
        # 3. Manque de pièces critiques
        if not any(p.get('type_piece') == 'decision_administrative' for p in pieces_parsed):
            weaknesses.append({
                "category": "evidence",
                "description": "Absence de la décision administrative contestée",
                "impact": "critical",
                "confidence": 0.95
            })
        
        # 4. Arguments juridiques faibles
        weak_matches = [m for m in matches if m.get('score_matching', 0) < 0.5]
        if len(weak_matches) > len(matches) * 0.5:
            weaknesses.append({
                "category": "legal",
                "description": f"{len(weak_matches)} arguments juridiques faibles",
                "impact": "medium",
                "confidence": 0.7
            })
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "strength_score": self._calculate_strength_score(strengths),
            "weakness_score": self._calculate_weakness_score(weaknesses)
        }
    
    async def _score_arguments(self, draft_v2: Dict[str, Any], context: NodeContext) -> Dict[str, Any]:
        """Score les arguments juridiques avec validation API officielle"""
        try:
            # Initialisation du service officiel si nécessaire
            if self.official_legal_service is None:
                self.official_legal_service = OfficialLegifranceService()
                await self.official_legal_service.initialize()
            
            content = draft_v2.get('contenu', '')
            axes_juridiques = await context.shared.get("axes_juridiques", [])
            matches = await context.shared.get("matches", [])
            
            arguments = []
            
            for axe in axes_juridiques:
                # Score de base selon la priorité de l'axe
                base_score = axe.get('priorite', 1) * 20
                
                # Validation des références juridiques via API officielle
                legal_validation_score = await self._validate_legal_references(
                    axe, content
                )
                
                # Score basé sur les preuves disponibles
                evidence_score = self._score_evidence_strength(axe, matches)
                
                # Score de cohérence narrative
                narrative_score = self._score_narrative_coherence(axe, content)
                
                # Score final (pondéré)
                final_score = min(100, (
                    base_score * 0.3 +
                    legal_validation_score * 0.4 +  # Poids élevé pour la validation officielle
                    evidence_score * 0.2 +
                    narrative_score * 0.1
                ))
                
                arguments.append({
                    "axe_id": axe.get('id'),
                    "theme": axe.get('theme', ''),
                    "score": round(final_score, 1),
                    "strength": self._categorize_strength(final_score),
                    "legal_validation": legal_validation_score,
                    "evidence_strength": evidence_score,
                    "narrative_coherence": narrative_score,
                    "recommendations": self._generate_argument_recommendations(
                        axe, final_score, legal_validation_score
                    )
                })
            
            # Statistiques globales
            total_score = sum(arg['score'] for arg in arguments)
            avg_score = total_score / len(arguments) if arguments else 0
            
            return {
                "arguments": arguments,
                "global_stats": {
                    "total_arguments": len(arguments),
                    "average_score": round(avg_score, 1),
                    "strong_arguments": len([a for a in arguments if a['score'] >= 70]),
                    "weak_arguments": len([a for a in arguments if a['score'] < 50]),
                    "legal_validation_avg": round(
                        sum(a['legal_validation'] for a in arguments) / len(arguments), 1
                    ) if arguments else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur scoring arguments: {e}")
            return {"arguments": [], "error": str(e)}
    
    async def _validate_legal_references(self, axe: Dict[str, Any], content: str) -> float:
        """Valide les références juridiques via l'API officielle Légifrance"""
        try:
            validation_score = 0
            total_refs = 0
            
            # Extraction des mots-clés de l'axe
            keywords = axe.get('mots_cles', [])
            articles_cibles = axe.get('articles_cibles', [])
            
            # Validation des articles cibles
            for article in articles_cibles:
                total_refs += 1
                try:
                    # Recherche via API officielle
                    results = await self.official_legal_service.search_legal_texts(
                        query=article,
                        nature=NatureTexte.CODE,
                        champ=TypeChamp.ALL,
                        page_size=1
                    )
                    
                    if results:
                        # Vérification de la présence dans le contenu
                        if article.lower() in content.lower():
                            validation_score += 25  # Référence trouvée et utilisée
                        else:
                            validation_score += 15  # Référence valide mais non utilisée
                    else:
                        validation_score += 0  # Référence invalide
                        
                except Exception as e:
                    logger.warning(f"Erreur validation article {article}: {e}")
                    validation_score += 5  # Score minimal pour erreur technique
            
            # Validation des concepts juridiques via recherche sémantique
            for keyword in keywords[:3]:  # Limite aux 3 premiers mots-clés
                total_refs += 1
                try:
                    results = await self.official_legal_service.search_legal_texts(
                        query=keyword,
                        nature=NatureTexte.LODA,  # Recherche dans les lois et décrets
                        champ=TypeChamp.ALL,
                        page_size=3
                    )
                    
                    if results:
                        # Score basé sur la pertinence des résultats
                        relevance_scores = [r.relevance_score for r in results]
                        avg_relevance = sum(relevance_scores) / len(relevance_scores)
                        validation_score += min(20, avg_relevance * 20)
                    
                except Exception as e:
                    logger.warning(f"Erreur validation concept {keyword}: {e}")
                    validation_score += 5
            
            # Normalisation du score (0-100)
            final_score = (validation_score / (total_refs * 25)) * 100 if total_refs > 0 else 0
            return min(100, final_score)
            
        except Exception as e:
            logger.error(f"Erreur validation références juridiques: {e}")
            return 0
    
    def _generate_argument_recommendations(self, axe: Dict[str, Any], score: float, legal_validation: float) -> List[str]:
        """Génère des recommandations pour améliorer l'argument"""
        recommendations = []
        
        if score < 50:
            recommendations.append("Argument faible - Renforcer avec plus de preuves")
        
        if legal_validation < 60:
            recommendations.append("Validation juridique insuffisante - Vérifier les références")
            recommendations.append("Consulter les dernières jurisprudences via Légifrance")
        
        if score < 70 and legal_validation > 80:
            recommendations.append("Bases juridiques solides - Améliorer la présentation narrative")
        
        # Recommandations spécifiques selon le thème
        theme = axe.get('theme', '').lower()
        if 'oqtf' in theme and score < 70:
            recommendations.append("OQTF: Vérifier les délais de recours et motifs d'annulation")
        elif 'titre' in theme and 'séjour' in theme and score < 70:
            recommendations.append("Titre de séjour: Documenter les conditions de renouvellement")
        elif 'regroupement' in theme and score < 70:
            recommendations.append("Regroupement familial: Justifier les conditions de ressources et logement")
        
        return recommendations[:3]  # Limite à 3 recommandations
    
    async def _generate_action_plan(self, strengths_weaknesses: Dict[str, Any],
                                   argument_scoring: Dict[str, Any],
                                   success_probability: float,
                                   context: NodeContext) -> Dict[str, Any]:
        """Génère un plan d'action stratégique"""
        
        if self.openai and not self.openai.simulation_mode:
            return await self._ai_action_plan(strengths_weaknesses, argument_scoring, success_probability)
        else:
            return self._mock_action_plan(strengths_weaknesses, argument_scoring)
    
    async def _ai_action_plan(self, strengths_weaknesses: Dict[str, Any],
                             argument_scoring: Dict[str, Any],
                             success_probability: float) -> Dict[str, Any]:
        """Génère un plan d'action avec IA"""
        
        try:
            strengths = strengths_weaknesses.get('strengths', [])
            weaknesses = strengths_weaknesses.get('weaknesses', [])
            weak_arguments = argument_scoring.get('weak_arguments', [])
            
            action_prompt = f"""En tant que stratège juridique expert, élabore un plan d'action pour optimiser ce dossier de recours administratif.

FORCES IDENTIFIÉES :
{chr(10).join([f"- {s.get('description', '')}" for s in strengths[:5]])}

FAIBLESSES IDENTIFIÉES :
{chr(10).join([f"- {w.get('description', '')}" for w in weaknesses[:5]])}

ARGUMENTS FAIBLES :
{chr(10).join([f"- {a.get('theme', '')}: {a.get('score', 0)}/100" for a in weak_arguments[:3]])}

PROBABILITÉ DE SUCCÈS ACTUELLE : {success_probability:.1f}%

Élabore un plan avec :
1. Actions immédiates (0-7 jours)
2. Actions à moyen terme (1-4 semaines)
3. Stratégies de renforcement
4. Plans de contingence

Réponds en JSON avec : immediate_actions, medium_term_actions, reinforcement_strategies, contingency_plans"""
            
            gpt_response = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": "Tu es un stratège juridique expert. Élabore un plan d'action précis et réalisable."},
                    {"role": "user", "content": action_prompt}
                ],
                model=self.openai.config.model_gpt4,
                temperature=0.3,
                max_tokens=1500
            )
            
            import json
            try:
                action_plan = json.loads(gpt_response.content)
                return action_plan
            except json.JSONDecodeError:
                return self._mock_action_plan(strengths_weaknesses, argument_scoring)
                
        except Exception as e:
            logger.error(f"Erreur génération plan d'action IA: {e}")
            return self._mock_action_plan(strengths_weaknesses, argument_scoring)
    
    def _mock_action_plan(self, strengths_weaknesses: Dict[str, Any],
                         argument_scoring: Dict[str, Any]) -> Dict[str, Any]:
        """Plan d'action mock"""
        
        weaknesses = strengths_weaknesses.get('weaknesses', [])
        weak_arguments = argument_scoring.get('weak_arguments', [])
        
        immediate_actions = [
            "Vérifier et compléter les pièces justificatives manquantes",
            "Renforcer la chronologie avec des dates précises",
            "Réviser les arguments juridiques les plus faibles"
        ]
        
        if any(w.get('category') == 'evidence' for w in weaknesses):
            immediate_actions.append("Rassembler les preuves supplémentaires")
        
        if weak_arguments:
            immediate_actions.append(f"Développer l'argument sur {weak_arguments[0].get('theme', '')}")
        
        return {
            "immediate_actions": immediate_actions[:5],
            "medium_term_actions": [
                "Préparer la défense orale si nécessaire",
                "Identifier des témoins potentiels",
                "Rechercher de la jurisprudence complémentaire"
            ],
            "reinforcement_strategies": [
                "Mettre l'accent sur les arguments les plus forts",
                "Développer l'aspect humain et familial",
                "Renforcer les preuves d'intégration"
            ],
            "contingency_plans": [
                "Préparer un recours hiérarchique en cas d'échec",
                "Envisager un référé en cas d'urgence",
                "Prévoir un appel devant le tribunal administratif"
            ]
        }
    
    async def _generate_final_recommendations(self, draft_v2: Dict[str, Any],
                                            strengths_weaknesses: Dict[str, Any],
                                            action_plan: Dict[str, Any],
                                            context: NodeContext) -> List[str]:
        """Génère les recommandations finales"""
        
        recommendations = []
        
        # Recommandations basées sur les faiblesses
        weaknesses = strengths_weaknesses.get('weaknesses', [])
        for weakness in weaknesses[:3]:
            if weakness.get('impact') in ['critical', 'high']:
                recommendations.append(f"PRIORITÉ HAUTE: {weakness.get('description', '')}")
        
        # Recommandations basées sur le plan d'action
        immediate_actions = action_plan.get('immediate_actions', [])
        for action in immediate_actions[:2]:
            recommendations.append(f"ACTION IMMÉDIATE: {action}")
        
        # Recommandations stratégiques
        reinforcement_strategies = action_plan.get('reinforcement_strategies', [])
        for strategy in reinforcement_strategies[:2]:
            recommendations.append(f"STRATÉGIE: {strategy}")
        
        return recommendations[:8]  # Maximum 8 recommandations
    
    def _calculate_strength_score(self, strengths: List[Dict]) -> float:
        """Calcule le score des forces"""
        if not strengths:
            return 0
        
        impact_weights = {'critical': 30, 'high': 20, 'medium': 10, 'low': 5}
        total_score = 0
        
        for strength in strengths:
            impact = strength.get('impact', 'low')
            confidence = strength.get('confidence', 0.5)
            score = impact_weights.get(impact, 5) * confidence
            total_score += score
        
        return min(100, total_score)
    
    def _calculate_weakness_score(self, weaknesses: List[Dict]) -> float:
        """Calcule le score des faiblesses (plus élevé = plus de faiblesses)"""
        if not weaknesses:
            return 0
        
        impact_weights = {'critical': 40, 'high': 25, 'medium': 15, 'low': 8}
        total_score = 0
        
        for weakness in weaknesses:
            impact = weakness.get('impact', 'low')
            confidence = weakness.get('confidence', 0.5)
            score = impact_weights.get(impact, 8) * confidence
            total_score += score
        
        return min(100, total_score)
    
    def _get_argument_recommendation(self, score: float) -> str:
        """Retourne une recommandation basée sur le score"""
        if score > 80:
            return "Argument fort - à mettre en avant"
        elif score > 60:
            return "Argument correct - à développer"
        elif score > 40:
            return "Argument faible - à renforcer"
        else:
            return "Argument très faible - à reconsidérer"
    
    def _assess_case_complexity(self, axes_juridiques: List[Dict], pieces_parsed: List[Dict]) -> str:
        """Évalue la complexité du dossier"""
        complexity_score = len(axes_juridiques) * 2 + len(pieces_parsed)
        
        if complexity_score > 15:
            return "complexe"
        elif complexity_score > 8:
            return "moyenne"
        else:
            return "simple"
    
    def _assess_urgency(self, meta_info: Dict[str, Any]) -> str:
        """Évalue l'urgence du dossier"""
        # Logique d'évaluation de l'urgence basée sur les métadonnées
        situation = meta_info.get('situation', '').lower()
        
        if any(keyword in situation for keyword in ['expulsion', 'éloignement', 'oqtf']):
            return "haute"
        elif any(keyword in situation for keyword in ['renouvellement', 'régularisation']):
            return "moyenne"
        else:
            return "normale"
