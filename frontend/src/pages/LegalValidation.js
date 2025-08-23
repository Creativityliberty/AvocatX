import {
    Article as ArticleIcon,
    Assessment as AssessmentIcon,
    Balance as BalanceIcon,
    BookmarkBorder as BookmarkBorderIcon,
    CheckCircle as CheckCircleIcon,
    Download as DownloadIcon,
    Error as ErrorIcon,
    Gavel as GavelIcon,
    Info as InfoIcon,
    Refresh as RefreshIcon,
    Report as ReportIcon,
    Timeline as TimelineIcon,
    TrendingUp as TrendingUpIcon,
    Verified as VerifiedIcon,
    Visibility as VisibilityIcon,
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
    Grid,
    IconButton,
    InputLabel,
    LinearProgress,
    List,
    ListItem,
    ListItemText,
    MenuItem,
    Paper,
    Select,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tabs,
    Typography
} from '@mui/material';
import React, { useState } from 'react';
import { CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, Tooltip as RechartsTooltip, ResponsiveContainer, XAxis, YAxis } from 'recharts';

const LegalValidation = () => {
  const [validationResults, setValidationResults] = useState([
    {
      id: 'case_1',
      caseId: 'CASE-2024-001',
      clientName: 'Jean Dupont',
      caseType: 'OQTF',
      status: 'validated',
      score: 92,
      validatedAt: '2024-01-15T10:30:00Z',
      validations: {
        legal: { score: 95, status: 'valid', issues: 0 },
        procedural: { score: 88, status: 'valid', issues: 1 },
        formal: { score: 94, status: 'valid', issues: 0 },
        coherence: { score: 91, status: 'valid', issues: 0 }
      },
      references: [
        { article: 'L511-1 CESEDA', status: 'valid', confidence: 98 },
        { article: 'L511-2 CESEDA', status: 'valid', confidence: 95 },
        { article: 'Art. 6 CEDH', status: 'valid', confidence: 92 }
      ],
      issues: [
        { type: 'procedural', severity: 'minor', description: 'Délai de recours à préciser' }
      ]
    },
    {
      id: 'case_2',
      caseId: 'CASE-2024-002',
      clientName: 'Marie Martin',
      caseType: 'Regroupement familial',
      status: 'warning',
      score: 78,
      validatedAt: '2024-01-14T14:20:00Z',
      validations: {
        legal: { score: 85, status: 'valid', issues: 0 },
        procedural: { score: 72, status: 'warning', issues: 2 },
        formal: { score: 80, status: 'valid', issues: 1 },
        coherence: { score: 75, status: 'warning', issues: 1 }
      },
      references: [
        { article: 'L411-1 CESEDA', status: 'valid', confidence: 88 },
        { article: 'L411-5 CESEDA', status: 'warning', confidence: 72 }
      ],
      issues: [
        { type: 'procedural', severity: 'major', description: 'Pièces justificatives manquantes' },
        { type: 'formal', severity: 'minor', description: 'Format de date non conforme' },
        { type: 'coherence', severity: 'major', description: 'Contradiction entre arguments' }
      ]
    },
    {
      id: 'case_3',
      caseId: 'CASE-2024-003',
      clientName: 'Ahmed Hassan',
      caseType: 'Naturalisation',
      status: 'error',
      score: 45,
      validatedAt: '2024-01-13T16:45:00Z',
      validations: {
        legal: { score: 60, status: 'warning', issues: 2 },
        procedural: { score: 35, status: 'error', issues: 4 },
        formal: { score: 50, status: 'error', issues: 3 },
        coherence: { score: 35, status: 'error', issues: 2 }
      },
      references: [
        { article: '21-2 CN', status: 'error', confidence: 45 },
        { article: '21-4 CN', status: 'warning', confidence: 68 }
      ],
      issues: [
        { type: 'legal', severity: 'critical', description: 'Base juridique incorrecte' },
        { type: 'procedural', severity: 'critical', description: 'Procédure non respectée' },
        { type: 'formal', severity: 'major', description: 'Structure du document invalide' }
      ]
    }
  ]);

  const [selectedCase, setSelectedCase] = useState(null);
  const [detailDialog, setDetailDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');

  const [validationStats, setValidationStats] = useState({
    total: 156,
    validated: 98,
    warnings: 42,
    errors: 16,
    avgScore: 84.2,
    trends: [
      { date: '2024-01-01', score: 78 },
      { date: '2024-01-02', score: 82 },
      { date: '2024-01-03', score: 85 },
      { date: '2024-01-04', score: 83 },
      { date: '2024-01-05', score: 87 },
      { date: '2024-01-06', score: 84 },
      { date: '2024-01-07', score: 89 }
    ]
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'validated': return <CheckCircleIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'validated': case 'valid': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'major': return 'warning';
      case 'minor': return 'info';
      default: return 'default';
    }
  };

  const filteredResults = validationResults.filter(result => {
    if (filterStatus !== 'all' && result.status !== filterStatus) return false;
    if (filterType !== 'all' && result.caseType !== filterType) return false;
    return true;
  });

  const runValidation = async (caseId) => {
    try {
      const response = await fetch(`/api/validation/run/${caseId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        // Mettre à jour les résultats
        setValidationResults(prev => prev.map(item => 
          item.caseId === caseId ? { ...item, ...result } : item
        ));
      }
    } catch (error) {
      console.error('Erreur validation:', error);
    }
  };

  const exportReport = (caseId) => {
    const caseData = validationResults.find(r => r.caseId === caseId);
    if (!caseData) return;

    const csvContent = "data:text/csv;charset=utf-8," 
      + "Type,Statut,Score,Description\n"
      + Object.entries(caseData.validations).map(([type, validation]) => 
          `"${type}","${validation.status}",${validation.score},"${validation.issues} issues"`
        ).join("\n")
      + "\n\nRéférences juridiques:\n"
      + caseData.references.map(ref => 
          `"${ref.article}","${ref.status}",${ref.confidence},""`
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `validation_report_${caseId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const pieData = [
    { name: 'Validés', value: validationStats.validated, color: '#4caf50' },
    { name: 'Avertissements', value: validationStats.warnings, color: '#ff9800' },
    { name: 'Erreurs', value: validationStats.errors, color: '#f44336' }
  ];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          <GavelIcon sx={{ mr: 2, verticalAlign: 'middle' }} />
          Validation Juridique
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Contrôle de conformité et validation des dossiers juridiques
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Statistiques globales */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Statistiques de Validation
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {validationStats.total}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total validations
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main">
                      {validationStats.validated}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Dossiers validés
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="warning.main">
                      {validationStats.warnings}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avertissements
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="error.main">
                      {validationStats.errors}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Erreurs critiques
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Grid container spacing={3} sx={{ mt: 2 }}>
              <Grid item xs={12} md={8}>
                <Typography variant="subtitle1" gutterBottom>
                  <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Évolution du Score de Validation
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={validationStats.trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Line type="monotone" dataKey="score" stroke="#2196f3" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" gutterBottom>
                  <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Répartition des Statuts
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Filtres */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Statut</InputLabel>
                  <Select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                  >
                    <MenuItem value="all">Tous les statuts</MenuItem>
                    <MenuItem value="validated">Validés</MenuItem>
                    <MenuItem value="warning">Avertissements</MenuItem>
                    <MenuItem value="error">Erreurs</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Type de dossier</InputLabel>
                  <Select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                  >
                    <MenuItem value="all">Tous les types</MenuItem>
                    <MenuItem value="OQTF">OQTF</MenuItem>
                    <MenuItem value="Regroupement familial">Regroupement familial</MenuItem>
                    <MenuItem value="Naturalisation">Naturalisation</MenuItem>
                    <MenuItem value="Titre de séjour">Titre de séjour</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  {filteredResults.length} résultat(s) affiché(s)
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Résultats de validation */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            <BalanceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Résultats de Validation
          </Typography>
          
          {filteredResults.map((result) => (
            <Card key={result.id} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {getStatusIcon(result.status)}
                      <Box component="span" sx={{ ml: 1 }}>
                        {result.caseId} - {result.clientName}
                      </Box>
                    </Typography>
                    
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Chip label={result.caseType} size="small" />
                      <Chip 
                        label={`Score: ${result.score}%`} 
                        size="small" 
                        color={getScoreColor(result.score)}
                      />
                      <Chip 
                        label={result.status} 
                        size="small" 
                        color={getStatusColor(result.status)}
                        variant="outlined"
                      />
                    </Box>
                    
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                      {Object.entries(result.validations).map(([type, validation]) => (
                        <Grid item xs={6} sm={3} key={type}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="caption" display="block" color="text.secondary">
                              {type.charAt(0).toUpperCase() + type.slice(1)}
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={validation.score}
                              color={getScoreColor(validation.score)}
                              sx={{ height: 6, borderRadius: 3, mb: 0.5 }}
                            />
                            <Typography variant="caption">
                              {validation.score}%
                            </Typography>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                    
                    {result.issues.length > 0 && (
                      <Alert severity="warning" sx={{ mb: 2 }}>
                        {result.issues.length} problème(s) détecté(s)
                      </Alert>
                    )}
                    
                    <Typography variant="caption" color="text.secondary">
                      Validé le {new Date(result.validatedAt).toLocaleString('fr-FR')}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
              
              <CardActions>
                <Button
                  size="small"
                  startIcon={<VisibilityIcon />}
                  onClick={() => {
                    setSelectedCase(result);
                    setDetailDialog(true);
                  }}
                >
                  Détails
                </Button>
                
                <Button
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={() => runValidation(result.caseId)}
                >
                  Re-valider
                </Button>
                
                <Button
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportReport(result.caseId)}
                >
                  Rapport
                </Button>
              </CardActions>
            </Card>
          ))}
        </Grid>
      </Grid>

      {/* Dialog détails de validation */}
      <Dialog 
        open={detailDialog} 
        onClose={() => setDetailDialog(false)} 
        maxWidth="lg" 
        fullWidth
      >
        <DialogTitle>
          Détails de Validation - {selectedCase?.caseId}
        </DialogTitle>
        <DialogContent>
          {selectedCase && (
            <Box sx={{ mt: 2 }}>
              <Tabs value={activeTab} onChange={(e, value) => setActiveTab(value)}>
                <Tab label="Vue d'ensemble" />
                <Tab label="Références juridiques" />
                <Tab label="Problèmes détectés" />
              </Tabs>

              {activeTab === 0 && (
                <Box sx={{ mt: 3 }}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>Scores de Validation</Typography>
                      {Object.entries(selectedCase.validations).map(([type, validation]) => (
                        <Box key={type} sx={{ mb: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2">
                              {type.charAt(0).toUpperCase() + type.slice(1)}
                            </Typography>
                            <Typography variant="body2">
                              {validation.score}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={validation.score}
                            color={getScoreColor(validation.score)}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                        </Box>
                      ))}
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>Informations du Dossier</Typography>
                      <List dense>
                        <ListItem>
                          <ListItemText
                            primary="ID du dossier"
                            secondary={selectedCase.caseId}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Client"
                            secondary={selectedCase.clientName}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Type de dossier"
                            secondary={selectedCase.caseType}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Score global"
                            secondary={`${selectedCase.score}%`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText
                            primary="Date de validation"
                            secondary={new Date(selectedCase.validatedAt).toLocaleString('fr-FR')}
                          />
                        </ListItem>
                      </List>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {activeTab === 1 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>Références Juridiques Validées</Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Article</TableCell>
                          <TableCell>Statut</TableCell>
                          <TableCell>Confiance</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedCase.references.map((ref, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <ArticleIcon sx={{ mr: 1 }} />
                                {ref.article}
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={ref.status} 
                                size="small" 
                                color={getStatusColor(ref.status)}
                              />
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={ref.confidence}
                                  color={getScoreColor(ref.confidence)}
                                  sx={{ width: 100, mr: 1, height: 6, borderRadius: 3 }}
                                />
                                {ref.confidence}%
                              </Box>
                            </TableCell>
                            <TableCell>
                              <IconButton size="small">
                                <BookmarkBorderIcon />
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}

              {activeTab === 2 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>Problèmes Détectés</Typography>
                  {selectedCase.issues.length === 0 ? (
                    <Alert severity="success">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <VerifiedIcon sx={{ mr: 1 }} />
                        Aucun problème détecté dans ce dossier
                      </Box>
                    </Alert>
                  ) : (
                    selectedCase.issues.map((issue, index) => (
                      <Alert 
                        key={index} 
                        severity={getSeverityColor(issue.severity)}
                        sx={{ mb: 2 }}
                      >
                        <Box>
                          <Typography variant="subtitle2">
                            {issue.type.charAt(0).toUpperCase() + issue.type.slice(1)} - {issue.severity}
                          </Typography>
                          <Typography variant="body2">
                            {issue.description}
                          </Typography>
                        </Box>
                      </Alert>
                    ))
                  )}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialog(false)}>Fermer</Button>
          <Button 
            variant="contained"
            startIcon={<ReportIcon />}
            onClick={() => exportReport(selectedCase?.caseId)}
          >
            Exporter le Rapport
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LegalValidation;
