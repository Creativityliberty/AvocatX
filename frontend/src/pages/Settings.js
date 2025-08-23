/**
 * Settings - Configuration et paramètres DEFENSEUR-IA
 */

import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Alert,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Paper,
  IconButton,
  Tooltip,
  InputAdornment,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Api as ApiIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Language as LanguageIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';

const Settings = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [showApiKey, setShowApiKey] = useState(false);
  const [apiKeyStatus, setApiKeyStatus] = useState('unchecked'); // 'unchecked', 'valid', 'invalid'
  const [settings, setSettings] = useState({
    // Paramètres généraux
    language: 'fr',
    timezone: 'Europe/Paris',
    theme: 'light',
    autoSave: true,
    
    // Configuration API
    geminiApiKey: '',
    openaiApiKey: '',
    legifranceClientId: 'contact@isais.fr',
    legifranceClientSecret: 'L@banane2025+',
    
    // Configuration Pipeline IA
    maxConcurrentAgents: 3,
    timeoutSeconds: 300,
    enableRRLA: true,
    embeddingModel: 'gemini-embedding-001',
    notifications: true,
    
    // Paramètres API
    openai_api_key: '',
    legifrance_id: '',
    legifrance_secret: '',
    api_timeout: 30,
    max_retries: 3,
    
    // Paramètres pipeline
    pipeline_timeout: 7200,
    max_concurrent_pipelines: 3,
    auto_start_pipeline: false,
    save_intermediate_results: true,
    
    // Paramètres OCR
    ocr_language: 'fra',
    ocr_confidence_threshold: 80,
    image_preprocessing: true,
    
    // Paramètres stockage
    storage_type: 'json',
    backup_enabled: true,
    backup_frequency: 'daily',
    retention_days: 90,
    
    // Paramètres sécurité
    session_timeout: 480,
    require_2fa: false,
    audit_logs: true,
    data_encryption: true,
  });

  const [unsavedChanges, setUnsavedChanges] = useState(false);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setUnsavedChanges(true);
  };

  const handleTestApiKey = async (apiType) => {
    setApiKeyStatus('testing');
    try {
      // Simulation du test de clé API
      await new Promise(resolve => setTimeout(resolve, 1500));
      setApiKeyStatus('valid');
    } catch (error) {
      setApiKeyStatus('invalid');
    }
  };

  const handleSaveSettings = () => {
    // Logique de sauvegarde
    console.log('Sauvegarde des paramètres:', settings);
    setUnsavedChanges(false);
  };

  const handleResetSettings = () => {
    // Logique de reset
    setUnsavedChanges(false);
  };

  const testApiConnection = (apiType) => {
    console.log(`Test de connexion ${apiType}`);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            Paramètres
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Configuration du système DEFENSEUR-IA
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleResetSettings}
            disabled={!unsavedChanges}
          >
            Réinitialiser
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
            disabled={!unsavedChanges}
          >
            Sauvegarder
          </Button>
        </Box>
      </Box>

      {/* Alerte modifications non sauvegardées */}
      {unsavedChanges && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Vous avez des modifications non sauvegardées. N'oubliez pas de sauvegarder vos changements.
        </Alert>
      )}

      {/* Onglets */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Général" icon={<LanguageIcon />} />
            <Tab label="API & Intégrations" icon={<ApiIcon />} />
            <Tab label="Pipeline IA" icon={<SpeedIcon />} />
            <Tab label="Stockage" icon={<StorageIcon />} />
            <Tab label="Sécurité" icon={<SecurityIcon />} />
            <Tab label="Notifications" icon={<NotificationsIcon />} />
          </Tabs>
        </Box>

        {/* Paramètres généraux */}
        {activeTab === 0 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Paramètres généraux
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Langue</InputLabel>
                  <Select
                    value={settings.language}
                    label="Langue"
                    onChange={(e) => handleSettingChange('language', e.target.value)}
                  >
                    <MenuItem value="fr">Français</MenuItem>
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="es">Español</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Fuseau horaire</InputLabel>
                  <Select
                    value={settings.timezone}
                    label="Fuseau horaire"
                    onChange={(e) => handleSettingChange('timezone', e.target.value)}
                  >
                    <MenuItem value="Europe/Paris">Europe/Paris (UTC+1)</MenuItem>
                    <MenuItem value="Europe/London">Europe/London (UTC+0)</MenuItem>
                    <MenuItem value="America/New_York">America/New_York (UTC-5)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Thème</InputLabel>
                  <Select
                    value={settings.theme}
                    label="Thème"
                    onChange={(e) => handleSettingChange('theme', e.target.value)}
                  >
                    <MenuItem value="light">Clair</MenuItem>
                    <MenuItem value="dark">Sombre</MenuItem>
                    <MenuItem value="auto">Automatique</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Préférences
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.autoSave}
                      onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                    />
                  }
                  label="Sauvegarde automatique"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.notifications}
                      onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                    />
                  }
                  label="Notifications activées"
                />
              </Grid>
            </Grid>
          </CardContent>
        )}

        {/* API & Intégrations */}
        {activeTab === 1 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Configuration API & Intégrations
            </Typography>

            <Grid container spacing={4}>
              {/* Gemini API */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <SmartToyIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      Google Gemini API
                    </Typography>
                    {apiKeyStatus === 'valid' && (
                      <Chip
                        icon={<CheckCircleIcon />}
                        label="Connecté"
                        color="success"
                        size="small"
                        sx={{ ml: 2 }}
                      />
                    )}
                    {apiKeyStatus === 'invalid' && (
                      <Chip
                        icon={<ErrorIcon />}
                        label="Erreur"
                        color="error"
                        size="small"
                        sx={{ ml: 2 }}
                      />
                    )}
                  </Box>
                  
                  <TextField
                    fullWidth
                    label="Clé API Gemini"
                    type={showApiKey ? 'text' : 'password'}
                    value={settings.geminiApiKey}
                    onChange={(e) => handleSettingChange('geminiApiKey', e.target.value)}
                    placeholder="Entrez votre clé API Gemini..."
                    helperText="Utilisée pour les embeddings et l'analyse sémantique"
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <Tooltip title={showApiKey ? 'Masquer' : 'Afficher'}>
                            <IconButton
                              onClick={() => setShowApiKey(!showApiKey)}
                              edge="end"
                            >
                              {showApiKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          </Tooltip>
                        </InputAdornment>
                      ),
                    }}
                    sx={{ mb: 2 }}
                  />
                  
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                      variant="outlined"
                      onClick={() => handleTestApiKey('gemini')}
                      disabled={!settings.geminiApiKey || apiKeyStatus === 'testing'}
                    >
                      {apiKeyStatus === 'testing' ? 'Test en cours...' : 'Tester la connexion'}
                    </Button>
                    
                    <FormControl sx={{ minWidth: 200 }}>
                      <InputLabel>Modèle d'embedding</InputLabel>
                      <Select
                        value={settings.embeddingModel}
                        label="Modèle d'embedding"
                        onChange={(e) => handleSettingChange('embeddingModel', e.target.value)}
                      >
                        <MenuItem value="gemini-embedding-001">gemini-embedding-001</MenuItem>
                        <MenuItem value="text-embedding-004">text-embedding-004</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                </Card>
              </Grid>

              {/* OpenAI API */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    OpenAI API
                  </Typography>
                  <TextField
                    fullWidth
                    label="Clé API OpenAI"
                    type="password"
                    value={settings.openaiApiKey}
                    onChange={(e) => handleSettingChange('openaiApiKey', e.target.value)}
                    placeholder="sk-..."
                    helperText="Utilisée pour les agents de génération de texte et Deep Research"
                  />
                </Card>
              </Grid>

              {/* Légifrance API */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    API Légifrance
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Client ID"
                        value={settings.legifranceClientId}
                        onChange={(e) => handleSettingChange('legifranceClientId', e.target.value)}
                        placeholder="contact@isais.fr"
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Client Secret"
                        type="password"
                        value={settings.legifranceClientSecret}
                        onChange={(e) => handleSettingChange('legifranceClientSecret', e.target.value)}
                        placeholder="L@banane2025+"
                      />
                    </Grid>
                  </Grid>
                </Card>
              </Grid>
            </Grid>
          </CardContent>
        )}

        {/* Pipeline IA */}
        {activeTab === 2 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Configuration du Pipeline IA
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Timeout pipeline (minutes): {Math.floor(settings.pipeline_timeout / 60)}
                </Typography>
                <Slider
                  value={settings.pipeline_timeout / 60}
                  onChange={(e, value) => handleSettingChange('pipeline_timeout', value * 60)}
                  min={30}
                  max={240}
                  marks={[
                    { value: 30, label: '30m' },
                    { value: 60, label: '1h' },
                    { value: 120, label: '2h' },
                    { value: 240, label: '4h' },
                  ]}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Pipelines simultanés: {settings.max_concurrent_pipelines}
                </Typography>
                <Slider
                  value={settings.max_concurrent_pipelines}
                  onChange={(e, value) => handleSettingChange('max_concurrent_pipelines', value)}
                  min={1}
                  max={10}
                  marks={[
                    { value: 1, label: '1' },
                    { value: 3, label: '3' },
                    { value: 5, label: '5' },
                    { value: 10, label: '10' },
                  ]}
                />
              </Grid>

              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Options du pipeline
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.auto_start_pipeline}
                      onChange={(e) => handleSettingChange('auto_start_pipeline', e.target.checked)}
                    />
                  }
                  label="Démarrage automatique du pipeline après upload"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.save_intermediate_results}
                      onChange={(e) => handleSettingChange('save_intermediate_results', e.target.checked)}
                    />
                  }
                  label="Sauvegarder les résultats intermédiaires"
                />
              </Grid>

              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Paramètres OCR
                </Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Langue OCR</InputLabel>
                  <Select
                    value={settings.ocr_language}
                    label="Langue OCR"
                    onChange={(e) => handleSettingChange('ocr_language', e.target.value)}
                  >
                    <MenuItem value="fra">Français</MenuItem>
                    <MenuItem value="eng">Anglais</MenuItem>
                    <MenuItem value="spa">Espagnol</MenuItem>
                    <MenuItem value="ara">Arabe</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Seuil de confiance OCR: {settings.ocr_confidence_threshold}%
                </Typography>
                <Slider
                  value={settings.ocr_confidence_threshold}
                  onChange={(e, value) => handleSettingChange('ocr_confidence_threshold', value)}
                  min={50}
                  max={100}
                  marks={[
                    { value: 50, label: '50%' },
                    { value: 70, label: '70%' },
                    { value: 80, label: '80%' },
                    { value: 90, label: '90%' },
                    { value: 100, label: '100%' },
                  ]}
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.image_preprocessing}
                      onChange={(e) => handleSettingChange('image_preprocessing', e.target.checked)}
                    />
                  }
                  label="Prétraitement des images (améliore la qualité OCR)"
                />
              </Grid>
            </Grid>
          </CardContent>
        )}

        {/* Stockage */}
        {activeTab === 3 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Configuration du stockage
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Type de stockage</InputLabel>
                  <Select
                    value={settings.storage_type}
                    label="Type de stockage"
                    onChange={(e) => handleSettingChange('storage_type', e.target.value)}
                  >
                    <MenuItem value="json">Fichiers JSON (développement)</MenuItem>
                    <MenuItem value="postgresql">PostgreSQL</MenuItem>
                    <MenuItem value="mongodb">MongoDB</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Fréquence de sauvegarde</InputLabel>
                  <Select
                    value={settings.backup_frequency}
                    label="Fréquence de sauvegarde"
                    onChange={(e) => handleSettingChange('backup_frequency', e.target.value)}
                  >
                    <MenuItem value="hourly">Toutes les heures</MenuItem>
                    <MenuItem value="daily">Quotidienne</MenuItem>
                    <MenuItem value="weekly">Hebdomadaire</MenuItem>
                    <MenuItem value="monthly">Mensuelle</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Rétention des données (jours): {settings.retention_days}
                </Typography>
                <Slider
                  value={settings.retention_days}
                  onChange={(e, value) => handleSettingChange('retention_days', value)}
                  min={30}
                  max={365}
                  marks={[
                    { value: 30, label: '30j' },
                    { value: 90, label: '90j' },
                    { value: 180, label: '180j' },
                    { value: 365, label: '1an' },
                  ]}
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.backup_enabled}
                      onChange={(e) => handleSettingChange('backup_enabled', e.target.checked)}
                    />
                  }
                  label="Sauvegardes automatiques activées"
                />
              </Grid>
            </Grid>
          </CardContent>
        )}

        {/* Sécurité */}
        {activeTab === 4 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Paramètres de sécurité
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Timeout de session (minutes): {settings.session_timeout}
                </Typography>
                <Slider
                  value={settings.session_timeout}
                  onChange={(e, value) => handleSettingChange('session_timeout', value)}
                  min={60}
                  max={1440}
                  marks={[
                    { value: 60, label: '1h' },
                    { value: 240, label: '4h' },
                    { value: 480, label: '8h' },
                    { value: 1440, label: '24h' },
                  ]}
                />
              </Grid>

              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Options de sécurité
                </Typography>
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.require_2fa}
                      onChange={(e) => handleSettingChange('require_2fa', e.target.checked)}
                    />
                  }
                  label="Authentification à deux facteurs obligatoire"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.audit_logs}
                      onChange={(e) => handleSettingChange('audit_logs', e.target.checked)}
                    />
                  }
                  label="Journalisation des actions utilisateur"
                />
              </Grid>

              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.data_encryption}
                      onChange={(e) => handleSettingChange('data_encryption', e.target.checked)}
                    />
                  }
                  label="Chiffrement des données sensibles"
                />
              </Grid>
            </Grid>
          </CardContent>
        )}

        {/* Notifications */}
        {activeTab === 5 && (
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Paramètres de notifications
            </Typography>

            <List>
              <ListItem>
                <ListItemText
                  primary="Pipeline terminé"
                  secondary="Notification quand un pipeline se termine avec succès"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="Erreur pipeline"
                  secondary="Notification en cas d'erreur dans le pipeline"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="Nouveau client"
                  secondary="Notification lors de l'ajout d'un nouveau client"
                />
                <ListItemSecondaryAction>
                  <Switch />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="Rendez-vous à venir"
                  secondary="Rappel 30 minutes avant un rendez-vous"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="Sauvegarde terminée"
                  secondary="Notification après chaque sauvegarde automatique"
                />
                <ListItemSecondaryAction>
                  <Switch />
                </ListItemSecondaryAction>
              </ListItem>

              <ListItem>
                <ListItemText
                  primary="Mise à jour système"
                  secondary="Notification des mises à jour disponibles"
                />
                <ListItemSecondaryAction>
                  <Switch defaultChecked />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </CardContent>
        )}
      </Card>

      {/* Informations système */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            Informations système
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <List dense>
                <ListItem>
                  <ListItemText primary="Version DEFENSEUR-IA" secondary="1.0.0" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Version Backend" secondary="FastAPI 0.104.1" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Version Frontend" secondary="React 18.2.0" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Base de données" secondary="JSON Files (dev mode)" />
                </ListItem>
              </List>
            </Grid>
            <Grid item xs={12} md={6}>
              <List dense>
                <ListItem>
                  <ListItemText primary="Dernière sauvegarde" secondary="Aujourd'hui 14:30" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Uptime système" secondary="2h 15m" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Espace disque utilisé" secondary="2.3 GB / 100 GB" />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Statut" 
                    secondary={
                      <Chip label="Opérationnel" size="small" color="success" />
                    } 
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Settings;
