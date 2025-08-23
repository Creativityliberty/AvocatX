/**
 * Dashboard - Tableau de bord principal DEFENSEUR-IA
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Button,
  IconButton,
  Alert,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  People as PeopleIcon,
  Description as DocumentIcon,
  Timeline as TimelineIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Folder as FolderIcon,
  Pause as PauseIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import NewCaseDialog from '../components/NewCaseDialog';
import { useCases, useStats } from '../hooks/useAPI';
import { useMongoDBAtlas, useMongoDBCases } from '../hooks/useMongoDBAtlas';
import { useBackendStatus } from '../hooks/useBackendStatus';
import { useNotifications } from '../hooks/useNotifications';

const Dashboard = () => {
  const navigate = useNavigate();
  
  // Hooks pour données locales (existants)
  const { cases: localCases, loading: casesLoading, createCase } = useCases();
  const { stats: localStats } = useStats();
  const { isConnected, isChecking } = useBackendStatus();
  const { showSuccess, showError, showInfo } = useNotifications();
  
  // Hooks MongoDB Atlas (données cloud prioritaires)
  const { stats: mongoStats } = useMongoDBAtlas();
  const { cases: mongoCases } = useMongoDBCases();
  
  // Utiliser MongoDB Atlas en priorité, fallback vers données locales
  // S'assurer que cases est toujours un tableau
  const cases = Array.isArray(mongoCases) && mongoCases.length > 0 
    ? mongoCases 
    : Array.isArray(localCases) 
      ? localCases 
      : [];
  const stats = mongoStats?.stats || localStats || {};

  const [recentActivity, setRecentActivity] = useState([]);
  const [openNewCaseDialog, setOpenNewCaseDialog] = useState(false);

  const [isCreatingCase, setIsCreatingCase] = useState(false);

  // Filtrer les dossiers récents (derniers 5)
  const recentCases = Array.isArray(cases) ? cases.slice(0, 5) : [];

  // Statistiques mockées si pas encore disponibles
  const dashboardStats = stats.overview || {
    totalCases: Array.isArray(cases) ? cases.length : 0,
    activePipelines: 3,
    completedToday: 2,
    pendingReview: 1,
    totalClients: 15,
    documentsGenerated: 45,
  };

  const handleCreateNewCase = () => {
    setOpenNewCaseDialog(true);
  };

  const handleCloseNewCaseDialog = () => {
    setOpenNewCaseDialog(false);
  };



  const handleSubmitNewCase = async (formData) => {
    if (!formData.nom_justiciable.trim()) {
      showError('Veuillez saisir le nom du justiciable');
      return;
    }

    setIsCreatingCase(true);
    showInfo('Création du dossier en cours...');
    
    try {
      const newCase = await createCase({
        nom_justiciable: formData.nom_justiciable,
        type_contentieux: formData.type_contentieux,
        description: formData.description,
        urgence: formData.urgence,
        status: 'draft',
        created_at: new Date().toISOString(),
      });
      
      showSuccess(`Dossier créé avec succès pour ${formData.nom_justiciable}`);
      handleCloseNewCaseDialog();
      
      // Navigation vers le nouveau dossier
      setTimeout(() => {
        navigate(`/cases/${newCase.dossier_id}`);
      }, 1000);
      
    } catch (error) {
      console.error('Erreur création dossier:', error);
      showError('Erreur lors de la création du dossier');
    } finally {
      setIsCreatingCase(false);
    }
  };

  // Mock des activités récentes
  useEffect(() => {
    setRecentActivity([
      {
        id: 1,
        type: 'pipeline_complete',
        message: 'Pipeline terminé pour DOSSIER_20240127_142530',
        time: '2 minutes',
        status: 'success'
      },
      {
        id: 2,
        type: 'document_generated',
        message: 'Requête finale générée pour Marie Dubois',
        time: '15 minutes',
        status: 'success'
      },
      {
        id: 3,
        type: 'pipeline_error',
        message: 'Erreur OCR sur document_scan_001.pdf',
        time: '1 heure',
        status: 'error'
      },
      {
        id: 4,
        type: 'client_added',
        message: 'Nouveau client ajouté: Ahmed Benali',
        time: '2 heures',
        status: 'info'
      },
    ]);
  }, []);

  const getActivityIcon = (type, status) => {
    switch (type) {
      case 'pipeline_complete':
        return <CheckIcon color="success" />;
      case 'pipeline_error':
        return <ErrorIcon color="error" />;
      case 'document_generated':
        return <DocumentIcon color="primary" />;
      case 'client_added':
        return <PeopleIcon color="info" />;
      default:
        return <TimelineIcon />;
    }
  };

  const getPipelineStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'warning';
      case 'error':
        return 'error';
      case 'pending':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* En-tête */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
          Tableau de bord
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Vue d'ensemble de vos dossiers et du pipeline DEFENSEUR-IA
        </Typography>
      </Box>

      {/* Alerte de connexion */}
      {!isConnected && !isChecking && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Connexion au backend interrompue. Certaines fonctionnalités peuvent être limitées.
        </Alert>
      )}
      {isConnected && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Backend DEFENSEUR-IA connecté et opérationnel.
        </Alert>
      )}

      {/* Section Agents IA Pipeline */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
            🤖 Pipeline DEFENSEUR-IA - Agents Actifs
          </Typography>
          
          <Grid container spacing={2}>
            {/* Agent 00 - Écouteur */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'success.light', width: 32, height: 32, mr: 1 }}>
                      🎤
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 00 - Écouteur
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Speech-to-Text
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 01 - Cadreur Juridique */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'primary.light', width: 32, height: 32, mr: 1 }}>
                      ⚖️
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 01 - Cadreur
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Analyse juridique Légifrance
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 02 - Parseur Preuves */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'info.light', width: 32, height: 32, mr: 1 }}>
                      📄
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 02 - Parseur
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    OCR & Extraction documents
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 03 - Juriste Matching */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'secondary.light', width: 32, height: 32, mr: 1 }}>
                      🔍
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 03 - Matching
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Embeddings & Similarité
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 04 - Recherche Web */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'warning.light', width: 32, height: 32, mr: 1 }}>
                      🌐
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 04 - Web
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Recherche jurisprudence
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 06 - Rédacteur Narratif */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'success.light', width: 32, height: 32, mr: 1 }}>
                      ✍️
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 06 - Rédacteur
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Génération narrative GPT-4
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 07 - Relecteur IA #1 */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'error.light', width: 32, height: 32, mr: 1 }}>
                      🔍
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 07 - QA #1
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Contrôle qualité technique
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 08 - Agrégateur Cohérence */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'purple', width: 32, height: 32, mr: 1 }}>
                      🔗
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 08 - Agrégateur
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Cohérence & Synthèse
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 09 - Relecteur IA #2 */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'orange', width: 32, height: 32, mr: 1 }}>
                      🔄
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 09 - QA #2
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Révision divergente
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 10 - Synthèse Stratégique */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'indigo', width: 32, height: 32, mr: 1 }}>
                      📊
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 10 - Synthèse
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Stratégie & Analyse
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent 11 - Avocat IA */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'primary.dark', width: 32, height: 32, mr: 1 }}>
                      👨‍💼
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent 11 - Avocat IA
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Requête finale & Validation
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>

            {/* Agent Enhanced - Recherche Web Avancée */}
            <Grid item xs={12} sm={6} md={4} lg={3}>
              <Card variant="outlined" sx={{ height: '100%' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar sx={{ bgcolor: 'teal', width: 32, height: 32, mr: 1 }}>
                      🚀
                    </Avatar>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      Agent Enhanced
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    Recherche Web Avancée
                  </Typography>
                  <Chip label="Actif" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              12/12 agents actifs • Pipeline opérationnel 🚀
            </Typography>
            <Button 
              variant="outlined" 
              size="small" 
              onClick={() => navigate('/agents-flows')}
            >
              Voir Logs & Flows
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Statistiques principales */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'primary.main' }}>
                    {dashboardStats.totalCases}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Dossiers totaux
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.light' }}>
                  <FolderIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                    {dashboardStats.activePipelines}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pipelines actifs
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.light' }}>
                  <TimelineIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                    {dashboardStats.completedToday}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Terminés aujourd'hui
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.light' }}>
                  <CheckIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                    {dashboardStats.totalClients}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Clients actifs
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.light' }}>
                  <PeopleIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Actions rapides */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Actions rapides
              </Typography>
              
              <Button
                variant="contained"
                fullWidth
                startIcon={<AddIcon />}
                onClick={handleCreateNewCase}
                sx={{ mb: 2 }}
              >
                Nouveau dossier
              </Button>

              <Button
                variant="outlined"
                fullWidth
                startIcon={<PeopleIcon />}
                onClick={() => navigate('/clients')}
                sx={{ mb: 2 }}
              >
                Ajouter un client
              </Button>

              <Button
                variant="outlined"
                fullWidth
                startIcon={<TimelineIcon />}
                onClick={() => navigate('/pipeline')}
              >
                Monitoring pipeline
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Dossiers récents */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Dossiers récents
                </Typography>
                <IconButton size="small" onClick={() => navigate('/cases')}>
                  <RefreshIcon />
                </IconButton>
              </Box>

              {casesLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : recentCases.length > 0 ? (
                <List dense>
                  {recentCases.map((caseItem, index) => (
                    <React.Fragment key={caseItem.dossier_id || index}>
                      <ListItem
                        button
                        onClick={() => navigate(`/cases/${caseItem.dossier_id}`)}
                        sx={{ px: 0 }}
                      >
                        <ListItemIcon>
                          <FolderIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={caseItem.client_name || `Dossier ${index + 1}`}
                          secondary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                              <Chip
                                label={caseItem.case_type || 'OQTF'}
                                size="small"
                                color="primary"
                                variant="outlined"
                              />
                              <Chip
                                label={caseItem.status || 'draft'}
                                size="small"
                                color={getPipelineStatusColor(caseItem.status)}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < recentCases.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                  Aucun dossier récent
                </Typography>
              )}

              <Button
                variant="text"
                fullWidth
                onClick={() => navigate('/cases')}
                sx={{ mt: 2 }}
              >
                Voir tous les dossiers
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Activité récente */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Activité récente
              </Typography>

              <List dense>
                {recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        {getActivityIcon(activity.type, activity.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.message}
                        secondary={`il y a ${activity.time}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                    {index < recentActivity.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Pipelines en cours */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Pipelines en cours
          </Typography>

          {/* Mock des pipelines actifs */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2">
                    DOSSIER_20240127_142530
                  </Typography>
                  <Chip label="Étape 6/12" size="small" color="warning" />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Rédaction narrative en cours...
                </Typography>
                <LinearProgress variant="determinate" value={50} sx={{ mb: 1 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    50% terminé
                  </Typography>
                  <IconButton size="small">
                    <PauseIcon />
                  </IconButton>
                </Box>
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="subtitle2">
                    DOSSIER_20240127_135420
                  </Typography>
                  <Chip label="Étape 3/12" size="small" color="info" />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Parsing des preuves...
                </Typography>
                <LinearProgress variant="determinate" value={25} sx={{ mb: 1 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    25% terminé
                  </Typography>
                  <IconButton size="small">
                    <PauseIcon />
                  </IconButton>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Nouveau Dialog pour création de dossier */}
      <NewCaseDialog
        open={openNewCaseDialog}
        onClose={handleCloseNewCaseDialog}
        onSubmit={handleSubmitNewCase}
        loading={isCreatingCase}
      />
    </Box>
  );
};

export default Dashboard;
