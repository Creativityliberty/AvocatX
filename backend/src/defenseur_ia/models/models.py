"""
Modèles de données Pydantic v2 pour DEFENSEUR-IA
Conforme aux spécifications exactes lues dans les docs
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, List, Dict, Any, Union
from datetime import datetime
from uuid import uuid4
import json

# Modèles de base
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
        description="Date de dernière mise à jour"
    )
    
    deadline: Optional[str] = Field(
        default=None,
        description="Date limite pour le dossier"
    )
    
    statut_pipeline: Literal[
        "pending", "processing", "completed", "error", "cancelled"
    ] = Field(default="pending")
    
    etape_actuelle: int = Field(default=0, ge=0, le=11)
    
    progression: float = Field(default=0.0, ge=0.0, le=100.0)

class Segment(BaseModel):
    """Segment de texte avec métadonnées temporelles et émotionnelles"""
    
    id: str = Field(
        default_factory=lambda: f"seg_{uuid4().hex[:8]}"
    )
    
    text: str = Field(..., description="Texte du segment")
    
    timestamp_start: Optional[float] = Field(
        default=None,
        description="Timestamp de début (secondes)"
    )
    
    timestamp_end: Optional[float] = Field(
        default=None,
        description="Timestamp de fin (secondes)"
    )
    
    emotion: Literal[
        "neutral", "happy", "sad", "angry", "fearful", 
        "surprised", "disgusted"
    ] = Field(default="neutral")
    
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class NarrationJusticiable(BaseModel):
    """Narration complète du justiciable"""
    
    langue: str = Field(default="fr")
    segments: List[Segment] = Field(default_factory=list)
    
    resume: Optional[str] = Field(
        default=None,
        description="Résumé automatique de la narration"
    )
    
    mots_cles: List[str] = Field(default_factory=list)
    
    duree_totale: Optional[float] = Field(
        default=None,
        description="Durée totale en secondes"
    )

class HypotheseRecherche(BaseModel):
    """Axe juridique à explorer avec métadonnées de recherche"""
    
    id: str = Field(
        default_factory=lambda: f"axe_{uuid4().hex[:8]}"
    )
    
    axe: str = Field(..., description="Description de l'axe juridique")
    
    categorie: Literal[
        "recours_legal", "exception_procedure", "fond_faits", 
        "preuve", "procedure", "delai", "autre"
    ] = Field(default="autre")
    
    priorite: int = Field(default=1, ge=1, le=5)
    
    sources_potentielles: List[str] = Field(default_factory=list)
    
    mots_cles_recherche: List[str] = Field(default_factory=list)
    
    articles_cibles: List[str] = Field(default_factory=list)

class CodeArticle(BaseModel):
    """Article de loi avec contexte et application"""
    
    id: str = Field(
        default_factory=lambda: f"art_{uuid4().hex[:8]}"
    )
    
    code: str = Field(..., description="Code juridique (CESEDA, CP, etc.)")
    
    article_num: str = Field(..., description="Numéro de l'article")
    
    article_titre: str = Field(..., description="Titre de l'article")
    
    texte_complet: str = Field(..., description="Texte complet de l'article")
    
    url_legifrance: Optional[str] = Field(default=None)
    
    date_publication: Optional[str] = Field(default=None)
    
    applicable_oqtf: bool = Field(default=False)
    
    applicable_titre_sejour: bool = Field(default=False)
    
    applicable_naturalisation: bool = Field(default=False)
    
    tags: List[str] = Field(default_factory=list)

class PieceParsed(BaseModel):
    """Pièce justificative parsée"""
    
    id: str = Field(
        default_factory=lambda: f"piece_{uuid4().hex[:8]}"
    )
    
    titre: str = Field(..., description="Titre de la pièce")
    
    type_piece: Literal[
        "identite", "residence", "famille", "professionnel", 
        "medical", "financier", "administratif", "autre"
    ] = Field(...)
    
    resume: str = Field(..., description="Résumé du contenu")
    
    texte_complet: str = Field(..., description="Texte complet extrait")
    
    date: Optional[str] = Field(default=None)
    
    source_fichier: str = Field(..., description="Chemin du fichier source")
    
    hash_fichier: str = Field(..., description="Hash SHA256 du fichier")
    
    annexe_num: str = Field(..., description="Numéro d'annexe pour le dossier")
    
    is_virtual: bool = Field(default=False)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MatchPieceArticle(BaseModel):
    """Correspondance entre pièce et article juridique"""
    
    id: str = Field(
        default_factory=lambda: f"match_{uuid4().hex[:8]}"
    )
    
    piece_id: str = Field(...)
    article_id: str = Field(...)
    
    piece_titre: str = Field(...)
    article_num: str = Field(...)
    
    score_similarite: float = Field(..., ge=0.0, le=1.0)
    
    justification: str = Field(...)
    
    contexte_extrait: str = Field(...)
    
    source_url: Optional[str] = Field(default=None)

class RessourceWeb(BaseModel):
    """Ressource web extraite"""
    
    id: str = Field(
        default_factory=lambda: f"web_{uuid4().hex[:8]}"
    )
    
    url: str = Field(...)
    titre: str = Field(...)
    snippet: str = Field(...)
    
    source: str = Field(..., description="Domaine de la source")
    
    score_credibilite: float = Field(default=0.5, ge=0.0, le=1.0)
    
    score_pertinence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    date_extraction: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    
    tags: List[str] = Field(default_factory=list)

class DraftNarratif(BaseModel):
    """Brouillon narratif généré"""
    
    version: str = Field(..., description="Version du draft")
    texte_markdown: str = Field(..., description="Texte complet en markdown")
    
    tokens_llm: int = Field(..., ge=0)
    
    date_creation: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    
    sources_utilisees: List[str] = Field(default_factory=list)
    
    structure_sections: Dict[str, Any] = Field(default_factory=dict)
    
    qualite_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class PlanStrategique(BaseModel):
    """Plan stratégique du dossier"""
    
    objectifs: List[str] = Field(default_factory=list)
    
    arguments_principaux: List[str] = Field(default_factory=list)
    
    pieces_cles: List[str] = Field(default_factory=list)
    
    articles_cles: List[str] = Field(default_factory=list)
    
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    
    risques: List[str] = Field(default_factory=list)

class RequeteFinale(BaseModel):
    """Requête finale complète"""
    
    titre: str = Field(...)
    
    introduction: str = Field(...)
    
    faits: str = Field(...)
    
    moyens: str = Field(...)
    
    conclusions: str = Field(...)
    
    annexes: List[str] = Field(default_factory=list)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CaseStatus(BaseModel):
    """Statut complet d'un dossier"""
    
    dossier_id: str
    statut: str
    etape_actuelle: int
    progression: float
    
    meta_info: MetaInfo
    narration: Optional[NarrationJusticiable] = None
    axes: List[HypotheseRecherche] = Field(default_factory=list)
    pieces: List[PieceParsed] = Field(default_factory=list)
    matches: List[MatchPieceArticle] = Field(default_factory=list)
    web_corpus: List[RessourceWeb] = Field(default_factory=list)
    draft: Dict[str, DraftNarratif] = Field(default_factory=dict)
    requete_finale: Optional[RequeteFinale] = None
    
    logs: List[Dict[str, Any]] = Field(default_factory=list)
    
    created_at: str
    updated_at: str

# Modèles API
class CaseCreateRequest(BaseModel):
    """Requête de création de dossier"""
    
    titre: str = Field(..., min_length=3, max_length=200)
    type_contentieux: Optional[str] = None
    urgence_niveau: Literal["faible", "moyen", "eleve", "critique"] = "moyen"
    deadline: Optional[str] = None
    client_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class CaseUpdateRequest(BaseModel):
    """Requête de mise à jour de dossier"""
    
    titre: Optional[str] = None
    type_contentieux: Optional[str] = None
    urgence_niveau: Optional[str] = None
    deadline: Optional[str] = None
    notes: Optional[str] = None

class DocumentUploadRequest(BaseModel):
    """Requête d'upload de document"""
    
    case_id: str
    type_document: str
    description: Optional[str] = None
    
class PipelineStatus(BaseModel):
    """Statut du pipeline"""
    
    dossier_id: str
    etape_actuelle: int
    nom_etape: str
    progression: float
    statut: Literal["pending", "processing", "completed", "error"]
    details: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class WebSocketMessage(BaseModel):
    """Message WebSocket"""
    
    type: str
    data: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
