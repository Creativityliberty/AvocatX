import {
    AutoAwesome as AutoAwesomeIcon,
    BookmarkAdd as BookmarkAddIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    ExpandMore as ExpandMoreIcon,
    Gavel as GavelIcon,
    Info as InfoIcon,
    Link as LinkIcon,
    Refresh as RefreshIcon,
    Search as SearchIcon,
    Share as ShareIcon,
    TrendingUp as TrendingUpIcon,
    Visibility as VisibilityIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Dialog,
    DialogActions,
    DialogContent,
    DialogTitle,
    Divider,
    IconButton,
    InputAdornment,
    List,
    ListItem,
    ListItemIcon,
    ListItemSecondaryAction,
    ListItemText,
    TextField,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';

const LegalReferencePanel = ({ 
  caseId = null,
  content = '',
  showSuggestions = true,
  showValidation = true,
  onReferenceAdd = null,
  maxReferences = 10
}) => {
  const [references, setReferences] = useState([
    {
      id: 'ref_1',
      article: 'L511-1 CESEDA',
      title: 'Obligation de quitter le territoire français',
      content: 'L\'autorité administrative peut prononcer par arrêté motivé l\'obligation pour un étranger de quitter le territoire français...',
      status: 'valid',
      confidence: 95,
      relevance: 'high',
      source: 'legifrance',
      url: 'https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335187',
      addedAt: '2024-01-15T10:30:00Z',
      validated: true
    },
    {
      id: 'ref_2',
      article: 'L511-2 CESEDA',
      title: 'Interdiction de retour',
      content: 'L\'obligation de quitter le territoire français peut être assortie d\'une interdiction de retour...',
      status: 'valid',
      confidence: 88,
      relevance: 'medium',
      source: 'legifrance',
      url: 'https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006335188',
      addedAt: '2024-01-15T10:35:00Z',
      validated: true
    },
    {
      id: 'ref_3',
      article: 'Art. 6 CEDH',
      title: 'Droit à un procès équitable',
      content: 'Toute personne a droit à ce que sa cause soit entendue équitablement...',
      status: 'warning',
      confidence: 72,
      relevance: 'low',
      source: 'external',
      url: 'https://www.echr.coe.int/documents/convention_fra.pdf',
      addedAt: '2024-01-15T10:40:00Z',
      validated: false
    }
  ]);

  const [suggestions, setSuggestions] = useState([
    {
      id: 'sug_1',
      article: 'L512-1 CESEDA',
      title: 'Délai de départ volontaire',
      reason: 'Pertinent pour les modalités d\'exécution de l\'OQTF',
      confidence: 85,
      source: 'ai_analysis'
    },
    {
      id: 'sug_2',
      article: 'L513-1 CESEDA',
      title: 'Recours contre l\'OQTF',
      reason: 'Applicable aux voies de recours disponibles',
      confidence: 92,
      source: 'ai_analysis'
    }
  ]);

  const [selectedReference, setSelectedReference] = useState(null);
  const [detailDialog, setDetailDialog] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);

  useEffect(() => {
    if (content && showSuggestions) {
      // Analyser le contenu pour suggérer des références
      analyzeLegalContent(content);
    }
  }, [content, showSuggestions]);

  const analyzeLegalContent = async (text) => {
    try {
      const response = await fetch('/api/legal/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text, caseId })
      });
      
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Erreur analyse juridique:', error);
    }
  };

  const validateReferences = async () => {
    setValidating(true);
    try {
      const response = await fetch('/api/legal/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          references: references.map(r => ({ id: r.id, article: r.article })),
          caseId 
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setReferences(prev => prev.map(ref => {
          const validation = data.validations.find(v => v.id === ref.id);
          return validation ? { ...ref, ...validation } : ref;
        }));
      }
    } catch (error) {
      console.error('Erreur validation:', error);
    } finally {
      setValidating(false);
    }
  };

  const addSuggestion = async (suggestion) => {
    try {
      const response = await fetch(`/api/legifrance/article/${suggestion.article}`, {
        method: 'GET'
      });
      
      if (response.ok) {
        const articleData = await response.json();
        const newReference = {
          id: `ref_${Date.now()}`,
          article: suggestion.article,
          title: suggestion.title,
          content: articleData.content || 'Contenu à charger...',
          status: 'pending',
          confidence: suggestion.confidence,
          relevance: 'suggested',
          source: 'legifrance',
          url: articleData.url,
          addedAt: new Date().toISOString(),
          validated: false
        };
        
        setReferences(prev => [...prev, newReference]);
        setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
        
        if (onReferenceAdd) {
          onReferenceAdd(newReference);
        }
      }
    } catch (error) {
      console.error('Erreur ajout référence:', error);
    }
  };

  const removeReference = (referenceId) => {
    setReferences(prev => prev.filter(r => r.id !== referenceId));
  };

  const searchReferences = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/legifrance/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, maxResults: 5 })
      });
      
      if (response.ok) {
        const data = await response.json();
        // Ajouter les résultats comme suggestions
        const newSuggestions = data.results.map(result => ({
          id: `search_${Date.now()}_${Math.random()}`,
          article: result.article,
          title: result.title,
          reason: `Trouvé par recherche: "${searchQuery}"`,
          confidence: result.relevance || 75,
          source: 'search'
        }));
        setSuggestions(prev => [...prev, ...newSuggestions]);
      }
    } catch (error) {
      console.error('Erreur recherche:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'valid': return <CheckCircleIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      case 'pending': return <InfoIcon color="info" />;
      default: return <InfoIcon />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'valid': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'pending': return 'info';
      default: return 'default';
    }
  };

  const getRelevanceColor = (relevance) => {
    switch (relevance) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      case 'suggested': return 'secondary';
      default: return 'default';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'success';
    if (confidence >= 70) return 'warning';
    return 'error';
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="h3">
            <GavelIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Références Juridiques ({references.length})
          </Typography>
          
          {showValidation && (
            <Button
              size="small"
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={validateReferences}
              disabled={validating}
            >
              {validating ? 'Validation...' : 'Valider'}
            </Button>
          )}
        </Box>

        {/* Recherche rapide */}
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Rechercher un article juridique..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchReferences()}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: searchQuery && (
                <InputAdornment position="end">
                  <IconButton 
                    size="small" 
                    onClick={searchReferences}
                    disabled={loading}
                  >
                    <SearchIcon />
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
        </Box>

        {/* Liste des références */}
        <List dense>
          {references.map((reference) => (
            <ListItem key={reference.id} divider>
              <ListItemIcon>
                {getStatusIcon(reference.status)}
              </ListItemIcon>
              
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2">
                      {reference.article}
                    </Typography>
                    <Chip 
                      label={reference.relevance} 
                      size="small" 
                      color={getRelevanceColor(reference.relevance)}
                      variant="outlined"
                    />
                    <Chip 
                      label={`${reference.confidence}%`} 
                      size="small" 
                      color={getConfidenceColor(reference.confidence)}
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" sx={{ mb: 0.5 }}>
                      {reference.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Ajouté le {new Date(reference.addedAt).toLocaleString('fr-FR')}
                    </Typography>
                  </Box>
                }
              />
              
              <ListItemSecondaryAction>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <Tooltip title="Voir détails">
                    <IconButton 
                      size="small"
                      onClick={() => {
                        setSelectedReference(reference);
                        setDetailDialog(true);
                      }}
                    >
                      <VisibilityIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Ouvrir sur Légifrance">
                    <IconButton 
                      size="small"
                      href={reference.url}
                      target="_blank"
                    >
                      <LinkIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="Supprimer">
                    <IconButton 
                      size="small"
                      onClick={() => removeReference(reference.id)}
                      color="error"
                    >
                      <ErrorIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        {references.length === 0 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Aucune référence juridique ajoutée. Utilisez la recherche ou les suggestions ci-dessous.
          </Alert>
        )}

        {/* Suggestions IA */}
        {showSuggestions && suggestions.length > 0 && (
          <Accordion sx={{ mt: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">
                <AutoAwesomeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Suggestions IA ({suggestions.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <List dense>
                {suggestions.map((suggestion) => (
                  <ListItem key={suggestion.id}>
                    <ListItemIcon>
                      <TrendingUpIcon color="primary" />
                    </ListItemIcon>
                    
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle2">
                            {suggestion.article}
                          </Typography>
                          <Chip 
                            label={`${suggestion.confidence}%`} 
                            size="small" 
                            color={getConfidenceColor(suggestion.confidence)}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" sx={{ mb: 0.5 }}>
                            {suggestion.title}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {suggestion.reason}
                          </Typography>
                        </Box>
                      }
                    />
                    
                    <ListItemSecondaryAction>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<BookmarkAddIcon />}
                        onClick={() => addSuggestion(suggestion)}
                      >
                        Ajouter
                      </Button>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        )}
      </CardContent>

      {/* Dialog détails référence */}
      <Dialog 
        open={detailDialog} 
        onClose={() => setDetailDialog(false)} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          {selectedReference?.article} - {selectedReference?.title}
        </DialogTitle>
        <DialogContent>
          {selectedReference && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                <Chip 
                  label={selectedReference.status} 
                  color={getStatusColor(selectedReference.status)}
                />
                <Chip 
                  label={selectedReference.relevance} 
                  color={getRelevanceColor(selectedReference.relevance)}
                  variant="outlined"
                />
                <Chip 
                  label={`Confiance: ${selectedReference.confidence}%`} 
                  color={getConfidenceColor(selectedReference.confidence)}
                />
              </Box>
              
              <Typography variant="body1" paragraph>
                {selectedReference.content}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" gutterBottom>Métadonnées</Typography>
              <Typography variant="body2">Source: {selectedReference.source}</Typography>
              <Typography variant="body2">
                Ajouté le: {new Date(selectedReference.addedAt).toLocaleString('fr-FR')}
              </Typography>
              <Typography variant="body2">
                Validé: {selectedReference.validated ? 'Oui' : 'Non'}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialog(false)}>Fermer</Button>
          <Button 
            variant="contained"
            href={selectedReference?.url}
            target="_blank"
            startIcon={<ShareIcon />}
          >
            Voir sur Légifrance
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default LegalReferencePanel;
