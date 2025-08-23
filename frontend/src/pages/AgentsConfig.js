import {
    CheckCircle as CheckCircleIcon,
    Code as CodeIcon,
    Edit as EditIcon,
    Error as ErrorIcon,
    Info as InfoIcon,
    PlayArrow as PlayArrowIcon,
    Psychology as PsychologyIcon,
    RestoreFromTrash as RestoreIcon,
    Save as SaveIcon,
    Settings as SettingsIcon,
    SmartToy as SmartToyIcon,
    Speed as SpeedIcon,
    Tune as TuneIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardActions,
    CardContent,
    Chip,
    Container,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    FormControl,
    FormControlLabel,
    Grid,
    InputLabel,
    LinearProgress,
    MenuItem,
    Paper,
    Select,
    Slider,
    Switch,
    Tab,
    Tabs,
    TextField,
    Typography
} from '@mui/material';
import React, { useState } from 'react';

const AgentsConfig = () => {
  const [agents, setAgents] = useState([
    {
      id: 'ecouteur',
      name: 'Écouteur STT',
      description: 'Transcription audio vers texte',
      status: 'active',
      enabled: true,
      performance: 92,
      config: {
        model: 'whisper-1',
        language: 'fr',
        temperature: 0.1,
        maxTokens: 1000,
        legifrance: {
          enabled: false,
          scopes: []
        }
      }
    },
    {
      id: 'cadreur_juridique',
      name: 'Cadreur Juridique',
      description: 'Identification des axes juridiques',
      status: 'active',
      enabled: true,
      performance: 88,
      config: {
        model: 'gpt-4o',
        temperature: 0.2,
        maxTokens: 2000,
        legifrance: {
          enabled: true,
          scopes: ['openid', 'read:codes', 'read:jurisprudence'],
          searchConfig: {
            nature: ['CODE', 'LODA'],
            champ: 'ALL',
            maxResults: 50
          }
        }
      }
    },
    {
      id: 'parseur_preuves',
      name: 'Parseur de Preuves',
      description: 'Extraction OCR et analyse documents',
      status: 'active',
      enabled: true,
      performance: 85,
      config: {
        ocrEngine: 'tesseract',
        languages: ['fra', 'eng'],
        confidence: 0.8,
        legifrance: {
          enabled: false,
          scopes: []
        }
      }
    },
    {
      id: 'juriste_matching',
      name: 'Juriste Matching',
      description: 'Correspondance articles/preuves',
      status: 'active',
      enabled: true,
      performance: 91,
      config: {
        embeddingModel: 'gemini-embedding-001',
        dimensions: 1536,
        similarity: 0.75,
        maxMatches: 10,
        legifrance: {
          enabled: true,
          scopes: ['openid', 'read:codes'],
          searchConfig: {
            nature: ['CODE'],
            champ: 'TEXTE',
            maxResults: 20
          }
        }
      }
    },
    {
      id: 'recherche_web',
      name: 'Recherche Web',
      description: 'Recherche jurisprudentielle approfondie',
      status: 'active',
      enabled: true,
      performance: 87,
      config: {
        sources: ['legifrance', 'judilibre', 'gisti', 'lacimade'],
        maxResults: 30,
        legifrance: {
          enabled: true,
          scopes: ['openid', 'read:codes', 'read:jurisprudence'],
          searchConfig: {
            nature: ['CODE', 'LODA', 'JURI'],
            champ: 'ALL',
            maxResults: 100
          }
        }
      }
    },
    {
      id: 'redacteur_narratif',
      name: 'Rédacteur Narratif',
      description: 'Génération du récit juridique',
      status: 'active',
      enabled: true,
      performance: 89,
      config: {
        model: 'gpt-4o',
        temperature: 0.3,
        maxTokens: 3000,
        style: 'formal',
        legifrance: {
          enabled: false,
          scopes: []
        }
      }
    },
    {
      id: 'relecteur_ia_1',
      name: 'Relecteur IA #1',
      description: 'Première relecture technique',
      status: 'active',
      enabled: true,
      performance: 93,
      config: {
        model: 'gpt-4o',
        temperature: 0.1,
        strictness: 0.9,
        legifrance: {
          enabled: true,
          scopes: ['openid', 'read:codes'],
          searchConfig: {
            nature: ['CODE'],
            champ: 'ALL',
            maxResults: 20
          }
        }
      }
    },
    {
      id: 'agregateur_coherence',
      name: 'Agrégateur Cohérence',
      description: 'Vérification cohérence globale',
      status: 'active',
      enabled: true,
      performance: 86,
      config: {
        model: 'gpt-4o',
        temperature: 0.1,
        coherenceThreshold: 0.8,
        legifrance: {
          enabled: false,
          scopes: []
        }
      }
    },
    {
      id: 'relecteur_ia_2',
      name: 'Relecteur IA #2',
      description: 'Seconde relecture divergente',
      status: 'active',
      enabled: true,
      performance: 90,
      config: {
        model: 'gpt-4o',
        temperature: 0.4,
        divergenceMode: true,
        legifrance: {
          enabled: false,
          scopes: []
        }
      }
    },
    {
      id: 'synthese_strategique',
      name: 'Synthèse Stratégique',
      description: 'Analyse stratégique et recommandations',
      status: 'active',
      enabled: true,
      performance: 94,
      config: {
        model: 'gpt-4o',
        temperature: 0.2,
        strategicDepth: 0.9,
        legifrance: {
          enabled: true,
          scopes: ['openid', 'read:codes', 'read:jurisprudence'],
          searchConfig: {
            nature: ['CODE', 'JURI'],
            champ: 'ALL',
            maxResults: 50
          }
        }
      }
    },
    {
      id: 'avocat_ia',
      name: 'Avocat IA',
      description: 'Rédaction finale de la requête',
      status: 'active',
      enabled: true,
      performance: 96,
      config: {
        model: 'gpt-4o',
        temperature: 0.2,
        formalStyle: true,
        legifrance: {
          enabled: true,
          scopes: ['openid', 'read:codes', 'read:jurisprudence'],
          searchConfig: {
            nature: ['CODE', 'LODA', 'JURI'],
            champ: 'ALL',
            maxResults: 100
          }
        }
      }
    },
    {
      id: 'export_final',
      name: 'Export Final',
      description: 'Génération PDF et archive ZIP',
      status: 'active',
      enabled: true,
      performance: 98,
      config: {
        format: 'pdf',
        includeAnnexes: true,
        watermark: false,
        legifrance: {
          enabled: false,
          scopes: []
        }
      }
    }
  ]);

  const [selectedAgent, setSelectedAgent] = useState(null);
  const [configDialog, setConfigDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [globalSettings, setGlobalSettings] = useState({
    pipelineMode: 'sequential',
    parallelism: 3,
    timeout: 300,
    retries: 2,
    logging: 'info'
  });

  const availableScopes = [
    { value: 'openid', label: 'OpenID Connect', description: 'Authentification de base' },
    { value: 'read:codes', label: 'Lecture Codes', description: 'Accès aux codes juridiques' },
    { value: 'read:jurisprudence', label: 'Lecture Jurisprudence', description: 'Accès à la jurisprudence' },
    { value: 'read:conventions', label: 'Lecture Conventions', description: 'Accès aux conventions collectives' },
    { value: 'read:jorf', label: 'Lecture JORF', description: 'Accès au Journal Officiel' }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircleIcon color="success" />;
      case 'error': return <ErrorIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      default: return <InfoIcon color="info" />;
    }
  };

  const getPerformanceColor = (performance) => {
    if (performance >= 90) return 'success';
    if (performance >= 70) return 'warning';
    return 'error';
  };

  const handleAgentToggle = (agentId) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId 
        ? { ...agent, enabled: !agent.enabled }
        : agent
    ));
  };

  const handleConfigSave = (agentId, newConfig) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId 
        ? { ...agent, config: { ...agent.config, ...newConfig } }
        : agent
    ));
    setConfigDialog(false);
  };

  const handleScopeChange = (agentId, scopes) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId 
        ? { 
            ...agent, 
            config: { 
              ...agent.config, 
              legifrance: { 
                ...agent.config.legifrance, 
                scopes 
              } 
            } 
          }
        : agent
    ));
  };

  const saveAllConfigurations = async () => {
    try {
      const response = await fetch('/api/agents/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agents, globalSettings })
      });
      
      if (response.ok) {
        // Notification de succès
        console.log('Configuration sauvegardée');
      }
    } catch (error) {
      console.error('Erreur sauvegarde:', error);
    }
  };

  const resetToDefaults = () => {
    // Réinitialiser aux valeurs par défaut
    setGlobalSettings({
      pipelineMode: 'sequential',
      parallelism: 3,
      timeout: 300,
      retries: 2,
      logging: 'info'
    });
  };

  const testAgent = async (agentId) => {
    try {
      const response = await fetch(`/api/agents/${agentId}/test`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Test agent:', result);
      }
    } catch (error) {
      console.error('Erreur test agent:', error);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          <SettingsIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          Configuration des Agents
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Gestion et paramétrage des agents du pipeline DEFENSEUR-IA
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Paramètres globaux */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              <TuneIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Paramètres Globaux du Pipeline
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Mode Pipeline</InputLabel>
                  <Select
                    value={globalSettings.pipelineMode}
                    onChange={(e) => setGlobalSettings(prev => ({ ...prev, pipelineMode: e.target.value }))}
                  >
                    <MenuItem value="sequential">Séquentiel</MenuItem>
                    <MenuItem value="parallel">Parallèle</MenuItem>
                    <MenuItem value="hybrid">Hybride</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Typography gutterBottom>Parallélisme: {globalSettings.parallelism}</Typography>
                <Slider
                  value={globalSettings.parallelism}
                  onChange={(e, value) => setGlobalSettings(prev => ({ ...prev, parallelism: value }))}
                  min={1}
                  max={8}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Timeout (secondes)"
                  type="number"
                  value={globalSettings.timeout}
                  onChange={(e) => setGlobalSettings(prev => ({ ...prev, timeout: parseInt(e.target.value) }))}
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <TextField
                  fullWidth
                  label="Tentatives"
                  type="number"
                  value={globalSettings.retries}
                  onChange={(e) => setGlobalSettings(prev => ({ ...prev, retries: parseInt(e.target.value) }))}
                />
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={saveAllConfigurations}
              >
                Sauvegarder Tout
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<RestoreIcon />}
                onClick={resetToDefaults}
              >
                Réinitialiser
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Liste des agents */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            <SmartToyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Agents du Pipeline ({agents.filter(a => a.enabled).length}/{agents.length} actifs)
          </Typography>
          
          <Grid container spacing={2}>
            {agents.map((agent) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={agent.id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" component="h3" gutterBottom>
                          {getStatusIcon(agent.status)}
                          <Box component="span" sx={{ ml: 1 }}>
                            {agent.name}
                          </Box>
                        </Typography>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {agent.description}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <SpeedIcon sx={{ mr: 1, fontSize: 16 }} />
                          <Typography variant="body2" sx={{ mr: 2 }}>
                            {agent.performance}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={agent.performance}
                            color={getPerformanceColor(agent.performance)}
                            sx={{ flex: 1, height: 6, borderRadius: 3 }}
                          />
                        </Box>
                        
                        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                          {agent.config.legifrance?.enabled && (
                            <Chip 
                              label="Légifrance" 
                              size="small" 
                              color="primary"
                              icon={<CodeIcon />}
                            />
                          )}
                          
                          {agent.config.legifrance?.scopes?.length > 0 && (
                            <Chip 
                              label={`${agent.config.legifrance.scopes.length} scopes`} 
                              size="small" 
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Box>
                      
                      <FormControlLabel
                        control={
                          <Switch
                            checked={agent.enabled}
                            onChange={() => handleAgentToggle(agent.id)}
                            color="primary"
                          />
                        }
                        label=""
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={() => {
                        setSelectedAgent(agent);
                        setConfigDialog(true);
                      }}
                    >
                      Configurer
                    </Button>
                    
                    <Button
                      size="small"
                      startIcon={<PlayArrowIcon />}
                      onClick={() => testAgent(agent.id)}
                      disabled={!agent.enabled}
                    >
                      Tester
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>

      {/* Dialog de configuration d'agent */}
      <Dialog 
        open={configDialog} 
        onClose={() => setConfigDialog(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          Configuration - {selectedAgent?.name}
        </DialogTitle>
        <DialogContent>
          {selectedAgent && (
            <Box sx={{ mt: 2 }}>
              <Tabs value={activeTab} onChange={(e, value) => setActiveTab(value)}>
                <Tab label="Général" />
                <Tab label="Légifrance" />
                <Tab label="Performance" />
              </Tabs>

              {activeTab === 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>Paramètres Généraux</Typography>
                  
                  {selectedAgent.config.model && (
                    <TextField
                      fullWidth
                      label="Modèle"
                      value={selectedAgent.config.model}
                      margin="normal"
                      disabled
                    />
                  )}
                  
                  {selectedAgent.config.temperature !== undefined && (
                    <Box sx={{ mt: 2 }}>
                      <Typography gutterBottom>
                        Température: {selectedAgent.config.temperature}
                      </Typography>
                      <Slider
                        value={selectedAgent.config.temperature}
                        onChange={(e, value) => {
                          const newConfig = { ...selectedAgent.config, temperature: value };
                          setSelectedAgent({ ...selectedAgent, config: newConfig });
                        }}
                        min={0}
                        max={1}
                        step={0.1}
                        marks
                        valueLabelDisplay="auto"
                      />
                    </Box>
                  )}
                  
                  {selectedAgent.config.maxTokens && (
                    <TextField
                      fullWidth
                      label="Tokens Maximum"
                      type="number"
                      value={selectedAgent.config.maxTokens}
                      margin="normal"
                      onChange={(e) => {
                        const newConfig = { ...selectedAgent.config, maxTokens: parseInt(e.target.value) };
                        setSelectedAgent({ ...selectedAgent, config: newConfig });
                      }}
                    />
                  )}
                </Box>
              )}

              {activeTab === 1 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>Configuration Légifrance</Typography>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={selectedAgent.config.legifrance?.enabled || false}
                        onChange={(e) => {
                          const newConfig = {
                            ...selectedAgent.config,
                            legifrance: {
                              ...selectedAgent.config.legifrance,
                              enabled: e.target.checked
                            }
                          };
                          setSelectedAgent({ ...selectedAgent, config: newConfig });
                        }}
                      />
                    }
                    label="Activer l'intégration Légifrance"
                    sx={{ mb: 2 }}
                  />
                  
                  {selectedAgent.config.legifrance?.enabled && (
                    <>
                      <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                        Scopes autorisés
                      </Typography>
                      
                      {availableScopes.map((scope) => (
                        <FormControlLabel
                          key={scope.value}
                          control={
                            <Switch
                              checked={selectedAgent.config.legifrance?.scopes?.includes(scope.value) || false}
                              onChange={(e) => {
                                const currentScopes = selectedAgent.config.legifrance?.scopes || [];
                                const newScopes = e.target.checked
                                  ? [...currentScopes, scope.value]
                                  : currentScopes.filter(s => s !== scope.value);
                                handleScopeChange(selectedAgent.id, newScopes);
                              }}
                            />
                          }
                          label={
                            <Box>
                              <Typography variant="body2">{scope.label}</Typography>
                              <Typography variant="caption" color="text.secondary">
                                {scope.description}
                              </Typography>
                            </Box>
                          }
                          sx={{ display: 'block', mb: 1 }}
                        />
                      ))}
                      
                      {selectedAgent.config.legifrance?.searchConfig && (
                        <Box sx={{ mt: 3 }}>
                          <Typography variant="subtitle1" gutterBottom>
                            Configuration de recherche
                          </Typography>
                          
                          <TextField
                            fullWidth
                            label="Résultats maximum"
                            type="number"
                            value={selectedAgent.config.legifrance.searchConfig.maxResults}
                            margin="normal"
                            onChange={(e) => {
                              const newConfig = {
                                ...selectedAgent.config,
                                legifrance: {
                                  ...selectedAgent.config.legifrance,
                                  searchConfig: {
                                    ...selectedAgent.config.legifrance.searchConfig,
                                    maxResults: parseInt(e.target.value)
                                  }
                                }
                              };
                              setSelectedAgent({ ...selectedAgent, config: newConfig });
                            }}
                          />
                        </Box>
                      )}
                    </>
                  )}
                </Box>
              )}

              {activeTab === 2 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>Métriques de Performance</Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <PsychologyIcon sx={{ mr: 2 }} />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body1">Performance Globale</Typography>
                      <LinearProgress
                        variant="determinate"
                        value={selectedAgent.performance}
                        color={getPerformanceColor(selectedAgent.performance)}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {selectedAgent.performance}%
                      </Typography>
                    </Box>
                  </Box>
                  
                  <Alert severity="info" sx={{ mt: 2 }}>
                    Les métriques de performance sont calculées automatiquement 
                    basées sur l'historique d'exécution de l'agent.
                  </Alert>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialog(false)}>Annuler</Button>
          <Button 
            variant="contained"
            onClick={() => handleConfigSave(selectedAgent?.id, selectedAgent?.config)}
          >
            Sauvegarder
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AgentsConfig;
