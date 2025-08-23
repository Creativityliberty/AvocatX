    @property
    def reference_complete(self) -> str:
        """Référence complète formatée pour citation"""
        return f"Article {self.numero} du {self.code_nom}"
    
    @property
    def est_en_vigueur(self) -> bool:
        """Vérifie si l'article est actuellement en vigueur"""
        if self.etat_juridique != "VIGUEUR":
            return False
        
        now = datetime.now().date()
        
        if self.date_debut_vigueur:
            debut = datetime.fromisoformat(self.date_debut_vigueur).date()
            if now < debut:
                return False
        
        if self.date_fin_vigueur:
            fin = datetime.fromisoformat(self.date_fin_vigueur).date()
            if now > fin:
                return False
        
        return True
```

### 4.2 PieceParsed - Pièce justificative traitée

```python
class EntiteAnonyme(BaseModel):
    """Entité détectée et anonymisée"""
    
    type_entite: Literal[
        "personne", "adresse", "telephone", "email", 
        "date", "montant", "organisation", "lieu"
    ]
    
    valeur_originale: str = Field(
        description="Valeur avant anonymisation (hashée)"
    )
    
    valeur_anonyme: str = Field(
        description="Valeur de remplacement (PERSON_X, etc.)"
    )
    
    position_debut: int = Field(ge=0)
    position_fin: int = Field(ge=0)
    confiance: float = Field(ge=0.0, le=1.0, default=0.8)

class PieceParsed(BaseModel):
    """Pièce justificative après parsing et anonymisation"""
    
    id_piece: str = Field(
        default_factory=lambda: f"piece_{uuid4().hex[:8]}",
        description="Identifiant unique de la pièce"
    )
    
    annexe_numero: str = Field(
        regex=r"^Annexe \d+$",
        description="Numéro d'annexe (Annexe 1, Annexe 2...)"
    )
    
    type_piece: Literal[
        "email", "pdf", "image", "docx", "texte", 
        "audio", "sms", "virtuel", "erreur"
    ] = Field(
        description="Type de document"
    )
    
    titre: str = Field(
        min_length=1,
        max_length=200,
        description="Titre ou objet du document"
    )
    
    date_document: Optional[str] = Field(
        default=None,
        description="Date du document (ISO 8601)"
    )
    
    date_evenement: Optional[str] = Field(
        default=None,
        description="Date de l'événement décrit"
    )
    
    texte_brut: str = Field(
        description="Texte extrait brut"
    )
    
    texte_anonymise: str = Field(
        description="Texte après anonymisation"
    )
    
    resume_automatique: str = Field(
        max_length=500,
        description="Résumé généré automatiquement"
    )
    
    entites_detectees: list[EntiteAnonyme] = Field(
        default_factory=list,
        description="Entités anonymisées"
    )
    
    mots_cles: list[str] = Field(
        default_factory=list,
        description="Mots-clés extraits"
    )
    
    meta_extraction: dict = Field(
        default_factory=dict,
        description="Métadonnées du processus d'extraction"
    )
    
    chemin_fichier_original: Optional[str] = Field(
        default=None,
        description="Chemin du fichier source"
    )
    
    hash_fichier: Optional[str] = Field(
        default=None,
        regex=r"^[a-f0-9]{64}$",
        description="Hash SHA-256 du fichier original"
    )
    
    taille_fichier: Optional[int] = Field(
        default=None,
        ge=0,
        description="Taille en octets"
    )
    
    is_virtual: bool = Field(
        default=False,
        description="Pièce virtuelle (déclaration)"
    )
    
    statut_virtuel: Optional[Literal[
        "placeholder", "definitif", "recherche_en_cours", "non_disponible"
    ]] = Field(
        default=None,
        description="Statut si pièce virtuelle"
    )
    
    axe_lie: Optional[str] = Field(
        default=None,
        description="ID de l'axe juridique associé"
    )
    
    utilite_juridique: Optional[str] = Field(
        default=None,
        max_length=300,
        description="Utilité identifiée pour le dossier"
    )
    
    qualite_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Score de qualité d'extraction"
    )

    @validator('annexe_numero')
    def validate_annexe_format(cls, v):
        if not v.startswith("Annexe "):
            raise ValueError("Le numéro d'annexe doit commencer par 'Annexe '")
        return v

    @property
    def est_exploitable(self) -> bool:
        """Détermine si la pièce est exploitable"""
        if self.type_piece == "erreur":
            return False
        if self.is_virtual and self.statut_virtuel == "placeholder":
            return False
        if len(self.texte_anonymise.strip()) < 50:
            return False
        return True
