"""
Agent 0 - Écouteur
Transforme audio/texte en NarrationJusticiable avec détection émotionnelle
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from defenseur_ia.core.base import BaseNode, NodeContext
from defenseur_ia.models import (
    NarrationJusticiable, Segment, MetaInfo
)
from defenseur_ia.services.stt_service import STTService
from defenseur_ia.services.emotion_detector import EmotionDetector

logger = logging.getLogger(__name__)

class EcouteurNode(BaseNode):
    """Agent 0 - Écouteur : Audio/Texte → NarrationJusticiable"""
    
    id = "ecouteur"
    name = "Écouteur (STT + Emotion)"
    description = "Transforme l'entrée audio/texte en narration structurée avec émotions"
    
    def __init__(self):
        super().__init__()
        self.stt_service = STTService()
        self.emotion_detector = EmotionDetector()
    
    async def exec(self, ctx: NodeContext) -> None:
        """Exécution principale de l'agent"""
        try:
            logger.info(f"🎧 Agent 0 - Écouteur démarré pour dossier {ctx.dossier_id}")
            
            # Récupération de l'entrée
            input_blob = await ctx.shared.get("input_blob")
            if not input_blob:
                raise ValueError("Aucune entrée trouvée")
            
            # Traitement selon le type d'entrée
            if isinstance(input_blob, dict) and input_blob.get("type") == "audio":
                narration = await self._process_audio(input_blob)
            else:
                narration = await self._process_text(str(input_blob))
            
            # Sauvegarde dans le SharedStore
            await ctx.shared.set("narration", narration)
            
            # Mise à jour du statut
            await ctx.shared.set("meta_info", MetaInfo(
                dossier_id=ctx.dossier_id,
                statut_pipeline="processing",
                etape_actuelle=0
            ))
            
            logger.info(f"✅ Agent 0 - Narration créée avec {len(narration.segments)} segments")
            
        except Exception as e:
            logger.error(f"❌ Agent 0 - Erreur: {str(e)}")
            await ctx.shared.set("error", str(e))
            raise
    
    async def _process_audio(self, audio_input: Dict[str, Any]) -> NarrationJusticiable:
        """Traite l'audio avec STT et détection émotionnelle"""
        
        # Transcription audio
        transcription = await self.stt_service.transcribe(
            audio_input.get("file_path"),
            audio_input.get("audio_data")
        )
        
        # Création des segments
        segments = []
        for segment_data in transcription.get("segments", []):
            text = segment_data["text"]
            
            # Détection des émotions
            emotion_result = await self.emotion_detector.detect(text)
            
            segment = Segment(
                id=f"seg_{uuid.uuid4().hex[:8]}",
                text=text,
                timestamp_start=segment_data.get("start"),
                timestamp_end=segment_data.get("end"),
                emotion=emotion_result["emotion"],
                confidence=emotion_result["confidence"]
            )
            segments.append(segment)
        
        # Génération du résumé
        resume = await self._generate_resume(segments)
        
        return NarrationJusticiable(
            langue=transcription.get("language", "fr"),
            segments=segments,
            resume=resume,
            mots_cles=self._extract_keywords(segments),
            duree_totale=transcription.get("duration")
        )
    
    async def _process_text(self, text: str) -> NarrationJusticiable:
        """Traite le texte direct avec détection émotionnelle"""
        
        # Découpage en segments (par phrases)
        segments = await self._split_into_segments(text)
        
        # Analyse émotionnelle pour chaque segment
        for segment in segments:
            emotion_result = await self.emotion_detector.detect(segment.text)
            segment.emotion = emotion_result["emotion"]
            segment.confidence = emotion_result["confidence"]
        
        # Génération du résumé
        resume = await self._generate_resume(segments)
        
        return NarrationJusticiable(
            langue="fr",
            segments=segments,
            resume=resume,
            mots_cles=self._extract_keywords(segments)
        )
    
    async def _split_into_segments(self, text: str) -> List[Segment]:
        """Découpe le texte en segments cohérents"""
        
        # Découpage par phrases
        import re
        sentences = re.split(r'[.!?]+', text)
        
        segments = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                segment = Segment(
                    id=f"seg_{uuid.uuid4().hex[:8]}",
                    text=sentence,
                    emotion="neutral",
                    confidence=1.0
                )
                segments.append(segment)
        
        return segments
    
    async def _generate_resume(self, segments: List[Segment]) -> str:
        """Génère un résumé automatique des segments"""
        
        if not segments:
            return ""
        
        full_text = " ".join([s.text for s in segments])
        
        # Si le texte est long, on le tronque
        if len(full_text) > 200:
            return full_text[:200] + "..."
        
        return full_text
    
    def _extract_keywords(self, segments: List[Segment]) -> List[str]:
        """Extrait les mots-clés des segments"""
        
        # Mots-clés simples basés sur la fréquence
        from collections import Counter
        import re
        
        all_text = " ".join([s.text.lower() for s in segments])
        words = re.findall(r'\b\w+\b', all_text)
        
        # Filtre les mots courts et communs
        stop_words = {
            'le', 'la', 'les', 'de', 'des', 'du', 'et', 'est', 'que',
            'pour', 'dans', 'sur', 'avec', 'ce', 'cette', 'un', 'une'
        }
        
        filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Top 10 mots les plus fréquents
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(10)]
