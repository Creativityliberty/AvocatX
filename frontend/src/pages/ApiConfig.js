import {
    Api as ApiIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Save as SaveIcon,
    Security as SecurityIcon,
    Settings as SettingsIcon,
    TestTube as TestIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    CircularProgress,
    Container,
    Divider,
    FormControl,
    FormControlLabel,
    Grid,
    InputLabel,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    MenuItem,
    Paper,
    Select,
    Switch,
    TextField,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';

const ApiConfig = () => {
  const [config, setConfig] = useState({
    clientId: 'contact@isais.fr',
    clientSecret: 'L@banane2025+',
    environment: 'sandbox',
    scopes: ['openid'],
    autoRefreshToken: true,
    enableLogging: true
  });

  const [connectionStatus, setConnectionStatus] = useState({
    status: 'disconnected', // 'connected', 'connecting', 'error'
    message: '',
    lastTest: null
  });

  const [availableScopes] = useState([
    { value: 'openid', label: 'OpenID Connect', description: 'Authentification de base' },
    { value: 'legifrance:read', label: 'Lecture Légifrance', description: 'Accès en lecture aux textes' },
    { value: 'legifrance:search', label: 'Recherche Légifrance', description: 'Recherche dans les textes' },
    { value: 'judilibre:read', label: 'Lecture Judilibre', description: 'Accès à la jurisprudence' }
  ]);

  const [agentConfigs, setAgentConfigs] = useState([
    { id: 'cadreur_juridique', name: 'Cadreur Juridique', enabled: true, priority: 'high' },
    { id: 'recherche_web', name: 'Recherche Web', enabled: true, priority: 'medium' },
    { id: 'relecteur_ia_1', name: 'Relecteur IA #1', enabled: true, priority: 'medium' },
    { id: 'synthese_strategique', name: 'Synthèse Stratégique', enabled: true, priority: 'high' },
    { id: 'avocat_ia', name: 'Avocat IA', enabled: false, priority: 'low' }
  ]);

  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    loadConfiguration();
  }, []);

  const loadConfiguration = async () => {
    try {
      // Simulation d'appel API pour charger la config
      const response = await fetch('/api/config/legifrance');
      if (response.ok) {
        const data = await response.json();
        setConfig(prev => ({ ...prev, ...data }));
      }
    } catch (error) {
      console.error('Erreur chargement configuration:', error);
    }
  };

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
    setSaveStatus(null);
  };

  const handleScopeToggle = (scope) => {
    const newScopes = config.scopes.includes(scope)
      ? config.scopes.filter(s => s !== scope)
      : [...config.scopes, scope];
    
    handleConfigChange('scopes', newScopes);
  };

  const testConnection = async () => {
    setLoading(true);
    setConnectionStatus({ status: 'connecting', message: 'Test de connexion...', lastTest: null });

    try {
      // Simulation d'appel API de test
      const response = await fetch('/api/legifrance/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });

      const result = await response.json();

      if (response.ok) {
        setConnectionStatus({
          status: 'connected',
          message: 'Connexion réussie ! API Légifrance accessible.',
          lastTest: new Date().toLocaleString()
        });
      } else {
        setConnectionStatus({
          status: 'error',
          message: result.error || 'Erreur de connexion',
          lastTest: new Date().toLocaleString()
        });
      }
    } catch (error) {
      setConnectionStatus({
        status: 'error',
        message: 'Erreur réseau : ' + error.message,
        lastTest: new Date().toLocaleString()
      });
    } finally {
      setLoading(false);
    }
  };

  const saveConfiguration = async () => {
    setLoading(true);
    setSaveStatus(null);

    try {
      const response = await fetch('/api/config/legifrance', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config, agentConfigs })
      });

      if (response.ok) {
        setSaveStatus({ type: 'success', message: 'Configuration sauvegardée avec succès' });
      } else {
        setSaveStatus({ type: 'error', message: 'Erreur lors de la sauvegarde' });
      }
    } catch (error) {
      setSaveStatus({ type: 'error', message: 'Erreur réseau : ' + error.message });
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus.status) {
      case 'connected': return <CheckCircleIcon color="success" />;
      case 'connecting': return <CircularProgress size={24} />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <WarningIcon color="warning" />;
    }
  };

  const getStatusColor = () => {
    switch (connectionStatus.status) {
      case 'connected': return 'success';
      case 'error': return 'error';
      case 'connecting': return 'info';
      default: return 'warning';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          <ApiIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          Configuration API Légifrance
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Gérez l'authentification OAuth2 et les paramètres d'accès à l'API officielle Légifrance
        </Typography>
      </Box>

      {saveStatus && (
        <Alert severity={saveStatus.type} sx={{ mb: 3 }}>
          {saveStatus.message}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Configuration OAuth2 */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Authentification OAuth2
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Client ID"
                  value={config.clientId}
                  onChange={(e) => handleConfigChange('clientId', e.target.value)}
                  helperText="Identifiant client fourni par la DILA"
                />
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Client Secret"
                  type="password"
                  value={config.clientSecret}
                  onChange={(e) => handleConfigChange('clientSecret', e.target.value)}
                  helperText="Clé secrète client (gardée confidentielle)"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Environnement</InputLabel>
                  <Select
                    value={config.environment}
                    onChange={(e) => handleConfigChange('environment', e.target.value)}
                  >
                    <MenuItem value="sandbox">Sandbox (Test)</MenuItem>
                    <MenuItem value="production">Production</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Box sx={{ mt: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.autoRefreshToken}
                        onChange={(e) => handleConfigChange('autoRefreshToken', e.target.checked)}
                      />
                    }
                    label="Renouvellement automatique du token"
                  />
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" gutterBottom>
              Scopes d'autorisation
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              {availableScopes.map((scope) => (
                <Card key={scope.value} sx={{ mb: 2 }}>
                  <CardContent sx={{ pb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Typography variant="subtitle1">{scope.label}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {scope.description}
                        </Typography>
                      </Box>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={config.scopes.includes(scope.value)}
                            onChange={() => handleScopeToggle(scope.value)}
                          />
                        }
                        label=""
                      />
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={saveConfiguration}
                disabled={loading}
              >
                Sauvegarder
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<TestIcon />}
                onClick={testConnection}
                disabled={loading}
              >
                Tester la connexion
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Status et Agents */}
        <Grid item xs={12} md={4}>
          {/* Status de connexion */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Status de connexion
            </Typography>
            
            <Alert severity={getStatusColor()} icon={getStatusIcon()}>
              {connectionStatus.message || 'Aucun test effectué'}
            </Alert>
            
            {connectionStatus.lastTest && (
              <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                Dernier test : {connectionStatus.lastTest}
              </Typography>
            )}
          </Paper>

          {/* Configuration des agents */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Agents configurés
            </Typography>
            
            <List dense>
              {agentConfigs.map((agent) => (
                <ListItem key={agent.id}>
                  <ListItemIcon>
                    {agent.enabled ? 
                      <CheckCircleIcon color="success" /> : 
                      <ErrorIcon color="disabled" />
                    }
                  </ListItemIcon>
                  <ListItemText
                    primary={agent.name}
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Chip 
                          label={agent.priority} 
                          size="small" 
                          color={agent.priority === 'high' ? 'error' : 
                                 agent.priority === 'medium' ? 'warning' : 'default'}
                        />
                        <Chip 
                          label={agent.enabled ? 'Actif' : 'Inactif'} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ApiConfig;
