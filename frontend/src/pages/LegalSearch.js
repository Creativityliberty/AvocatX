import {
    Article as ArticleIcon,
    BookmarkAdd as BookmarkAddIcon,
    Clear as ClearIcon,
    Download as DownloadIcon,
    ExpandMore as ExpandMoreIcon,
    FilterList as FilterListIcon,
    History as HistoryIcon,
    Search as SearchIcon,
    Share as ShareIcon,
    StarBorder as StarBorderIcon,
    Star as StarIcon,
    Visibility as VisibilityIcon
} from '@mui/icons-material';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
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
    Divider,
    FormControl,
    Grid,
    IconButton,
    InputLabel,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    MenuItem,
    Pagination,
    Paper,
    Select,
    Tab,
    Tabs,
    TextField,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';

const LegalSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    nature: 'all',
    champ: 'all',
    code: 'all',
    dateDebut: '',
    dateFin: '',
    tri: 'pertinence'
  });
  
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [savedSearches, setSavedSearches] = useState([
    { id: 1, query: 'OQTF article L511-1', date: '2024-01-15', results: 23 },
    { id: 2, query: 'regroupement familial conditions', date: '2024-01-14', results: 45 },
    { id: 3, query: 'titre séjour renouvellement', date: '2024-01-13', results: 67 }
  ]);
  
  const [searchHistory, setSearchHistory] = useState([
    'OQTF motifs annulation',
    'naturalisation conditions assimilation',
    'visa conjoint français',
    'carte résident permanent',
    'protection subsidiaire OFPRA'
  ]);
  
  const [favorites, setFavorites] = useState(new Set());
  const [activeTab, setActiveTab] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const natureOptions = [
    { value: 'all', label: 'Toutes les natures' },
    { value: 'CODE', label: 'Codes' },
    { value: 'LODA', label: 'Lois et décrets' },
    { value: 'JORF', label: 'Journal officiel' },
    { value: 'KALI', label: 'Conventions collectives' }
  ];

  const champOptions = [
    { value: 'all', label: 'Tous les champs' },
    { value: 'ALL', label: 'Texte complet' },
    { value: 'TITLE', label: 'Titre uniquement' },
    { value: 'TEXTE', label: 'Contenu uniquement' }
  ];

  const codeOptions = [
    { value: 'all', label: 'Tous les codes' },
    { value: 'CESEDA', label: 'Code de l\'entrée et du séjour des étrangers' },
    { value: 'CN', label: 'Code de la nationalité' },
    { value: 'CCiv', label: 'Code civil' },
    { value: 'CPP', label: 'Code de procédure pénale' }
  ];

  useEffect(() => {
    // Simulation de données de résultats
    if (searchQuery) {
      setSearchResults([
        {
          id: 'art_1',
          titre: 'Article L511-1 du CESEDA',
          code: 'CESEDA',
          nature: 'CODE',
          contenu: 'L\'autorité administrative peut prononcer par arrêté motivé l\'obligation pour un étranger de quitter le territoire français...',
          url: 'https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335187',
          date: '2024-01-01',
          pertinence: 95,
          metadata: {
            ministere: 'Intérieur',
            nor: 'INTK1234567A'
          }
        },
        {
          id: 'art_2',
          titre: 'Article L511-2 du CESEDA',
          code: 'CESEDA',
          nature: 'CODE',
          contenu: 'L\'obligation de quitter le territoire français peut être assortie d\'une interdiction de retour sur le territoire français...',
          url: 'https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335188',
          date: '2024-01-01',
          pertinence: 88,
          metadata: {
            ministere: 'Intérieur',
            nor: 'INTK1234568A'
          }
        },
        {
          id: 'art_3',
          titre: 'Décret n° 2024-123 relatif aux OQTF',
          code: 'Décrets',
          nature: 'LODA',
          contenu: 'Les modalités d\'application des dispositions relatives à l\'obligation de quitter le territoire français...',
          url: 'https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000012345678',
          date: '2024-01-15',
          pertinence: 82,
          metadata: {
            ministere: 'Intérieur',
            nor: 'INTD2400123D'
          }
        }
      ]);
    }
  }, [searchQuery, filters, page]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    
    try {
      // Ajout à l'historique
      if (!searchHistory.includes(searchQuery)) {
        setSearchHistory(prev => [searchQuery, ...prev.slice(0, 9)]);
      }
      
      // Simulation d'appel API
      const response = await fetch('/api/legifrance/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          filters,
          page,
          pageSize: 10
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
        setTotalPages(Math.ceil(data.total / 10));
      }
    } catch (error) {
      console.error('Erreur de recherche:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({
      nature: 'all',
      champ: 'all',
      code: 'all',
      dateDebut: '',
      dateFin: '',
      tri: 'pertinence'
    });
  };

  const saveSearch = () => {
    const newSearch = {
      id: Date.now(),
      query: searchQuery,
      date: new Date().toISOString().split('T')[0],
      results: searchResults.length,
      filters: { ...filters }
    };
    setSavedSearches(prev => [newSearch, ...prev]);
  };

  const loadSavedSearch = (search) => {
    setSearchQuery(search.query);
    setFilters(search.filters || {});
    handleSearch();
  };

  const toggleFavorite = (articleId) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(articleId)) {
        newFavorites.delete(articleId);
      } else {
        newFavorites.add(articleId);
      }
      return newFavorites;
    });
  };

  const exportResults = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Titre,Code,Nature,Pertinence,URL,Date\n"
      + searchResults.map(result => 
          `"${result.titre}","${result.code}","${result.nature}",${result.pertinence},"${result.url}","${result.date}"`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "recherche_juridique.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getPertinenceColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'default';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          <SearchIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          Recherche Juridique Légifrance
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Interface de recherche avancée dans la base officielle Légifrance
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Zone de recherche */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                fullWidth
                label="Recherche juridique"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Ex: OQTF article L511-1, regroupement familial..."
                InputProps={{
                  endAdornment: searchQuery && (
                    <IconButton onClick={() => setSearchQuery('')}>
                      <ClearIcon />
                    </IconButton>
                  )
                }}
              />
              <Button
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
                disabled={loading || !searchQuery.trim()}
                sx={{ minWidth: 120 }}
              >
                {loading ? 'Recherche...' : 'Rechercher'}
              </Button>
            </Box>

            {/* Filtres avancés */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">
                  <FilterListIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Filtres avancés
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Nature du texte</InputLabel>
                      <Select
                        value={filters.nature}
                        onChange={(e) => handleFilterChange('nature', e.target.value)}
                      >
                        {natureOptions.map(option => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Champ de recherche</InputLabel>
                      <Select
                        value={filters.champ}
                        onChange={(e) => handleFilterChange('champ', e.target.value)}
                      >
                        {champOptions.map(option => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Code spécifique</InputLabel>
                      <Select
                        value={filters.code}
                        onChange={(e) => handleFilterChange('code', e.target.value)}
                      >
                        {codeOptions.map(option => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6} md={3}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Tri par</InputLabel>
                      <Select
                        value={filters.tri}
                        onChange={(e) => handleFilterChange('tri', e.target.value)}
                      >
                        <MenuItem value="pertinence">Pertinence</MenuItem>
                        <MenuItem value="date">Date</MenuItem>
                        <MenuItem value="titre">Titre</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Date de début"
                      type="date"
                      value={filters.dateDebut}
                      onChange={(e) => handleFilterChange('dateDebut', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Date de fin"
                      type="date"
                      value={filters.dateFin}
                      onChange={(e) => handleFilterChange('dateFin', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                </Grid>
                
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<ClearIcon />}
                    onClick={clearFilters}
                  >
                    Effacer les filtres
                  </Button>
                </Box>
              </AccordionDetails>
            </Accordion>
          </Paper>

          {/* Résultats de recherche */}
          {searchResults.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Résultats de recherche ({searchResults.length})
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<BookmarkAddIcon />}
                    onClick={saveSearch}
                    size="small"
                  >
                    Sauvegarder
                  </Button>
                  
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={exportResults}
                    size="small"
                  >
                    Exporter
                  </Button>
                </Box>
              </Box>

              {searchResults.map((result) => (
                <Card key={result.id} sx={{ mb: 2 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" component="h3" gutterBottom>
                          <ArticleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                          {result.titre}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                          <Chip label={result.code} size="small" />
                          <Chip label={result.nature} size="small" variant="outlined" />
                          <Chip 
                            label={`${result.pertinence}% pertinent`} 
                            size="small" 
                            color={getPertinenceColor(result.pertinence)}
                          />
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {result.contenu.substring(0, 200)}...
                        </Typography>
                        
                        <Typography variant="caption" color="text.secondary">
                          Publié le {result.date} • {result.metadata.ministere}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, ml: 2 }}>
                        <IconButton
                          onClick={() => toggleFavorite(result.id)}
                          color={favorites.has(result.id) ? 'warning' : 'default'}
                        >
                          {favorites.has(result.id) ? <StarIcon /> : <StarBorderIcon />}
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<VisibilityIcon />}
                      onClick={() => setSelectedArticle(result)}
                    >
                      Voir détails
                    </Button>
                    
                    <Button
                      size="small"
                      startIcon={<ShareIcon />}
                      href={result.url}
                      target="_blank"
                    >
                      Légifrance
                    </Button>
                  </CardActions>
                </Card>
              ))}

              {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(e, value) => setPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </Paper>
          )}
        </Grid>

        {/* Panneau latéral */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Tabs value={activeTab} onChange={(e, value) => setActiveTab(value)}>
              <Tab label="Historique" />
              <Tab label="Sauvegardées" />
            </Tabs>

            {activeTab === 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Recherches récentes
                </Typography>
                
                <List dense>
                  {searchHistory.map((query, index) => (
                    <ListItem
                      key={index}
                      button
                      onClick={() => {
                        setSearchQuery(query);
                        handleSearch();
                      }}
                    >
                      <ListItemIcon>
                        <SearchIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={query}
                        primaryTypographyProps={{
                          variant: 'body2',
                          sx: { 
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {activeTab === 1 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  <BookmarkAddIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Recherches sauvegardées
                </Typography>
                
                <List dense>
                  {savedSearches.map((search) => (
                    <ListItem key={search.id}>
                      <ListItemText
                        primary={search.query}
                        secondary={`${search.date} • ${search.results} résultats`}
                        primaryTypographyProps={{
                          variant: 'body2',
                          sx: { 
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }
                        }}
                      />
                      <IconButton
                        size="small"
                        onClick={() => loadSavedSearch(search)}
                      >
                        <SearchIcon />
                      </IconButton>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Dialog détails article */}
      <Dialog 
        open={!!selectedArticle} 
        onClose={() => setSelectedArticle(null)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          {selectedArticle?.titre}
        </DialogTitle>
        <DialogContent>
          {selectedArticle && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                <Chip label={selectedArticle.code} />
                <Chip label={selectedArticle.nature} variant="outlined" />
                <Chip 
                  label={`${selectedArticle.pertinence}% pertinent`} 
                  color={getPertinenceColor(selectedArticle.pertinence)}
                />
              </Box>
              
              <Typography variant="body1" paragraph>
                {selectedArticle.contenu}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" gutterBottom>Métadonnées</Typography>
              <Typography variant="body2">Date de publication: {selectedArticle.date}</Typography>
              <Typography variant="body2">Ministère: {selectedArticle.metadata.ministere}</Typography>
              <Typography variant="body2">NOR: {selectedArticle.metadata.nor}</Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedArticle(null)}>Fermer</Button>
          <Button 
            variant="contained"
            href={selectedArticle?.url}
            target="_blank"
          >
            Voir sur Légifrance
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LegalSearch;