```

### 4.3 MatchPieceArticle - Correspondance pièce ↔ article

```python
class MatchPieceArticle(BaseModel):
    """Correspondance entre une pièce et un article de loi"""
    
    id_match: str = Field(
        default_factory=lambda: f"match_{uuid4().hex[:8]}",
        description="Identifiant unique du match"
    )
    
    piece_id: str = Field(
        description="ID de la pièce concernée"
    )
    
    piece_titre: str = Field(
        description="Titre de la pièce pour affichage"
    )
    
    article_cid: str = Field(
        description="CID Légifrance de l'article"
    )
    
    article_numero: str = Field(
        description="Numéro de l'article"
    )
    
    article_titre: str = Field(
        description="Titre de l'article"
    )
    
    similarite_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Score de similarité sémantique"
    )
    
    rang: int = Field(
        ge=1,
        description="Rang dans les résultats de matching"
    )
    
    justification: str = Field(
        max_length=500,
        description="Explication du lien identifié"
    )
    
    type_correspondance: Literal[
        "semantique", "keyword", "citation_directe", "contextuel"
    ] = Field(
        default="semantique",
        description="Type de correspondance détectée"
    )
    
    source_url: str = Field(
        description="URL de l'article sur Légifrance"
    )
    
    validation_humaine: Optional[bool] = Field(
        default=None,
        description="Validation manuelle (None=pas encore)"
    )
    
    commentaire_validation: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Commentaire de la validation"
    )
    
    date_match: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Date de création du match"
    )

    @property
    def niveau_pertinence(self) -> str:
        """Niveau de pertinence lisible"""
        if self.similarite_score >= 0.8:
            return "🟢 Très pertinent"
        elif self.similarite_score >= 0.6:
            return "🟡 Pertinent"
        elif self.similarite_score >= 0.4:
            return "🟠 Possiblement pertinent"
        else:
            return "🔴 Peu pertinent"
    
    @property
    def necessite_validation(self) -> bool:
        """Détermine si une validation humaine est recommandée"""
        return (
            self.validation_humaine is None and 
            self.similarite_score < 0.7 and 
            self.type_correspondance == "semantique"
        )
```

### 4.4 RessourceWeb - Source web complémentaire

```python
class RessourceWeb(BaseModel):
    """Ressource web trouvée par l'agent Web Scout"""
    
    id_ressource: str = Field(
        default_factory=lambda: f"web_{uuid4().hex[:8]}",
        description="Identifiant unique de la ressource"
    )
    
    url: str = Field(
        regex=r"^https?://.*",
        description="URL de la ressource"
    )
    
    titre: str = Field(
        max_length=300,
        description="Titre de la page"
    )
    
    domaine: str = Field(
        description="Domaine du site (ex: gisti.org)"
    )
    
    contenu_extrait: str = Field(
        max_length=5000,
        description="Contenu textuel extrait"
    )
    
    snippet_recherche: str = Field(
        default="",
        max_length=500,
        description="Extrait de la recherche"
    )
    
    axe_associe: str = Field(
        description="Axe juridique qui a généré cette recherche"
    )
    
    score_pertinence: float = Field(
        ge=0.0,
        le=1.0,
        description="Score de pertinence calculé"
    )
    
    type_source: Literal[
        "officiel", "association", "forum", "presse_juridique", 
        "jurisprudence", "doctrine", "autre"
    ] = Field(
        description="Classification de la source"
    )
    
    credibilite: Literal["haute", "moyenne", "faible", "inconnue"] = Field(
        default="moyenne",
        description="Évaluation de crédibilité"
    )
    
    date_extraction: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Date d'extraction du contenu"
    )
    
    date_publication: Optional[str] = Field(
        default=None,
        description="Date de publication estimée"
    )
    
    langues_detectees: list[str] = Field(
        default_factory=lambda: ["fr"],
        description="Langues détectées dans le contenu"
    )
    
    mots_cles_pertinents: list[str] = Field(
        default_factory=list,
        description="Mots-clés pertinents identifiés"
    )

    @property
    def affichage_credibilite(self) -> str:
        """Affichage de la crédibilité avec emoji"""
        if self.type_source == "officiel":
            return "🏛️ Source officielle"
        elif self.type_source == "association":
            return "🤝 Association reconnue"
        elif self.type_source == "presse_juridique":
            return "📰 Presse spécialisée"
        elif self.type_source == "forum":
            return "💬 Forum (à vérifier)"
        else:
            return "❓ Source à vérifier"
