"""
Service de détection d'émotions pour DEFENSEUR-IA
"""

import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)


class EmotionDetector:
    """
    Détecteur d'émotions basé sur des mots-clés et patterns
    """
    
    def __init__(self):
        # Dictionnaire de mots-clés émotionnels
        self.emotion_keywords = {
            "sad": [
                "triste", "tristesse", "désespoir", "pleure", "pleurer", "déprimé", 
                "malheureux", "chagrin", "mélancolie", "abattu", "découragé"
            ],
            "angry": [
                "colère", "furieux", "énervé", "injuste", "révoltant", "indigné",
                "rage", "irrité", "exaspéré", "outré", "scandalisé"
            ],
            "fearful": [
                "peur", "angoisse", "terrifié", "inquiet", "stress", "anxieux",
                "effrayé", "paniqué", "craintif", "appréhension", "terreur"
            ],
            "happy": [
                "joie", "heureux", "content", "ravi", "sourire", "bonheur",
                "satisfait", "enchanté", "réjoui", "optimiste", "espoir"
            ],
            "surprised": [
                "surpris", "étonnant", "incroyable", "choqué", "stupéfait",
                "abasourdi", "sidéré", "ébahi", "médusé"
            ],
            "disgusted": [
                "dégoût", "écœuré", "répugnant", "horrible", "ignoble",
                "nauséabond", "révoltant", "abject"
            ]
        }
    
    def detect_emotion(self, text: str) -> str:
        """
        Détecte l'émotion dominante dans un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Émotion détectée ("neutral" par défaut)
        """
        if not text or len(text.strip()) < 3:
            return "neutral"
        
        text_lower = text.lower()
        emotion_scores = {}
        
        # Comptage des mots-clés par émotion
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                # Recherche de mots complets (éviter les faux positifs)
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            if score > 0:
                emotion_scores[emotion] = score
        
        # Retourne l'émotion avec le score le plus élevé
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            logger.debug(f"Émotion détectée: {dominant_emotion} (score: {emotion_scores[dominant_emotion]})")
            return dominant_emotion
        
        return "neutral"
    
    def detect_emotions_batch(self, texts: List[str]) -> List[str]:
        """
        Détecte les émotions pour une liste de textes
        
        Args:
            texts: Liste de textes à analyser
            
        Returns:
            Liste des émotions détectées
        """
        return [self.detect_emotion(text) for text in texts]
    
    def get_emotion_confidence(self, text: str, emotion: str) -> float:
        """
        Calcule un score de confiance pour une émotion donnée
        
        Args:
            text: Texte à analyser
            emotion: Émotion à évaluer
            
        Returns:
            Score de confiance entre 0.0 et 1.0
        """
        if emotion not in self.emotion_keywords:
            return 0.0
        
        text_lower = text.lower()
        keywords = self.emotion_keywords[emotion]
        
        # Comptage des occurrences
        total_matches = 0
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = len(re.findall(pattern, text_lower))
            total_matches += matches
        
        # Normalisation par rapport à la longueur du texte
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        # Score normalisé (max 1.0)
        confidence = min(1.0, total_matches / max(1, word_count / 10))
        return confidence


# Instance globale
emotion_detector = EmotionDetector()
