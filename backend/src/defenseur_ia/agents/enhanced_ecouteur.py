"""
Agent Écouteur amélioré avec raisonnement RRLA
Démonstrateur de l'intégration du schéma de reasoning avancé
"""

import asyncio
import json
from typing import Dict, Any, List
import logging

from .enhanced_agent_base import EnhancedAgentBase
from ..core.shared_store import SharedStore
from ..core.reasoning_schema import LogicProposition, KnowledgeTriplet
from ..services.stt_service import STTService
from ..services.emotion_detector import EmotionDetector

logger = logging.getLogger(__name__)


class EnhancedEcouteurAgent(EnhancedAgentBase):
    """
    Agent Écouteur avec capacités de raisonnement RRLA avancées
    Démonstrateur du nouveau système de reasoning
    """
    
    def __init__(self):
        super().__init__(agent_type="ecouteur")
        
        # Services spécialisés
        self.stt_service = STTService()
        self.emotion_detector = EmotionDetector()
        
        # Initialiser les connaissances spécifiques
        self._initialize_domain_knowledge()
        
        logger.info(f"🎤 Agent Écouteur RRLA initialisé: {self.agent_id}")
    
    def _initialize_domain_knowledge(self):
        """Initialise les connaissances spécifiques au domaine audio/transcription"""
        
        # Ajouter des triplets de connaissance
        knowledge_triplets = [
            KnowledgeTriplet(sub="audio_quality", pred="affects", obj="transcription_accuracy"),
            KnowledgeTriplet(sub="emotional_stress", pred="indicates", obj="urgency_level"),
            KnowledgeTriplet(sub="speech_patterns", pred="reveal", obj="narrative_structure"),
            KnowledgeTriplet(sub="background_noise", pred="reduces", obj="transcription_quality"),
            KnowledgeTriplet(sub="french_accent", pred="requires", obj="specialized_model")
        ]
        
        self.reasoning.kg.tri.extend(knowledge_triplets)
        
        # Ajouter des propositions logiques de base
        base_propositions = [
            LogicProposition(
                symb="Q(audio) → A(transcription)",
                nl="La qualité audio détermine la précision de la transcription"
            ),
            LogicProposition(
                symb="E(stress) → U(urgent)",
                nl="Un stress émotionnel élevé indique une situation urgente"
            ),
            LogicProposition(
                symb="S(segments) → C(coherence)",
                nl="La segmentation améliore la cohérence narrative"
            )
        ]
        
        self.reasoning.logic.propos.extend(base_propositions)
    
    async def _execute_step(self, step, shared_store: SharedStore, previous_results: Dict, **kwargs) -> Any:
        """
        Exécution spécialisée des étapes de l'agent Écouteur
        """
        
        step_index = step.index
        
        if step_index == 0:
            # Étape 0: Analyser la qualité audio
            return await self._analyze_audio_quality(shared_store, **kwargs)
        
        elif step_index == 1:
            # Étape 1: Transcription initiale
            return await self._perform_transcription(shared_store, previous_results, **kwargs)
        
        elif step_index == 2:
            # Étape 2: Détection émotionnelle
            return await self._detect_emotions(shared_store, previous_results, **kwargs)
        
        elif step_index == 3:
            # Étape 3: Segmentation narrative
            return await self._segment_narrative(shared_store, previous_results, **kwargs)
        
        else:
            raise ValueError(f"Étape inconnue: {step_index}")
    
    async def _analyze_audio_quality(self, shared_store: SharedStore, **kwargs) -> Dict[str, Any]:
        """Étape 0: Analyse de la qualité audio"""
        
        # Récupérer les données audio
        audio_data = await shared_store.get("audio_input")
        if not audio_data:
            # Simuler pour la démo
            audio_data = {"file_path": "/tmp/demo_audio.wav", "duration": 120, "format": "wav"}
        
        # Analyse de qualité (simulée)
        quality_analysis = {
            "sample_rate": 44100,
            "bit_depth": 16,
            "duration_seconds": audio_data.get("duration", 0),
            "noise_level": "low",
            "clarity_score": 0.85,
            "language_detected": "fr-FR",
            "quality_grade": "good"
        }
        
        # Raisonnement logique
        if quality_analysis["clarity_score"] < 0.7:
            self.reasoning.logic.doubts.append(
                LogicProposition(
                    symb="Q(audio) < 0.7 → ?A(transcription)",
                    nl="Qualité audio faible peut compromettre la transcription"
                )
            )
            self.reasoning.chain.warn.append("Qualité audio suboptimale détectée")
        
        # Mise à jour des connaissances
        self.reasoning.kg.tri.append(
            KnowledgeTriplet(
                sub=f"audio_{shared_store.get('meta_info', {}).get('dossier_id', 'unknown')}",
                pred="has_quality_score",
                obj=str(quality_analysis["clarity_score"])
            )
        )
        
        # Sauvegarder dans le store partagé
        await shared_store.set("audio_quality_analysis", quality_analysis)
        
        logger.info(f"🔍 Qualité audio analysée: {quality_analysis['quality_grade']} (score: {quality_analysis['clarity_score']})")
        
        return quality_analysis
    
    async def _perform_transcription(self, shared_store: SharedStore, previous_results: Dict, **kwargs) -> Dict[str, Any]:
        """Étape 1: Transcription audio avec Whisper/Gemini"""
        
        audio_quality = previous_results.get("step_0", {})
        
        # Choisir le modèle en fonction de la qualité
        if audio_quality.get("clarity_score", 0) > 0.8:
            model_choice = "whisper-large"
            confidence_boost = 0.1
        else:
            model_choice = "gemini-live"  # Meilleur pour audio dégradé
            confidence_boost = 0.0
        
        # Simulation de transcription (en production: appel réel à STTService)
        transcription_result = {
            "model_used": model_choice,
            "text": """
            Bonjour, je m'appelle Marie Dubois. J'ai reçu une OQTF le 15 mars 2024 et je ne comprends pas pourquoi. 
            Je suis en France depuis 2018, j'ai un travail stable comme aide-soignante à l'hôpital de Créteil. 
            J'ai déposé une demande de titre de séjour en février mais je n'ai pas encore eu de réponse. 
            Ma fille va à l'école ici, elle est en CM2. On a notre vie ici maintenant.
            """.strip(),
            "confidence": 0.87 + confidence_boost,
            "language": "fr-FR",
            "duration_processed": audio_quality.get("duration_seconds", 120),
            "word_count": 67,
            "processing_time": 8.5
        }
        
        # Raisonnement sur la qualité de transcription
        if transcription_result["confidence"] > 0.85:
            self.reasoning.logic.proofs.append(
                LogicProposition(
                    symb="C(transcription) > 0.85 → R(reliable)",
                    nl="Confiance élevée indique une transcription fiable"
                )
            )
        else:
            self.reasoning.logic.doubts.append(
                LogicProposition(
                    symb="C(transcription) < 0.85 → ?R(reliable)",
                    nl="Confiance modérée nécessite vérification manuelle"
                )
            )
        
        # Mise à jour des connaissances
        self.reasoning.kg.tri.append(
            KnowledgeTriplet(
                sub="transcription_model",
                pred="achieved_confidence",
                obj=str(transcription_result["confidence"])
            )
        )
        
        # Sauvegarder dans le store
        await shared_store.set("transcription_result", transcription_result)
        
        logger.info(f"🎤 Transcription terminée: {transcription_result['word_count']} mots, confiance: {transcription_result['confidence']:.2f}")
        
        return transcription_result
    
    async def _detect_emotions(self, shared_store: SharedStore, previous_results: Dict, **kwargs) -> Dict[str, Any]:
        """Étape 2: Détection émotionnelle dans la transcription"""
        
        transcription = previous_results.get("step_1", {})
        text = transcription.get("text", "")
        
        # Analyse émotionnelle (simulée)
        emotion_analysis = {
            "primary_emotion": "anxiety",
            "emotion_intensity": 0.75,
            "emotional_markers": [
                {"text": "je ne comprends pas pourquoi", "emotion": "confusion", "intensity": 0.8},
                {"text": "On a notre vie ici maintenant", "emotion": "attachment", "intensity": 0.9},
                {"text": "Ma fille va à l'école ici", "emotion": "protection", "intensity": 0.85}
            ],
            "stress_indicators": ["urgency", "family_concerns", "administrative_confusion"],
            "urgency_level": "high",
            "empathy_score": 0.82
        }
        
        # Raisonnement émotionnel
        if emotion_analysis["urgency_level"] == "high":
            self.reasoning.logic.proofs.append(
                LogicProposition(
                    symb="U(high) ∧ F(family) → P(priority)",
                    nl="Urgence élevée avec enjeux familiaux nécessite traitement prioritaire"
                )
            )
            
            # Anticipation des besoins
            self.reasoning.rrla_ext.anticipation.extend([
                "Besoin d'accompagnement psychologique",
                "Urgence administrative à traiter",
                "Risque de détresse familiale"
            ])
        
        # Mise à jour du réseau relationnel
        self.reasoning.rrla_ext.relational_networks.append({
            "concept": "situation_familiale",
            "related_to": ["scolarité_enfant", "stabilité_professionnelle", "intégration_sociale"]
        })
        
        # Sauvegarder
        await shared_store.set("emotion_analysis", emotion_analysis)
        
        logger.info(f"😟 Émotions détectées: {emotion_analysis['primary_emotion']} (intensité: {emotion_analysis['emotion_intensity']:.2f})")
        
        return emotion_analysis
    
    async def _segment_narrative(self, shared_store: SharedStore, previous_results: Dict, **kwargs) -> Dict[str, Any]:
        """Étape 3: Segmentation narrative du témoignage"""
        
        transcription = previous_results.get("step_1", {})
        emotions = previous_results.get("step_2", {})
        
        text = transcription.get("text", "")
        
        # Segmentation intelligente
        narrative_segments = [
            {
                "index": 0,
                "type": "identification",
                "contenu": "Bonjour, je m'appelle Marie Dubois.",
                "emotion": "neutral",
                "importance": "administrative"
            },
            {
                "index": 1,
                "type": "probleme_principal",
                "contenu": "J'ai reçu une OQTF le 15 mars 2024 et je ne comprends pas pourquoi.",
                "emotion": "confusion",
                "importance": "critique"
            },
            {
                "index": 2,
                "type": "situation_professionnelle",
                "contenu": "Je suis en France depuis 2018, j'ai un travail stable comme aide-soignante à l'hôpital de Créteil.",
                "emotion": "pride",
                "importance": "forte"
            },
            {
                "index": 3,
                "type": "demarches_administratives",
                "contenu": "J'ai déposé une demande de titre de séjour en février mais je n'ai pas encore eu de réponse.",
                "emotion": "frustration",
                "importance": "forte"
            },
            {
                "index": 4,
                "type": "situation_familiale",
                "contenu": "Ma fille va à l'école ici, elle est en CM2. On a notre vie ici maintenant.",
                "emotion": "attachment",
                "importance": "critique"
            }
        ]
        
        segmentation_result = {
            "total_segments": len(narrative_segments),
            "segments": narrative_segments,
            "narrative_structure": "chronological_with_emotional_peaks",
            "key_themes": ["famille", "travail", "administration", "intégration"],
            "coherence_score": 0.91
        }
        
        # Raisonnement sur la structure narrative
        self.reasoning.logic.proofs.append(
            LogicProposition(
                symb="S(coherent) ∧ T(themes) → N(strong_narrative)",
                nl="Segments cohérents avec thèmes clairs forment un récit solide"
            )
        )
        
        # Mise à jour finale du raisonnement
        self.reasoning.rrla_ext.explainability = f"""
        Agent Écouteur - Analyse complète:
        - Audio de qualité {previous_results.get('step_0', {}).get('quality_grade', 'unknown')}
        - Transcription {transcription.get('word_count', 0)} mots (confiance: {transcription.get('confidence', 0):.2f})
        - Émotion dominante: {emotions.get('primary_emotion', 'unknown')} (urgence: {emotions.get('urgency_level', 'unknown')})
        - {len(narrative_segments)} segments narratifs identifiés
        - Cohérence narrative: {segmentation_result['coherence_score']:.2f}
        """
        
        # Sauvegarder le résultat final
        await shared_store.set("narration", segmentation_result)
        
        logger.info(f"📝 Segmentation terminée: {len(narrative_segments)} segments, cohérence: {segmentation_result['coherence_score']:.2f}")
        
        return segmentation_result


# Factory pour créer l'agent amélioré
def create_enhanced_ecouteur() -> EnhancedEcouteurAgent:
    """Crée un agent Écouteur avec raisonnement RRLA"""
    return EnhancedEcouteurAgent()
