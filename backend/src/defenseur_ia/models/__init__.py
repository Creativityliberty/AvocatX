# Models package
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Modèles de base pour DEFENSEUR-IA
class NarrationJusticiable(BaseModel):
    """Modèle pour la narration du justiciable"""
    contenu: str
    timestamp: datetime
    segments: List["Segment"] = []
    meta_info: Optional["MetaInfo"] = None

class Segment(BaseModel):
    """Segment de narration"""
    id: str
    contenu: str
    debut: float
    fin: float
    confiance: float = 0.0
    type_segment: str = "audio"

class MetaInfo(BaseModel):
    """Métadonnées d'un segment"""
    duree_totale: float
    qualite_audio: str = "moyenne"
    langue_detectee: str = "fr"
    nb_segments: int = 0

class CaseData(BaseModel):
    """Données d'un dossier"""
    dossier_id: str
    nom_justiciable: str
    type_contentieux: str
    description: str
    status: str = "nouveau"
    created_at: datetime
    updated_at: datetime
    documents: List[Dict[str, Any]] = []
    pipeline_results: Dict[str, Any] = {}

class AgentResult(BaseModel):
    """Résultat d'un agent"""
    agent_id: str
    agent_name: str
    status: str
    result: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    errors: List[str] = []

class PipelineStatus(BaseModel):
    """Statut du pipeline"""
    dossier_id: str
    status: str
    current_step: int
    total_steps: int
    progress: float
    logs: List[str] = []
    agent_results: List[AgentResult] = []

class CaseStatus(str, Enum):
    """Statuts possibles d'un dossier"""
    NOUVEAU = "nouveau"
    EN_COURS = "en_cours"
    EN_ATTENTE = "en_attente"
    TERMINE = "termine"
    ERREUR = "erreur"

class CaseCreateRequest(BaseModel):
    """Requête de création de dossier"""
    nom_justiciable: str
    type_contentieux: str
    description: str
    urgence: str = "normale"

class CaseUpdateRequest(BaseModel):
    """Requête de mise à jour de dossier"""
    nom_justiciable: Optional[str] = None
    type_contentieux: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    urgence: Optional[str] = None

class DocumentUploadRequest(BaseModel):
    """Requête d'upload de document"""
    dossier_id: str
    filename: str
    content_type: str
    size: int

# Modèles additionnels pour les agents
class HypotheseRecherche(BaseModel):
    """Hypothèse de recherche juridique"""
    id: str
    titre: str
    description: str
    mots_cles: List[str] = []
    domaine_juridique: str
    confiance: float = 0.0

class CodeArticle(BaseModel):
    """Article de code juridique"""
    code: str
    article: str
    titre: str
    contenu: str
    url: Optional[str] = None
    pertinence: float = 0.0

class PieceParsed(BaseModel):
    """Pièce justificative parsée"""
    id: str
    filename: str
    type_document: str
    contenu_texte: str
    metadata: Dict[str, Any] = {}
    confiance_ocr: float = 0.0

class MatchPieceArticle(BaseModel):
    """Match entre pièce et article"""
    piece_id: str
    article_id: str
    score_similarite: float
    justification: str
    pertinence: str = "moyenne"

class RessourceWeb(BaseModel):
    """Ressource web trouvée"""
    url: str
    titre: str
    description: str
    contenu: str
    source: str
    pertinence: float = 0.0
    date_acces: datetime

class DraftNarratif(BaseModel):
    """Brouillon narratif"""
    id: str
    version: int
    contenu: str
    sections: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    statut: str = "brouillon"
    created_at: datetime
    updated_at: datetime

class RequeteFinale(BaseModel):
    """Requête finale générée"""
    id: str
    dossier_id: str
    contenu: str
    sections: List[Dict[str, Any]] = []
    references_juridiques: List[CodeArticle] = []
    pieces_jointes: List[str] = []
    statut: str = "finale"
    created_at: datetime
    qualite_score: float = 0.0

# Mise à jour des références forward
NarrationJusticiable.model_rebuild()
Segment.model_rebuild()
MetaInfo.model_rebuild()
HypotheseRecherche.model_rebuild()
CodeArticle.model_rebuild()
PieceParsed.model_rebuild()
MatchPieceArticle.model_rebuild()
RessourceWeb.model_rebuild()
DraftNarratif.model_rebuild()
RequeteFinale.model_rebuild()