```

---

## 5. Modèles de sortie

### 5.1 DraftNarratif - Versions du récit

```python
class DraftNarratif(BaseModel):
    """Version d'un draft du récit juridique"""
    
    version: str = Field(
        regex=r"^v\d+$",
        description="Version du draft (v0, v1, v2...)"
    )
    
    texte_markdown: str = Field(
        min_length=100,
        description="Contenu en Markdown"
    )
    
    tokens_llm_utilises: int = Field(
        ge=0,
        description="Nombre de tokens LLM utilisés"
    )
    
    date_creation: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Date de création de cette version"
    )
    
    agent_createur: str = Field(
        description="Agent ayant créé cette version"
    )
    
    sources_utilisees: list[str] = Field(
        default_factory=list,
        description="Liste des sources citées"
    )
    
    structure_sections: dict = Field(
        default_factory=dict,
        description="Analyse de la structure du document"
    )
    
    statistiques_contenu: dict = Field(
        default_factory=dict,
        description="Statistiques du contenu (longueur, etc.)"
    )
    
    annotations: list[dict] = Field(
        default_factory=list,
        description="Annotations ou commentaires"
    )

    @property
    def longueur_lisible(self) -> str:
        """Longueur en format lisible"""
        chars = len(self.texte_markdown)
        if chars < 1000:
            return f"{chars} caractères"
        elif chars < 10000:
            return f"{chars/1000:.1f}k caractères"
        else:
            return f"{chars/1000:.0f}k caractères"
    
    @property
    def temps_lecture_estime(self) -> str:
        """Temps de lecture estimé"""
        mots = len(self.texte_markdown.split())
        minutes = max(1, mots // 200)  # 200 mots/min
        return f"{minutes} min"

class DraftCorrige(DraftNarratif):
    """Draft corrigé avec suggestions d'amélioration"""
    
    suggestions_appliquees: list[str] = Field(
        default_factory=list,
        description="Liste des corrections appliquées"
    )
    
    checks_qualite: dict = Field(
        default_factory=dict,
        description="Résultats des vérifications qualité"
    )
    
    score_qualite: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Score global de qualité"
    )
    
    nombre_corrections: int = Field(
        default=0,
        ge=0,
        description="Nombre de corrections appliquées"
    )

class DraftVersions(BaseModel):
    """Container pour toutes les versions de draft"""
    
    v0: Optional[DraftNarratif] = None
    v1: Optional[DraftCorrige] = None
    v2: Optional[DraftCorrige] = None
    
    version_courante: str = Field(
        default="v0",
        regex=r"^v\d+$",
        description="Version actuellement active"
    )
    
    historique_modifications: list[dict] = Field(
        default_factory=list,
        description="Historique des modifications"
    )

    def get_latest_draft(self) -> Optional[DraftNarratif]:
        """Retourne le draft le plus récent"""
        if self.version_courante == "v2" and self.v2:
            return self.v2
        elif self.version_courante == "v1" and self.v1:
            return self.v1
        elif self.version_courante == "v0" and self.v0:
            return self.v0
        return None
