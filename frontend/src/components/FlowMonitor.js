import {
    Archive,
    CheckCircle,
    Description,
    Error,
    Gavel,
    Pause,
    PlayArrow,
    Psychology,
    Search,
    Settings,
    Stop,
    Timeline,
    Visibility,
    Warning,
    Cable as WebSocketIcon
} from '@mui/icons-material';
import {
    Alert,
    Badge,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Grid,
    IconButton,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Step,
    StepContent,
    StepLabel,
    Stepper,
    Typography
} from '@mui/material';
import {
    CategoryScale,
    Chart as ChartJS,
    Tooltip as ChartTooltip,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Title,
} from 'chart.js';
import React, { useEffect, useRef, useState } from 'react';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

const FlowMonitor = () => {
  const [flows, setFlows] = useState([]);
  const [selectedFlow, setSelectedFlow] = useState(null);
  const [metrics, setMetrics] = useState({});
  const [pipelineConfig, setPipelineConfig] = useState({ agents: [] });
  const [wsConnected, setWsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showLogsDialog, setShowLogsDialog] = useState(false);
  const [flowLogs, setFlowLogs] = useState([]);
  const [newCaseData, setNewCaseData] = useState({
    title: '',
    description: '',
    client_info: { name: '', nationality: '' },
    priority: 'normal'
  });

  const wsRef = useRef(null);

  // Icônes pour les agents
  const getAgentIcon = (agentName) => {
    const icons = {
      'ecouteur': <Psychology />,
      'cadreur_juridique': <Gavel />,
      'parseur_preuves': <Search />,
      'juriste_matching': <Gavel />,
      'recherche_web': <Search />,
      'redacteur_narratif': <Description />,
      'relecteur_ia_1': <Visibility />,
      'synthese_strategique': <Timeline />,
      'relecteur_ia_2': <Visibility />,
      'avocat_ia': <Gavel />,
      'generateur_documents': <Description />,
      'archiveur': <Archive />
    };
    return icons[agentName] || <Settings />;
  };

  // Couleurs pour les statuts
  const getStatusColor = (status) => {
    const colors = {
      'pending': 'default',
      'running': 'primary',
      'completed': 'success',
      'failed': 'error',
      'paused': 'warning'
    };
    return colors[status] || 'default';
  };

  // Initialisation WebSocket
  useEffect(() => {
    connectWebSocket();
    loadInitialData();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8000/api/flow/ws`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setWsConnected(true);
      console.log('WebSocket connecté');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    wsRef.current.onclose = () => {
      setWsConnected(false);
      console.log('WebSocket déconnecté');
      // Tentative de reconnexion après 5 secondes
      setTimeout(connectWebSocket, 5000);
    };

    wsRef.current.onerror = (error) => {
      console.error('Erreur WebSocket:', error);
      setWsConnected(false);
    };
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'initial_state':
        setFlows(data.data.flows);
        setMetrics(data.data.metrics);
        setLoading(false);
        break;
      case 'flow_event':
        handleFlowEvent(data.event, data.data);
        break;
      case 'ping':
        // Répondre au ping pour maintenir la connexion
        break;
      default:
        console.log('Message WebSocket non géré:', data);
    }
  };

  const handleFlowEvent = (event, data) => {
    switch (event) {
      case 'flow_created':
      case 'flow_started':
      case 'flow_completed':
      case 'flow_failed':
      case 'flow_paused':
      case 'flow_resumed':
      case 'flow_cancelled':
        updateFlowInList(data);
        break;
      case 'step_started':
      case 'step_completed':
      case 'step_failed':
        updateFlowInList(data.flow);
        break;
      default:
        console.log('Événement de flow non géré:', event);
    }
  };

  const updateFlowInList = (updatedFlow) => {
    setFlows(prevFlows => {
      const index = prevFlows.findIndex(f => f.id === updatedFlow.id);
      if (index >= 0) {
        const newFlows = [...prevFlows];
        newFlows[index] = updatedFlow;
        return newFlows;
      } else {
        return [...prevFlows, updatedFlow];
      }
    });

    // Mettre à jour le flow sélectionné si c'est le même
    if (selectedFlow && selectedFlow.id === updatedFlow.id) {
      setSelectedFlow(updatedFlow);
    }
  };

  const loadInitialData = async () => {
    try {
      // Charger la configuration du pipeline
      const configResponse = await fetch('/api/flow/pipeline-config');
      const configData = await configResponse.json();
      setPipelineConfig(configData);

      // Charger les flows existants
      const flowsResponse = await fetch('/api/flow/list');
      const flowsData = await flowsResponse.json();
      setFlows(flowsData.flows);

      // Charger les métriques
      const metricsResponse = await fetch('/api/flow/metrics');
      const metricsData = await metricsResponse.json();
      setMetrics(metricsData);

    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  const createAndExecuteFlow = async () => {
    try {
      const response = await fetch('/api/flow/create-and-execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCaseData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Flow créé et lancé:', result);
        setShowCreateDialog(false);
        setNewCaseData({
          title: '',
          description: '',
          client_info: { name: '', nationality: '' },
          priority: 'normal'
        });
      } else {
        console.error('Erreur lors de la création du flow');
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const controlFlow = async (flowId, action) => {
    try {
      const response = await fetch(`/api/flow/${action}/${flowId}`, {
        method: 'POST'
      });

      if (response.ok) {
        console.log(`Action ${action} exécutée sur le flow ${flowId}`);
      } else {
        console.error(`Erreur lors de l'action ${action}`);
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const loadFlowLogs = async (flowId) => {
    try {
      const response = await fetch(`/api/flow/logs/${flowId}`);
      const data = await response.json();
      setFlowLogs(data.logs);
      setShowLogsDialog(true);
    } catch (error) {
      console.error('Erreur lors du chargement des logs:', error);
    }
  };

  const getProgressPercentage = (flow) => {
    if (!flow.steps || flow.steps.length === 0) return 0;
    const completedSteps = flow.steps.filter(step => step.status === 'completed').length;
    return (completedSteps / flow.steps.length) * 100;
  };

  const getCurrentStep = (flow) => {
    if (!flow.steps) return null;
    return flow.steps.find(step => step.status === 'running') || 
           flow.steps.find(step => step.status === 'pending');
  };

  // Données pour le graphique de performance
  const performanceChartData = {
    labels: Object.keys(metrics.agent_performance || {}),
    datasets: [
      {
        label: 'Durée moyenne (s)',
        data: Object.values(metrics.agent_performance || {}).map(perf => perf.avg_duration),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }
    ]
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height={400}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* En-tête avec statut de connexion */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Monitoring des Flows DEFENSEUR-IA
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Badge color={wsConnected ? "success" : "error"} variant="dot">
            <WebSocketIcon />
          </Badge>
          <Typography variant="body2" color={wsConnected ? "success.main" : "error.main"}>
            {wsConnected ? "Connecté" : "Déconnecté"}
          </Typography>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => setShowCreateDialog(true)}
          >
            Nouveau Flow
          </Button>
        </Box>
      </Box>

      {/* Métriques globales */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Flows Total
              </Typography>
              <Typography variant="h4">
                {metrics.total_flows || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Flows Actifs
              </Typography>
              <Typography variant="h4" color="primary">
                {metrics.active_flows || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Taux de Succès
              </Typography>
              <Typography variant="h4" color="success.main">
                {metrics.success_rate || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Durée Moyenne
              </Typography>
              <Typography variant="h4">
                {metrics.avg_duration || 0}s
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Liste des flows */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Flows Actifs
              </Typography>
              {flows.length === 0 ? (
                <Typography color="textSecondary">
                  Aucun flow en cours
                </Typography>
              ) : (
                flows.map((flow) => (
                  <Card key={flow.id} variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                        <Box>
                          <Typography variant="h6">
                            {flow.case_id}
                          </Typography>
                          <Chip 
                            label={flow.status} 
                            color={getStatusColor(flow.status)}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          {flow.total_duration && (
                            <Typography variant="body2" color="textSecondary">
                              Durée: {flow.total_duration.toFixed(2)}s
                            </Typography>
                          )}
                        </Box>
                        <Box>
                          <IconButton onClick={() => setSelectedFlow(flow)}>
                            <Visibility />
                          </IconButton>
                          <IconButton onClick={() => loadFlowLogs(flow.id)}>
                            <Timeline />
                          </IconButton>
                          {flow.status === 'running' && (
                            <IconButton onClick={() => controlFlow(flow.id, 'pause')}>
                              <Pause />
                            </IconButton>
                          )}
                          {flow.status === 'paused' && (
                            <IconButton onClick={() => controlFlow(flow.id, 'resume')}>
                              <PlayArrow />
                            </IconButton>
                          )}
                          <IconButton onClick={() => controlFlow(flow.id, 'cancel')}>
                            <Stop />
                          </IconButton>
                        </Box>
                      </Box>

                      {/* Barre de progression */}
                      <Box mb={2}>
                        <Typography variant="body2" gutterBottom>
                          Progression: {getProgressPercentage(flow).toFixed(0)}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={getProgressPercentage(flow)}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>

                      {/* Étape actuelle */}
                      {getCurrentStep(flow) && (
                        <Box display="flex" alignItems="center" gap={1}>
                          {getAgentIcon(getCurrentStep(flow).agent_name)}
                          <Typography variant="body2">
                            Étape actuelle: {getCurrentStep(flow).agent_name}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Configuration du pipeline */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Pipeline DEFENSEUR-IA
              </Typography>
              <Stepper orientation="vertical">
                {pipelineConfig.agents.map((agent, index) => (
                  <Step key={agent.name} active={true}>
                    <StepLabel icon={getAgentIcon(agent.name)}>
                      <Typography variant="body2" fontWeight="bold">
                        {agent.name}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" color="textSecondary">
                        {agent.description}
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Graphique de performance */}
      {Object.keys(metrics.agent_performance || {}).length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance des Agents
            </Typography>
            <Box height={300}>
              <Line 
                data={performanceChartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'top',
                    },
                    title: {
                      display: true,
                      text: 'Durée moyenne d\'exécution par agent'
                    }
                  }
                }}
              />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Dialog de création de flow */}
      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Créer un Nouveau Flow</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Typography variant="body2" gutterBottom>
                  Titre du dossier
                </Typography>
                <input
                  type="text"
                  value={newCaseData.title}
                  onChange={(e) => setNewCaseData({...newCaseData, title: e.target.value})}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                  placeholder="Ex: Demande de titre de séjour"
                />
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" gutterBottom>
                  Description
                </Typography>
                <textarea
                  value={newCaseData.description}
                  onChange={(e) => setNewCaseData({...newCaseData, description: e.target.value})}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px', minHeight: '100px' }}
                  placeholder="Description détaillée du dossier..."
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" gutterBottom>
                  Nom du client
                </Typography>
                <input
                  type="text"
                  value={newCaseData.client_info.name}
                  onChange={(e) => setNewCaseData({
                    ...newCaseData, 
                    client_info: {...newCaseData.client_info, name: e.target.value}
                  })}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                  placeholder="Nom du client"
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" gutterBottom>
                  Nationalité
                </Typography>
                <input
                  type="text"
                  value={newCaseData.client_info.nationality}
                  onChange={(e) => setNewCaseData({
                    ...newCaseData, 
                    client_info: {...newCaseData.client_info, nationality: e.target.value}
                  })}
                  style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                  placeholder="Nationalité"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCreateDialog(false)}>
            Annuler
          </Button>
          <Button onClick={createAndExecuteFlow} variant="contained">
            Créer et Lancer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog des logs */}
      <Dialog open={showLogsDialog} onClose={() => setShowLogsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Logs du Flow</DialogTitle>
        <DialogContent>
          <List>
            {flowLogs.map((log, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {log.level === 'ERROR' ? <Error color="error" /> : 
                   log.level === 'WARNING' ? <Warning color="warning" /> : 
                   <CheckCircle color="success" />}
                </ListItemIcon>
                <ListItemText
                  primary={log.message}
                  secondary={`${new Date(log.timestamp).toLocaleString()} - Agent: ${log.agent}`}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowLogsDialog(false)}>
            Fermer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de détail du flow */}
      {selectedFlow && (
        <Dialog open={!!selectedFlow} onClose={() => setSelectedFlow(null)} maxWidth="lg" fullWidth>
          <DialogTitle>
            Détails du Flow - {selectedFlow.case_id}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Informations Générales
                </Typography>
                <Typography><strong>ID:</strong> {selectedFlow.id}</Typography>
                <Typography><strong>Statut:</strong> 
                  <Chip 
                    label={selectedFlow.status} 
                    color={getStatusColor(selectedFlow.status)}
                    size="small"
                    sx={{ ml: 1 }}
                  />
                </Typography>
                <Typography><strong>Début:</strong> {new Date(selectedFlow.start_time).toLocaleString()}</Typography>
                {selectedFlow.end_time && (
                  <Typography><strong>Fin:</strong> {new Date(selectedFlow.end_time).toLocaleString()}</Typography>
                )}
                {selectedFlow.total_duration && (
                  <Typography><strong>Durée totale:</strong> {selectedFlow.total_duration.toFixed(2)}s</Typography>
                )}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Métriques
                </Typography>
                {selectedFlow.metrics && (
                  <>
                    <Typography>Agents complétés: {selectedFlow.metrics.completed_agents || 0}</Typography>
                    <Typography>Agents échoués: {selectedFlow.metrics.failed_agents || 0}</Typography>
                    <Typography>Appels API: {selectedFlow.metrics.api_calls || 0}</Typography>
                    <Typography>Appels Embedding: {selectedFlow.metrics.embedding_calls || 0}</Typography>
                    <Typography>Appels Légifrance: {selectedFlow.metrics.legifrance_calls || 0}</Typography>
                  </>
                )}
              </Grid>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Étapes du Pipeline
                </Typography>
                <Stepper orientation="vertical">
                  {selectedFlow.steps && selectedFlow.steps.map((step, index) => (
                    <Step key={step.id} active={step.status !== 'pending'} completed={step.status === 'completed'}>
                      <StepLabel 
                        icon={getAgentIcon(step.agent_name)}
                        error={step.status === 'failed'}
                      >
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body1">
                            {step.agent_name}
                          </Typography>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Chip 
                              label={step.status} 
                              color={getStatusColor(step.status)}
                              size="small"
                            />
                            {step.duration && (
                              <Typography variant="body2" color="textSecondary">
                                {step.duration.toFixed(2)}s
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </StepLabel>
                      <StepContent>
                        {step.error && (
                          <Alert severity="error" sx={{ mb: 1 }}>
                            {step.error}
                          </Alert>
                        )}
                        {step.metrics && (
                          <Typography variant="body2" color="textSecondary">
                            Métriques: {JSON.stringify(step.metrics, null, 2)}
                          </Typography>
                        )}
                      </StepContent>
                    </Step>
                  ))}
                </Stepper>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSelectedFlow(null)}>
              Fermer
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default FlowMonitor;
