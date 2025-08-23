import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  Chip,
  Avatar,
  Button,
  IconButton,
  Alert,
  Divider,
  Tabs,
  Tab,
  Paper,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Snackbar,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Timeline as TimelineIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  Stop as StopIcon,
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAgentsFlows } from '../hooks/useAgentsFlows';

const AgentsFlows = () => {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });
  
  // Utilisation du hook API réel
  const {
    agentsStatus,
    flowLogs,
    metrics,
    isLoading,
    error,
    wsConnection,
    actions
  } = useAgentsFlows();

  // Actions sur les flows avec feedback utilisateur
  const handleFlowAction = async (action, flowId, actionName) => {
    try {
      await action(flowId);
      setSnackbar({
        open: true,
        message: `Flow ${actionName} avec succès`,
        severity: 'success'
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: `Erreur lors de ${actionName} du flow`,
        severity: 'error'
      });
    }
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const getStatusColor = (status) => {
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckIcon color="success" />;
      case 'running':
        return <PlayIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'pending':
        return <PauseIcon color="disabled" />;
      default:
        return <TimelineIcon />;
    }
  };

  // Affichage d'erreur si problème de connexion
  if (error && agentsStatus.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" sx={{ mb: 3 }}>
          🤖 Agents & Flows - DEFENSEUR-IA
        </Typography>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button 
          variant="contained" 
          onClick={actions.refreshAll}
          startIcon={<RefreshIcon />}
        >
          Réessayer
        </Button>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" sx={{ mb: 3 }}>
          🤖 Agents & Flows - DEFENSEUR-IA
        </Typography>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Chargement des données des agents...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* En-tête avec statut connexion */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h4">
            🤖 Agents & Flows - DEFENSEUR-IA
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              icon={wsConnection ? <WifiIcon /> : <WifiOffIcon />}
              label={wsConnection ? 'Temps réel' : 'Hors ligne'}
              color={wsConnection ? 'success' : 'default'}
              variant="outlined"
              size="small"
            />
            <IconButton onClick={actions.refreshAll} title="Actualiser">
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Monitoring détaillé des {agentsStatus.length} agents du pipeline IA et suivi des flows d'exécution
        </Typography>
        {metrics.totalFlows && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            📊 {metrics.totalFlows} flows total • {metrics.activeFlows} actifs • Taux de succès: {metrics.successRate}%
          </Typography>
        )}
      </Box>

      {/* Onglets principaux */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={selectedTab} onChange={handleTabChange} variant="fullWidth">
          <Tab label="Vue d'ensemble Agents" />
          <Tab label="Logs & Flows Détaillés" />
          <Tab label="Métriques & Performance" />
        </Tabs>
      </Paper>

      {/* Contenu selon l'onglet sélectionné */}
      {selectedTab === 0 && (
        <Grid container spacing={3}>
          {agentsStatus.map((agent) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
              <Card 
                variant="outlined" 
                sx={{ 
                  height: '100%',
                  cursor: 'pointer',
                  '&:hover': { boxShadow: 3 }
                }}
                onClick={() => setSelectedAgent(agent)}
              >
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ bgcolor: agent.color, width: 40, height: 40, mr: 2 }}>
                      {agent.emoji}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        Agent {agent.id}
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {agent.name}
                      </Typography>
                    </Box>
                    <Chip 
                      label="Actif" 
                      color="success" 
                      size="small" 
                      variant="outlined"
                    />
                  </Box>
                  
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                    {agent.description}
                  </Typography>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption">Dernière exécution:</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 500 }}>
                      {agent.executionTime}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption">Taux de succès:</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 500, color: 'success.main' }}>
                      {agent.successRate}%
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption">Total exécutions:</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 500 }}>
                      {agent.totalExecutions.toLocaleString()}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {selectedTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              Flows d'exécution en cours et historique
            </Typography>
            <Box>
              <IconButton>
                <RefreshIcon />
              </IconButton>
              <IconButton>
                <DownloadIcon />
              </IconButton>
            </Box>
          </Box>

          {flowLogs.map((flow) => (
            <Accordion key={flow.id} sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {flow.caseName}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Flow ID: {flow.id} • Démarré: {flow.startTime}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Chip 
                      label={flow.status === 'completed' ? 'Terminé' : 'En cours'} 
                      color={getStatusColor(flow.status)} 
                      size="small" 
                    />
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {flow.totalDuration}
                    </Typography>
                  </Box>
                </Box>
              </AccordionSummary>
              
              <AccordionDetails>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Agent</TableCell>
                        <TableCell>Statut</TableCell>
                        <TableCell>Durée</TableCell>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {flow.steps.map((step) => {
                        const agent = agentsStatus.find(a => a.id === step.agentId);
                        return (
                          <TableRow key={step.agentId}>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Avatar sx={{ bgcolor: agent?.color || 'primary.main', width: 24, height: 24, mr: 1, fontSize: '0.8rem' }}>
                                  {agent?.emoji || '🤖'}
                                </Avatar>
                                <Typography variant="body2">
                                  {agent?.name || `Agent ${step.agentId}`}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                {getStatusIcon(step.status)}
                                <Typography variant="body2" sx={{ ml: 1 }}>
                                  {step.status === 'completed' ? 'Terminé' : 
                                   step.status === 'running' ? 'En cours' : 
                                   step.status === 'pending' ? 'En attente' : step.status}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                {step.duration || '-'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                {step.timestamp || '-'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', gap: 1 }}>
                                <IconButton size="small" title="Voir détails">
                                  <ViewIcon fontSize="small" />
                                </IconButton>
                                {step.status === 'running' && (
                                  <IconButton 
                                    size="small" 
                                    title="Mettre en pause"
                                    onClick={() => handleFlowAction(actions.pauseFlow, flow.id, 'mis en pause')}
                                  >
                                    <PauseIcon fontSize="small" />
                                  </IconButton>
                                )}
                                {step.status === 'pending' && flow.status === 'running' && (
                                  <IconButton 
                                    size="small" 
                                    title="Annuler le flow"
                                    onClick={() => handleFlowAction(actions.cancelFlow, flow.id, 'annulé')}
                                  >
                                    <StopIcon fontSize="small" />
                                  </IconButton>
                                )}
                              </Box>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}

      {selectedTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info">
              <Typography variant="body2">
                📊 Métriques détaillées et analytics de performance des agents en cours de développement.
                Cette section affichera bientôt les graphiques de performance, les tendances d'exécution,
                et les analyses prédictives du pipeline DEFENSEUR-IA.
              </Typography>
            </Alert>
          </Grid>
        </Grid>
      )}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AgentsFlows;
