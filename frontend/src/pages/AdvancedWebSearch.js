import {
    Article as ArticleIcon,
    AutoAwesome as AutoAwesomeIcon,
    BookmarkBorder as BookmarkIcon,
    CheckCircle as CheckCircleIcon,
    Download as DownloadIcon,
    Error as ErrorIcon,
    ExpandMore as ExpandMoreIcon,
    History as HistoryIcon,
    Info as InfoIcon,
    Link as LinkIcon,
    Psychology as PsychologyIcon,
    Refresh as RefreshIcon,
    Search as SearchIcon,
    Settings as SettingsIcon,
    Share as ShareIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
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
    FormControl,
    FormControlLabel,
    Grid,
    IconButton,
    InputLabel,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    MenuItem,
    Paper,
    Select,
    Switch,
    Tab,
    Tabs,
    TextField,
    Typography
} from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';

const AdvancedWebSearch = () => {
  // États principaux
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  // Configuration de recherche
  const [searchConfig, setSearchConfig] = useState({
    useDeepResearch: true,
    useClarification: true,
    useQueryRewriting: true,
    researchDepth: 'detailed',
    includeJurisprudence: true,
    includeProcedures: true,
    fallbackToTraditional: true
  });

  // États UI
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [expandedAccordions, setExpandedAccordions] = useState({});

  // Références
  const searchInputRef = useRef(null);

  // Données de cas simulées
  const [availableCases] = useState([
    {
      id: 'case_001',
      title: 'Refus titre de séjour étudiant',
      description: 'Étudiant algérien en master, renouvellement refusé',
      client_info: { nationality: 'Algérienne' },
      legal_domain: 'titre_sejour'
    },
    {
      id: 'case_002',
      title: 'Regroupement familial',
      description: 'Demande de regroupement familial pour conjoint',
      client_info: { nationality: 'Marocaine' },
      legal_domain: 'regroupement_familial'
    },
    {
      id: 'case_003',
      title: 'Recours OQTF',
      description: 'Recours contre obligation de quitter le territoire',
      client_info: { nationality: 'Tunisienne' },
      legal_domain: 'oqtf'
    }
  ]);

  // Exemples de requêtes suggérées
  const suggestedQueries = [
    "Conditions pour obtenir un titre de séjour étudiant",
    "Recours contre un refus de regroupement familial",
    "Délais pour contester une OQTF",
    "Procédure de naturalisation française",
    "Droits des demandeurs d'asile en France"
  ];

  useEffect(() => {
    // Charger l'historique depuis le localStorage
    const savedHistory = localStorage.getItem('webSearchHistory');
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsSearching(true);
    
    try {
      const searchPayload = {
        query: query.trim(),
        case_data: selectedCase,
        urgency: 'normal',
        config: searchConfig
      };

      // Simulation d'appel API
      const response = await fetch('/api/agents/recherche-web-enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchPayload)
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la recherche');
      }

      const result = await response.json();
      
      // Traitement des résultats
      const processedResults = {
        ...result,
        timestamp: new Date().toISOString(),
        query: query.trim(),
        case_context: selectedCase?.title || 'Aucun dossier sélectionné'
      };

      setSearchResults(processedResults);
      
      // Ajouter à l'historique
      const newHistoryItem = {
        id: Date.now(),
        query: query.trim(),
        timestamp: new Date().toISOString(),
        case_title: selectedCase?.title,
        success: result.success,
        citations_count: result.metadata?.citations?.length || 0
      };
      
      const updatedHistory = [newHistoryItem, ...searchHistory.slice(0, 19)]; // Garder 20 éléments max
      setSearchHistory(updatedHistory);
      localStorage.setItem('webSearchHistory', JSON.stringify(updatedHistory));

    } catch (error) {
      console.error('Erreur de recherche:', error);
      setSearchResults({
        success: false,
        content: `Erreur lors de la recherche: ${error.message}`,
        metadata: { error: error.message }
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleSuggestedQuery = (suggestedQuery) => {
    setQuery(suggestedQuery);
    searchInputRef.current?.focus();
  };

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedAccordions(prev => ({
      ...prev,
      [panel]: isExpanded
    }));
  };

  const exportResults = () => {
    if (!searchResults) return;
    
    const exportData = {
      query: searchResults.query,
      timestamp: searchResults.timestamp,
      case_context: searchResults.case_context,
      content: searchResults.content,
      citations: searchResults.metadata?.citations || [],
      metrics: searchResults.metadata?.metrics || {}
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recherche_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`search-tabpanel-${index}`}
      aria-labelledby={`search-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* En-tête */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AutoAwesomeIcon color="primary" />
          Recherche Web Avancée
          <Chip label="Deep Research API" color="primary" size="small" />
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Recherche juridique approfondie avec IA avancée, clarification automatique et sources multiples
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Panneau de recherche */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            {/* Sélection du dossier */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Dossier associé (optionnel)</InputLabel>
              <Select
                value={selectedCase?.id || ''}
                onChange={(e) => {
                  const caseData = availableCases.find(c => c.id === e.target.value);
                  setSelectedCase(caseData || null);
                }}
              >
                <MenuItem value="">
                  <em>Aucun dossier sélectionné</em>
                </MenuItem>
                {availableCases.map((caseItem) => (
                  <MenuItem key={caseItem.id} value={caseItem.id}>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {caseItem.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {caseItem.description} - {caseItem.client_info.nationality}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Champ de recherche */}
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                ref={searchInputRef}
                fullWidth
                multiline
                rows={3}
                placeholder="Posez votre question juridique détaillée..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    handleSearch();
                  }
                }}
                disabled={isSearching}
              />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  disabled={!query.trim() || isSearching}
                  startIcon={isSearching ? <CircularProgress size={20} /> : <SearchIcon />}
                  sx={{ minWidth: 120 }}
                >
                  {isSearching ? 'Recherche...' : 'Rechercher'}
                </Button>
                <IconButton onClick={() => setConfigDialogOpen(true)} title="Configuration">
                  <SettingsIcon />
                </IconButton>
                <IconButton onClick={() => setHistoryDialogOpen(true)} title="Historique">
                  <Badge badgeContent={searchHistory.length} color="primary">
                    <HistoryIcon />
                  </Badge>
                </IconButton>
              </Box>
            </Box>

            {/* Requêtes suggérées */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Suggestions :
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {suggestedQueries.map((suggestion, index) => (
                  <Chip
                    key={index}
                    label={suggestion}
                    variant="outlined"
                    size="small"
                    onClick={() => handleSuggestedQuery(suggestion)}
                    clickable
                  />
                ))}
              </Box>
            </Box>

            {/* Indicateur de progression */}
            {isSearching && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                  Recherche en cours avec Deep Research API...
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Résultats de recherche */}
          {searchResults && (
            <Paper sx={{ p: 3 }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
                  <Tab label="Résultats" icon={<ArticleIcon />} />
                  <Tab label="Citations" icon={<LinkIcon />} />
                  <Tab label="Métriques" icon={<TrendingUpIcon />} />
                  <Tab label="Détails" icon={<InfoIcon />} />
                </Tabs>
              </Box>

              {/* Onglet Résultats */}
              <TabPanel value={activeTab} index={0}>
                <Box sx={{ mb: 2, display: 'flex', justifyContent: 'between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {searchResults.success ? (
                      <CheckCircleIcon color="success" />
                    ) : (
                      <ErrorIcon color="error" />
                    )}
                    <Typography variant="h6">
                      Résultats de recherche
                    </Typography>
                    {searchResults.metadata?.metrics && (
                      <Chip
                        label={`${searchResults.metadata.metrics.total_results} source(s)`}
                        size="small"
                        color="primary"
                      />
                    )}
                  </Box>
                  <Box>
                    <IconButton onClick={exportResults} title="Exporter">
                      <DownloadIcon />
                    </IconButton>
                    <IconButton title="Partager">
                      <ShareIcon />
                    </IconButton>
                    <IconButton title="Sauvegarder">
                      <BookmarkIcon />
                    </IconButton>
                  </Box>
                </Box>

                {searchResults.success ? (
                  <Box>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
                      {searchResults.content}
                    </Typography>
                  </Box>
                ) : (
                  <Alert severity="error">
                    {searchResults.content}
                  </Alert>
                )}
              </TabPanel>

              {/* Onglet Citations */}
              <TabPanel value={activeTab} index={1}>
                {searchResults.metadata?.citations?.length > 0 ? (
                  <List>
                    {searchResults.metadata.citations.map((citation, index) => (
                      <ListItem key={index} divider>
                        <ListItemIcon>
                          <LinkIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={citation.title || `Citation ${index + 1}`}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {citation.url}
                              </Typography>
                              {citation.snippet && (
                                <Typography variant="body2" sx={{ mt: 1 }}>
                                  {citation.snippet}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography color="text.secondary">
                    Aucune citation disponible
                  </Typography>
                )}
              </TabPanel>

              {/* Onglet Métriques */}
              <TabPanel value={activeTab} index={2}>
                {searchResults.metadata?.metrics && (
                  <Grid container spacing={2}>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography color="text.secondary" gutterBottom>
                            Temps d'exécution
                          </Typography>
                          <Typography variant="h6">
                            {searchResults.execution_time?.toFixed(2)}s
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography color="text.secondary" gutterBottom>
                            Citations
                          </Typography>
                          <Typography variant="h6">
                            {searchResults.metadata.metrics.total_citations || 0}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography color="text.secondary" gutterBottom>
                            Modèles utilisés
                          </Typography>
                          <Typography variant="h6">
                            {searchResults.metadata.metrics.models_used?.length || 0}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Card>
                        <CardContent>
                          <Typography color="text.secondary" gutterBottom>
                            Confiance
                          </Typography>
                          <Typography variant="h6">
                            {(searchResults.confidence_score * 100).toFixed(0)}%
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                )}
              </TabPanel>

              {/* Onglet Détails */}
              <TabPanel value={activeTab} index={3}>
                {searchResults.metadata && (
                  <Box>
                    <Accordion expanded={expandedAccordions.reasoning} onChange={handleAccordionChange('reasoning')}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Étapes de raisonnement</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {searchResults.metadata.reasoning_steps?.map((step, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <PsychologyIcon />
                              </ListItemIcon>
                              <ListItemText primary={step} />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>

                    <Accordion expanded={expandedAccordions.queries} onChange={handleAccordionChange('queries')}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Requêtes de recherche</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {searchResults.metadata.search_queries?.map((query, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <SearchIcon />
                              </ListItemIcon>
                              <ListItemText primary={query} />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>

                    <Accordion expanded={expandedAccordions.context} onChange={handleAccordionChange('context')}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Contexte de recherche</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        {searchResults.metadata.research_context && (
                          <Box>
                            <Typography variant="body2">
                              <strong>Domaine juridique:</strong> {searchResults.metadata.research_context.legal_domain}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Nationalité client:</strong> {searchResults.metadata.research_context.client_nationality || 'Non spécifiée'}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Type de procédure:</strong> {searchResults.metadata.research_context.procedure_type || 'Non spécifié'}
                            </Typography>
                            <Typography variant="body2">
                              <strong>Niveau d'urgence:</strong> {searchResults.metadata.research_context.urgency_level}
                            </Typography>
                          </Box>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  </Box>
                )}
              </TabPanel>
            </Paper>
          )}
        </Grid>

        {/* Panneau latéral */}
        <Grid item xs={12} md={4}>
          {/* Configuration rapide */}
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Configuration rapide
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={searchConfig.useDeepResearch}
                  onChange={(e) => setSearchConfig(prev => ({ ...prev, useDeepResearch: e.target.checked }))}
                />
              }
              label="Deep Research API"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={searchConfig.includeJurisprudence}
                  onChange={(e) => setSearchConfig(prev => ({ ...prev, includeJurisprudence: e.target.checked }))}
                />
              }
              label="Inclure jurisprudence"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={searchConfig.includeProcedures}
                  onChange={(e) => setSearchConfig(prev => ({ ...prev, includeProcedures: e.target.checked }))}
                />
              }
              label="Guides procéduraux"
            />
          </Paper>

          {/* Historique récent */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recherches récentes
            </Typography>
            {searchHistory.slice(0, 5).map((item) => (
              <Card key={item.id} sx={{ mb: 1, cursor: 'pointer' }} onClick={() => setQuery(item.query)}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="body2" noWrap>
                    {item.query}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </Typography>
                    <Chip
                      size="small"
                      label={item.success ? 'Succès' : 'Erreur'}
                      color={item.success ? 'success' : 'error'}
                    />
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>
      </Grid>

      {/* Dialog de configuration */}
      <Dialog open={configDialogOpen} onClose={() => setConfigDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Configuration de recherche avancée</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Profondeur de recherche</InputLabel>
                <Select
                  value={searchConfig.researchDepth}
                  onChange={(e) => setSearchConfig(prev => ({ ...prev, researchDepth: e.target.value }))}
                >
                  <MenuItem value="auto">Automatique</MenuItem>
                  <MenuItem value="summary">Résumé</MenuItem>
                  <MenuItem value="detailed">Détaillé</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={searchConfig.useClarification}
                    onChange={(e) => setSearchConfig(prev => ({ ...prev, useClarification: e.target.checked }))}
                  />
                }
                label="Clarification automatique des requêtes"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={searchConfig.useQueryRewriting}
                    onChange={(e) => setSearchConfig(prev => ({ ...prev, useQueryRewriting: e.target.checked }))}
                  />
                }
                label="Réécriture optimisée des requêtes"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={searchConfig.fallbackToTraditional}
                    onChange={(e) => setSearchConfig(prev => ({ ...prev, fallbackToTraditional: e.target.checked }))}
                  />
                }
                label="Recherche traditionnelle en fallback"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Annuler</Button>
          <Button onClick={() => setConfigDialogOpen(false)} variant="contained">Sauvegarder</Button>
        </DialogActions>
      </Dialog>

      {/* Dialog d'historique */}
      <Dialog open={historyDialogOpen} onClose={() => setHistoryDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Historique des recherches</DialogTitle>
        <DialogContent>
          <List>
            {searchHistory.map((item) => (
              <ListItem key={item.id} divider>
                <ListItemText
                  primary={item.query}
                  secondary={
                    <Box>
                      <Typography variant="caption">
                        {new Date(item.timestamp).toLocaleString()}
                      </Typography>
                      {item.case_title && (
                        <Typography variant="caption" sx={{ ml: 2 }}>
                          Dossier: {item.case_title}
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    size="small"
                    label={item.success ? 'Succès' : 'Erreur'}
                    color={item.success ? 'success' : 'error'}
                  />
                  <IconButton size="small" onClick={() => setQuery(item.query)}>
                    <RefreshIcon />
                  </IconButton>
                </Box>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialogOpen(false)}>Fermer</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdvancedWebSearch;
