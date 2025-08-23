"""
AGENT 6 - Rédacteur Narratif
Transforme un témoignage brut en récit structuré et argumenté pour un recours administratif
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.base import BaseNode, NodeContext
from ..models import DraftNarratif
from ..services.openai_service import OpenAIService, create_openai_service

logger = logging.getLogger(__name__)

class RedacteurNarratifNode(BaseNode):
    """
    Agent responsable de la rédaction du premier brouillon narratif
    
    Inputs: narration, matches, web_corpus, pieces, axes
    Output: draft.v0 (premier brouillon du récit)
    """
    
    id = "redacteur_narratif"
    name = "Rédacteur Narratif"
    
    def __init__(self):
        super().__init__()
        self.openai: Optional[OpenAIService] = create_openai_service()
        
    async def exec(self, context: NodeContext) -> Dict[str, Any]:
        """
        Rédige le premier brouillon du récit juridique
        """
        try:
            logger.info("✍️ Début de la rédaction du récit narratif")
            
            # Récupération des données nécessaires
            narration = await context.shared.get("narration", {})
            matches = await context.shared.get("matches", [])
            web_corpus = await context.shared.get("web_corpus", [])
            pieces_parsed = await context.shared.get("pieces_parsed", [])
            axes_juridiques = await context.shared.get("axes_juridiques", [])
            meta_info = await context.shared.get("meta_info", {})
            
            if not narration.get('segments'):
                logger.error("Aucune narration disponible pour la rédaction")
                raise ValueError("Narration manquante")
            
            # Initialisation du client OpenAI
            await self._init_openai_client(context)
            
            # Construction du contexte riche pour le LLM
            rich_context = self._build_rich_context(
                narration, matches, web_corpus, pieces_parsed, axes_juridiques, meta_info
            )
            
            # Génération du brouillon avec GPT-4o
            draft_content = await self._generate_narrative_draft(rich_context)
            
            # Structuration du brouillon
            draft = DraftNarratif(
                version="v0",
                contenu=draft_content,
                sections=self._extract_sections(draft_content),
                references_pieces=self._extract_piece_references(draft_content, pieces_parsed),
                references_articles=self._extract_article_references(draft_content, matches),
                metadata={
                    "generated_at": datetime.now().isoformat(),
                    "model_used": (self.openai.config.model_gpt4 if self.openai and not self.openai.simulation_mode else "simulation"),
                    "context_elements": len(rich_context),
                    "word_count": len(draft_content.split()),
                    "agent_version": "1.0"
                }
            )
            
            # Sauvegarde dans le store
            await context.shared.set("draft", {"v0": draft.dict()})
            
            logger.info(f"✅ Brouillon narratif généré ({len(draft_content.split())} mots)")
            
            return {
                "draft": draft.dict(),
                "stats": {
                    "word_count": len(draft_content.split()),
                    "sections": len(draft.sections),
                    "piece_references": len(draft.references_pieces),
                    "article_references": len(draft.references_articles)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans le rédacteur narratif: {e}")
            raise
    
    async def _init_openai_client(self, context: NodeContext):
        """Initialise le service OpenAI"""
        try:
            # Ré-initialise pour s'assurer d'une config à jour
            self.openai = create_openai_service()
            if self.openai and self.openai.simulation_mode:
                logger.warning("Clé API OpenAI manquante, utilisation du mode simulation")
            else:
                logger.info("✅ OpenAIService initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation OpenAI: {e}")
            self.openai = None
    
    def _build_rich_context(self, narration: Dict, matches: List, web_corpus: List, 
                           pieces: List, axes: List, meta_info: Dict) -> Dict[str, Any]:
        """Construit un contexte riche pour le LLM"""
        
        # Extraction des éléments narratifs
        story_elements = self._extract_story_elements(narration)
        
        # Sélection des matches les plus pertinents
        top_matches = sorted(matches, key=lambda x: x.get('score_matching', 0), reverse=True)[:10]
        
        # Sélection des ressources web les plus pertinentes
        top_web_resources = sorted(web_corpus, key=lambda x: x.get('pertinence', 0), reverse=True)[:5]
        
        # Informations sur les pièces justificatives
        piece_summary = self._summarize_pieces(pieces)
        
        context = {
            "meta_info": meta_info,
            "story_elements": story_elements,
            "legal_axes": axes,
            "supporting_evidence": piece_summary,
            "legal_references": top_matches,
            "web_resources": top_web_resources,
            "narrative_tone": self._determine_narrative_tone(narration),
            "case_complexity": self._assess_case_complexity(axes, matches, pieces)
        }
        
        return context
    
    def _extract_story_elements(self, narration: Dict) -> Dict[str, Any]:
        """Extrait les éléments narratifs clés"""
        segments = narration.get('segments', [])
        
        # Chronologie des événements
        chronology = []
        # Personnages impliqués
        characters = set()
        # Lieux mentionnés
        locations = set()
        # Émotions dominantes
        emotions = []
        
        for segment in segments:
            text = segment.get('texte', '')
            emotion = segment.get('emotion', {})
            
            # Extraction basique d'entités
            # TODO: Améliorer avec NER (Named Entity Recognition)
            
            chronology.append({
                "text": text,
                "emotion": emotion.get('emotion', 'neutre'),
                "confidence": emotion.get('confidence', 0)
            })
            
            if emotion.get('emotion'):
                emotions.append(emotion.get('emotion'))
        
        return {
            "chronology": chronology,
            "characters": list(characters),
            "locations": list(locations),
            "dominant_emotions": emotions,
            "total_segments": len(segments)
        }
    
    def _summarize_pieces(self, pieces: List[Dict]) -> Dict[str, Any]:
        """Résume les pièces justificatives"""
        piece_types = {}
        total_pieces = len(pieces)
        
        for piece in pieces:
            piece_type = piece.get('type_piece', 'unknown')
            if piece_type not in piece_types:
                piece_types[piece_type] = []
            piece_types[piece_type].append({
                "filename": piece.get('filename', ''),
                "summary": piece.get('contenu_brut', '')[:200] + "..." if len(piece.get('contenu_brut', '')) > 200 else piece.get('contenu_brut', '')
            })
        
        return {
            "total_pieces": total_pieces,
            "piece_types": piece_types,
            "key_documents": self._identify_key_documents(pieces)
        }
    
    def _identify_key_documents(self, pieces: List[Dict]) -> List[Dict]:
        """Identifie les documents clés pour le dossier"""
        key_docs = []
        
        priority_types = [
            "decision_administrative",
            "piece_identite", 
            "document_travail",
            "justificatif_domicile"
        ]
        
        for piece in pieces:
            if piece.get('type_piece') in priority_types:
                key_docs.append({
                    "filename": piece.get('filename', ''),
                    "type": piece.get('type_piece', ''),
                    "importance": "haute"
                })
        
        return key_docs[:5]  # Top 5 documents clés
    
    def _determine_narrative_tone(self, narration: Dict) -> str:
        """Détermine le ton narratif approprié"""
        segments = narration.get('segments', [])
        
        # Analyse des émotions pour déterminer le ton
        emotions = []
        for segment in segments:
            emotion = segment.get('emotion', {}).get('emotion', 'neutre')
            emotions.append(emotion)
        
        if 'detresse' in emotions or 'peur' in emotions:
            return "empathique_urgent"
        elif 'colere' in emotions:
            return "ferme_determine"
        else:
            return "factuel_respectueux"
    
    def _assess_case_complexity(self, axes: List, matches: List, pieces: List) -> str:
        """Évalue la complexité du dossier"""
        complexity_score = 0
        
        # Nombre d'axes juridiques
        complexity_score += len(axes) * 2
        
        # Qualité des matches
        high_quality_matches = len([m for m in matches if m.get('score_matching', 0) > 0.8])
        complexity_score += high_quality_matches
        
        # Nombre de pièces
        complexity_score += len(pieces)
        
        if complexity_score > 20:
            return "complexe"
        elif complexity_score > 10:
            return "moyenne"
        else:
            return "simple"
    
    async def _generate_narrative_draft(self, context: Dict[str, Any]) -> str:
        """Génère le brouillon narratif avec GPT-4o"""
        
        if not self.openai or self.openai.simulation_mode:
            return self._generate_mock_narrative(context)
        
        try:
            # Construction du prompt système détaillé
            system_prompt = self._build_system_prompt()
            
            # Construction du prompt utilisateur avec le contexte
            user_prompt = self._build_user_prompt(context)
            
            # Appel via OpenAIService
            resp = await self.openai.gpt_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            return resp.content
            
        except Exception as e:
            logger.error(f"Erreur génération GPT: {e}")
            return self._generate_mock_narrative(context)
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système pour GPT-4o"""
        return """Tu es un rédacteur juridique expert spécialisé dans le droit des étrangers en France. 

Ta mission est de transformer un témoignage brut en un récit structuré, empathique et juridiquement solide pour un recours administratif.

RÈGLES DE RÉDACTION :
1. STRUCTURE : Introduction - Contexte personnel - Chronologie des faits - Arguments juridiques - Conclusion
2. TON : Respectueux, factuel, empathique mais ferme
3. STYLE : Français juridique correct, phrases claires, éviter le jargon excessif
4. RÉFÉRENCES : Citer les pièces justificatives (Annexe X) et articles de loi pertinents
5. LONGUEUR : 1500-2500 mots selon la complexité

ÉLÉMENTS OBLIGATOIRES :
- Présentation de la situation personnelle
- Chronologie claire des événements
- Références aux textes de loi applicables
- Mention des pièces justificatives
- Arguments juridiques structurés
- Demande claire et motivée

ÉVITER :
- Répétitions inutiles
- Émotions excessives
- Accusations non fondées
- Détails non pertinents juridiquement"""

    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """Construit le prompt utilisateur avec le contexte"""
        
        # Informations de base
        meta_info = context.get('meta_info', {})
        story_elements = context.get('story_elements', {})
        
        prompt = f"""
CONTEXTE DU DOSSIER :
- Type de procédure : {meta_info.get('type_procedure', 'Recours administratif')}
- Situation : {meta_info.get('situation', 'Non spécifiée')}

RÉCIT DU JUSTICIABLE :
"""
        
        # Ajout de la chronologie
        chronology = story_elements.get('chronology', [])
        for i, event in enumerate(chronology[:10]):  # Limite à 10 événements
            prompt += f"{i+1}. {event.get('text', '')}\n"
        
        prompt += f"""

AXES JURIDIQUES IDENTIFIÉS :
"""
        
        # Ajout des axes juridiques
        axes = context.get('legal_axes', [])
        for axe in axes[:5]:  # Top 5 axes
            prompt += f"- {axe.get('theme', '')}: {axe.get('description', '')}\n"
        
        prompt += f"""

PIÈCES JUSTIFICATIVES DISPONIBLES :
"""
        
        # Ajout des pièces clés
        evidence = context.get('supporting_evidence', {})
        key_docs = evidence.get('key_documents', [])
        for i, doc in enumerate(key_docs):
            prompt += f"Annexe {i+1}: {doc.get('filename', '')} ({doc.get('type', '')})\n"
        
        prompt += f"""

RÉFÉRENCES JURIDIQUES PERTINENTES :
"""
        
        # Ajout des références légales
        legal_refs = context.get('legal_references', [])
        for ref in legal_refs[:5]:  # Top 5 références
            prompt += f"- {ref.get('article_titre', '')}\n"
        
        prompt += f"""

CONSIGNE :
Rédige un récit narratif structuré et argumenté pour ce recours administratif. 
Le récit doit être empathique mais factuel, avec des références précises aux pièces et aux textes de loi.
Ton narratif : {context.get('narrative_tone', 'factuel_respectueux')}
Complexité du dossier : {context.get('case_complexity', 'moyenne')}
"""
        
        return prompt
    
    def _generate_mock_narrative(self, context: Dict[str, Any]) -> str:
        """Génère un récit mock pour les tests"""
        meta_info = context.get('meta_info', {})
        
        return f"""
RECOURS GRACIEUX CONTRE UNE DÉCISION D'OBLIGATION DE QUITTER LE TERRITOIRE FRANÇAIS

Madame, Monsieur le Préfet,

J'ai l'honneur de solliciter par la présente un recours gracieux contre la décision d'obligation de quitter le territoire français qui m'a été notifiée en date du [DATE].

I. PRÉSENTATION DE MA SITUATION PERSONNELLE

Je suis [NOM], de nationalité [NATIONALITÉ], né(e) le [DATE] à [LIEU]. Je réside en France depuis [DURÉE] et ma situation s'est progressivement stabilisée au fil des années.

II. CHRONOLOGIE DES FAITS

[Récit chronologique basé sur la narration fournie...]

III. MOYENS DE DROIT

La décision contestée méconnaît plusieurs dispositions légales et réglementaires :

1. Au regard de l'article L. 511-4 du CESEDA...
2. Concernant l'appréciation de ma situation personnelle...

IV. PIÈCES JUSTIFICATIVES

Les pièces suivantes, jointes au présent recours, attestent de ma situation :
- Annexe 1 : [Document]
- Annexe 2 : [Document]

V. CONCLUSION

Pour tous ces motifs, je vous demande respectueusement de bien vouloir rapporter la décision d'OQTF et de procéder à un réexamen de ma situation.

Je vous prie d'agréer, Madame, Monsieur le Préfet, l'expression de ma haute considération.

[Signature]
"""
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extrait les sections du contenu"""
        sections = []
        
        # Recherche des sections basée sur les numéros romains et titres
        import re
        section_pattern = r'^(I{1,3}V?|IV|V|VI{1,3})\.\s*(.+)$'
        
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            match = re.match(section_pattern, line.strip())
            if match:
                # Sauvegarde de la section précédente
                if current_section:
                    sections.append({
                        "titre": current_section,
                        "contenu": '\n'.join(current_content).strip()
                    })
                
                # Nouvelle section
                current_section = match.group(2)
                current_content = []
            else:
                current_content.append(line)
        
        # Dernière section
        if current_section:
            sections.append({
                "titre": current_section,
                "contenu": '\n'.join(current_content).strip()
            })
        
        return sections
    
    def _extract_piece_references(self, content: str, pieces: List[Dict]) -> List[str]:
        """Extrait les références aux pièces dans le contenu"""
        import re
        
        # Recherche des références "Annexe X"
        annexe_pattern = r'Annexe\s+(\d+)'
        matches = re.findall(annexe_pattern, content, re.IGNORECASE)
        
        references = []
        for match in matches:
            annexe_num = int(match)
            if annexe_num <= len(pieces):
                piece = pieces[annexe_num - 1]
                references.append(piece.get('filename', f'Annexe {annexe_num}'))
        
        return list(set(references))  # Déduplication
    
    def _extract_article_references(self, content: str, matches: List[Dict]) -> List[str]:
        """Extrait les références aux articles de loi"""
        import re
        
        # Recherche des références d'articles
        article_pattern = r'article\s+L\.\s*\d+-\d+'
        found_articles = re.findall(article_pattern, content, re.IGNORECASE)
        
        references = []
        for article_ref in found_articles:
            # Recherche dans les matches pour trouver le titre complet
            for match in matches:
                if article_ref.lower() in match.get('article_titre', '').lower():
                    references.append(match.get('article_titre', article_ref))
                    break
            else:
                references.append(article_ref)
        
        return list(set(references))  # Déduplication
