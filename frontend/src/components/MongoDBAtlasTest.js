/**
 * Composant de test MongoDB Atlas - DEFENSEUR-IA
 * Interface pour tester la connexion et les fonctionnalités MongoDB Atlas
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  CloudDone as CloudDoneIcon,
  CloudOff as CloudOffIcon,
  Storage as StorageIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Description as DescriptionIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { useMongoDBAtlas, useMongoDBCases } from '../hooks/useMongoDBAtlas';

const MongoDBAtlasTest = () => {
  const { health, stats, loading: atlasLoading, error: atlasError, checkHealth, getStats } = useMongoDBAtlas();
  const { 
    cases, 
    currentCase, 
    loading: casesLoading, 
    error: casesError, 
    createCase, 
    getCaseById, 
    listCases,
    updateCase 
  } = useMongoDBCases();

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);
  const [newCaseData, setNewCaseData] = useState({
    nom_client: '',
    type_contentieux: 'OQTF',
    description: '',
    nationalite: '',
    urgence: 'normale'
  });
  const [editCaseData, setEditCaseData] = useState({});

  // Gestion de la création de dossier
  const handleCreateCase = async () => {
    if (!newCaseData.nom_client || !newCaseData.description) {
      alert('Veuillez remplir au moins le nom du client et la description');
      return;
    }

    const result = await createCase({
      ...newCaseData,
      status: 'nouveau',
      created_by: 'test_frontend'
    });

    if (result) {
      setCreateDialogOpen(false);
      setNewCaseData({
        nom_client: '',
        type_contentieux: 'OQTF',
        description: '',
        nationalite: '',
        urgence: 'normale'
      });
    }
  };

  // Gestion de la modification de dossier
  const handleEditCase = (caseItem) => {
    setSelectedCase(caseItem);
    setEditCaseData({
      nom_client: caseItem.nom_client,
      type_contentieux: caseItem.type_contentieux,
      description: caseItem.description,
      nationalite: caseItem.nationalite || '',
      urgence: caseItem.urgence || 'normale'
    });
    setEditDialogOpen(true);
  };

  const handleUpdateCase = async () => {
    if (!selectedCase || !editCaseData.nom_client || !editCaseData.description) {
      alert('Veuillez remplir au moins le nom du client et la description');
      return;
    }

    const result = await updateCase(selectedCase.dossier_id, {
      ...editCaseData,
      updated_at: new Date().toISOString()
    });

    if (result) {
      setEditDialogOpen(false);
      setSelectedCase(null);
      setEditCaseData({});
    }
  };

  // Gestion de la suppression de dossier
  const handleDeleteCase = (caseItem) => {
    setSelectedCase(caseItem);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!selectedCase) return;

    try {
      // Pour l'instant, on simule la suppression (pas d'endpoint DELETE encore)
      alert(`Suppression simulée du dossier: ${selectedCase.nom_client}`);
      setDeleteDialogOpen(false);
      setSelectedCase(null);
      // Recharger la liste
      await listCases();
    } catch (error) {
      console.error('Erreur suppression:', error);
    }
  };

  // Statut de connexion
  const getConnectionStatus = () => {
    if (atlasLoading) return { status: 'loading', color: 'info', text: 'Vérification...' };
    if (atlasError) return { status: 'error', color: 'error', text: 'Erreur connexion' };
    if (health?.success && health?.status === 'connected') {
      return { status: 'connected', color: 'success', text: 'Connecté MongoDB Atlas' };
    }
    return { status: 'disconnected', color: 'warning', text: 'Déconnecté' };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🔗 Test MongoDB Atlas - DEFENSEUR-IA
      </Typography>
      
      <Grid container spacing={3}>
        {/* Statut de connexion */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                {connectionStatus.status === 'connected' ? (
                  <CloudDoneIcon color="success" sx={{ mr: 1 }} />
                ) : (
                  <CloudOffIcon color="error" sx={{ mr: 1 }} />
                )}
                <Typography variant="h6">
                  Statut de connexion
                </Typography>
              </Box>
              
              <Chip 
                label={connectionStatus.text}
                color={connectionStatus.color}
                sx={{ mb: 2 }}
              />
              
              {health && (
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Base de données: {health.database}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Dernière vérification: {new Date(health.timestamp).toLocaleString()}
                  </Typography>
                </Box>
              )}
              
              <Box mt={2}>
                <Button 
                  variant="outlined" 
                  onClick={checkHealth}
                  disabled={atlasLoading}
                  startIcon={atlasLoading ? <CircularProgress size={16} /> : <RefreshIcon />}
                >
                  Vérifier connexion
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Statistiques MongoDB Atlas */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <StorageIcon sx={{ mr: 1 }} />
                <Typography variant="h6">
                  Statistiques MongoDB Atlas
                </Typography>
              </Box>
              
              {stats?.success && (
                <Box>
                  <Typography variant="body2">
                    📊 Dossiers: {stats.stats.total_cases}
                  </Typography>
                  <Typography variant="body2">
                    📄 Documents: {stats.stats.total_documents}
                  </Typography>
                  <Typography variant="body2">
                    🔄 Pipeline runs: {stats.stats.total_pipeline_runs}
                  </Typography>
                  <Typography variant="body2">
                    🤖 Résultats agents: {stats.stats.total_agent_results}
                  </Typography>
                  <Typography variant="body2">
                    💬 Sessions chat: {stats.stats.total_chat_sessions}
                  </Typography>
                </Box>
              )}
              
              <Box mt={2}>
                <Button 
                  variant="outlined" 
                  onClick={getStats}
                  disabled={atlasLoading}
                  startIcon={atlasLoading ? <CircularProgress size={16} /> : <RefreshIcon />}
                >
                  Actualiser stats
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Gestion des dossiers */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center">
                  <DescriptionIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">
                    Dossiers MongoDB Atlas ({cases.length})
                  </Typography>
                </Box>
                
                <Box>
                  <Button 
                    variant="contained" 
                    onClick={() => setCreateDialogOpen(true)}
                    startIcon={<AddIcon />}
                    sx={{ mr: 1 }}
                  >
                    Créer dossier
                  </Button>
                  <Button 
                    variant="outlined" 
                    onClick={listCases}
                    disabled={casesLoading}
                    startIcon={casesLoading ? <CircularProgress size={16} /> : <RefreshIcon />}
                  >
                    Actualiser
                  </Button>
                </Box>
              </Box>

              {casesError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  Erreur: {casesError}
                </Alert>
              )}

              {cases.length === 0 ? (
                <Alert severity="info">
                  Aucun dossier trouvé. Créez votre premier dossier MongoDB Atlas !
                </Alert>
              ) : (
                <List>
                  {cases.map((caseItem, index) => (
                    <React.Fragment key={caseItem._id || index}>
                      <ListItem>
                        <ListItemIcon>
                          <TimelineIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={`${caseItem.nom_client} - ${caseItem.type_contentieux}`}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                {caseItem.description}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                ID: {caseItem.dossier_id} | Statut: {caseItem.status} | 
                                Créé: {new Date(caseItem.created_at).toLocaleDateString()}
                              </Typography>
                            </Box>
                          }
                        />
                        <Box>
                          <Button 
                            size="small" 
                            onClick={() => getCaseById(caseItem.dossier_id)}
                            sx={{ mr: 1 }}
                          >
                            Détails
                          </Button>
                          <Button 
                            size="small" 
                            color="primary"
                            onClick={() => handleEditCase(caseItem)}
                            sx={{ mr: 1 }}
                          >
                            Modifier
                          </Button>
                          <Button 
                            size="small" 
                            color="error"
                            onClick={() => handleDeleteCase(caseItem)}
                          >
                            Supprimer
                          </Button>
                        </Box>
                      </ListItem>
                      {index < cases.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Détails du dossier courant */}
        {currentCase && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📋 Détails du dossier: {currentCase.nom_client}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2"><strong>ID:</strong> {currentCase.dossier_id}</Typography>
                    <Typography variant="body2"><strong>Type:</strong> {currentCase.type_contentieux}</Typography>
                    <Typography variant="body2"><strong>Statut:</strong> {currentCase.status}</Typography>
                    <Typography variant="body2"><strong>Nationalité:</strong> {currentCase.nationalite}</Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2"><strong>Urgence:</strong> {currentCase.urgence}</Typography>
                    <Typography variant="body2"><strong>Créé par:</strong> {currentCase.created_by}</Typography>
                    <Typography variant="body2"><strong>Créé le:</strong> {new Date(currentCase.created_at).toLocaleString()}</Typography>
                    <Typography variant="body2"><strong>Modifié le:</strong> {new Date(currentCase.updated_at).toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2"><strong>Description:</strong></Typography>
                    <Typography variant="body2" sx={{ mt: 1, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
                      {currentCase.description}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Dialog de création de dossier */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Créer un nouveau dossier MongoDB Atlas</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Nom du client"
              value={newCaseData.nom_client}
              onChange={(e) => setNewCaseData({ ...newCaseData, nom_client: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              select
              label="Type de contentieux"
              value={newCaseData.type_contentieux}
              onChange={(e) => setNewCaseData({ ...newCaseData, type_contentieux: e.target.value })}
              margin="normal"
              SelectProps={{ native: true }}
            >
              <option value="OQTF">OQTF</option>
              <option value="Titre de séjour">Titre de séjour</option>
              <option value="Regroupement familial">Regroupement familial</option>
              <option value="Naturalisation">Naturalisation</option>
              <option value="Asile">Asile</option>
            </TextField>
            <TextField
              fullWidth
              label="Nationalité"
              value={newCaseData.nationalite}
              onChange={(e) => setNewCaseData({ ...newCaseData, nationalite: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              select
              label="Urgence"
              value={newCaseData.urgence}
              onChange={(e) => setNewCaseData({ ...newCaseData, urgence: e.target.value })}
              margin="normal"
              SelectProps={{ native: true }}
            >
              <option value="faible">Faible</option>
              <option value="normale">Normale</option>
              <option value="élevée">Élevée</option>
              <option value="critique">Critique</option>
            </TextField>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Description du dossier"
              value={newCaseData.description}
              onChange={(e) => setNewCaseData({ ...newCaseData, description: e.target.value })}
              margin="normal"
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Annuler</Button>
          <Button 
            onClick={handleCreateCase} 
            variant="contained"
            disabled={casesLoading}
          >
            {casesLoading ? <CircularProgress size={20} /> : 'Créer'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de modification de dossier */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Modifier le dossier: {selectedCase?.nom_client}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Nom du client"
              value={editCaseData.nom_client || ''}
              onChange={(e) => setEditCaseData({ ...editCaseData, nom_client: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              select
              label="Type de contentieux"
              value={editCaseData.type_contentieux || 'OQTF'}
              onChange={(e) => setEditCaseData({ ...editCaseData, type_contentieux: e.target.value })}
              margin="normal"
              SelectProps={{ native: true }}
            >
              <option value="OQTF">OQTF</option>
              <option value="Titre de séjour">Titre de séjour</option>
              <option value="Regroupement familial">Regroupement familial</option>
              <option value="Naturalisation">Naturalisation</option>
              <option value="Asile">Asile</option>
            </TextField>
            <TextField
              fullWidth
              label="Nationalité"
              value={editCaseData.nationalite || ''}
              onChange={(e) => setEditCaseData({ ...editCaseData, nationalite: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              select
              label="Urgence"
              value={editCaseData.urgence || 'normale'}
              onChange={(e) => setEditCaseData({ ...editCaseData, urgence: e.target.value })}
              margin="normal"
              SelectProps={{ native: true }}
            >
              <option value="faible">Faible</option>
              <option value="normale">Normale</option>
              <option value="élevée">Élevée</option>
              <option value="critique">Critique</option>
            </TextField>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Description du dossier"
              value={editCaseData.description || ''}
              onChange={(e) => setEditCaseData({ ...editCaseData, description: e.target.value })}
              margin="normal"
              required
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Annuler</Button>
          <Button 
            onClick={handleUpdateCase} 
            variant="contained"
            disabled={casesLoading}
          >
            {casesLoading ? <CircularProgress size={20} /> : 'Modifier'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de confirmation de suppression */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="sm">
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le dossier de <strong>{selectedCase?.nom_client}</strong> ?
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Cette action est irréversible.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Annuler</Button>
          <Button 
            onClick={handleConfirmDelete} 
            variant="contained"
            color="error"
            disabled={casesLoading}
          >
            {casesLoading ? <CircularProgress size={20} /> : 'Supprimer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MongoDBAtlasTest;
