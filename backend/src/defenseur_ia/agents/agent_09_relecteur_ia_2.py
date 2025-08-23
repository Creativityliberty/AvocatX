"""
AGENT 9 - Relecteur IA #2
Deuxième niveau de relecture : peaufinage style, empathie, divergent
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.base import BaseNode, NodeContext
from ..models import DraftNarratif
from ..services.openai_service import OpenAIService, create_openai_service

logger = logging.getLogger(__name__)

class RelecteurIA2Node(BaseNode):
    """
    Agent responsable de la deuxième relecture (style et empathie)
    
    Inputs: draft.v1, coherence_report
    Output: draft.v2 (version peaufinée)
    """
    
    def __init__(self):
        super().__init__("relecteur_ia_2", "Relecteur IA #2")
        self.openai: Optional[OpenAIService] = create_openai_service()
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Effectue la deuxième relecture avec focus sur le style et l'empathie
        """
        try:
            logger.info("✨ Début de la deuxième relecture IA (style & empathie)")
            
            # Récupération des données
            draft_data = await context.shared.get("draft", {})
            draft_v1 = draft_data.get("v1")
            coherence_report = await context.shared.get("coherence_report", {})
            narration = await context.shared.get("narration", {})
            
            if not draft_v1:
                logger.error("Aucun brouillon v1 disponible pour la relecture")
                raise ValueError("Brouillon v1 manquant")
            
            # Initialisation du client OpenAI
            await self._init_openai_client(context)
            
            # Analyse stylistique et émotionnelle
            style_analysis = await self._analyze_style_and_tone(draft_v1, narration, context)
            
            # Amélioration du style et de l'empathie
            improved_content = await self._improve_style_and_empathy(
                draft_v1, style_analysis, coherence_report, context
            )
            
            # Relecture divergente (approche critique)
            divergent_analysis = await self._divergent_review(improved_content, context)
            
            # Application des améliorations divergentes
            final_content = await self._apply_divergent_improvements(
                improved_content, divergent_analysis, context
            )
            
            # Création du draft v2
            draft_v2 = DraftNarratif(
                version="v2",
                contenu=final_content,
                sections=self._extract_sections(final_content),
                references_pieces=draft_v1.get('references_pieces', []),
                references_articles=draft_v1.get('references_articles', []),
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "model_used": (self.openai.config.model_gpt4 if self.openai and not self.openai.simulation_mode else "simulation"),
                    "style_improvements": len(style_analysis.get('improvements', [])),
                    "empathy_score": style_analysis.get('empathy_score', 0),
                    "readability_score": style_analysis.get('readability_score', 0),
                    "divergent_points": len(divergent_analysis.get('critical_points', [])),
                    "agent_version": "1.0",
                    "previous_version": "v1"
                }
            )
            
            # Sauvegarde dans le store
            draft_data["v2"] = draft_v2.dict()
            await context.shared.set("draft", draft_data)
            
            # Rapport de relecture v2
            review_report_v2 = {
                "style_improvements": len(style_analysis.get('improvements', [])),
                "empathy_enhancements": style_analysis.get('empathy_enhancements', []),
                "readability_improvements": style_analysis.get('readability_improvements', []),
                "divergent_insights": divergent_analysis.get('critical_points', []),
                "tone_adjustments": style_analysis.get('tone_adjustments', [])
            }
            
            await context.shared.set("review_report_v2", review_report_v2)
            
            logger.info(f"✅ Deuxième relecture terminée (Score empathie: {style_analysis.get('empathy_score', 0):.1f})")
            
            return {
                "draft_v2": draft_v2.dict(),
                "review_report_v2": review_report_v2,
                "stats": {
                    "style_improvements": len(style_analysis.get('improvements', [])),
                    "empathy_score": style_analysis.get('empathy_score', 0),
                    "readability_score": style_analysis.get('readability_score', 0),
                    "word_count": len(final_content.split())
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans le relecteur IA #2: {e}")
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
    
    async def _analyze_style_and_tone(self, draft_v1: Dict[str, Any], narration: Dict[str, Any],
                                     context: NodeContext) -> Dict[str, Any]:
        """Analyse le style et le ton du brouillon"""
        
        content = draft_v1.get('contenu', '')
        
        # Analyse automatique du style
        style_analysis = {
            "improvements": [],
            "empathy_score": 0,
            "readability_score": 0,
            "tone_adjustments": [],
            "empathy_enhancements": [],
            "readability_improvements": []
        }
        
        # 1. Analyse de l'empathie
        empathy_analysis = self._analyze_empathy(content, narration)
        style_analysis.update(empathy_analysis)
        
        # 2. Analyse de la lisibilité
        readability_analysis = self._analyze_readability(content)
        style_analysis.update(readability_analysis)
        
        # 3. Analyse du ton juridique
        tone_analysis = self._analyze_legal_tone(content)
        style_analysis.update(tone_analysis)
        
        # 4. Analyse IA avancée
        if self.openai and not self.openai.simulation_mode:
            ai_style_analysis = await self._ai_style_analysis(content, narration)
            style_analysis.update(ai_style_analysis)
        else:
            mock_analysis = self._mock_style_analysis(content)
            style_analysis.update(mock_analysis)
        
        return style_analysis
    
    def _analyze_empathy(self, content: str, narration: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le niveau d'empathie du texte"""
        
        empathy_indicators = [
            "situation difficile", "comprendre", "respectueusement",
            "sollicite", "bienveillance", "considération",
            "famille", "enfants", "santé", "intégration"
        ]
        
        empathy_score = 0
        empathy_enhancements = []
        
        content_lower = content.lower()
        
        # Comptage des indicateurs d'empathie
        for indicator in empathy_indicators:
            if indicator in content_lower:
                empathy_score += 10
        
        # Analyse des émotions dans la narration originale
        segments = narration.get('segments', [])
        emotional_context = []
        
        for segment in segments:
            emotion = segment.get('emotion', {})
            if emotion.get('emotion') in ['detresse', 'peur', 'tristesse']:
                emotional_context.append(emotion.get('emotion'))
        
        # Recommandations d'empathie
        if empathy_score < 30:
            empathy_enhancements.append("Ajouter plus d'éléments empathiques")
            
        if emotional_context and "famille" not in content_lower:
            empathy_enhancements.append("Mentionner l'impact familial si pertinent")
            
        if "respectueusement" not in content_lower:
            empathy_enhancements.append("Utiliser des formules de politesse plus empathiques")
        
        return {
            "empathy_score": min(100, empathy_score),
            "empathy_enhancements": empathy_enhancements,
            "emotional_context": emotional_context
        }
    
    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyse la lisibilité du texte"""
        
        readability_score = 70  # Score de base
        readability_improvements = []
        
        sentences = content.split('.')
        words = content.split()
        
        # Analyse de la longueur des phrases
        long_sentences = [s for s in sentences if len(s.split()) > 25]
        if len(long_sentences) > len(sentences) * 0.3:
            readability_score -= 15
            readability_improvements.append("Raccourcir les phrases trop longues")
        
        # Analyse de la complexité lexicale
        complex_words = [
            "nonobstant", "néanmoins", "subséquemment", "concomitamment",
            "subséquent", "afférent", "subrogation"
        ]
        
        complex_count = sum(1 for word in complex_words if word in content.lower())
        if complex_count > 5:
            readability_score -= 10
            readability_improvements.append("Simplifier le vocabulaire juridique")
        
        # Analyse de la structure
        if "I." not in content or "II." not in content:
            readability_score -= 10
            readability_improvements.append("Améliorer la structuration avec des sections claires")
        
        # Analyse des transitions
        transition_words = ["par ailleurs", "en outre", "de plus", "cependant", "néanmoins"]
        transition_count = sum(1 for word in transition_words if word in content.lower())
        
        if transition_count < 3:
            readability_score -= 5
            readability_improvements.append("Ajouter plus de mots de transition")
        
        return {
            "readability_score": max(0, readability_score),
            "readability_improvements": readability_improvements,
            "average_sentence_length": len(words) / max(len(sentences), 1),
            "complex_words_count": complex_count
        }
    
    def _analyze_legal_tone(self, content: str) -> Dict[str, Any]:
        """Analyse le ton juridique approprié"""
        
        tone_adjustments = []
        
        # Vérification du registre de langue
        informal_expressions = [
            "je pense que", "il me semble", "peut-être", "j'espère",
            "ça", "super", "génial", "cool"
        ]
        
        for expr in informal_expressions:
            if expr in content.lower():
                tone_adjustments.append(f"Remplacer '{expr}' par une formulation plus formelle")
        
        # Vérification des formules juridiques appropriées
        required_formulas = [
            "j'ai l'honneur", "sollicite respectueusement", "vous prie d'agréer"
        ]
        
        missing_formulas = []
        for formula in required_formulas:
            if formula not in content.lower():
                missing_formulas.append(formula)
        
        if missing_formulas:
            tone_adjustments.append("Ajouter les formules de politesse juridiques manquantes")
        
        # Vérification de l'assertivité
        weak_expressions = ["je crois", "il semblerait", "probablement"]
        for expr in weak_expressions:
            if expr in content.lower():
                tone_adjustments.append(f"Renforcer l'assertivité en remplaçant '{expr}'")
        
        return {
            "tone_adjustments": tone_adjustments,
            "formality_level": "appropriate" if not tone_adjustments else "needs_improvement"
        }
    
    async def _ai_style_analysis(self, content: str, narration: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse stylistique avancée avec IA"""
        
        try:
            # Extraction du contexte émotionnel
            emotional_context = self._extract_emotional_context(narration)
            
            system_prompt = """Tu es un expert en rédaction juridique empathique. Analyse ce brouillon de recours et suggère des améliorations de style, d'empathie et de ton.

Focus sur :
1. L'empathie et l'humanisation du récit
2. La clarté et la lisibilité
3. L'équilibre entre fermeté juridique et respect
4. Les transitions et la fluidité

Réponds en JSON avec : improvements, empathy_suggestions, readability_fixes, tone_refinements"""
            
            user_prompt = f"""Contexte émotionnel original : {emotional_context}

Brouillon à analyser :
{content}

Analyse et suggère des améliorations stylistiques."""
            
            resp = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1500
            )
            
            import json
            try:
                ai_analysis = json.loads(resp.content)
                return ai_analysis
            except json.JSONDecodeError:
                return self._mock_style_analysis(content)
                
        except Exception as e:
            logger.error(f"Erreur analyse stylistique IA: {e}")
            return self._mock_style_analysis(content)
    
    def _mock_style_analysis(self, content: str) -> Dict[str, Any]:
        """Analyse stylistique mock"""
        return {
            "improvements": [
                {
                    "type": "empathy",
                    "suggestion": "Ajouter une phrase sur l'impact familial",
                    "priority": "high"
                },
                {
                    "type": "readability",
                    "suggestion": "Diviser le paragraphe 3 en deux parties",
                    "priority": "medium"
                }
            ],
            "empathy_suggestions": [
                "Mentionner l'attachement à la France",
                "Évoquer les liens familiaux et sociaux"
            ],
            "readability_fixes": [
                "Simplifier la phrase sur l'article L.511-4",
                "Ajouter des connecteurs logiques"
            ],
            "tone_refinements": [
                "Renforcer la formule de politesse finale",
                "Équilibrer fermeté et respect"
            ]
        }
    
    async def _improve_style_and_empathy(self, draft_v1: Dict[str, Any], 
                                        style_analysis: Dict[str, Any],
                                        coherence_report: Dict[str, Any],
                                        context: NodeContext) -> str:
        """Améliore le style et l'empathie du brouillon"""
        
        content = draft_v1.get('contenu', '')
        
        if not (self.openai and not self.openai.simulation_mode):
            return self._apply_basic_style_improvements(content, style_analysis)
        
        try:
            # Récupération des recommandations
            improvements = style_analysis.get('improvements', [])
            empathy_suggestions = style_analysis.get('empathy_suggestions', [])
            coherence_recommendations = coherence_report.get('recommendations', [])
            
            improvement_prompt = f"""Améliore ce brouillon de recours en appliquant ces recommandations :

AMÉLIORATIONS STYLISTIQUES :
{chr(10).join([f"- {imp.get('suggestion', '')}" for imp in improvements[:5]])}

SUGGESTIONS D'EMPATHIE :
{chr(10).join([f"- {sugg}" for sugg in empathy_suggestions[:3]])}

RECOMMANDATIONS DE COHÉRENCE :
{chr(10).join([f"- {rec}" for rec in coherence_recommendations[:3]])}

BROUILLON À AMÉLIORER :
{content}

Retourne uniquement le texte amélioré, en conservant la structure et les références."""
            
            resp = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": "Tu es un rédacteur juridique expert en empathie et style. Améliore le texte selon les recommandations."},
                    {"role": "user", "content": improvement_prompt}
                ],
                model="gpt-4o",
                temperature=0.3,
                max_tokens=4000
            )
            
            return resp.content
            
        except Exception as e:
            logger.error(f"Erreur amélioration style IA: {e}")
            return self._apply_basic_style_improvements(content, style_analysis)
    
    def _apply_basic_style_improvements(self, content: str, style_analysis: Dict[str, Any]) -> str:
        """Applique des améliorations stylistiques basiques"""
        
        improved_content = content
        
        # Améliorations automatiques simples
        replacements = {
            "je demande": "je sollicite respectueusement",
            "je pense": "j'estime",
            "il faut": "il convient de",
            "c'est pourquoi": "par conséquent",
            "en plus": "en outre"
        }
        
        for original, replacement in replacements.items():
            improved_content = improved_content.replace(original, replacement)
        
        return improved_content
    
    async def _divergent_review(self, content: str, context: NodeContext) -> Dict[str, Any]:
        """Effectue une relecture divergente (approche critique)"""
        
        if not (self.openai and not self.openai.simulation_mode):
            return self._mock_divergent_analysis(content)
        
        try:
            divergent_prompt = f"""Effectue une relecture CRITIQUE et DIVERGENTE de ce recours administratif.

Adopte le point de vue d'un avocat adverse ou d'un agent administratif sceptique.

Identifie :
1. Les faiblesses argumentaires
2. Les points vulnérables
3. Les contre-arguments possibles
4. Les éléments manquants qui pourraient être exploités
5. Les améliorations défensives nécessaires

RECOURS À ANALYSER :
{content}

Réponds en JSON avec : critical_points, vulnerabilities, counter_arguments, defensive_improvements"""
            
            resp = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": "Tu es un avocat expérimenté effectuant une analyse critique divergente. Sois constructif mais rigoureux."},
                    {"role": "user", "content": divergent_prompt}
                ],
                model="gpt-4o",
                temperature=0.5,
                max_tokens=1500
            )
            
            import json
            try:
                divergent_analysis = json.loads(resp.content)
                return divergent_analysis
            except json.JSONDecodeError:
                return self._mock_divergent_analysis(content)
                
        except Exception as e:
            logger.error(f"Erreur analyse divergente: {e}")
            return self._mock_divergent_analysis(content)
    
    def _mock_divergent_analysis(self, content: str) -> Dict[str, Any]:
        """Analyse divergente mock"""
        return {
            "critical_points": [
                "Manque de précision sur les dates de résidence",
                "Arguments sur l'intégration peu développés",
                "Références juridiques insuffisamment expliquées"
            ],
            "vulnerabilities": [
                "Chronologie floue qui pourrait être contestée",
                "Absence de témoignages tiers"
            ],
            "counter_arguments": [
                "L'administration pourrait contester la régularité du séjour",
                "Les preuves d'intégration pourraient être jugées insuffisantes"
            ],
            "defensive_improvements": [
                "Renforcer la chronologie avec des dates précises",
                "Ajouter des éléments sur l'intégration sociale",
                "Anticiper les objections administratives"
            ]
        }
    
    async def _apply_divergent_improvements(self, content: str, divergent_analysis: Dict[str, Any],
                                          context: NodeContext) -> str:
        """Applique les améliorations issues de l'analyse divergente"""
        
        if not (self.openai and not self.openai.simulation_mode):
            return content  # Pas d'amélioration sans IA
        
        try:
            defensive_improvements = divergent_analysis.get('defensive_improvements', [])
            vulnerabilities = divergent_analysis.get('vulnerabilities', [])
            
            if not defensive_improvements:
                return content
            
            defensive_prompt = f"""Renforce ce recours en appliquant ces améliorations défensives :

AMÉLIORATIONS À APPLIQUER :
{chr(10).join([f"- {imp}" for imp in defensive_improvements[:4]])}

VULNÉRABILITÉS À CORRIGER :
{chr(10).join([f"- {vuln}" for vuln in vulnerabilities[:3]])}

RECOURS À RENFORCER :
{content}

Retourne le texte renforcé, en conservant la structure originale."""
            
            resp = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": "Tu es un avocat expert en défense. Renforce le texte contre les objections potentielles."},
                    {"role": "user", "content": defensive_prompt}
                ],
                model="gpt-4o",
                temperature=0.2,
                max_tokens=4000
            )
            
            return resp.content
            
        except Exception as e:
            logger.error(f"Erreur application améliorations divergentes: {e}")
            return content
    
    def _extract_emotional_context(self, narration: Dict[str, Any]) -> str:
        """Extrait le contexte émotionnel de la narration"""
        segments = narration.get('segments', [])
        emotions = []
        
        for segment in segments:
            emotion = segment.get('emotion', {})
            if emotion.get('emotion'):
                emotions.append(emotion.get('emotion'))
        
        return f"Émotions dominantes: {', '.join(set(emotions))}" if emotions else "Contexte émotionnel neutre"
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extrait les sections du contenu"""
        sections = []
        
        import re
        section_pattern = r'^(I{1,3}V?|IV|V|VI{1,3})\.\s*(.+)$'
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            match = re.match(section_pattern, line.strip())
            if match:
                if current_section:
                    sections.append({
                        "titre": current_section,
                        "contenu": '\n'.join(current_content).strip()
                    })
                
                current_section = match.group(2)
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections.append({
                "titre": current_section,
                "contenu": '\n'.join(current_content).strip()
            })
        
        return sections
