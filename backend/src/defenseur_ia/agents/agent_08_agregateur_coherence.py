"""
AGENT 8 - Agrégateur de Cohérence
Synthèse des axes juridiques et vérification de la couverture globale du dossier
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.base import BaseNode, NodeContext

logger = logging.getLogger(__name__)

class AgregateurCoherenceNode(BaseNode):
    """
    Agent responsable de l'agrégation et de la vérification de cohérence
    
    Inputs: draft.v1, axes_juridiques, matches, pieces_parsed
    Output: coherence_report, coverage_analysis
    """
    
    def __init__(self):
        super().__init__("agregateur_coherence", "Agrégateur de Cohérence")
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Effectue l'analyse de cohérence et de couverture du dossier
        """
        try:
            logger.info("📊 Début de l'analyse de cohérence globale")
            
            # Récupération des données
            draft_data = await context.shared.get("draft", {})
            draft_v1 = draft_data.get("v1")
            axes_juridiques = await context.shared.get("axes_juridiques", [])
            matches = await context.shared.get("matches", [])
            pieces_parsed = await context.shared.get("pieces_parsed", [])
            web_corpus = await context.shared.get("web_corpus", [])
            
            if not draft_v1:
                logger.error("Aucun brouillon v1 disponible pour l'analyse")
                raise ValueError("Brouillon v1 manquant")
            
            # Analyse de cohérence
            coherence_analysis = self._analyze_coherence(draft_v1, axes_juridiques, matches)
            
            # Analyse de couverture
            coverage_analysis = self._analyze_coverage(
                draft_v1, axes_juridiques, pieces_parsed, matches, web_corpus
            )
            
            # Analyse des lacunes
            gap_analysis = self._identify_gaps(
                axes_juridiques, matches, pieces_parsed, draft_v1
            )
            
            # Score global de qualité
            global_quality_score = self._calculate_global_quality(
                coherence_analysis, coverage_analysis, gap_analysis
            )
            
            # Recommandations d'amélioration
            recommendations = self._generate_recommendations(
                coherence_analysis, coverage_analysis, gap_analysis
            )
            
            # Rapport final
            coherence_report = {
                "coherence_score": coherence_analysis.get("score", 0),
                "coverage_score": coverage_analysis.get("score", 0),
                "global_quality_score": global_quality_score,
                "gaps_identified": len(gap_analysis.get("gaps", [])),
                "recommendations": recommendations,
                "analysis_details": {
                    "coherence": coherence_analysis,
                    "coverage": coverage_analysis,
                    "gaps": gap_analysis
                },
                "generated_at": datetime.now().isoformat(),
                "agent_version": "1.0"
            }
            
            # Sauvegarde dans le store
            await context.shared.set("coherence_report", coherence_report)
            
            logger.info(f"✅ Analyse de cohérence terminée (Score global: {global_quality_score:.1f}/100)")
            
            return {
                "coherence_report": coherence_report,
                "stats": {
                    "coherence_score": coherence_analysis.get("score", 0),
                    "coverage_score": coverage_analysis.get("score", 0),
                    "global_quality_score": global_quality_score,
                    "recommendations_count": len(recommendations)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans l'agrégateur de cohérence: {e}")
            raise
    
    def _analyze_coherence(self, draft_v1: Dict[str, Any], axes_juridiques: List[Dict], 
                          matches: List[Dict]) -> Dict[str, Any]:
        """Analyse la cohérence interne du dossier"""
        
        content = draft_v1.get('contenu', '')
        sections = draft_v1.get('sections', [])
        
        coherence_issues = []
        coherence_score = 100.0
        
        # 1. Cohérence entre axes juridiques et contenu
        for axe in axes_juridiques:
            theme = axe.get('theme', '')
            if theme and theme.lower() not in content.lower():
                coherence_issues.append({
                    "type": "missing_axis",
                    "severity": "high",
                    "message": f"Axe juridique '{theme}' non traité dans le récit",
                    "impact": -15
                })
                coherence_score -= 15
        
        # 2. Cohérence des références juridiques
        import re
        article_refs = re.findall(r'article\s+L\.\s*\d+-\d+', content, re.IGNORECASE)
        
        for article_ref in article_refs:
            # Vérifier si l'article est supporté par les matches
            found_match = False
            for match in matches:
                if article_ref.lower() in match.get('article_titre', '').lower():
                    found_match = True
                    break
            
            if not found_match:
                coherence_issues.append({
                    "type": "unsupported_reference",
                    "severity": "medium",
                    "message": f"Référence '{article_ref}' sans support dans les matches",
                    "impact": -8
                })
                coherence_score -= 8
        
        # 3. Cohérence structurelle
        required_flow = ["présentation", "faits", "droit", "conclusion"]
        content_lower = content.lower()
        
        for i, element in enumerate(required_flow):
            if element not in content_lower:
                coherence_issues.append({
                    "type": "structural_gap",
                    "severity": "medium",
                    "message": f"Élément structurel manquant: {element}",
                    "impact": -10
                })
                coherence_score -= 10
        
        # 4. Cohérence temporelle
        dates_mentioned = re.findall(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}', content)
        if len(dates_mentioned) < 2:
            coherence_issues.append({
                "type": "temporal_vagueness",
                "severity": "low",
                "message": "Chronologie peu précise (peu de dates mentionnées)",
                "impact": -5
            })
            coherence_score -= 5
        
        return {
            "score": max(0, coherence_score),
            "issues": coherence_issues,
            "article_references_count": len(article_refs),
            "supported_references": len(article_refs) - len([i for i in coherence_issues if i["type"] == "unsupported_reference"]),
            "structural_completeness": (len(required_flow) - len([i for i in coherence_issues if i["type"] == "structural_gap"])) / len(required_flow) * 100
        }
    
    def _analyze_coverage(self, draft_v1: Dict[str, Any], axes_juridiques: List[Dict],
                         pieces_parsed: List[Dict], matches: List[Dict], 
                         web_corpus: List[Dict]) -> Dict[str, Any]:
        """Analyse la couverture du dossier"""
        
        content = draft_v1.get('contenu', '')
        coverage_score = 0.0
        coverage_details = {}
        
        # 1. Couverture des axes juridiques (40% du score)
        axes_coverage = 0
        if axes_juridiques:
            covered_axes = 0
            for axe in axes_juridiques:
                theme = axe.get('theme', '')
                mots_cles = axe.get('mots_cles', [])
                
                # Vérifier si l'axe est traité
                theme_covered = theme.lower() in content.lower() if theme else False
                keywords_covered = any(kw.lower() in content.lower() for kw in mots_cles)
                
                if theme_covered or keywords_covered:
                    covered_axes += 1
            
            axes_coverage = (covered_axes / len(axes_juridiques)) * 40
        
        coverage_details["axes_coverage"] = axes_coverage
        
        # 2. Couverture des pièces justificatives (30% du score)
        pieces_coverage = 0
        if pieces_parsed:
            referenced_pieces = 0
            important_pieces = [p for p in pieces_parsed if p.get('type_piece') in [
                'decision_administrative', 'piece_identite', 'document_travail', 'justificatif_domicile'
            ]]
            
            import re
            annexe_refs = re.findall(r'annexe\s+\d+', content, re.IGNORECASE)
            
            # Estimation du nombre de pièces référencées
            referenced_pieces = min(len(annexe_refs), len(important_pieces))
            
            if important_pieces:
                pieces_coverage = (referenced_pieces / len(important_pieces)) * 30
        
        coverage_details["pieces_coverage"] = pieces_coverage
        
        # 3. Couverture des références juridiques (20% du score)
        legal_coverage = 0
        if matches:
            high_quality_matches = [m for m in matches if m.get('score_matching', 0) > 0.7]
            article_refs = re.findall(r'article\s+L\.\s*\d+-\d+', content, re.IGNORECASE)
            
            if high_quality_matches:
                referenced_ratio = min(len(article_refs) / len(high_quality_matches), 1.0)
                legal_coverage = referenced_ratio * 20
        
        coverage_details["legal_coverage"] = legal_coverage
        
        # 4. Utilisation des ressources web (10% du score)
        web_coverage = 0
        if web_corpus:
            # Vérifier si des éléments du corpus web sont mentionnés
            web_elements_used = 0
            for resource in web_corpus[:5]:  # Top 5 ressources
                titre = resource.get('titre', '')
                if any(word in content.lower() for word in titre.lower().split()[:3]):
                    web_elements_used += 1
            
            if web_corpus:
                web_coverage = min(web_elements_used / min(len(web_corpus), 5), 1.0) * 10
        
        coverage_details["web_coverage"] = web_coverage
        
        # Score total de couverture
        total_coverage = axes_coverage + pieces_coverage + legal_coverage + web_coverage
        
        return {
            "score": total_coverage,
            "details": coverage_details,
            "axes_covered": coverage_details.get("axes_coverage", 0) / 40 * 100,
            "pieces_covered": coverage_details.get("pieces_coverage", 0) / 30 * 100,
            "legal_covered": coverage_details.get("legal_coverage", 0) / 20 * 100,
            "web_covered": coverage_details.get("web_coverage", 0) / 10 * 100
        }
    
    def _identify_gaps(self, axes_juridiques: List[Dict], matches: List[Dict],
                      pieces_parsed: List[Dict], draft_v1: Dict[str, Any]) -> Dict[str, Any]:
        """Identifie les lacunes du dossier"""
        
        gaps = []
        content = draft_v1.get('contenu', '')
        
        # 1. Axes juridiques non exploités
        for axe in axes_juridiques:
            theme = axe.get('theme', '')
            if theme and theme.lower() not in content.lower():
                gaps.append({
                    "type": "missing_legal_axis",
                    "severity": "high",
                    "description": f"Axe juridique '{theme}' non développé",
                    "suggestion": f"Développer l'argumentation sur {theme}",
                    "priority": "high"
                })
        
        # 2. Matches de haute qualité non utilisés
        high_quality_matches = [m for m in matches if m.get('score_matching', 0) > 0.8]
        used_articles = re.findall(r'article\s+L\.\s*\d+-\d+', content, re.IGNORECASE)
        
        for match in high_quality_matches:
            article_titre = match.get('article_titre', '')
            if not any(art.lower() in article_titre.lower() for art in used_articles):
                gaps.append({
                    "type": "unused_high_quality_match",
                    "severity": "medium",
                    "description": f"Match de haute qualité non utilisé: {article_titre}",
                    "suggestion": f"Considérer l'inclusion de {article_titre}",
                    "priority": "medium"
                })
        
        # 3. Pièces importantes non référencées
        important_pieces = [p for p in pieces_parsed if p.get('type_piece') in [
            'decision_administrative', 'piece_identite'
        ]]
        
        annexe_refs = re.findall(r'annexe\s+\d+', content, re.IGNORECASE)
        
        if len(important_pieces) > len(annexe_refs):
            gaps.append({
                "type": "missing_piece_references",
                "severity": "medium",
                "description": f"{len(important_pieces) - len(annexe_refs)} pièces importantes non référencées",
                "suggestion": "Ajouter les références aux pièces manquantes",
                "priority": "medium"
            })
        
        # 4. Manque de précision temporelle
        dates_mentioned = re.findall(r'\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}', content)
        if len(dates_mentioned) < 3:
            gaps.append({
                "type": "temporal_imprecision",
                "severity": "low",
                "description": "Chronologie peu détaillée",
                "suggestion": "Ajouter plus de précisions temporelles",
                "priority": "low"
            })
        
        return {
            "gaps": gaps,
            "high_priority_gaps": [g for g in gaps if g.get("priority") == "high"],
            "medium_priority_gaps": [g for g in gaps if g.get("priority") == "medium"],
            "low_priority_gaps": [g for g in gaps if g.get("priority") == "low"]
        }
    
    def _calculate_global_quality(self, coherence_analysis: Dict, coverage_analysis: Dict,
                                 gap_analysis: Dict) -> float:
        """Calcule le score global de qualité"""
        
        # Pondération des scores
        coherence_weight = 0.4
        coverage_weight = 0.4
        gaps_weight = 0.2
        
        coherence_score = coherence_analysis.get("score", 0)
        coverage_score = coverage_analysis.get("score", 0)
        
        # Pénalité pour les lacunes
        gaps = gap_analysis.get("gaps", [])
        gap_penalty = len([g for g in gaps if g.get("priority") == "high"]) * 10
        gap_penalty += len([g for g in gaps if g.get("priority") == "medium"]) * 5
        gap_penalty += len([g for g in gaps if g.get("priority") == "low"]) * 2
        
        gaps_score = max(0, 100 - gap_penalty)
        
        global_score = (
            coherence_score * coherence_weight +
            coverage_score * coverage_weight +
            gaps_score * gaps_weight
        )
        
        return round(global_score, 1)
    
    def _generate_recommendations(self, coherence_analysis: Dict, coverage_analysis: Dict,
                                 gap_analysis: Dict) -> List[str]:
        """Génère des recommandations d'amélioration"""
        
        recommendations = []
        
        # Recommandations basées sur la cohérence
        coherence_score = coherence_analysis.get("score", 0)
        if coherence_score < 70:
            recommendations.append("Améliorer la cohérence interne du récit")
            
        coherence_issues = coherence_analysis.get("issues", [])
        for issue in coherence_issues[:3]:  # Top 3 issues
            if issue.get("severity") in ["high", "medium"]:
                recommendations.append(f"Corriger: {issue.get('message', '')}")
        
        # Recommandations basées sur la couverture
        coverage_details = coverage_analysis.get("details", {})
        
        if coverage_details.get("axes_coverage", 0) < 30:
            recommendations.append("Développer davantage les axes juridiques identifiés")
            
        if coverage_details.get("pieces_coverage", 0) < 20:
            recommendations.append("Améliorer les références aux pièces justificatives")
            
        if coverage_details.get("legal_coverage", 0) < 15:
            recommendations.append("Renforcer les références juridiques")
        
        # Recommandations basées sur les lacunes
        high_priority_gaps = gap_analysis.get("high_priority_gaps", [])
        for gap in high_priority_gaps[:2]:  # Top 2 gaps prioritaires
            recommendations.append(gap.get("suggestion", ""))
        
        # Limitation à 8 recommandations maximum
        return recommendations[:8]
