"""
AGENT 11 - Avocat IA
Rédaction finale de la requête avec style juridique professionnel
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.base import BaseNode, NodeContext
from ..models import RequeteFinale
from ..services.openai_service import OpenAIService, create_openai_service

logger = logging.getLogger(__name__)

class AvocatIANode(BaseNode):
    """
    Agent responsable de la rédaction finale de la requête juridique
    
    Inputs: draft.v2, strategic_synthesis
    Output: requete_finale (document juridique final)
    """
    
    def __init__(self):
        super().__init__("avocat_ia", "Avocat IA")
        self.openai: Optional[OpenAIService] = create_openai_service()
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Rédige la requête finale avec style juridique professionnel
        """
        try:
            logger.info("⚖️ Début de la rédaction finale par l'Avocat IA")
            
            # Récupération des données
            draft_data = await context.shared.get("draft", {})
            draft_v2 = draft_data.get("v2")
            strategic_synthesis = await context.shared.get("strategic_synthesis", {})
            meta_info = await context.shared.get("meta_info", {})
            axes_juridiques = await context.shared.get("axes_juridiques", [])
            pieces_parsed = await context.shared.get("pieces_parsed", [])
            
            if not draft_v2:
                logger.error("Aucun brouillon v2 disponible pour la rédaction finale")
                raise ValueError("Brouillon v2 manquant")
            
            # Initialisation du client OpenAI
            await self._init_openai_client(context)
            
            # Analyse du contexte juridique
            legal_context = self._analyze_legal_context(
                meta_info, axes_juridiques, strategic_synthesis
            )
            
            # Rédaction de la requête finale
            final_content = await self._generate_final_request(
                draft_v2, strategic_synthesis, legal_context, context
            )
            
            # Structuration juridique finale
            structured_request = self._structure_legal_document(
                final_content, pieces_parsed, axes_juridiques
            )
            
            # Validation juridique
            validation_report = self._validate_legal_document(structured_request)
            
            # Création de la requête finale
            requete_finale = RequeteFinale(
                contenu=structured_request,
                type_procedure=meta_info.get('type_procedure', 'Recours gracieux'),
                destinataire=self._determine_recipient(meta_info, legal_context),
                pieces_jointes=self._list_attachments(pieces_parsed),
                references_juridiques=self._extract_legal_references(structured_request),
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "model_used": (self.openai.config.model_gpt4 if self.openai and not self.openai.simulation_mode else "simulation"),
                    "word_count": len(structured_request.split()),
                    "legal_validation_score": validation_report.get('score', 0),
                    "success_probability": strategic_synthesis.get('case_overview', {}).get('success_probability', 0),
                    "agent_version": "1.0",
                    "final_version": True
                }
            )
            
            # Sauvegarde dans le store
            await context.shared.set("requete_finale", requete_finale.dict())
            
            # Rapport final
            final_report = {
                "document_ready": True,
                "validation_score": validation_report.get('score', 0),
                "validation_issues": validation_report.get('issues', []),
                "word_count": len(structured_request.split()),
                "legal_references_count": len(requete_finale.references_juridiques),
                "attachments_count": len(requete_finale.pieces_jointes)
            }
            
            await context.shared.set("final_report", final_report)
            
            logger.info(f"✅ Requête finale générée ({len(structured_request.split())} mots)")
            
            return {
                "requete_finale": requete_finale.dict(),
                "final_report": final_report,
                "stats": {
                    "word_count": len(structured_request.split()),
                    "validation_score": validation_report.get('score', 0),
                    "success_probability": strategic_synthesis.get('case_overview', {}).get('success_probability', 0),
                    "legal_references": len(requete_finale.references_juridiques)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans l'Avocat IA: {e}")
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
    
    def _analyze_legal_context(self, meta_info: Dict[str, Any], axes_juridiques: List[Dict],
                              strategic_synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le contexte juridique pour la rédaction finale"""
        
        context = {
            "procedure_type": meta_info.get('type_procedure', 'Recours gracieux'),
            "jurisdiction": self._determine_jurisdiction(meta_info),
            "urgency_level": strategic_synthesis.get('case_overview', {}).get('urgency_level', 'normale'),
            "complexity": strategic_synthesis.get('case_overview', {}).get('complexity_level', 'moyenne'),
            "primary_legal_axes": [axe.get('theme', '') for axe in axes_juridiques[:3]],
            "success_probability": strategic_synthesis.get('case_overview', {}).get('success_probability', 50),
            "tone_required": self._determine_legal_tone(meta_info, strategic_synthesis)
        }
        
        return context
    
    def _determine_jurisdiction(self, meta_info: Dict[str, Any]) -> str:
        """Détermine la juridiction compétente"""
        procedure = meta_info.get('type_procedure', '').lower()
        
        if 'contentieux' in procedure or 'tribunal' in procedure:
            return "Tribunal administratif"
        elif 'recours' in procedure:
            return "Préfecture"
        else:
            return "Administration compétente"
    
    def _determine_legal_tone(self, meta_info: Dict[str, Any], 
                             strategic_synthesis: Dict[str, Any]) -> str:
        """Détermine le ton juridique approprié"""
        
        urgency = strategic_synthesis.get('case_overview', {}).get('urgency_level', 'normale')
        success_prob = strategic_synthesis.get('case_overview', {}).get('success_probability', 50)
        
        if urgency == 'haute' and success_prob > 70:
            return "ferme_et_confiant"
        elif success_prob > 80:
            return "confiant_respectueux"
        elif success_prob < 40:
            return "humble_mais_determine"
        else:
            return "respectueux_et_factuel"
    
    async def _generate_final_request(self, draft_v2: Dict[str, Any],
                                      strategic_synthesis: Dict[str, Any],
                                      legal_context: Dict[str, Any],
                                      context: NodeContext) -> str:
        """Génère la requête finale avec style juridique professionnel"""
        
        if not self.openai or self.openai.simulation_mode:
            return self._generate_mock_final_request(draft_v2, legal_context)
        
        try:
            # Récupération des éléments stratégiques
            action_plan = strategic_synthesis.get('action_plan', {})
            strengths = strategic_synthesis.get('strengths_weaknesses', {}).get('strengths', [])
            final_recommendations = strategic_synthesis.get('final_recommendations', [])
            
            # Construction du prompt pour l'Avocat IA
            system_prompt = self._build_lawyer_system_prompt(legal_context)
            user_prompt = self._build_lawyer_user_prompt(
                draft_v2, strategic_synthesis, legal_context, action_plan
            )
            
            # Génération via OpenAIService (GPT-4.x) en mode "Avocat expert"
            gpt_response = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Très faible pour cohérence juridique
                max_tokens=4000
            )
            
            return gpt_response.content
            
        except Exception as e:
            logger.error(f"Erreur génération requête finale IA: {e}")
            return self._generate_mock_final_request(draft_v2, legal_context)
    
    def _build_lawyer_system_prompt(self, legal_context: Dict[str, Any]) -> str:
        """Construit le prompt système pour l'Avocat IA"""
        
        tone = legal_context.get('tone_required', 'respectueux_et_factuel')
        procedure = legal_context.get('procedure_type', 'Recours gracieux')
        jurisdiction = legal_context.get('jurisdiction', 'Préfecture')
        
        return f"""Tu es un avocat expert en droit des étrangers avec 20 ans d'expérience. Tu rédiges une {procedure} destinée à {jurisdiction}.

STYLE REQUIS :
- Français juridique impeccable et précis
- Ton {tone.replace('_', ' ')}
- Structure rigoureuse et logique
- Citations juridiques exactes
- Formules de politesse appropriées

STRUCTURE OBLIGATOIRE :
1. En-tête avec destinataire et objet
2. Formule d'appel respectueuse
3. Exposé des faits chronologique
4. Moyens de droit structurés (I., II., III.)
5. Demandes précises et motivées
6. Formule de politesse finale
7. Signature et date

RÈGLES JURIDIQUES :
- Citer les articles de loi avec précision
- Référencer les pièces justificatives (Annexe 1, 2, etc.)
- Utiliser la jurisprudence si pertinente
- Éviter les répétitions
- Être factuel et précis

LONGUEUR : 2000-3000 mots selon la complexité."""
    
    def _build_lawyer_user_prompt(self, draft_v2: Dict[str, Any],
                                 strategic_synthesis: Dict[str, Any],
                                 legal_context: Dict[str, Any],
                                 action_plan: Dict[str, Any]) -> str:
        """Construit le prompt utilisateur pour l'Avocat IA"""
        
        content = draft_v2.get('contenu', '')
        strengths = strategic_synthesis.get('strengths_weaknesses', {}).get('strengths', [])
        strong_arguments = strategic_synthesis.get('argument_scoring', {}).get('strong_arguments', [])
        
        prompt = f"""
CONTEXTE JURIDIQUE :
- Procédure : {legal_context.get('procedure_type', 'Recours gracieux')}
- Destinataire : {legal_context.get('jurisdiction', 'Préfecture')}
- Niveau d'urgence : {legal_context.get('urgency_level', 'normale')}
- Probabilité de succès : {legal_context.get('success_probability', 50):.1f}%

BROUILLON À FINALISER :
{content}

FORCES DU DOSSIER À METTRE EN AVANT :
{chr(10).join([f"- {s.get('description', '')}" for s in strengths[:4]])}

ARGUMENTS JURIDIQUES FORTS :
{chr(10).join([f"- {a.get('theme', '')}: {a.get('score', 0)}/100" for a in strong_arguments[:3]])}

STRATÉGIES DE RENFORCEMENT :
{chr(10).join([f"- {strategy}" for strategy in action_plan.get('reinforcement_strategies', [])[:3]])}

MISSION :
Transforme ce brouillon en une requête juridique finale professionnelle, en appliquant ton expertise d'avocat pour :
1. Perfectionner le style juridique
2. Optimiser l'argumentation
3. Renforcer les points forts identifiés
4. Structurer de manière impeccable
5. Ajouter les formules juridiques appropriées

La requête doit être prête à être envoyée sans modification."""
        
        return prompt
    
    def _generate_mock_final_request(self, draft_v2: Dict[str, Any], 
                                    legal_context: Dict[str, Any]) -> str:
        """Génère une requête finale mock"""
        
        content = draft_v2.get('contenu', '')
        procedure = legal_context.get('procedure_type', 'Recours gracieux')
        jurisdiction = legal_context.get('jurisdiction', 'Préfecture')
        
        return f"""
{jurisdiction}
[Adresse administrative]

Objet : {procedure} contre décision d'obligation de quitter le territoire français

Madame, Monsieur le Préfet,

J'ai l'honneur de solliciter par la présente un recours gracieux contre la décision d'obligation de quitter le territoire français qui m'a été notifiée en date du [DATE], et de vous exposer respectueusement les motifs qui justifient le réexamen de ma situation.

I. EXPOSÉ DES FAITS

{self._extract_facts_section(content)}

II. MOYENS DE DROIT

{self._extract_legal_section(content)}

III. DEMANDES

Pour tous les motifs exposés ci-dessus, j'ai l'honneur de solliciter respectueusement :

- L'annulation de la décision d'obligation de quitter le territoire français en date du [DATE]
- Le réexamen de ma situation au regard des éléments nouveaux portés à votre connaissance
- L'octroi d'un titre de séjour correspondant à ma situation

Je vous prie d'agréer, Madame, Monsieur le Préfet, l'expression de ma haute considération.

Fait à [VILLE], le [DATE]

[Signature]
[NOM ET PRÉNOM]

Pièces jointes : [LISTE DES ANNEXES]
"""
    
    def _structure_legal_document(self, content: str, pieces_parsed: List[Dict],
                                 axes_juridiques: List[Dict]) -> str:
        """Structure le document juridique final"""
        
        # Vérification et amélioration de la structure
        structured_content = content
        
        # Ajout des références aux pièces si manquantes
        if "Pièces jointes" not in content and pieces_parsed:
            annexes_list = []
            for i, piece in enumerate(pieces_parsed[:10], 1):
                filename = piece.get('filename', f'Document {i}')
                piece_type = piece.get('type_piece', 'Document')
                annexes_list.append(f"Annexe {i} : {filename} ({piece_type})")
            
            annexes_section = f"\n\nPièces jointes :\n" + "\n".join(annexes_list)
            structured_content += annexes_section
        
        # Ajout de la date si manquante
        if "Fait à" not in content:
            structured_content += f"\n\nFait à [VILLE], le {datetime.now().strftime('%d %B %Y')}"
        
        return structured_content
    
    def _validate_legal_document(self, content: str) -> Dict[str, Any]:
        """Valide le document juridique final"""
        
        validation_score = 100
        issues = []
        
        # Vérifications obligatoires
        required_elements = [
            ("Objet :", "En-tête avec objet"),
            ("J'ai l'honneur", "Formule d'appel respectueuse"),
            ("I.", "Structure avec sections numérotées"),
            ("Pour tous les motifs", "Section des demandes"),
            ("Je vous prie d'agréer", "Formule de politesse finale"),
            ("Pièces jointes", "Liste des pièces jointes")
        ]
        
        for element, description in required_elements:
            if element not in content:
                validation_score -= 15
                issues.append({
                    "type": "missing_element",
                    "description": f"Élément manquant : {description}",
                    "severity": "high"
                })
        
        # Vérifications de style
        if len(content.split()) < 800:
            validation_score -= 10
            issues.append({
                "type": "length",
                "description": "Document trop court pour une requête complète",
                "severity": "medium"
            })
        
        # Vérifications des références juridiques
        import re
        article_refs = re.findall(r'article\s+L\.\s*\d+-\d+', content, re.IGNORECASE)
        if len(article_refs) < 2:
            validation_score -= 10
            issues.append({
                "type": "legal_references",
                "description": "Peu de références juridiques",
                "severity": "medium"
            })
        
        return {
            "score": max(0, validation_score),
            "issues": issues,
            "word_count": len(content.split()),
            "legal_references_count": len(article_refs)
        }
    
    def _determine_recipient(self, meta_info: Dict[str, Any], 
                           legal_context: Dict[str, Any]) -> str:
        """Détermine le destinataire de la requête"""
        
        jurisdiction = legal_context.get('jurisdiction', 'Préfecture')
        
        if 'tribunal' in jurisdiction.lower():
            return "Monsieur le Président du Tribunal administratif"
        elif 'préfecture' in jurisdiction.lower():
            return "Monsieur le Préfet"
        else:
            return "Monsieur le Directeur"
    
    def _list_attachments(self, pieces_parsed: List[Dict]) -> List[str]:
        """Liste les pièces jointes"""
        
        attachments = []
        
        for i, piece in enumerate(pieces_parsed[:15], 1):  # Max 15 pièces
            filename = piece.get('filename', f'Document {i}')
            piece_type = piece.get('type_piece', 'Document')
            
            # Description plus précise selon le type
            type_descriptions = {
                'decision_administrative': 'Décision administrative',
                'piece_identite': 'Pièce d\'identité',
                'document_travail': 'Justificatif professionnel',
                'justificatif_domicile': 'Justificatif de domicile',
                'document_medical': 'Certificat médical',
                'acte_etat_civil': 'Acte d\'état civil',
                'email': 'Correspondance électronique'
            }
            
            description = type_descriptions.get(piece_type, 'Document justificatif')
            attachments.append(f"Annexe {i} : {filename} ({description})")
        
        return attachments
    
    def _extract_legal_references(self, content: str) -> List[str]:
        """Extrait les références juridiques du document"""
        
        import re
        
        # Recherche des articles de loi
        article_pattern = r'article\s+L\.\s*\d+-\d+[^\w]*([^.]*)'
        articles = re.findall(article_pattern, content, re.IGNORECASE)
        
        # Recherche des codes
        code_pattern = r'(Code[^.]*)'
        codes = re.findall(code_pattern, content, re.IGNORECASE)
        
        # Recherche de jurisprudence
        jurisprudence_pattern = r'(CE[^.]*\d{4}[^.]*)'
        jurisprudence = re.findall(jurisprudence_pattern, content, re.IGNORECASE)
        
        references = []
        
        # Nettoyage et formatage des références
        for article in articles[:10]:  # Max 10 articles
            clean_ref = re.sub(r'\s+', ' ', article.strip())
            if clean_ref and len(clean_ref) > 5:
                references.append(f"Article L. {clean_ref}")
        
        for code in codes[:5]:  # Max 5 codes
            clean_code = re.sub(r'\s+', ' ', code.strip())
            if clean_code and len(clean_code) > 10:
                references.append(clean_code)
        
        for juris in jurisprudence[:3]:  # Max 3 jurisprudences
            clean_juris = re.sub(r'\s+', ' ', juris.strip())
            if clean_juris and len(clean_juris) > 10:
                references.append(clean_juris)
        
        return list(set(references))  # Déduplication
    
    def _extract_facts_section(self, content: str) -> str:
        """Extrait la section des faits du brouillon"""
        
        # Recherche de la section des faits
        import re
        
        # Patterns pour identifier la section des faits
        facts_patterns = [
            r'(I\.\s*[^I]*?)(?=II\.|$)',
            r'(PRÉSENTATION[^I]*?)(?=II\.|MOYENS|$)',
            r'(EXPOSÉ[^I]*?)(?=II\.|MOYENS|$)'
        ]
        
        for pattern in facts_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                facts_text = match.group(1).strip()
                # Nettoyage
                facts_text = re.sub(r'^I\.\s*', '', facts_text)
                facts_text = re.sub(r'PRÉSENTATION.*?\n', '', facts_text)
                facts_text = re.sub(r'EXPOSÉ.*?\n', '', facts_text)
                return facts_text
        
        # Si pas de section identifiée, prendre le début du contenu
        paragraphs = content.split('\n\n')
        return '\n\n'.join(paragraphs[1:3]) if len(paragraphs) > 2 else "Section des faits à compléter."
    
    def _extract_legal_section(self, content: str) -> str:
        """Extrait la section juridique du brouillon"""
        
        import re
        
        # Recherche de la section juridique
        legal_patterns = [
            r'(II\.\s*[^I]*?)(?=III\.|CONCLUSION|$)',
            r'(MOYENS DE DROIT[^I]*?)(?=III\.|CONCLUSION|$)',
            r'(DROIT[^I]*?)(?=III\.|CONCLUSION|$)'
        ]
        
        for pattern in legal_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                legal_text = match.group(1).strip()
                # Nettoyage
                legal_text = re.sub(r'^II\.\s*', '', legal_text)
                legal_text = re.sub(r'MOYENS DE DROIT.*?\n', '', legal_text)
                return legal_text
        
        # Si pas de section identifiée, chercher les références juridiques
        article_sentences = []
        sentences = content.split('.')
        
        for sentence in sentences:
            if re.search(r'article\s+L\.\s*\d+-\d+', sentence, re.IGNORECASE):
                article_sentences.append(sentence.strip() + '.')
        
        return '\n\n'.join(article_sentences[:3]) if article_sentences else "Arguments juridiques à développer."