```

### 5.2 PlanStrategique - Stratégie juridique

```python
class AngleAttaque(BaseModel):
    """Angle d'attaque juridique avec scoring"""
    
    intitule: str = Field(
        max_length=200,
        description="Libellé de l'angle d'attaque"
    )
    
    description: str = Field(
        max_length=1000,
        description="Description détaillée"
    )
    
    fondement_juridique: list[str] = Field(
        description="Articles ou principes juridiques"
    )
    
    pieces_support: list[str] = Field(
        description="IDs des pièces supportant cet angle"
    )
    
    force_estimee: int = Field(
        ge=1,
        le=10,
        description="Force estimée de l'argument (1-10)"
    )
    
    probabilite_succes: float = Field(
        ge=0.0,
        le=1.0,
        description="Probabilité de succès estimée"
    )
    
    complexite: Literal["simple", "moyen", "complexe"] = Field(
        description="Complexité de mise en œuvre"
    )
    
    urgence: bool = Field(
        default=False,
        description="Nécessite une action urgente"
    )

class PlanStrategique(BaseModel):
    """Plan stratégique global du dossier"""
    
    angles_attaque: list[AngleAttaque] = Field(
        min_items=1,
        description="Liste des angles d'attaque identifiés"
    )
    
    angle_principal: str = Field(
        description="Angle principal recommandé"
    )
    
    angles_secondaires: list[str] = Field(
        default_factory=list,
        description="Angles de soutien"
    )
    
    risques_identifies: list[str] = Field(
        default_factory=list,
        description="Risques et faiblesses identifiés"
    )
    
    opportunites: list[str] = Field(
        default_factory=list,
        description="Opportunités à saisir"
    )
    
    precedents_utiles: list[dict] = Field(
        default_factory=list,
        description="Précédents jurisprudentiels pertinents"
    )
    
    delais_contraintes: dict = Field(
        default_factory=dict,
        description="Délais et contraintes procédurales"
    )
    
    recommandations_action: list[str] = Field(
        description="Actions recommandées par ordre de priorité"
    )
    
    score_global_dossier: float = Field(
        ge=0.0,
        le=10.0,
        description="Score global du dossier (0-10)"
    )
    
    confiance_evaluation: float = Field(
        ge=0.0,
        le=1.0,
        description="Confiance dans l'évaluation"
    )

    @property
    def niveau_dossier(self) -> str:
        """Évaluation qualitative du niveau du dossier"""
        if self.score_global_dossier >= 8:
            return "🟢 Très solide"
        elif self.score_global_dossier >= 6:
            return "🟡 Correct"
        elif self.score_global_dossier >= 4:
            return "🟠 Moyen"
        else:
            return "🔴 Difficile"
