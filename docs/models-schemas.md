# 05 · MODÈLES & SCHÉMAS DE DONNÉES

> **Spécifications complètes des structures de données**  
> Tous les modèles Pydantic v2 pour le SharedStore, avec exemples JSON  
> et règles de validation.

---

## 📋 Sommaire

1. [Architecture des données](#1-architecture-des-données)
2. [Modèles de base](#2-modèles-de-base)
3. [Modèles d'entrée](#3-modèles-dentrée)
4. [Modèles intermédiaires](#4-modèles-intermédiaires)
5. [Modèles de sortie](#5-modèles-de-sortie)
6. [Validation et contraintes](#6-validation-et-contraintes)
7. [Exemples JSON complets](#7-exemples-json-complets)
8. [Migration et versioning](#8-migration-et-versioning)

---

## 1. Architecture des données

### 1.1 Vue d'ensemble du SharedStore

```mermaid
graph TD
    A[SharedStore] --> B[meta: MetaInfo]
    A --> C[narration: NarrationJusticiable]
    A --> D[axes: List[HypotheseRecherche]]
    A --> E[legal_corpus: List[CodeArticle]]
    A --> F[pieces: List[PieceParsed]]
    A --> G[matches: List[MatchPieceArticle]]
    A --> H[web_corpus: List[RessourceWeb]]
    A --> I[draft: DraftVersions]
    A --> J[plan: PlanStrategique]
    A --> K[requete_finale: RequeteFinale]
    A --> L[logs: LogsHistory]
```

### 1.2 Flux de transformation des données

```
input_blob → narration → axes → legal_corpus
                ↓              ↓
           pieces → matches → web_corpus
                         ↓
           draft.v0 → draft.v1 → draft.v2
                         ↓
           plan → requete_finale → output_files
```

---

## 2. Modèles de base

### 2.1 MetaInfo - Métadonnées du dossier

```python
# src/defenseur_ia/types/models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from uuid import uuid4

class MetaInfo(BaseModel):
    """Métadonnées générales du dossier"""
    
    dossier_id: str = Field(
        default_factory=lambda: f"CASE_{datetime.now().strftime('%Y%m%d')}_{str(uuid4())[:8]}",
        description="Identifiant unique du dossier"
    )
    
    version_schema: str = Field(
        default="2024.12.01",
        description="Version du schéma de données"
    )
    
    langue_principale: Literal["fr", "en", "es", "ar", "auto"] = Field(
        default="fr",
        description="Langue principale du dossier"
    )
    
    type_contentieux: Optional[Literal[
        "oqtf", "titre_sejour", "regroupement_familial", 
        "naturalisation", "visa", "asile", "autre"
    ]] = Field(
        default=None,
        description="Type de contentieux identifié"
    )
    
    urgence_niveau: Literal["faible", "moyen", "eleve", "critique"] = Field(
        default="moyen",
        description="Niveau d'urgence évalué"
    )
    
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Date de création"
    )
    
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Dernière modification"
    )
    
    created_by: Optional[str] = Field(
        default=None,
        description="Utilisateur ou système créateur"
    )
    
    tags: list[str] = Field(
        default_factory=list,
        description="Tags libres pour classification"
    )
    
    confidentialite: Literal["public", "interne", "confidentiel", "secret"] = Field(
        default="confidentiel",
        description="Niveau de confidentialité"
    )

    @validator('dossier_id')
    def validate_dossier_id(cls, v):
        if not v or len(v) < 8:
            raise ValueError("L'ID dossier doit faire au moins 8 caractères")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### 2.2 Segment - Unité de base de la narration

```python
class Segment(BaseModel):
    """Segment de texte avec métadonnées temporelles et émotionnelles"""
    
    id: str = Field(
        default_factory=lambda: f"seg_{uuid4().hex[:8]}",
        description="Identifiant unique du segment"
    )
    
    start_time: float = Field(
        ge=0.0,
        description="Temps de début en secondes (0 si texte)"
    )
    
    end_time: float = Field(
        ge=0.0, 
        description="Temps de fin en secondes"
    )
    
    text: str = Field(
        min_length=1,
        max_length=5000,
        description="Texte du segment"
    )
    
    emotion: Literal[
        "neutral", "sad", "angry", "joy", "fear", 
        "surprise", "disgust", "trust", "anticipation"
    ] = Field(
        default="neutral",
        description="Émotion détectée"
    )
    
    emotion_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confiance dans la détection d'émotion"
    )
    
    entities: list[str] = Field(
        default_factory=list,
        description="Entités nommées détectées"
    )
    
    keywords: list[str] = Field(
        default_factory=list,
        description="Mots-clés juridiques identifiés"
    )
    
    importance_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Score d'importance du segment"
    )

    @validator('end_time')
    def validate_time_order(cls, v, values):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError("end_time doit être >= start_time")
        return v
```

---

## 3. Modèles d'entrée

### 3.1 NarrationJusticiable - Témoignage structuré

```python
class NarrationJusticiable(BaseModel):
    """Narration complète du justiciable avec métadonnées"""
    
    langue: str = Field(
        default="fr",
        description="Code langue ISO 639-1"
    )
    
    segments: list[Segment] = Field(
        min_items=1,
        description="Liste des segments de narration"
    )
    
    transcription_raw: Optional[str] = Field(
        default=None,
        description="Transcription brute si audio"
    )
    
    source_type: Literal["audio", "text", "dictee", "import"] = Field(
        default="text",
        description="Type de source originale"
    )
    
    duree_totale: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Durée totale en secondes (audio seulement)"
    )
    
    qualite_transcription: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Score de qualité STT"
    )
    
    resume_automatique: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Résumé généré automatiquement"
    )
    
    chronologie_events: list[dict] = Field(
        default_factory=list,
        description="Événements chronologiques détectés"
    )

    @property
    def texte_complet(self) -> str:
        """Reconstitue le texte complet depuis les segments"""
        return " ".join(segment.text for segment in self.segments)
    
    @property
    def emotions_principales(self) -> dict[str, int]:
        """Compte des émotions par type"""
        emotions = {}
        for segment in self.segments:
            emotions[segment.emotion] = emotions.get(segment.emotion, 0) + 1
        return emotions
    
    @property
    def mots_cles_globaux(self) -> list[str]:
        """Tous les mots-clés uniques"""
        all_keywords = []
        for segment in self.segments:
            all_keywords.extend(segment.keywords)
        return list(set(all_keywords))
```

### 3.2 HypotheseRecherche - Axes juridiques

```python
class HypotheseRecherche(BaseModel):
    """Axe juridique à explorer avec métadonnées de recherche"""
    
    id: str = Field(
        default_factory=lambda: f"axe_{uuid4().hex[:8]}",
        description="Identifiant unique de l'axe"
    )
    
    intitule: str = Field(
        min_length=10,
        max_length=200,
        description="Libellé de l'axe juridique"
    )
    
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Description détaillée"
    )
    
    priorite: int = Field(
        ge=1,
        le=5,
        description="Priorité (1=faible, 5=critique)"
    )
    
    domaine_juridique: Literal[
        "droit_etrangers", "droit_civil", "droit_administratif",
        "droit_famille", "droit_travail", "droit_social", "autre"
    ] = Field(
        default="droit_etrangers",
        description="Domaine juridique principal"
    )
    
    mots_cles_recherche: list[str] = Field(
        min_items=1,
        description="Mots-clés pour recherche Légifrance"
    )
    
    codes_cibles: list[str] = Field(
        default_factory=list,
        description="Codes juridiques à prioriser"
    )
    
    confidence_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confiance dans la pertinence de l'axe"
    )
    
    source_segments: list[str] = Field(
        default_factory=list,
        description="IDs des segments ayant généré cet axe"
    )
    
    statut: Literal["actif", "explore", "abandonne", "fusionne"] = Field(
        default="actif",
        description="Statut de l'axe dans le traitement"
    )

    @validator('mots_cles_recherche')
    def validate_keywords(cls, v):
        if not v or all(len(keyword.strip()) < 3 for keyword in v):
            raise ValueError("Au moins un mot-clé de 3+ caractères requis")
        return [keyword.strip() for keyword in v if keyword.strip()]
```

---

## 4. Modèles intermédiaires

### 4.1 CodeArticle - Article de loi Légifrance

```python
class CodeArticle(BaseModel):
    """Article de code ou loi depuis Légifrance"""
    
    cid: str = Field(
        regex=r"^LEGIARTI\d{12}$|^LEGITEXT\d{12}$",
        description="Identifiant Légifrance (CID)"
    )
    
    numero: str = Field(
        min_length=1,
        max_length=50,
        description="Numéro d'article (ex: L.511-1)"
    )
    
    titre: str = Field(
        max_length=500,
        description="Titre de l'article"
    )
    
    texte_html: str = Field(
        description="Contenu HTML de l'article"
    )
    
    texte_brut: Optional[str] = Field(
        default=None,
        description="Contenu nettoyé sans HTML"
    )
    
    code_nom: str = Field(
        description="Nom du code (CESEDA, Code civil...)"
    )
    
    section_nom: Optional[str] = Field(
        default=None,
        description="Nom de la section si applicable"
    )
    
    etat_juridique: Literal[
        "VIGUEUR", "VIGUEUR_DIFF", "ABROGE", "MODIFIE", "PERIME"
    ] = Field(
        default="VIGUEUR",
        description="État juridique de l'article"
    )
    
    date_debut_vigueur: Optional[str] = Field(
        default=None,
        description="Date d'entrée en vigueur (ISO)"
    )
    
    date_fin_vigueur: Optional[str] = Field(
        default=None,
        description="Date de fin de vigueur (ISO)"
    )
    
    source_url: str = Field(
        regex=r"^https://.*legifrance\.gouv\.fr.*",
        description="URL source Légifrance"
    )
    
    fond: Literal["CODE", "LODA", "JORF", "KALI"] = Field(
        description="Fonds documentaire Légifrance"
    )
    
    derniere_modification: Optional[str] = Field(
        default=None,
        description="Date dernière modification"
    )
    
    notes: Optional[str] = Field(
        default=None,
        description="Notes ou remarques"
    )

    @property
    def reference_complete(self) -> str: