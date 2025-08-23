"""
AGENT 7 - Relecteur IA #1
Premier niveau de relecture : correction cohérence, vérifications techniques
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.base import BaseNode, NodeContext
from ..models import DraftNarratif
from ..services.official_legifrance_service import OfficialLegifranceService
from ..services.openai_service import OpenAIService, create_openai_service

logger = logging.getLogger(__name__)

class RelecteurIA1Node(BaseNode):
    """
    Agent responsable de la première relecture technique
    
    Inputs: draft.v0
    Output: draft.v1 (version corrigée)
    """
    
    def __init__(self):
        super().__init__("relecteur_ia_1", "Relecteur IA #1")
        self.openai: Optional[OpenAIService] = create_openai_service()
        self.official_legal_service = None
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Effectue la première relecture technique du brouillon
        """
        try:
            logger.info("🔍 Début de la première relecture IA")
            
            # Récupération du brouillon v0
            draft_data = await context.shared.get("draft", {})
            draft_v0 = draft_data.get("v0")
            
            if not draft_v0:
                logger.error("Aucun brouillon v0 disponible pour la relecture")
                raise ValueError("Brouillon v0 manquant")
            
            # Initialisation du client OpenAI
            await self._init_openai_client(context)
            
            # Analyse du brouillon
            analysis = await self._analyze_draft(draft_v0, context)
            
            # Corrections automatiques
            corrected_content = await self._apply_corrections(draft_v0, analysis, context)
            
            # Création du draft v1
            draft_v1 = DraftNarratif(
                version="v1",
                contenu=corrected_content,
                sections=self._extract_sections(corrected_content),
                references_pieces=draft_v0.get('references_pieces', []),
                references_articles=draft_v0.get('references_articles', []),
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "model_used": (self.openai.config.model_gpt4 if self.openai and not self.openai.simulation_mode else "simulation"),
                    "corrections_applied": len(analysis.get('corrections', [])),
                    "quality_score": analysis.get('quality_score', 0),
                    "agent_version": "1.0",
                    "previous_version": "v0"
                }
            )
            
            # Sauvegarde dans le store
            draft_data["v1"] = draft_v1.dict()
            await context.shared.set("draft", draft_data)
            
            # Rapport de relecture
            review_report = {
                "corrections_count": len(analysis.get('corrections', [])),
                "quality_improvement": analysis.get('quality_improvement', 0),
                "issues_found": analysis.get('issues', []),
                "recommendations": analysis.get('recommendations', [])
            }
            
            await context.shared.set("review_report_v1", review_report)
            
            logger.info(f"✅ Première relecture terminée ({len(analysis.get('corrections', []))} corrections)")
            
            return {
                "draft_v1": draft_v1.dict(),
                "review_report": review_report,
                "stats": {
                    "corrections_applied": len(analysis.get('corrections', [])),
                    "quality_score": analysis.get('quality_score', 0),
                    "word_count": len(corrected_content.split())
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans le relecteur IA #1: {e}")
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
    
    async def _analyze_draft(self, draft_v0: Dict[str, Any], context: NodeContext) -> Dict[str, Any]:
        """Analyse le brouillon pour identifier les problèmes"""
        
        content = draft_v0.get('contenu', '')
        
        # Analyses automatiques
        analysis = {
            "corrections": [],
            "issues": [],
            "recommendations": [],
            "quality_score": 0,
            "quality_improvement": 0
        }
        
        # 1. Vérifications structurelles
        structural_issues = self._check_structure(content)
        analysis["issues"].extend(structural_issues)
        
        # 2. Vérifications linguistiques
        linguistic_issues = self._check_language(content)
        analysis["issues"].extend(linguistic_issues)
        
        # 3. Vérifications juridiques
        legal_issues = await self._check_legal_consistency(content, context)
        analysis["issues"].extend(legal_issues)
        
        # 4. Vérifications des références
        reference_issues = self._check_references(draft_v0, context)
        analysis["issues"].extend(reference_issues)
        
        # 5. Analyse IA avec GPT-4o
        if self.openai and not self.openai.simulation_mode:
            ai_analysis = await self._ai_analysis(content)
            analysis.update(ai_analysis)
        else:
            analysis.update(self._mock_ai_analysis(content))
        
        # Calcul du score de qualité
        analysis["quality_score"] = self._calculate_quality_score(analysis)
        
        return analysis
    
    def _check_structure(self, content: str) -> List[Dict[str, str]]:
        """Vérifie la structure du document"""
        issues = []
        
        # Vérification des sections obligatoires
        required_sections = [
            "présentation",
            "chronologie", 
            "moyens de droit",
            "pièces justificatives",
            "conclusion"
        ]
        
        content_lower = content.lower()
        
        for section in required_sections:
            if section not in content_lower:
                issues.append({
                    "type": "structure",
                    "severity": "medium",
                    "message": f"Section manquante : {section}",
                    "suggestion": f"Ajouter une section '{section}'"
                })
        
        # Vérification de la longueur
        word_count = len(content.split())
        if word_count < 800:
            issues.append({
                "type": "structure",
                "severity": "high",
                "message": f"Document trop court ({word_count} mots)",
                "suggestion": "Développer davantage les arguments"
            })
        elif word_count > 3000:
            issues.append({
                "type": "structure",
                "severity": "medium",
                "message": f"Document très long ({word_count} mots)",
                "suggestion": "Considérer une synthèse plus concise"
            })
        
        return issues
    
    def _check_references(self, draft_v0: Dict[str, Any], context: NodeContext) -> List[Dict[str, Any]]:
        """Vérifie la cohérence basique des références (pièces, articles)."""
        issues: List[Dict[str, Any]] = []
        content = draft_v0.get("contenu", "")
        
        # Vérification des références de pièces
        refs_pieces = draft_v0.get("references_pieces", []) or []
        seen_pieces = set()
        for ref in refs_pieces:
            ref_id = None
            if isinstance(ref, dict):
                ref_id = ref.get("id") or ref.get("numero") or ref.get("label")
            elif isinstance(ref, (str, int)):
                ref_id = str(ref)
            if not ref_id:
                issues.append({
                    "type": "reference_piece",
                    "severity": "low",
                    "message": "Référence de pièce invalide (format inconnu)",
                    "suggestion": "Utiliser un objet avec une clé 'id' ou un identifiant de pièce clair"
                })
                continue
            if ref_id in seen_pieces:
                issues.append({
                    "type": "reference_piece",
                    "severity": "low",
                    "message": f"Doublon de référence de pièce: {ref_id}",
                    "suggestion": "Supprimer les références dupliquées"
                })
            seen_pieces.add(ref_id)
            # Vérifie que la référence est citée dans le texte
            if str(ref_id).lower() not in content.lower():
                issues.append({
                    "type": "reference_piece",
                    "severity": "low",
                    "message": f"La pièce '{ref_id}' n'est pas citée dans le contenu",
                    "suggestion": "Citer explicitement la pièce dans le brouillon ou retirer la référence"
                })
        
        # Vérification des références d'articles
        refs_articles = draft_v0.get("references_articles", []) or []
        seen_articles = set()
        for ref in refs_articles:
            ref_text = None
            if isinstance(ref, dict):
                ref_text = ref.get("reference") or ref.get("article") or ref.get("label")
            elif isinstance(ref, str):
                ref_text = ref
            if not ref_text:
                issues.append({
                    "type": "reference_article",
                    "severity": "medium",
                    "message": "Référence d'article invalide (format inconnu)",
                    "suggestion": "Utiliser une chaîne 'reference' lisible (ex: 'article L.511-4 du CESEDA')"
                })
                continue
            norm = ref_text.strip().lower()
            if norm in seen_articles:
                issues.append({
                    "type": "reference_article",
                    "severity": "low",
                    "message": f"Doublon de référence d'article: {ref_text}",
                    "suggestion": "Supprimer les références dupliquées"
                })
            seen_articles.add(norm)
            if norm not in content.lower():
                issues.append({
                    "type": "reference_article",
                    "severity": "low",
                    "message": f"La référence '{ref_text}' n'est pas citée dans le contenu",
                    "suggestion": "Citer explicitement l'article ou retirer la référence"
                })
        
        return issues
    
    def _check_language(self, content: str) -> List[Dict[str, str]]:
        """Vérifie la qualité linguistique"""
        issues = []
        
        # Vérifications basiques
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Lignes trop longues
            if len(line) > 200:
                issues.append({
                    "type": "language",
                    "severity": "low",
                    "message": f"Ligne {i+1} très longue",
                    "suggestion": "Diviser en phrases plus courtes"
                })
            
            # Répétitions
            words = line.lower().split()
            if len(words) != len(set(words)) and len(words) > 5:
                issues.append({
                    "type": "language",
                    "severity": "low",
                    "message": f"Répétitions possibles ligne {i+1}",
                    "suggestion": "Vérifier les répétitions de mots"
                })
        
        # Vérification du ton juridique
        if "je pense" in content.lower() or "il me semble" in content.lower():
            issues.append({
                "type": "language",
                "severity": "medium",
                "message": "Formulations trop subjectives",
                "suggestion": "Utiliser un langage plus affirmatif et factuel"
            })
        
        return issues
    
    async def _check_legal_consistency(self, content: str, context: NodeContext) -> List[Dict[str, Any]]:
        """Vérifications de cohérence juridique avec l'API officielle"""
        issues = []
        
        try:
            # Initialisation du service officiel si nécessaire
            if self.official_legal_service is None:
                self.official_legal_service = OfficialLegifranceService()
                await self.official_legal_service.initialize()
            
            # Extraction des références juridiques du contenu
            legal_refs = self._extract_legal_references(content)
            
            # Vérification de chaque référence via l'API officielle
            for ref in legal_refs:
                try:
                    # Recherche de l'article via l'API officielle
                    results = await self.official_legal_service.search_legal_texts(
                        query=ref["reference"],
                        nature=ref.get("nature"),
                        champ="ALL",
                        page_size=1
                    )
                    
                    if not results:
                        issues.append({
                            "type": "legal_reference",
                            "severity": "high",
                            "message": f"Référence juridique non trouvée: {ref['reference']}",
                            "suggestion": "Vérifier la référence ou utiliser une source alternative",
                            "location": ref["position"]
                        })
                    else:
                        # Vérification de la cohérence du contenu
                        article_content = results[0].content
                        if not self._check_content_consistency(ref["context"], article_content):
                            issues.append({
                                "type": "legal_consistency",
                                "severity": "medium",
                                "message": f"Incohérence détectée avec {ref['reference']}",
                                "suggestion": "Réviser l'interprétation de l'article",
                                "location": ref["position"]
                            })
                        
                except Exception as e:
                    logger.warning(f"Erreur vérification référence {ref['reference']}: {e}")
                    
        except Exception as e:
            logger.error(f"Erreur vérification juridique: {e}")
            issues.append({
                "type": "system_error",
                "severity": "low",
                "message": "Impossible de vérifier les références juridiques",
                "suggestion": "Vérification manuelle recommandée"
            })
        
        return issues
    
    def _extract_legal_references(self, content: str) -> List[Dict[str, Any]]:
        """Extrait les références juridiques du contenu"""
        import re
        
        references = []
        
        # Patterns pour différents types de références
        patterns = {
            "article": r"(article\s+[A-Z]?\d+(?:-\d+)*(?:\s+du\s+code\s+[^.]+)?)",
            "code": r"(code\s+[^.]+)",
            "loi": r"(loi\s+n°\s*\d{4}-\d+)",
            "decret": r"(décret\s+n°\s*\d{4}-\d+)"
        }
        
        for ref_type, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                references.append({
                    "reference": match.group(1),
                    "type": ref_type,
                    "position": match.start(),
                    "context": content[max(0, match.start()-100):match.end()+100],
                    "nature": self._map_ref_type_to_nature(ref_type)
                })
        
        return references
    
    def _map_ref_type_to_nature(self, ref_type: str) -> str:
        """Mappe le type de référence à la nature API"""
        mapping = {
            "article": "CODE",
            "code": "CODE", 
            "loi": "LODA",
            "decret": "LODA"
        }
        return mapping.get(ref_type, "CODE")
    
    def _check_content_consistency(self, context: str, article_content: str) -> bool:
        """Vérifie la cohérence entre le contexte et le contenu de l'article"""
        # Implémentation simplifiée - en production, utiliser des embeddings
        context_words = set(context.lower().split())
        article_words = set(article_content.lower().split())
        
        # Calcul de similarité basique
        common_words = context_words.intersection(article_words)
        similarity = len(common_words) / max(len(context_words), len(article_words), 1)
        
        return similarity > 0.1  # Seuil minimal de cohérence
    
    async def _ai_analysis(self, content: str) -> Dict[str, Any]:
        """Analyse IA avec GPT-4o"""
        try:
            system_prompt = """Tu es un relecteur juridique expert. Analyse ce brouillon de recours administratif et identifie :

1. Les problèmes de cohérence
2. Les améliorations stylistiques nécessaires
3. Les faiblesses argumentaires
4. Les suggestions d'amélioration

Réponds en JSON avec les clés : corrections, recommendations, quality_improvement"""
            
            resp = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyse ce brouillon :\n\n{content}"}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse de la réponse JSON
            import json
            try:
                ai_result = json.loads(resp.content)
                return ai_result
            except json.JSONDecodeError:
                return self._mock_ai_analysis(content)
                
        except Exception as e:
            logger.error(f"Erreur analyse IA: {e}")
            return self._mock_ai_analysis(content)
    
    def _mock_ai_analysis(self, content: str) -> Dict[str, Any]:
        """Analyse mock pour les tests"""
        return {
            "corrections": [
                {
                    "type": "style",
                    "original": "je demande",
                    "corrected": "je sollicite respectueusement",
                    "reason": "Formulation plus juridique"
                }
            ],
            "recommendations": [
                "Renforcer l'argumentation sur l'article L.511-4",
                "Améliorer la transition entre les sections",
                "Préciser les dates mentionnées"
            ],
            "quality_improvement": 15
        }
    
    async def _apply_corrections(self, draft_v0: Dict[str, Any], analysis: Dict[str, Any], context: NodeContext) -> str:
        """Applique les corrections identifiées"""
        
        content = draft_v0.get('contenu', '')
        corrections = analysis.get('corrections', [])
        
        # Application des corrections automatiques
        corrected_content = content
        
        for correction in corrections:
            if correction.get('type') == 'style':
                original = correction.get('original', '')
                corrected = correction.get('corrected', '')
                if original and corrected:
                    corrected_content = corrected_content.replace(original, corrected)
        
        # Corrections IA avancées si disponible
        if self.openai and not self.openai.simulation_mode:
            corrected_content = await self._ai_corrections(corrected_content, analysis)
        
        return corrected_content
    
    async def _ai_corrections(self, content: str, analysis: Dict[str, Any]) -> str:
        """Corrections IA avec GPT-4o"""
        try:
            issues = analysis.get('issues', [])
            recommendations = analysis.get('recommendations', [])
            
            correction_prompt = f"""Corrige ce brouillon en tenant compte de ces problèmes identifiés :

PROBLÈMES :
{chr(10).join([f"- {issue.get('message', '')}" for issue in issues[:5]])}

RECOMMANDATIONS :
{chr(10).join([f"- {rec}" for rec in recommendations[:5]])}

BROUILLON À CORRIGER :
{content}

Retourne uniquement le texte corrigé, sans commentaires."""
            
            resp = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": "Tu es un relecteur juridique expert. Corrige le texte selon les indications."},
                    {"role": "user", "content": correction_prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            return resp.content
            
        except Exception as e:
            logger.error(f"Erreur corrections IA: {e}")
            return content
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calcule un score de qualité du document"""
        base_score = 70.0
        
        issues = analysis.get('issues', [])
        
        # Pénalités par type d'issue
        penalties = {
            'high': -10,
            'medium': -5,
            'low': -2
        }
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            base_score += penalties.get(severity, -2)
        
        # Bonus pour les améliorations IA
        ai_improvement = analysis.get('quality_improvement', 0)
        base_score += ai_improvement
        
        return max(0, min(100, base_score))
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extrait les sections du contenu corrigé"""
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
