/**
 * Pipeline - Monitoring temps réel du pipeline DEFENSEUR-IA
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Divider,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';

import {
  ExpandMore as ExpandMoreIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';

import { useWebSocket } from '../hooks/useAPI';

const Pipeline = () => {
  const { connected } = useWebSocket();
  const [activePipelines, setActivePipelines] = useState([]);
  const [systemStats, setSystemStats] = useState({});
  const [logs, setLogs] = useState([]);
  const [_selectedPipeline, _setSelectedPipeline] = useState(null);

  // Mock des pipelines actifs
  useEffect(() => {
    setActivePipelines([
      {
        dossier_id: 'DOSSIER_20240127_142530',
        client_name: 'Marie Dubois',
        status: 'running',
        current_agent: 'agent_06_redacteur_narratif',
        progress: 45,
        step: 6,
        total_steps: 12,
        started_at: '2024-01-27T14:30:00Z',
        estimated_completion: '2024-01-27T16:00:00Z',
        agents_completed: ['agent_00_ecouteur', 'agent_01_cadreur_juridique', 'agent_02_parseur_preuves', 'agent_03_juriste_matching', 'agent_04_recherche_web'],
        current_step_progress: 75,
      },
      {
        dossier_id: 'DOSSIER_20240127_135420',
        client_name: 'Ahmed Benali',
        status: 'running',
        current_agent: 'agent_03_juriste_matching',
        progress: 25,
        step: 3,
        total_steps: 12,
        started_at: '2024-01-27T13:54:00Z',
        estimated_completion: '2024-01-27T17:30:00Z',
        agents_completed: ['agent_00_ecouteur', 'agent_01_cadreur_juridique', 'agent_02_parseur_preuves'],
        current_step_progress: 60,
      },
    ]);

    setSystemStats({
      cpu_usage: 45,
      memory_usage: 62,
      disk_usage: 78,
      active_agents: 8,
      queue_size: 3,
      processed_today: 12,
      avg_processing_time: '2h 15m',
      success_rate: 94.5,
    });

    setLogs([
      { id: 1, timestamp: '2024-01-27T14:45:30Z', level: 'INFO', agent: 'agent_06_redacteur_narratif', dossier_id: 'DOSSIER_20240127_142530', message: 'Génération du récit narratif en cours - 75% terminé' },
      { id: 2, timestamp: '2024-01-27T14:44:15Z', level: 'SUCCESS', agent: 'agent_04_recherche_web', dossier_id: 'DOSSIER_20240127_142530', message: 'Recherche web terminée - 15 ressources trouvées' },
      { id: 3, timestamp: '2024-01-27T14:42:10Z', level: 'WARNING', agent: 'agent_04_recherche_web', dossier_id: 'DOSSIER_20240127_142530', message: 'Délai d\'attente API - retry en cours' },
      { id: 4, timestamp: '2024-01-27T14:40:45Z', level: 'INFO', agent: 'agent_03_juriste_matching', dossier_id: 'DOSSIER_20240127_135420', message: 'Matching FAISS en cours - 60% terminé' },
      { id: 5, timestamp: '2024-01-27T14:38:20Z', level: 'SUCCESS', agent: 'agent_03_juriste_matching', dossier_id: 'DOSSIER_20240127_142530', message: 'Matching terminé - 15 articles pertinents trouvés' },
      { id: 6, timestamp: '2024-01-27T14:35:15Z', level: 'INFO', agent: 'agent_02_parseur_preuves', dossier_id: 'DOSSIER_20240127_135420', message: 'OCR en cours sur scan_titre_sejour.jpg' },
      { id: 7, timestamp: '2024-01-27T14:32:30Z', level: 'SUCCESS', agent: 'agent_02_parseur_preuves', dossier_id: 'DOSSIER_20240127_142530', message: '3 documents PDF traités avec succès' },
      { id: 8, timestamp: '2024-01-27T14:30:00Z', level: 'INFO', agent: 'agent_00_ecouteur', dossier_id: 'DOSSIER_20240127_142530', message: 'Pipeline démarré pour Marie Dubois' },
    ]);
  }, []);

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
    };
    return agentNames[agentId] || agentId;
  };

  const getLogIcon = (level) => {
    switch (level) {
      case 'SUCCESS':
        return <CheckIcon color="success" />;
      case 'ERROR':
        return <ErrorIcon color="error" />;
      case 'WARNING':
        return <WarningIcon color="warning" />;
      case 'INFO':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const _getLogColor = (level) => {
    switch (level) {
      case 'SUCCESS':
        return 'success';
      case 'ERROR':
        return 'error';
      case 'WARNING':
        return 'warning';
      case 'INFO':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatDuration = (startTime) => {
    const start = new Date(startTime);
    const now = new Date();
    const diff = now - start;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const formatETA = (etaTime) => {
    const eta = new Date(etaTime);
    const now = new Date();
    const diff = eta - now;
    if (diff <= 0) return 'Terminé';
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m restant`;
  };

  return (
    <Box>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            Pipeline IA
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Monitoring temps réel du traitement DEFENSEUR-IA
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
          >
            Actualiser
          </Button>
          <Chip
            icon={connected ? <CheckIcon /> : <ErrorIcon />}
            label={connected ? 'Connecté' : 'Déconnecté'}
            color={connected ? 'success' : 'error'}
          />
        </Box>
      </Box>

      {/* Alerte de connexion */}
      {!connected && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Mode simulation activé. Le monitoring temps réel sera disponible lors de la connexion WebSocket.
        </Alert>
      )}

      {/* Statistiques système */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'primary.main' }}>
                    {activePipelines.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pipelines actifs
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.light' }}>
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
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                    {systemStats.active_agents}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Agents actifs
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.light' }}>
                  <SpeedIcon />
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
                    {systemStats.processed_today}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Traités aujourd'hui
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
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                    {systemStats.success_rate}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Taux de succès
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.light' }}>
                  <CheckIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Pipelines actifs */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Pipelines en cours d'exécution
              </Typography>

              {activePipelines.length > 0 ? (
                activePipelines.map((pipeline) => (
                  <Accordion key={pipeline.dossier_id} sx={{ mb: 2 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box sx={{ width: '100%', pr: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {pipeline.client_name}
                          </Typography>
                          <Chip
                            label={`Étape ${pipeline.step}/${pipeline.total_steps}`}
                            size="small"
                            color="primary"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {pipeline.dossier_id} • {getAgentName(pipeline.current_agent)}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <LinearProgress
                            variant="determinate"
                            value={pipeline.progress}
                            sx={{ flexGrow: 1, height: 6 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {pipeline.progress}%
                          </Typography>
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2" sx={{ mb: 1 }}>
                            Progression détaillée
                          </Typography>
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                              Étape actuelle: {getAgentName(pipeline.current_agent)}
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={pipeline.current_step_progress}
                              sx={{ height: 4, mb: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {pipeline.current_step_progress}% de l'étape terminé
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <Typography variant="subtitle2" sx={{ mb: 1 }}>
                            Informations
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Démarré: {formatDuration(pipeline.started_at)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            ETA: {formatETA(pipeline.estimated_completion)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Agents terminés: {pipeline.agents_completed.length}
                          </Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                            <Button size="small" startIcon={<PauseIcon />}>
                              Pause
                            </Button>
                            <Button size="small" startIcon={<StopIcon />} color="error">
                              Arrêter
                            </Button>
                            <Button size="small" startIcon={<ViewIcon />}>
                              Détails
                            </Button>
                          </Box>
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                ))
              ) : (
                <Alert severity="info">
                  Aucun pipeline en cours d'exécution.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar - Statistiques système et logs */}
        <Grid item xs={12} lg={4}>
          {/* Ressources système */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Ressources système
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">CPU</Typography>
                  <Typography variant="body2">{systemStats.cpu_usage}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={systemStats.cpu_usage}
                  color={systemStats.cpu_usage > 80 ? 'error' : systemStats.cpu_usage > 60 ? 'warning' : 'primary'}
                  sx={{ height: 6 }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Mémoire</Typography>
                  <Typography variant="body2">{systemStats.memory_usage}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={systemStats.memory_usage}
                  color={systemStats.memory_usage > 80 ? 'error' : systemStats.memory_usage > 60 ? 'warning' : 'primary'}
                  sx={{ height: 6 }}
                />
              </Box>

              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Disque</Typography>
                  <Typography variant="body2">{systemStats.disk_usage}%</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={systemStats.disk_usage}
                  color={systemStats.disk_usage > 80 ? 'error' : systemStats.disk_usage > 60 ? 'warning' : 'primary'}
                  sx={{ height: 6 }}
                />
              </Box>
            </CardContent>
          </Card>

          {/* Logs récents */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Logs récents
              </Typography>

              <List dense>
                {logs.slice(0, 8).map((log, index) => (
                  <React.Fragment key={log.id}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        {getLogIcon(log.level)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {getAgentName(log.agent)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                              {log.dossier_id}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" sx={{ mt: 0.5 }}>
                              {log.message}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(log.timestamp).toLocaleTimeString('fr-FR')}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < logs.slice(0, 8).length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>

              <Button variant="text" fullWidth sx={{ mt: 1 }}>
                Voir tous les logs
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tableau des performances */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            Performances des agents
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Agent</TableCell>
                  <TableCell>Statut</TableCell>
                  <TableCell>Temps moyen</TableCell>
                  <TableCell>Taux de succès</TableCell>
                  <TableCell>Dernière exécution</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {[
                  { name: 'Écouteur (STT)', status: 'active', avgTime: '2m 30s', successRate: 98.5, lastRun: '14:45' },
                  { name: 'Cadreur Juridique', status: 'active', avgTime: '1m 45s', successRate: 96.2, lastRun: '14:43' },
                  { name: 'Parseur Preuves', status: 'active', avgTime: '5m 20s', successRate: 94.8, lastRun: '14:40' },
                  { name: 'Juriste Matching', status: 'active', avgTime: '8m 15s', successRate: 97.1, lastRun: '14:38' },
                  { name: 'Recherche Web', status: 'warning', avgTime: '12m 30s', successRate: 89.3, lastRun: '14:35' },
                  { name: 'Rédacteur Narratif', status: 'active', avgTime: '15m 45s', successRate: 95.7, lastRun: '14:30' },
                ].map((agent, index) => (
                  <TableRow key={index}>
                    <TableCell>{agent.name}</TableCell>
                    <TableCell>
                      <Chip
                        label={agent.status === 'active' ? 'Actif' : 'Attention'}
                        size="small"
                        color={agent.status === 'active' ? 'success' : 'warning'}
                      />
                    </TableCell>
                    <TableCell>{agent.avgTime}</TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        color={agent.successRate > 95 ? 'success.main' : agent.successRate > 90 ? 'warning.main' : 'error.main'}
                      >
                        {agent.successRate}%
                      </Typography>
                    </TableCell>
                    <TableCell>{agent.lastRun}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Pipeline;
