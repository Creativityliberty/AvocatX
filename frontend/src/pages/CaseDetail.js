/**
 * CaseDetail - Vue détaillée d'un dossier DEFENSEUR-IA
 */

import {
    Assessment as AssessmentIcon,
    CheckCircle as CheckIcon,
    Description as DocumentIcon,
    Download as DownloadIcon,
    ExpandMore as ExpandMoreIcon,
    FileDownload as FileDownloadIcon,
    Gavel as GavelIcon,
    Pause as PauseIcon,
    Person as PersonIcon,
    PlayArrow as PlayIcon,
    Refresh as RefreshIcon,
    Schedule as ScheduleIcon,
    Security as SecurityIcon,
    Timeline as TimelineIcon,
    Upload as UploadIcon
} from '@mui/icons-material';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    Grid,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Paper,
    Tab,
    Tabs,
    TextField,
    Typography
} from '@mui/material';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import LegalReferencePanel from '../components/LegalReferencePanel';
import LegifranceWidget from '../components/LegifranceWidget';
import { useCases, usePipeline } from '../hooks/useAPI';

const CaseDetail = () => {
  const { id } = useParams();
  const { cases, loading } = useCases();
  const { pipelineStatus, pipelineLogs, startPipeline, stopPipeline, uploadFiles } = usePipeline(id);

  const [activeTab, setActiveTab] = useState(0);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [legalValidationExpanded, setLegalValidationExpanded] = useState(true);

  // Données mockées étendues avec validation juridique
  const mockCaseData = {
    dossier_id: id || 'CASE-2024-001',
    client_name: 'Marie Dubois',
    case_type: 'OQTF',
    status: 'running',
    priority: 'high',
    created_at: '2024-01-27T10:00:00Z',
    updated_at: '2024-01-27T14:30:00Z',
    description: 'Recours contre OQTF - Situation familiale complexe',
    progress: 65,
    // Nouvelles données de validation juridique
    legalValidation: {
      score: 78,
      references: 12,
      issues: 2,
      lastValidated: '2024-01-27T14:00:00Z',
      details: {
        conformity: 82,
        completeness: 75,
        relevance: 85
      },
      suggestions: [
        'Ajouter une référence à l\'article L.511-1 du CESEDA',
        'Préciser les éléments de vie privée et familiale',
        'Renforcer l\'argumentation sur l\'intérêt supérieur de l\'enfant'
      ]
    },
    // Références juridiques associées
    legalReferences: [
      {
        id: 1,
        type: 'article',
        title: 'Article L.511-1 du CESEDA',
        content: 'L\'étranger ne peut être éloigné du territoire français...',
        source: 'Légifrance',
        url: 'https://legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335187',
        validated: true,
        relevanceScore: 95,
        addedBy: 'agent_01_cadreur_juridique',
        addedAt: '2024-01-27T12:30:00Z'
      },
      {
        id: 2,
        type: 'jurisprudence',
        title: 'CE, 10 avril 2019, n° 428218',
        content: 'Considérant que l\'administration doit tenir compte...',
        source: 'Judilibre',
        url: 'https://judilibre.fr/decision/428218',
        validated: true,
        relevanceScore: 88,
        addedBy: 'agent_04_recherche_web',
        addedAt: '2024-01-27T13:15:00Z'
      }
    ]
  };

  const mockPipelineStatus = pipelineStatus || {
    status: 'running',
    current_step: 6,
    progress: 65,
    started_at: '2024-01-27T14:30:00Z',
    estimated_completion: '2024-01-27T16:00:00Z',
  };

  const mockLogs = pipelineLogs.length > 0 ? pipelineLogs : [
    { timestamp: '2024-01-27T14:30:00Z', level: 'INFO', agent: 'agent_00_ecouteur', message: 'Transcription audio terminée' },
    { timestamp: '2024-01-27T14:32:15Z', level: 'INFO', agent: 'agent_01_cadreur_juridique', message: 'Axes juridiques identifiés: OQTF, droit au séjour' },
    { timestamp: '2024-01-27T14:35:20Z', level: 'INFO', agent: 'agent_02_parseur_preuves', message: '3 documents PDF traités avec OCR' },
    { timestamp: '2024-01-27T14:38:45Z', level: 'INFO', agent: 'agent_03_juriste_matching', message: 'Matching FAISS: 15 articles pertinents trouvés' },
    { timestamp: '2024-01-27T14:42:10Z', level: 'WARNING', agent: 'agent_04_recherche_web', message: 'Délai d\'attente API - retry en cours' },
    { timestamp: '2024-01-27T14:45:30Z', level: 'INFO', agent: 'agent_06_redacteur_narratif', message: 'Génération du récit en cours...' },
    // Nouveaux logs de validation juridique
    { timestamp: '2024-01-27T14:00:00Z', level: 'INFO', agent: 'legifrance_validator', message: 'Validation juridique lancée - 12 références à vérifier' },
    { timestamp: '2024-01-27T14:02:30Z', level: 'SUCCESS', agent: 'legifrance_validator', message: 'Score de validation: 78% - 2 problèmes détectés' },
  ];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleStartPipeline = async () => {
    try {
      await startPipeline();
    } catch (error) {
      console.error('Erreur démarrage pipeline:', error);
    }
  };

  const handleStopPipeline = async () => {
    try {
      await stopPipeline();
    } catch (error) {
      console.error('Erreur arrêt pipeline:', error);
    }
  };

  const handleFileUpload = async () => {
    if (selectedFiles.length > 0) {
      try {
        await uploadFiles(selectedFiles);
        setUploadDialog(false);
        setSelectedFiles([]);
      } catch (error) {
        console.error('Erreur upload:', error);
      }
    }
  };

  const handleValidateLegalReferences = async () => {
    // Simulation de validation des références juridiques
    console.log('Validation des références juridiques...');
  };

  const handleExportLegalReport = () => {
    // Simulation d'export du rapport juridique
    console.log('Export du rapport juridique...');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'warning';
      case 'error': return 'error';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getValidationColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getAgentName = (agentId) => {
    const agentNames = {
      'agent_00_ecouteur': 'Écouteur (STT)',
      'agent_01_cadreur_juridique': 'Cadreur Juridique',
      'agent_02_parseur_preuves': 'Parseur Preuves',
      'agent_03_juriste_matching': 'Juriste Matching',
      'agent_04_recherche_web': 'Recherche Web',
      'agent_06_redacteur_narratif': 'Rédacteur Narratif',
      'agent_07_relecteur_ia_1': 'Relecteur IA #1',
      'agent_08_agregateur_coherence': 'Agrégateur Cohérence',
      'agent_09_relecteur_ia_2': 'Relecteur IA #2',
      'agent_10_synthese_strategique': 'Synthèse Stratégique',
      'agent_11_avocat_ia': 'Avocat IA',
      'legifrance_validator': 'Validateur Légifrance',
    };
    return agentNames[agentId] || agentId;
  };

  const pipelineSteps = [
    { id: 0, name: 'Écouteur', description: 'Transcription audio' },
    { id: 1, name: 'Cadreur Juridique', description: 'Identification des axes légaux' },
    { id: 2, name: 'Parseur Preuves', description: 'OCR et extraction documents' },
    { id: 3, name: 'Juriste Matching', description: 'Matching sémantique FAISS' },
    { id: 4, name: 'Recherche Web', description: 'Recherche complémentaire' },
    { id: 6, name: 'Rédacteur Narratif', description: 'Génération du récit' },
    { id: 7, name: 'Relecteur IA #1', description: 'Première relecture' },
    { id: 8, name: 'Agrégateur', description: 'Analyse de cohérence' },
    { id: 9, name: 'Relecteur IA #2', description: 'Seconde relecture' },
    { id: 10, name: 'Synthèse Stratégique', description: 'Plan d\'action' },
    { id: 11, name: 'Avocat IA', description: 'Requête finale' },
  ];

  return (
    <Box>
      {/* En-tête du dossier avec validation juridique */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Typography variant="h4" sx={{ fontWeight: 600 }}>
                  {mockCaseData.client_name}
                </Typography>
                <Chip
                  label={mockCaseData.case_type}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={mockCaseData.status}
                  color={getStatusColor(mockCaseData.status)}
                />
              </Box>
              
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {mockCaseData.description}
              </Typography>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  ID: {mockCaseData.dossier_id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Créé le {new Date(mockCaseData.created_at).toLocaleDateString('fr-FR')}
                </Typography>
              </Box>
            </Grid>

            {/* Nouvelle section de validation juridique */}
            <Grid item xs={12} md={3}>
              <Card variant="outlined" sx={{ bgcolor: 'background.default' }}>
                <CardContent sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="h3" color={getValidationColor(mockCaseData.legalValidation.score)} sx={{ fontWeight: 600 }}>
                    {mockCaseData.legalValidation.score}%
                  </Typography>
                  <Typography variant="caption">Score de validation</Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<GavelIcon />}
                  onClick={handleValidateLegalReferences}
                  fullWidth
                >
                  Valider références
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<FileDownloadIcon />}
                  onClick={handleExportLegalReport}
                  fullWidth
                  size="small"
                >
                  Export rapport
                </Button>
              </Box>
            </Grid>
          </Grid>

          {/* Progression du pipeline */}
          <Box sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Progression du pipeline
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {mockPipelineStatus.progress}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={mockPipelineStatus.progress}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Colonne principale avec onglets */}
        <Grid item xs={12} md={8}>
          <Card>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={activeTab} onChange={handleTabChange}>
                <Tab label="Pipeline" icon={<TimelineIcon />} />
                <Tab label="Documents" icon={<DocumentIcon />} />
                <Tab label="Client" icon={<PersonIcon />} />
                <Tab label="Validation Juridique" icon={<GavelIcon />} />
              </Tabs>
            </Box>

            {/* Onglet Pipeline */}
            {activeTab === 0 && (
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6">Pipeline DEFENSEUR-IA</Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {mockPipelineStatus.status === 'running' ? (
                      <Button
                        variant="outlined"
                        startIcon={<PauseIcon />}
                        onClick={handleStopPipeline}
                        color="warning"
                      >
                        Arrêter
                      </Button>
                    ) : (
                      <Button
                        variant="contained"
                        startIcon={<PlayIcon />}
                        onClick={handleStartPipeline}
                      >
                        Démarrer
                      </Button>
                    )}
                    <Button
                      variant="outlined"
                      startIcon={<UploadIcon />}
                      onClick={() => setUploadDialog(true)}
                    >
                      Upload
                    </Button>
                  </Box>
                </Box>

                {/* Étapes du pipeline */}
                <List>
                  {pipelineSteps.map((step, index) => (
                    <ListItem key={step.id} sx={{ py: 1 }}>
                      <ListItemIcon>
                        {mockPipelineStatus.current_step > step.id ? (
                          <CheckIcon color="success" />
                        ) : mockPipelineStatus.current_step === step.id ? (
                          <ScheduleIcon color="warning" />
                        ) : (
                          <ScheduleIcon color="disabled" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={`${step.id}. ${step.name}`}
                        secondary={step.description}
                        primaryTypographyProps={{
                          color: mockPipelineStatus.current_step >= step.id ? 'textPrimary' : 'textSecondary'
                        }}
                      />
                    </ListItem>
                  ))}
                </List>

                {/* Logs du pipeline */}
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" sx={{ mb: 2 }}>Logs du pipeline</Typography>
                <Paper variant="outlined" sx={{ maxHeight: 300, overflow: 'auto', p: 2 }}>
                  {mockLogs.map((log, index) => (
                    <Box key={index} sx={{ mb: 1, fontFamily: 'monospace', fontSize: '0.875rem' }}>
                      <Typography component="span" color="text.secondary">
                        [{new Date(log.timestamp).toLocaleTimeString('fr-FR')}]
                      </Typography>
                      <Typography component="span" color={log.level === 'ERROR' ? 'error.main' : log.level === 'WARNING' ? 'warning.main' : 'success.main'} sx={{ mx: 1 }}>
                        {log.level}
                      </Typography>
                      <Typography component="span" color="primary.main">
                        {getAgentName(log.agent)}:
                      </Typography>
                      <Typography component="span" sx={{ ml: 1 }}>
                        {log.message}
                      </Typography>
                    </Box>
                  ))}
                </Paper>
              </CardContent>
            )}

            {/* Onglet Documents */}
            {activeTab === 1 && (
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Documents du dossier</Typography>
                <Alert severity="info">
                  Fonctionnalité de gestion des documents en cours de développement
                </Alert>
              </CardContent>
            )}

            {/* Onglet Client */}
            {activeTab === 2 && (
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Informations client</Typography>
                <Alert severity="info">
                  Fonctionnalité de gestion des clients en cours de développement
                </Alert>
              </CardContent>
            )}

            {/* Nouvel onglet Validation Juridique */}
            {activeTab === 3 && (
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Validation Juridique Détaillée</Typography>
                
                {/* Métriques de validation */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={4}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', py: 2 }}>
                        <Typography variant="h4" color="info.main">
                          {mockCaseData.legalValidation.details.conformity}%
                        </Typography>
                        <Typography variant="caption">Conformité</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={4}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', py: 2 }}>
                        <Typography variant="h4" color="warning.main">
                          {mockCaseData.legalValidation.details.completeness}%
                        </Typography>
                        <Typography variant="caption">Complétude</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={4}>
                    <Card variant="outlined">
                      <CardContent sx={{ textAlign: 'center', py: 2 }}>
                        <Typography variant="h4" color="success.main">
                          {mockCaseData.legalValidation.details.relevance}%
                        </Typography>
                        <Typography variant="caption">Pertinence</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Suggestions d'amélioration */}
                <Accordion expanded={legalValidationExpanded} onChange={() => setLegalValidationExpanded(!legalValidationExpanded)}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1">Suggestions d'amélioration ({mockCaseData.legalValidation.suggestions.length})</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List>
                      {mockCaseData.legalValidation.suggestions.map((suggestion, index) => (
                        <ListItem key={index}>
                          <ListItemIcon>
                            <GavelIcon color="warning" />
                          </ListItemIcon>
                          <ListItemText primary={suggestion} />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            )}
          </Card>
        </Grid>

        {/* Colonne droite avec widgets */}
        <Grid item xs={12} md={4}>
          {/* Widget API Légifrance */}
          <Box sx={{ mb: 3 }}>
            <LegifranceWidget 
              size="small" 
              showDetails={true} 
              showActions={false}
            />
          </Box>

          {/* Panel des références juridiques */}
          <Box sx={{ mb: 3 }}>
            <LegalReferencePanel 
              caseId={mockCaseData.dossier_id}
              references={mockCaseData.legalReferences}
              validationScore={mockCaseData.legalValidation.score}
              onValidate={handleValidateLegalReferences}
              showSuggestions={true}
            />
          </Box>

          {/* Actions rapides */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Actions rapides</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<SecurityIcon />}
                  onClick={() => window.open('/legal-search', '_blank')}
                  fullWidth
                >
                  Recherche juridique
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AssessmentIcon />}
                  onClick={() => window.open('/api-monitoring', '_blank')}
                  fullWidth
                >
                  Monitoring API
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={handleValidateLegalReferences}
                  fullWidth
                >
                  Revalider
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportLegalReport}
                  fullWidth
                >
                  Export complet
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Dialog d'upload */}
      <Dialog open={uploadDialog} onClose={() => setUploadDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload de documents</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Fonctionnalité d'upload en cours de développement
          </Alert>
          <TextField
            fullWidth
            type="file"
            inputProps={{ multiple: true }}
            onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialog(false)}>Annuler</Button>
          <Button onClick={handleFileUpload} variant="contained">
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CaseDetail;