```

### 5.3 RequeteFinale - Document final

```python
class RequeteFinale(BaseModel):
    """Requête finale formatée pour le tribunal"""
    
    titre_complet: str = Field(
        max_length=300,
        description="Titre complet de la requête"
    )
    
    juridiction_destinataire: str = Field(
        description="Tribunal ou juridiction destinataire"
    )
    
    type_procedure: Literal[
        "recours_annulation", "recours_suspension", "referé", 
        "requete_principale", "requete_complementaire"
    ] = Field(
        description="Type de procédure"
    )
    
    corps_markdown: str = Field(
        min_length=500,
        description="Corps de la requête en Markdown"
    )
    
    corps_html: Optional[str] = Field(
        default=None,
        description="Version HTML pour preview"
    )
    
    annexes_references: list[str] = Field(
        description="Liste des annexes référencées"
    )
    
    articles_cites: list[str] = Field(
        description="Articles de loi cités"
    )
    
    jurisprudence_citee: list[dict] = Field(
        default_factory=list,
        description="Jurisprudence citée avec références"
    )
    
    demandes_formelles: list[str] = Field(
        min_items=1,
        description="Demandes formelles au tribunal"
    )
    
    delai_reponse_souhaite: Optional[str] = Field(
        default=None,
        description="Délai de réponse souhaité"
    )
    
    voies_recours: list[str] = Field(
        default_factory=list,
        description="Voies de recours mentionnées"
    )
    
    signature_bloc: str = Field(
        description="Bloc signature (avocat/justiciable)"
    )
    
    metadonnees_generation: dict = Field(
        default_factory=dict,
        description="Métadonnées de génération"
    )
    
    version_document: str = Field(
        default="1.0",
        description="Version du document"
    )
    
    date_generation: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Date de génération"
    )

    @property
    def nombre_pages_estime(self) -> int:
        """Estimation du nombre de pages"""
        # Approximation : 500 mots par page
        mots = len(self.corps_markdown.split())
        return max(1, mots // 500)
    
    @property
    def liste_annexes_formatee(self) -> str:
        """Liste des annexes formatée pour inclusion"""
        if not self.annexes_references:
            return "Aucune annexe"
        
        annexes_formatees = []
        for annexe in self.annexes_references:
            annexes_formatees.append(f"- {annexe}")
        
        return "\n".join(annexes_formatees)
```

---

## 6. Validation et contraintes

### 6.1 Validators personnalisés

```python
class ValidationHelpers:
    """Helpers de validation pour les modèles"""
    
    @staticmethod
    def validate_phone_number(v: str) -> str:
        """Valide un numéro de téléphone français"""
        import re
        pattern = r"^(?:\+33|0)[1-9](?:[0-9]{8})$"
        if not re.match(pattern, v.replace(" ", "").replace(".", "")):
            raise ValueError("Format de téléphone invalide")
        return v
    
    @staticmethod
    def validate_email(v: str) -> str:
        """Valide une adresse email"""
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Format d'email invalide")
        return v
    
    @staticmethod
    def validate_date_iso(v: str) -> str:
        """Valide une date ISO 8601"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("Format de date invalide (attendu: ISO 8601)")
    
    @staticmethod
    def sanitize_html(v: str) -> str:
        """Nettoie le HTML potentiellement dangereux"""
        import re
        # Supprime les scripts et autres éléments dangereux
        v = re.sub(r'<script.*?</script>', '', v, flags=re.DOTALL | re.IGNORECASE)
        v = re.sub(r'<.*?on\w+.*?>', '', v, flags=re.IGNORECASE)
        return v
```

### 6.2 Contraintes de cohérence

```python
class SharedStoreValidator:
    """Validateur de cohérence globale du SharedStore"""
    
    def validate_pieces_annexes_coherence(self, pieces: list[PieceParsed], draft: str) -> list[str]:
        """Vérifie que toutes les annexes citées existent"""
        import re
        
        # Extraction des références d'annexes dans le draft
        annexes_citees = set(re.findall(r'Annexe \d+', draft))
        
        # Annexes disponibles
        annexes_disponibles = set(piece.annexe_numero for piece in pieces)
        
        # Détection des incohérences
        erreurs = []
        
        annexes_manquantes = annexes_citees - annexes_disponibles
        if annexes_manquantes:
            erreurs.append(f"Annexes citées mais manquantes: {', '.join(annexes_manquantes)}")
        
        annexes_non_citees = annexes_disponibles - annexes_citees
        if annexes_non_citees:
            erreurs.append(f"Annexes disponibles mais non citées: {', '.join(annexes_non_citees)}")
        
        return erreurs
    
    def validate_axes_pieces_coverage(self, axes: list[HypotheseRecherche], pieces: list[PieceParsed]) -> list[str]:
        """Vérifie que chaque axe a au moins une pièce support"""
        erreurs = []
        
        for axe in axes:
            pieces_liees = [p for p in pieces if p.axe_lie == axe.id]
            if not pieces_liees and axe.priorite >= 4:
                erreurs.append(f"Axe prioritaire '{axe.intitule}' sans pièce support")
        
        return erreurs
```

---

## 7. Exemples JSON complets

### 7.1 SharedStore minimal (cas simple)

```json
{
  "meta": {
    "dossier_id": "CASE_20241201_a3f7b8c9",
    "version_schema": "2024.12.01",
    "langue_principale": "fr",
    "type_contentieux": "oqtf",
    "urgence_niveau": "eleve",
    "created_at": "2024-12-01T14:30:00Z",
    "updated_at": "2024-12-01T14:45:00Z",
    "tags": ["oqtf", "vie_familiale", "enfants"],
    "confidentialite": "confidentiel"
  },
  
  "narration": {
    "langue": "fr",
    "segments": [
      {
        "id": "seg_abc12345",
        "start_time": 0.0,
        "end_time": 15.2,
        "text": "Je m'appelle Marie Dubois, j'ai 34 ans et je vis en France depuis 8 ans.",
        "emotion": "neutral",
        "emotion_confidence": 0.7,
        "entities": ["PERSON_X"],
        "keywords": ["france", "séjour"],
        "importance_score": 0.8
      }
    ],
    "source_type": "text",
    "resume_automatique": "Femme de 34 ans en France depuis 8 ans"
  },
  
  "axes": [
    {
      "id": "axe_def67890",
      "intitule": "Violation du droit à la vie familiale (Article 8 CEDH)",
      "priorite": 5,
      "domaine_juridique": "droit_etrangers",
      "mots_cles_recherche": ["vie familiale", "article 8", "cedh", "oqtf"],
      "confidence_score": 0.9,
      "statut": "actif"
    }
  ],
  
  "pieces": [
    {
      "id_piece": "piece_12345678",
      "annexe_numero": "Annexe 1",
      "type_piece": "pdf",
      "titre": "Acte de mariage",
      "date_document": "2020-06-15",
      "texte_anonymise": "Acte de mariage entre PERSON_X et PERSON_Y...",
      "resume_automatique": "Acte de mariage prouvant l'union avec un citoyen français",
      "is_virtual": false,
      "qualite_score": 0.95
    }
  ],
  
  "draft": {
    "v0": {
      "version": "v0",
      "texte_markdown": "# Contexte\n\nMadame PERSON_X...",
      "tokens_llm_utilises": 1250,
      "agent_createur": "redacteur_narratif",
      "sources_utilisees": ["Annexe 1", "Article L.511-1"]
    },
    "version_courante": "v0"
  },
  
  "logs": {
    "history": [
      "2024-12-01T14:30:05Z ▶ START ecouteur",
      "2024-12-01T14:30:12Z ✅ END ecouteur",
      "2024-12-01T14:30:12Z ▶ START cadreur_juridique"
    ]
  }
}
```

### 7.2 Exemple de pièce complexe (email)

```json
{
  "id_piece": "piece_email001",
  "annexe_numero": "Annexe 3",
  "type_piece": "email",
  "titre": "Email: Notification OQTF - PERSON_X",
  "date_document": "2024-03-15T09:30:00Z",
  "date_evenement": "2024-03-15",
  "texte_brut": "=== MÉTADONNÉES EMAIL ===\nDe: prefecture@gouv.fr\nÀ: PERSON_X@email.com\nObjet: Notification OQTF...",
  "texte_anonymise": "=== MÉTADONNÉES EMAIL ===\nDe: ADMIN_X@gouv.fr\nÀ: PERSON_X@EMAIL_X\nObjet: Notification OQTF...",
  "resume_automatique": "Email de notification d'OQTF de la préfecture, mentionnant les délais de recours et l'obligation de quitter le territoire.",
  "entites_detectees": [
    {
      "type_entite": "email",
      "valeur_originale": "hash_abc123",
      "valeur_anonyme": "EMAIL_X# 05 · MODÈLES & SCHÉMAS DE DONNÉES

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