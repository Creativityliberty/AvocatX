import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  Chip,
  Avatar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Checkbox,
  LinearProgress,
  Divider,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Folder as FolderIcon,
  Description as DocumentIcon,
  AudioFile as AudioIcon,
  Image as ImageIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  ArrowForward as ArrowIcon,
} from '@mui/icons-material';

const FlowPlayground = () => {
  
  // États principaux
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [agentResults, setAgentResults] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [showDocumentSelector, setShowDocumentSelector] = useState(false);
  const [showResultEditor, setShowResultEditor] = useState(false);
  const [editingResult, setEditingResult] = useState('');
  const [editingAgentId, setEditingAgentId] = useState(null);
  const [flowState, setFlowState] = useState('idle'); // idle, running, paused, completed
  const [showAgentConfig, setShowAgentConfig] = useState(false);
  const [agentConfigs, setAgentConfigs] = useState({});

  // SharedStore pour les données partagées entre agents
  const [sharedStore, setSharedStore] = useState({});

  // Profils d'exécution
  const executionProfiles = {
    fast: {
      description: "Traitement rapide, qualité standard",
      skip_agents: ['05'], // Pas de Web Scout
      llm_model: "gpt-4o-mini",
      max_tokens: 2000,
      parallel_enabled: true
    },
    standard: {
      description: "Équilibre qualité/performance",
      skip_agents: [],
      llm_model: "gpt-4o",
      max_tokens: 4000,
      parallel_enabled: true
    },
    thorough: {
      description: "Qualité maximale, tous les agents",
      skip_agents: [],
      llm_model: "gpt-4o",
      max_tokens: 8000,
      parallel_enabled: false,
      double_validation: true
    }
  };

  const [selectedProfile, setSelectedProfile] = useState('standard');

  // Fonctions de validation du flow
  const validateAgentOutput = (agentId, result) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent || !agent.validation_rules) return { isValid: true, errors: [], warnings: [] };
    
    const rules = agent.validation_rules;
    const errors = [];
    const warnings = [];
    
    // Vérification des sorties requises
    if (rules.required_outputs) {
      for (const output of rules.required_outputs) {
        if (!result[output]) {
          errors.push(`Sortie manquante: ${output}`);
        }
      }
    }
    
    // Validations spécifiques par agent
    if (agentId === '00' && rules.min_segments && result.segments?.length < rules.min_segments) {
      errors.push('Narration trop courte');
    }
    
    if (agentId === '01' && rules.min_axes && result.axes?.length < rules.min_axes) {
      errors.push('Aucun axe juridique identifié');
    }
    
    if (agentId === '03' && rules.min_pieces && result.pieces?.length < rules.min_pieces) {
      errors.push('Aucune pièce traitée');
    }
    
    if (agentId === '04' && rules.min_matches && result.matches?.length < rules.min_matches) {
      errors.push('Aucune correspondance trouvée');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  };
  
  const checkPrerequisites = (agentId) => {
    const agent = agents.find(a => a.id === agentId);
    if (!agent?.prerequisites) return true;
    
    return agent.prerequisites.every(req => sharedStore[req]);
  };
  
  const updateSharedStore = (key, value) => {
    setSharedStore(prev => ({ ...prev, [key]: value }));
  };
  
  // Initialiser les configurations par défaut des agents
  const initializeAgentConfigs = () => {
    const configs = {};
    agents.forEach(agent => {
      if (agent.parameters) {
        configs[agent.id] = {};
        Object.entries(agent.parameters).forEach(([key, param]) => {
          configs[agent.id][key] = param.default;
        });
      }
    });
    setAgentConfigs(configs);
  };
  
  // Initialiser au montage du composant
  useEffect(() => {
    initializeAgentConfigs();
  }, []);

  // Configuration des 12 agents du pipeline DEFENSEUR-IA
  const agents = [
    {
      id: '00',
      name: 'Écouteur',
      emoji: '🎤',
      description: 'Speech-to-Text et analyse émotionnelle',
      color: 'success.light',
      inputTypes: ['audio', 'text'],
      outputFormat: 'transcription',
      capabilities: [
        'Transcription audio en français',
        'Détection des émotions (anxiété, stress, colère)',
        'Analyse de la prosodie et du débit',
        'Identification des mots-clés juridiques',
        'Support formats: MP3, WAV, M4A'
      ],
      parameters: {
        language: { type: 'select', options: ['fr-FR', 'en-US', 'ar-AR'], default: 'fr-FR', label: 'Langue' },
        emotion_analysis: { type: 'boolean', default: true, label: 'Analyse émotionnelle' },
        confidence_threshold: { type: 'slider', min: 0.5, max: 1.0, default: 0.8, label: 'Seuil de confiance' },
        output_format: { type: 'select', options: ['text', 'json', 'srt'], default: 'json', label: 'Format de sortie' }
      }
    },
    {
      id: '01',
      name: 'Cadreur Juridique',
      emoji: '⚖️',
      description: 'Analyse juridique via Légifrance',
      color: 'primary.light',
      inputTypes: ['transcription'],
      outputFormat: 'legal_analysis',
      capabilities: [
        'Identification du cadre juridique applicable (CESEDA, Code civil)',
        'Recherche dans Légifrance et Judilibre',
        'Analyse des articles de loi pertinents',
        'Détection des procédures (OQTF, naturalisation, regroupement familial)',
        'Évaluation de l\'urgence juridique'
      ],
      parameters: {
        legal_domain: { type: 'select', options: ['OQTF', 'Naturalisation', 'Regroupement familial', 'Titre de séjour', 'Asile'], default: 'OQTF', label: 'Domaine juridique' },
        search_depth: { type: 'select', options: ['basic', 'advanced', 'exhaustive'], default: 'advanced', label: 'Profondeur de recherche' },
        include_jurisprudence: { type: 'boolean', default: true, label: 'Inclure jurisprudence' },
        max_articles: { type: 'number', min: 5, max: 50, default: 20, label: 'Nombre max d\'articles' }
      }
    },
    {
      id: '02',
      name: 'Parseur Preuves',
      emoji: '📄',
      description: 'OCR et extraction de documents',
      color: 'info.light',
      inputTypes: ['pdf', 'image', 'document'],
      outputFormat: 'extracted_data',
      capabilities: [
        'OCR multilingue (français, arabe, anglais)',
        'Extraction de données structurées (dates, noms, numéros)',
        'Reconnaissance de documents officiels (passeports, CNI, diplômes)',
        'Validation de l\'authenticité des documents',
        'Support formats: PDF, JPG, PNG, TIFF'
      ],
      parameters: {
        ocr_language: { type: 'select', options: ['fra', 'ara', 'eng', 'auto'], default: 'auto', label: 'Langue OCR' },
        document_type: { type: 'select', options: ['auto', 'passport', 'id_card', 'diploma', 'contract'], default: 'auto', label: 'Type de document' },
        extraction_mode: { type: 'select', options: ['fast', 'accurate', 'comprehensive'], default: 'accurate', label: 'Mode d\'extraction' },
        confidence_threshold: { type: 'slider', min: 0.6, max: 1.0, default: 0.85, label: 'Seuil de confiance OCR' }
      },
      prerequisites: ['narration'],
      validation_rules: {
        required_outputs: ['pieces'],
        min_pieces: 1,
        max_virtual_ratio: 0.5
      }
    },
    {
      id: '03',
      name: 'Juriste Matching',
      emoji: '⚖️',
      description: 'Matching par embeddings et similarité',
      color: 'secondary.light',
      inputTypes: ['pieces', 'legal_corpus'],
      outputFormat: 'matches',
      capabilities: [
        'Recherche de correspondances par embeddings',
        'Analyse de similarité sémantique',
        'Scoring de pertinence juridique',
        'Identification de précédents similaires',
        'Recommandations stratégiques'
      ],
      parameters: {
        similarity_threshold: { type: 'slider', min: 0.3, max: 0.9, default: 0.6, label: 'Seuil de similarité' },
        max_matches: { type: 'number', min: 5, max: 50, default: 15, label: 'Nombre max de correspondances' },
        include_precedents: { type: 'boolean', default: true, label: 'Inclure précédents' },
        scoring_method: { type: 'select', options: ['semantic', 'keyword', 'hybrid'], default: 'hybrid', label: 'Méthode de scoring' }
      },
      prerequisites: ['pieces', 'legal_corpus'],
      validation_rules: {
        required_outputs: ['matches'],
        min_matches: 1,
        min_similarity: 0.4
      }
    },
    {
      id: '04',
      name: 'Web Scout',
      emoji: '🌐',
      description: 'Recherche web et jurisprudentielle',
      color: 'warning.light',
      inputTypes: ['axes'],
      outputFormat: 'web_corpus',
      capabilities: [
        'Recherche jurisprudentielle approfondie',
        'Scraping de sources spécialisées (GISTI, La Cimade)',
        'Analyse de précédents favorables',
        'Veille juridique automatisée',
        'Extraction de citations pertinentes'
      ],
      parameters: {
        search_depth: { type: 'select', options: ['basic', 'standard', 'exhaustive'], default: 'standard', label: 'Profondeur de recherche' },
        include_associations: { type: 'boolean', default: true, label: 'Inclure associations' },
        max_sources: { type: 'number', min: 5, max: 30, default: 15, label: 'Nombre max de sources' },
        time_range: { type: 'select', options: ['1year', '3years', '5years', 'all'], default: '3years', label: 'Période de recherche' }
      },
      prerequisites: ['axes'],
      validation_rules: {
        required_outputs: ['web_corpus'],
        min_sources: 1
      },
      optional: true
    },
    {
      id: '06',
      name: 'Rédacteur Narratif',
      emoji: '✍️',
      description: 'Génération narrative GPT-4',
      color: 'error.light',
      inputTypes: ['narration', 'axes', 'pieces', 'matches', 'web_corpus'],
      outputFormat: 'draft_v0',
      capabilities: [
        'Rédaction narrative structurée',
        'Intégration de toutes les données précédentes',
        'Style juridique professionnel',
        'Argumentation cohérente',
        'Respect des standards de requête'
      ],
      parameters: {
        writing_style: { type: 'select', options: ['formal', 'standard', 'accessible'], default: 'standard', label: 'Style de rédaction' },
        max_length: { type: 'number', min: 1000, max: 10000, default: 5000, label: 'Longueur max (mots)' },
        include_citations: { type: 'boolean', default: true, label: 'Inclure citations' },
        structure_type: { type: 'select', options: ['chronological', 'thematic', 'legal'], default: 'legal', label: 'Structure' }
      },
      prerequisites: ['narration', 'axes', 'pieces', 'matches'],
      validation_rules: {
        required_outputs: ['draft_v0'],
        min_length: 500
      }
    },
    {
      id: '07',
      name: 'Relecteur IA #1',
      emoji: '🔍',
      description: 'Première relecture et correction',
      color: 'success.light',
      inputTypes: ['draft_v0'],
      outputFormat: 'draft_v1',
      capabilities: [
        'Correction orthographique et grammaticale',
        'Vérification cohérence argumentaire',
        'Amélioration style et clarté',
        'Validation références juridiques',
        'Optimisation structure'
      ],
      parameters: {
        correction_level: { type: 'select', options: ['light', 'standard', 'thorough'], default: 'standard', label: 'Niveau de correction' },
        preserve_style: { type: 'boolean', default: true, label: 'Préserver le style' },
        check_references: { type: 'boolean', default: true, label: 'Vérifier références' }
      },
      prerequisites: ['draft_v0'],
      validation_rules: {
        required_outputs: ['draft_v1']
      }
    },
    {
      id: '07b',
      name: 'Agrégateur Cohérence',
      emoji: '🧩',
      description: 'Vérification cohérence globale',
      color: 'info.light',
      inputTypes: ['draft_v1', 'axes'],
      outputFormat: 'draft_v1b',
      capabilities: [
        'Analyse de couverture des axes',
        'Détection de pièces manquantes',
        'Vérification cohérence globale',
        'Suggestions d\'amélioration',
        'Validation complétude dossier'
      ],
      parameters: {
        coverage_threshold: { type: 'slider', min: 0.5, max: 1.0, default: 0.8, label: 'Seuil de couverture' },
        suggest_missing: { type: 'boolean', default: true, label: 'Suggérer pièces manquantes' },
        strict_validation: { type: 'boolean', default: false, label: 'Validation stricte' }
      },
      prerequisites: ['draft_v1', 'axes'],
      validation_rules: {
        required_outputs: ['draft_v1b'],
        min_coverage: 0.6
      }
    },
    {
      id: '08',
      name: 'Relecteur IA #2',
      emoji: '🔍',
      description: 'Seconde relecture approfondie',
      color: 'secondary.light',
      inputTypes: ['draft_v1b'],
      outputFormat: 'draft_v2',
      capabilities: [
        'Relecture approfondie finale',
        'Optimisation argumentaire',
        'Peaufinage style juridique',
        'Validation finale cohérence',
        'Préparation version finale'
      ],
      parameters: {
        focus_areas: { type: 'select', options: ['all', 'legal', 'style', 'structure'], default: 'all', label: 'Zones de focus' },
        final_polish: { type: 'boolean', default: true, label: 'Peaufinage final' }
      },
      prerequisites: ['draft_v1b'],
      validation_rules: {
        required_outputs: ['draft_v2']
      }
    },
    {
      id: '09',
      name: 'Synthèse Stratégique',
      emoji: '💡',
      description: 'Analyse stratégique et recommandations',
      color: 'warning.light',
      inputTypes: ['draft_v2'],
      outputFormat: 'strategic_plan',
      capabilities: [
        'Analyse stratégique du dossier',
        'Évaluation chances de succès',
        'Recommandations procédurales',
        'Identification points faibles',
        'Plan d\'action juridique'
      ],
      parameters: {
        risk_assessment: { type: 'boolean', default: true, label: 'Évaluation des risques' },
        success_probability: { type: 'boolean', default: true, label: 'Probabilité de succès' },
        alternative_strategies: { type: 'boolean', default: true, label: 'Stratégies alternatives' }
      },
      prerequisites: ['draft_v2'],
      validation_rules: {
        required_outputs: ['strategic_plan']
      }
    },
    {
      id: '10',
      name: 'Avocat IA',
      emoji: '⚖️',
      description: 'Finalisation juridique experte',
      color: 'primary.light',
      inputTypes: ['strategic_plan', 'draft_v2'],
      outputFormat: 'final_request',
      capabilities: [
        'Finalisation juridique experte',
        'Validation conformité procédurale',
        'Optimisation argumentation',
        'Préparation requête finale',
        'Contrôle qualité juridique'
      ],
      parameters: {
        expertise_level: { type: 'select', options: ['standard', 'expert', 'senior'], default: 'expert', label: 'Niveau d\'expertise' },
        include_precedents: { type: 'boolean', default: true, label: 'Inclure précédents' },
        formal_validation: { type: 'boolean', default: true, label: 'Validation formelle' }
      },
      prerequisites: ['strategic_plan', 'draft_v2'],
      validation_rules: {
        required_outputs: ['final_request'],
        min_quality_score: 0.8
      }
    },
    {
      id: '11',
      name: 'Export Final',
      emoji: '💾',
      description: 'Génération PDF et archivage',
      color: 'success.light',
      inputTypes: ['final_request', 'pieces'],
      outputFormat: 'pdf_zip',
      capabilities: [
        'Génération PDF professionnel',
        'Compilation dossier complet',
        'Archivage sécurisé',
        'Export multi-formats',
        'Métadonnées complètes'
      ],
      parameters: {
        pdf_quality: { type: 'select', options: ['standard', 'high', 'print'], default: 'high', label: 'Qualité PDF' },
        include_annexes: { type: 'boolean', default: true, label: 'Inclure annexes' },
        watermark: { type: 'boolean', default: false, label: 'Filigrane' },
        compression: { type: 'select', options: ['none', 'standard', 'high'], default: 'standard', label: 'Compression' }
      },
      prerequisites: ['final_request', 'pieces'],
      validation_rules: {
        required_outputs: ['pdf_zip'],
        min_file_size: 1024
      }
    }
  ];

  // Données mock pour les dossiers et documents
  const mockCases = [
    {
      id: 'dossier_17591da5',
      name: 'Ahmed Benali - OQTF',
      client: 'Ahmed Benali',
      type: 'OQTF',
      status: 'En cours',
      documents: [
        { id: 'doc1', name: 'Passeport_Ahmed.pdf', type: 'pdf', size: '2.3 MB' },
        { id: 'doc2', name: 'Temoignage_Audio.mp3', type: 'audio', size: '15.7 MB' },
        { id: 'doc3', name: 'Certificat_Medical.pdf', type: 'pdf', size: '1.1 MB' },
        { id: 'doc4', name: 'Lettre_Motivation.docx', type: 'document', size: '456 KB' }
      ]
    },
    {
      id: 'dossier_32fdac91',
      name: 'Marie Dubois - Titre de séjour',
      client: 'Marie Dubois',
      type: 'Titre de séjour',
      status: 'Nouveau',
      documents: [
        { id: 'doc5', name: 'CNI_Marie.pdf', type: 'pdf', size: '1.8 MB' },
        { id: 'doc6', name: 'Contrat_Travail.pdf', type: 'pdf', size: '2.1 MB' },
        { id: 'doc7', name: 'Justificatif_Domicile.pdf', type: 'pdf', size: '890 KB' }
      ]
    }
  ];

  // Charger l'état sauvegardé au démarrage
  useEffect(() => {
    const savedState = localStorage.getItem('flowPlaygroundState');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setCurrentStep(parsed.currentStep || 0);
        setSelectedCase(parsed.selectedCase || null);
        setSelectedDocuments(parsed.selectedDocuments || []);
        setAgentResults(parsed.agentResults || {});
        setFlowState(parsed.flowState || 'idle');
      } catch (err) {
        console.error('Erreur lors du chargement de l\'état sauvegardé:', err);
      }
    }
  }, []);

  // Sauvegarder l'état à chaque changement
  useEffect(() => {
    const saveState = () => {
      const state = {
        currentStep,
        selectedCase,
        selectedDocuments,
        agentResults,
        flowState,
        timestamp: new Date().toISOString()
      };
      localStorage.setItem('flowPlaygroundState', JSON.stringify(state));
    };
    saveState();
  }, [currentStep, selectedCase, selectedDocuments, agentResults, flowState]);

  // Démarrer le traitement d'un agent
  const processAgent = async (agentIndex) => {
    setIsProcessing(true);
    setFlowState('running');
    
    try {
      // Simulation du traitement de l'agent
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const agent = agents[agentIndex];
      const mockResult = generateMockResult(agent);
      
      setAgentResults(prev => ({
        ...prev,
        [agent.id]: mockResult
      }));
      
      setFlowState('paused');
    } catch (error) {
      console.error('Erreur lors du traitement de l\'agent:', error);
      setFlowState('idle');
    } finally {
      setIsProcessing(false);
    }
  };

  // Générer un résultat mock selon le type d'agent
  const generateMockResult = (agent) => {
    const mockResults = {
      '00': {
        transcription: "Je m'appelle Ahmed Benali, je suis arrivé en France en 2019 avec un visa étudiant. J'ai terminé mes études en informatique et j'ai trouvé un emploi dans une entreprise française. Cependant, j'ai reçu une OQTF et je ne comprends pas pourquoi...",
        emotion: "Anxiété, inquiétude",
        confidence: 0.95,
        duration: "3m 42s",
        input_documents: ["Temoignage_Audio.mp3"],
        output_documents: ["transcription.txt", "analyse_emotionnelle.json"]
      },
      '01': {
        legal_framework: "Code de l'entrée et du séjour des étrangers (CESEDA)",
        applicable_articles: ["L. 511-1", "L. 512-1", "L. 512-2"],
        procedure_type: "OQTF avec délai de départ volontaire",
        recourse_possible: true,
        urgency_level: "Élevé",
        input_documents: ["transcription.txt"],
        output_documents: ["analyse_juridique.pdf", "articles_applicables.json"]
      },
      '02': {
        extracted_documents: [
          { type: "Passeport", validity: "Valide", expiry: "2027-03-15" },
          { type: "Diplôme", level: "Master Informatique", institution: "Université Paris-Saclay" },
          { type: "Contrat de travail", employer: "TechCorp France", duration: "CDI" }
        ],
        ocr_confidence: 0.98,
        missing_documents: ["Justificatif de domicile récent"],
        input_documents: ["Passeport_Ahmed.pdf", "Certificat_Medical.pdf"],
        output_documents: ["donnees_extraites.json", "documents_analyses.pdf"]
      },
      '03': {
        matches_found: 15,
        similarity_scores: [0.94, 0.89, 0.87],
        best_match: "Cas similaire OQTF étudiant → salarié",
        recommendations: ["Recours gracieux", "Demande de régularisation"],
        input_documents: ["analyse_juridique.pdf", "donnees_extraites.json"],
        output_documents: ["correspondances.json", "recommandations.pdf"]
      },
      '04': {
        web_sources: 8,
        jurisprudence_found: ["CE, 10 avril 2019, n° 421456", "CAA Paris, 15 mars 2020"],
        legal_precedents: "Favorable dans 73% des cas similaires",
        input_documents: ["analyse_juridique.pdf"],
        output_documents: ["recherche_web.json", "jurisprudence.pdf"]
      }
    };
    
    const baseResult = mockResults[agent.id] || {
      status: "Traitement terminé",
      result: `Résultat généré par ${agent.name}`,
      confidence: Math.random() * 0.3 + 0.7,
      processing_time: `${Math.floor(Math.random() * 10) + 1}s`,
      input_documents: [],
      output_documents: [`resultat_${agent.id}.pdf`]
    };
    
    return {
      ...baseResult,
      timestamp: new Date().toISOString(),
      agent_id: agent.id,
      agent_name: agent.name
    };
  };

  // Continuer vers l'agent suivant
  const continueToNextAgent = () => {
    if (currentStep < agents.length - 1) {
      setCurrentStep(currentStep + 1);
      setFlowState('idle');
    } else {
      setFlowState('completed');
    }
  };

  // Modifier le résultat d'un agent
  const editResult = (agentId) => {
    const result = agentResults[agentId];
    setEditingResult(JSON.stringify(result, null, 2));
    setShowResultEditor(true);
  };

  // Sauvegarder les modifications
  const saveEditedResult = () => {
    try {
      const agent = agents[currentStep];
      const parsedResult = JSON.parse(editingResult);
      setAgentResults(prev => ({
        ...prev,
        [agent.id]: parsedResult
      }));
      setShowResultEditor(false);
    } catch (error) {
      alert('Format JSON invalide');
    }
  };

  // Obtenir l'icône selon le type de document
  const getDocumentIcon = (type) => {
    switch (type) {
      case 'audio': return <AudioIcon />;
      case 'pdf': case 'document': return <DocumentIcon />;
      case 'image': return <ImageIcon />;
      default: return <DocumentIcon />;
    }
  };

  const currentAgent = agents[currentStep];
  const currentResult = agentResults[currentAgent?.id];

  return (
    <Box sx={{ p: 3 }}>
      {/* En-tête */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4">
            🎮 Flow Playground - DEFENSEUR-IA
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Chip 
              label={`Étape ${currentStep + 1}/${agents.length}`}
              color="primary"
              variant="outlined"
            />
            <Chip 
              label={flowState === 'idle' ? 'En attente' : 
                     flowState === 'running' ? 'En cours' :
                     flowState === 'paused' ? 'En pause' : 'Terminé'}
              color={flowState === 'completed' ? 'success' : 'default'}
            />
          </Box>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Interface procédurale pour contrôler chaque étape du pipeline IA
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Colonne gauche - Sélection et contrôles */}
        <Grid item xs={12} md={4}>
          {/* Sélection du dossier */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <FolderIcon sx={{ mr: 1 }} />
                Dossier sélectionné
              </Typography>
              
              {selectedCase ? (
                <Box>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    <strong>{selectedCase.name}</strong><br />
                    Type: {selectedCase.type} • Statut: {selectedCase.status}
                  </Alert>
                  <Button 
                    variant="outlined" 
                    onClick={() => setShowDocumentSelector(true)}
                    fullWidth
                  >
                    Sélectionner documents ({selectedDocuments.length})
                  </Button>
                </Box>
              ) : (
                <Button 
                  variant="contained" 
                  onClick={() => setShowDocumentSelector(true)}
                  fullWidth
                  startIcon={<FolderIcon />}
                >
                  Choisir un dossier
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Agent actuel */}
          {currentAgent && (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: currentAgent.color, mr: 2 }}>
                    {currentAgent.emoji}
                  </Avatar>
                  <Box>
                    <Typography variant="h6">
                      {currentAgent.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {currentAgent.description}
                    </Typography>
                  </Box>
                </Box>

                <CardActions sx={{ p: 0, pt: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => processAgent(currentStep)}
                    disabled={isProcessing || !selectedCase || selectedDocuments.length === 0}
                    startIcon={isProcessing ? <LinearProgress /> : <PlayIcon />}
                    fullWidth
                  >
                    {isProcessing ? 'Traitement...' : 'Lancer l\'agent'}
                  </Button>
                </CardActions>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Colonne droite - Résultats et progression */}
        <Grid item xs={12} md={8}>
          {/* Stepper de progression */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Progression du pipeline
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={(currentStep / agents.length) * 100} 
              sx={{ mb: 2 }}
            />
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {agents.map((agent, index) => (
                <Chip
                  key={agent.id}
                  label={`${agent.emoji} ${agent.name}`}
                  color={
                    index < currentStep ? 'success' :
                    index === currentStep ? 'primary' : 'default'
                  }
                  variant={index === currentStep ? 'filled' : 'outlined'}
                  size="small"
                />
              ))}
            </Box>
          </Paper>

          {/* Résultat de l'agent actuel */}
          {currentResult && (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">
                    📋 Résultat - {currentAgent.name}
                  </Typography>
                  <Box>
                    <IconButton onClick={() => editResult(currentAgent.id)} title="Modifier">
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => processAgent(currentStep)} title="Relancer">
                      <RefreshIcon />
                    </IconButton>
                  </Box>
                </Box>

                <Paper sx={{ p: 2, bgcolor: 'grey.50', mb: 2 }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                    {JSON.stringify(currentResult, null, 2)}
                  </pre>
                </Paper>

                <CardActions sx={{ p: 0 }}>
                  <Button
                    variant="contained"
                    onClick={continueToNextAgent}
                    disabled={flowState !== 'paused'}
                    startIcon={<CheckIcon />}
                    color="success"
                  >
                    Valider et continuer
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => editResult(currentAgent.id)}
                    startIcon={<EditIcon />}
                  >
                    Modifier
                  </Button>
                </CardActions>
              </CardContent>
            </Card>
          )}

          {/* Message si flow terminé */}
          {flowState === 'completed' && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="h6">🎉 Pipeline terminé avec succès !</Typography>
              <Typography>
                Tous les agents ont été exécutés. Vous pouvez maintenant télécharger les documents générés.
              </Typography>
            </Alert>
          )}
        </Grid>
      </Grid>

      {/* Section Historique des Agents */}
      {Object.keys(agentResults).length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
            📜 Historique des Agents
            <Chip 
              label={`${Object.keys(agentResults).length} agents exécutés`}
              color="primary"
              variant="outlined"
              size="small"
              sx={{ ml: 2 }}
            />
          </Typography>

          {agents.slice(0, currentStep + (flowState === 'completed' ? 1 : 0)).map((agent, index) => {
            const result = agentResults[agent.id];
            if (!result) return null;

            return (
              <Accordion key={agent.id} sx={{ mb: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Avatar sx={{ bgcolor: agent.color, mr: 2, width: 32, height: 32 }}>
                      {agent.emoji}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6">
                        Agent {agent.id} - {agent.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {agent.description}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip 
                        icon={<CheckIcon />}
                        label="Terminé"
                        color="success"
                        size="small"
                      />
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {result.processing_time}
                      </Typography>
                    </Box>
                  </Box>
                </AccordionSummary>
                
                <AccordionDetails>
                  <Grid container spacing={3}>
                    {/* Input Documents */}
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                        <Typography variant="subtitle1" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                          <ArrowIcon sx={{ mr: 1, transform: 'rotate(180deg)' }} />
                          Documents d'entrée
                        </Typography>
                        {result.input_documents && result.input_documents.length > 0 ? (
                          <List dense>
                            {result.input_documents.map((doc, idx) => (
                              <ListItem key={idx} sx={{ py: 0.5 }}>
                                <ListItemIcon sx={{ minWidth: 32 }}>
                                  {getDocumentIcon('pdf')}
                                </ListItemIcon>
                                <ListItemText 
                                  primary={doc}
                                  primaryTypographyProps={{ variant: 'body2' }}
                                />
                                <Tooltip title="Voir le contenu">
                                  <IconButton size="small">
                                    <ViewIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </ListItem>
                            ))}
                          </List>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Aucun document d'entrée
                          </Typography>
                        )}
                      </Paper>
                    </Grid>

                    {/* Output Documents */}
                    <Grid item xs={12} md={6}>
                      <Paper sx={{ p: 2, bgcolor: 'success.50' }}>
                        <Typography variant="subtitle1" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                          <ArrowIcon sx={{ mr: 1 }} />
                          Documents générés
                        </Typography>
                        {result.output_documents && result.output_documents.length > 0 ? (
                          <List dense>
                            {result.output_documents.map((doc, idx) => (
                              <ListItem key={idx} sx={{ py: 0.5 }}>
                                <ListItemIcon sx={{ minWidth: 32 }}>
                                  {getDocumentIcon('pdf')}
                                </ListItemIcon>
                                <ListItemText 
                                  primary={doc}
                                  primaryTypographyProps={{ variant: 'body2' }}
                                />
                                <Box sx={{ display: 'flex', gap: 0.5 }}>
                                  <Tooltip title="Voir le contenu">
                                    <IconButton size="small">
                                      <ViewIcon fontSize="small" />
                                    </IconButton>
                                  </Tooltip>
                                  <Tooltip title="Télécharger">
                                    <IconButton size="small">
                                      <DownloadIcon fontSize="small" />
                                    </IconButton>
                                  </Tooltip>
                                </Box>
                              </ListItem>
                            ))}
                          </List>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            Aucun document généré
                          </Typography>
                        )}
                      </Paper>
                    </Grid>

                    {/* Résultat détaillé */}
                    <Grid item xs={12}>
                      <Paper sx={{ p: 2 }}>
                        <Typography variant="subtitle1" sx={{ mb: 2 }}>
                          📋 Résultat détaillé
                        </Typography>
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          <pre style={{ 
                            margin: 0, 
                            whiteSpace: 'pre-wrap', 
                            fontFamily: 'inherit',
                            fontSize: '0.875rem'
                          }}>
                            {JSON.stringify(result, null, 2)}
                          </pre>
                        </Paper>
                        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<EditIcon />}
                            onClick={() => editResult(agent.id)}
                          >
                            Modifier
                          </Button>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<RefreshIcon />}
                            onClick={() => processAgent(index)}
                          >
                            Relancer
                          </Button>
                        </Box>
                      </Paper>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </Box>
      )}

      {/* Dossier Final */}
      {flowState === 'completed' && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ mb: 3 }}>
            📁 Dossier Final Généré
          </Typography>
          
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Documents du dossier "{selectedCase?.name}"
              </Typography>
              
              <Grid container spacing={2}>
                {Object.values(agentResults).flatMap(result => 
                  result.output_documents || []
                ).map((doc, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ mr: 2 }}>
                        {getDocumentIcon('pdf')}
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {doc}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Généré automatiquement
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="Voir">
                          <IconButton size="small">
                            <ViewIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Télécharger">
                          <IconButton size="small">
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
              
              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  size="large"
                >
                  Télécharger tout (ZIP)
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ViewIcon />}
                >
                  Aperçu complet
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Dialog de sélection des documents */}
      <Dialog 
        open={showDocumentSelector} 
        onClose={() => setShowDocumentSelector(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Sélectionner un dossier et ses documents</DialogTitle>
        <DialogContent>
          {/* Sélection du dossier */}
          <Typography variant="h6" sx={{ mb: 2 }}>Dossiers disponibles</Typography>
          <List>
            {mockCases.map((caseItem) => (
              <ListItemButton
                key={caseItem.id}
                selected={selectedCase?.id === caseItem.id}
                onClick={() => setSelectedCase(caseItem)}
              >
                <ListItemIcon>
                  <FolderIcon />
                </ListItemIcon>
                <ListItemText
                  primary={caseItem.name}
                  secondary={`${caseItem.type} • ${caseItem.documents.length} documents`}
                />
              </ListItemButton>
            ))}
          </List>

          {/* Sélection des documents */}
          {selectedCase && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" sx={{ mb: 2 }}>
                Documents du dossier "{selectedCase.name}"
              </Typography>
              <List>
                {selectedCase.documents.map((doc) => (
                  <ListItem key={doc.id}>
                    <ListItemIcon>
                      <Checkbox
                        checked={selectedDocuments.some(d => d.id === doc.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedDocuments([...selectedDocuments, doc]);
                          } else {
                            setSelectedDocuments(selectedDocuments.filter(d => d.id !== doc.id));
                          }
                        }}
                      />
                    </ListItemIcon>
                    <ListItemIcon>
                      {getDocumentIcon(doc.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={doc.name}
                      secondary={`${doc.type.toUpperCase()} • ${doc.size}`}
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDocumentSelector(false)}>
            Annuler
          </Button>
          <Button 
            onClick={() => setShowDocumentSelector(false)}
            variant="contained"
            disabled={!selectedCase || selectedDocuments.length === 0}
          >
            Confirmer ({selectedDocuments.length} documents)
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog d'édition des résultats */}
      <Dialog 
        open={showResultEditor} 
        onClose={() => setShowResultEditor(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Modifier le résultat - {currentAgent?.name}</DialogTitle>
        <DialogContent>
          <TextField
            multiline
            rows={15}
            fullWidth
            value={editingResult}
            onChange={(e) => setEditingResult(e.target.value)}
            variant="outlined"
            sx={{ mt: 1 }}
            placeholder="Format JSON..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowResultEditor(false)}>
            Annuler
          </Button>
          <Button 
            onClick={saveEditedResult}
            variant="contained"
            startIcon={<SaveIcon />}
          >
            Sauvegarder
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de configuration des agents */}
      <Dialog 
        open={showAgentConfig} 
        onClose={() => setShowAgentConfig(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h5">
              🔧 Configuration des Agents DEFENSEUR-IA
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip 
                label={`${agents.length} agents`}
                color="primary"
                variant="outlined"
              />
              <Chip 
                label={selectedProfile.toUpperCase()}
                color="secondary"
              />
            </Box>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {/* Sélection du profil d'exécution */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              🎯 Profil d'Exécution
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(executionProfiles).map(([key, profile]) => (
                <Grid item xs={12} md={4} key={key}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      border: selectedProfile === key ? 2 : 1,
                      borderColor: selectedProfile === key ? 'primary.main' : 'grey.300'
                    }}
                    onClick={() => setSelectedProfile(key)}
                  >
                    <CardContent>
                      <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
                        {key}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {profile.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip size="small" label={profile.llm_model} />
                        <Chip size="small" label={`${profile.max_tokens} tokens`} />
                        {profile.parallel_enabled && <Chip size="small" label="Parallèle" color="success" />}
                        {profile.skip_agents?.length > 0 && (
                          <Chip size="small" label={`Skip ${profile.skip_agents.length}`} color="warning" />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Configuration des agents */}
          <Typography variant="h6" sx={{ mb: 3 }}>
            ⚙️ Configuration des Agents
          </Typography>
          
          {agents.map((agent, index) => {
            const isSkipped = executionProfiles[selectedProfile].skip_agents?.includes(agent.id);
            
            return (
              <Accordion key={agent.id} sx={{ mb: 2, opacity: isSkipped ? 0.6 : 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Avatar sx={{ bgcolor: agent.color, mr: 2, width: 32, height: 32 }}>
                      {agent.emoji}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6">
                        Agent {agent.id} - {agent.name}
                        {isSkipped && <Chip label="IGNORÉ" size="small" color="warning" sx={{ ml: 1 }} />}
                        {agent.optional && <Chip label="OPTIONNEL" size="small" color="info" sx={{ ml: 1 }} />}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {agent.description}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {agent.prerequisites && (
                        <Tooltip title={`Prérequis: ${agent.prerequisites.join(', ')}`}>
                          <Chip size="small" label={`${agent.prerequisites.length} prérequis`} />
                        </Tooltip>
                      )}
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {agent.inputTypes?.join(' → ')} → {agent.outputFormat}
                      </Typography>
                    </Box>
                  </Box>
                </AccordionSummary>
                
                <AccordionDetails>
                  <Grid container spacing={3}>
                    {/* Capacités */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                        💪 Capacités
                      </Typography>
                      {agent.capabilities ? (
                        <List dense>
                          {agent.capabilities.map((capability, idx) => (
                            <ListItem key={idx} sx={{ py: 0.5 }}>
                              <ListItemIcon sx={{ minWidth: 24 }}>
                                <CheckIcon fontSize="small" color="success" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={capability}
                                primaryTypographyProps={{ variant: 'body2' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Capacités par défaut
                        </Typography>
                      )}
                    </Grid>

                    {/* Paramètres */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
                        ⚙️ Paramètres
                      </Typography>
                      {agent.parameters ? (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                          {Object.entries(agent.parameters).map(([key, param]) => {
                            const currentValue = agentConfigs[agent.id]?.[key] ?? param.default;
                            
                            return (
                              <Box key={key}>
                                <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                                  {param.label}
                                </Typography>
                                
                                {param.type === 'select' && (
                                  <TextField
                                    select
                                    size="small"
                                    fullWidth
                                    value={currentValue}
                                    onChange={(e) => {
                                      setAgentConfigs(prev => ({
                                        ...prev,
                                        [agent.id]: {
                                          ...prev[agent.id],
                                          [key]: e.target.value
                                        }
                                      }));
                                    }}
                                  >
                                    {param.options.map(option => (
                                      <option key={option} value={option}>
                                        {option}
                                      </option>
                                    ))}
                                  </TextField>
                                )}
                                
                                {param.type === 'boolean' && (
                                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                    <Checkbox
                                      checked={currentValue}
                                      onChange={(e) => {
                                        setAgentConfigs(prev => ({
                                          ...prev,
                                          [agent.id]: {
                                            ...prev[agent.id],
                                            [key]: e.target.checked
                                          }
                                        }));
                                      }}
                                    />
                                    <Typography variant="body2">
                                      {currentValue ? 'Activé' : 'Désactivé'}
                                    </Typography>
                                  </Box>
                                )}
                                
                                {param.type === 'number' && (
                                  <TextField
                                    type="number"
                                    size="small"
                                    fullWidth
                                    value={currentValue}
                                    inputProps={{ min: param.min, max: param.max }}
                                    onChange={(e) => {
                                      setAgentConfigs(prev => ({
                                        ...prev,
                                        [agent.id]: {
                                          ...prev[agent.id],
                                          [key]: parseInt(e.target.value)
                                        }
                                      }));
                                    }}
                                  />
                                )}
                                
                                {param.type === 'slider' && (
                                  <Box sx={{ px: 1 }}>
                                    <input
                                      type="range"
                                      min={param.min}
                                      max={param.max}
                                      step={0.1}
                                      value={currentValue}
                                      onChange={(e) => {
                                        setAgentConfigs(prev => ({
                                          ...prev,
                                          [agent.id]: {
                                            ...prev[agent.id],
                                            [key]: parseFloat(e.target.value)
                                          }
                                        }));
                                      }}
                                      style={{ width: '100%' }}
                                    />
                                    <Typography variant="caption" sx={{ display: 'block', textAlign: 'center' }}>
                                      {currentValue}
                                    </Typography>
                                  </Box>
                                )}
                              </Box>
                            );
                          })}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Aucun paramètre configurable
                        </Typography>
                      )}
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setShowAgentConfig(false)}>
            Annuler
          </Button>
          <Button 
            onClick={() => {
              setShowAgentConfig(false);
              // Sauvegarder la configuration
              console.log('Configuration sauvegardée:', { selectedProfile, agentConfigs });
            }}
            variant="contained"
            startIcon={<SaveIcon />}
          >
            Sauvegarder Configuration
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FlowPlayground;
