import {
    CheckCircle as CheckCircleIcon,
    Download as DownloadIcon,
    Error as ErrorIcon,
    Refresh as RefreshIcon,
    Speed as SpeedIcon,
    Timeline as TimelineIcon,
    TrendingUp as TrendingUpIcon,
    Visibility as VisibilityIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Container,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { CartesianGrid, Cell, Line, LineChart, Pie, PieChart, Tooltip as RechartsTooltip, ResponsiveContainer, XAxis, YAxis } from 'recharts';

const ApiMonitoring = () => {
  const [metrics, setMetrics] = useState({
    totalRequests: 1247,
    successfulRequests: 1198,
    failedRequests: 49,
    averageResponseTime: 245,
    quotaUsed: 67,
    quotaLimit: 10000
  });

  const [realtimeData, setRealtimeData] = useState([]);
  const [agentMetrics, setAgentMetrics] = useState([
    { agent: 'cadreur_juridique', requests: 456, success: 98.2, avgTime: 234, errors: 8 },
    { agent: 'recherche_web', requests: 389, success: 95.6, avgTime: 312, errors: 17 },
    { agent: 'relecteur_ia_1', requests: 234, success: 99.1, avgTime: 189, errors: 2 },
    { agent: 'synthese_strategique', requests: 168, success: 97.0, avgTime: 278, errors: 5 },
    { agent: 'avocat_ia', requests: 0, success: 0, avgTime: 0, errors: 0 }
  ]);

  const [apiLogs, setApiLogs] = useState([
    { id: 1, timestamp: '2024-01-15 14:32:15', agent: 'cadreur_juridique', endpoint: '/search', status: 200, responseTime: 234, query: 'OQTF article L511-1' },
    { id: 2, timestamp: '2024-01-15 14:31:58', agent: 'recherche_web', endpoint: '/search', status: 200, responseTime: 312, query: 'regroupement familial' },
    { id: 3, timestamp: '2024-01-15 14:31:42', agent: 'relecteur_ia_1', endpoint: '/validate', status: 429, responseTime: 0, query: 'validation référence' },
    { id: 4, timestamp: '2024-01-15 14:31:28', agent: 'synthese_strategique', endpoint: '/search', status: 200, responseTime: 278, query: 'titre séjour L313-1' },
    { id: 5, timestamp: '2024-01-15 14:31:15', agent: 'cadreur_juridique', endpoint: '/search', status: 200, responseTime: 189, query: 'naturalisation conditions' }
  ]);

  const [filters, setFilters] = useState({
    timeRange: '24h',
    agent: 'all',
    status: 'all'
  });

  const [selectedLog, setSelectedLog] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadMetrics();
    generateRealtimeData();
    
    const interval = autoRefresh ? setInterval(() => {
      loadMetrics();
      updateRealtimeData();
    }, 5000) : null;

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const loadMetrics = async () => {
    try {
      const response = await fetch('/api/legifrance/metrics');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Erreur chargement métriques:', error);
    }
  };

  const generateRealtimeData = () => {
    const data = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        time: time.getHours() + ':00',
        requests: Math.floor(Math.random() * 100) + 20,
        errors: Math.floor(Math.random() * 10),
        responseTime: Math.floor(Math.random() * 200) + 150
      });
    }
    setRealtimeData(data);
  };

  const updateRealtimeData = () => {
    setRealtimeData(prev => {
      const newData = [...prev.slice(1)];
      const now = new Date();
      newData.push({
        time: now.getHours() + ':' + now.getMinutes().toString().padStart(2, '0'),
        requests: Math.floor(Math.random() * 100) + 20,
        errors: Math.floor(Math.random() * 10),
        responseTime: Math.floor(Math.random() * 200) + 150
      });
      return newData;
    });
  };

  const getStatusColor = (status) => {
    if (status >= 200 && status < 300) return 'success';
    if (status >= 400 && status < 500) return 'warning';
    if (status >= 500) return 'error';
    return 'default';
  };

  const getStatusIcon = (status) => {
    if (status >= 200 && status < 300) return <CheckCircleIcon color="success" />;
    if (status >= 400 && status < 500) return <WarningIcon color="warning" />;
    if (status >= 500) return <ErrorIcon color="error" />;
    return <ErrorIcon color="disabled" />;
  };

  const exportLogs = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Timestamp,Agent,Endpoint,Status,Response Time,Query\n"
      + apiLogs.map(log => 
          `${log.timestamp},${log.agent},${log.endpoint},${log.status},${log.responseTime},${log.query}`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "api_logs.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const pieData = [
    { name: 'Succès', value: metrics.successfulRequests, color: '#4caf50' },
    { name: 'Erreurs', value: metrics.failedRequests, color: '#f44336' }
  ];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            <TimelineIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
            Monitoring API Légifrance
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Surveillance en temps réel des appels API et métriques de performance
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadMetrics}
          >
            Actualiser
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={exportLogs}
          >
            Exporter
          </Button>
        </Box>
      </Box>

      {/* Métriques principales */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Requêtes totales
                  </Typography>
                  <Typography variant="h4">
                    {metrics.totalRequests.toLocaleString()}
                  </Typography>
                </Box>
                <TrendingUpIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Taux de succès
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {((metrics.successfulRequests / metrics.totalRequests) * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Temps de réponse moyen
                  </Typography>
                  <Typography variant="h4">
                    {metrics.averageResponseTime}ms
                  </Typography>
                </Box>
                <SpeedIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Quota utilisé
              </Typography>
              <Typography variant="h4">
                {metrics.quotaUsed}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={metrics.quotaUsed} 
                sx={{ mt: 1 }}
                color={metrics.quotaUsed > 80 ? 'error' : metrics.quotaUsed > 60 ? 'warning' : 'primary'}
              />
              <Typography variant="caption" color="textSecondary">
                {Math.floor(metrics.quotaLimit * metrics.quotaUsed / 100)} / {metrics.quotaLimit}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Graphiques */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Activité en temps réel (24h)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={realtimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <RechartsTooltip />
                <Line type="monotone" dataKey="requests" stroke="#2196f3" strokeWidth={2} />
                <Line type="monotone" dataKey="errors" stroke="#f44336" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Répartition des réponses
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Métriques par agent */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Performance par agent
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Agent</TableCell>
                <TableCell align="right">Requêtes</TableCell>
                <TableCell align="right">Taux de succès</TableCell>
                <TableCell align="right">Temps moyen</TableCell>
                <TableCell align="right">Erreurs</TableCell>
                <TableCell align="right">Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {agentMetrics.map((agent) => (
                <TableRow key={agent.agent}>
                  <TableCell component="th" scope="row">
                    {agent.agent.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </TableCell>
                  <TableCell align="right">{agent.requests}</TableCell>
                  <TableCell align="right">
                    <Chip 
                      label={`${agent.success}%`}
                      color={agent.success > 95 ? 'success' : agent.success > 90 ? 'warning' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">{agent.avgTime}ms</TableCell>
                  <TableCell align="right">
                    <Chip 
                      label={agent.errors}
                      color={agent.errors === 0 ? 'success' : agent.errors < 10 ? 'warning' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    {agent.requests > 0 ? 
                      <CheckCircleIcon color="success" /> : 
                      <ErrorIcon color="disabled" />
                    }
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Logs des API */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">
            Logs des appels API
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Période</InputLabel>
              <Select
                value={filters.timeRange}
                onChange={(e) => setFilters(prev => ({ ...prev, timeRange: e.target.value }))}
              >
                <MenuItem value="1h">1 heure</MenuItem>
                <MenuItem value="24h">24 heures</MenuItem>
                <MenuItem value="7d">7 jours</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Agent</InputLabel>
              <Select
                value={filters.agent}
                onChange={(e) => setFilters(prev => ({ ...prev, agent: e.target.value }))}
              >
                <MenuItem value="all">Tous</MenuItem>
                <MenuItem value="cadreur_juridique">Cadreur</MenuItem>
                <MenuItem value="recherche_web">Recherche</MenuItem>
                <MenuItem value="relecteur_ia_1">Relecteur</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Agent</TableCell>
                <TableCell>Endpoint</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Temps</TableCell>
                <TableCell>Requête</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {apiLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>{log.timestamp}</TableCell>
                  <TableCell>{log.agent}</TableCell>
                  <TableCell>{log.endpoint}</TableCell>
                  <TableCell>
                    <Chip 
                      icon={getStatusIcon(log.status)}
                      label={log.status}
                      color={getStatusColor(log.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">{log.responseTime}ms</TableCell>
                  <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {log.query}
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="Voir détails">
                      <IconButton 
                        size="small"
                        onClick={() => setSelectedLog(log)}
                      >
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Dialog détails log */}
      <Dialog open={!!selectedLog} onClose={() => setSelectedLog(null)} maxWidth="md" fullWidth>
        <DialogTitle>Détails de l'appel API</DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Informations générales</Typography>
              <Typography variant="body2">Timestamp: {selectedLog.timestamp}</Typography>
              <Typography variant="body2">Agent: {selectedLog.agent}</Typography>
              <Typography variant="body2">Endpoint: {selectedLog.endpoint}</Typography>
              <Typography variant="body2">Status: {selectedLog.status}</Typography>
              <Typography variant="body2">Temps de réponse: {selectedLog.responseTime}ms</Typography>
              <Typography variant="body2">Requête: {selectedLog.query}</Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedLog(null)}>Fermer</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ApiMonitoring;
