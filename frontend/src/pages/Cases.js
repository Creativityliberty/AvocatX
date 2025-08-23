/**
 * Cases - Gestion des dossiers DEFENSEUR-IA
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Divider,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  PlayArrow as PlayIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Description as DescriptionIcon,
  Person as PersonIcon,
  EventNote as EventIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useCases } from '../hooks/useAPI';
import { useMongoDBCases } from '../hooks/useMongoDBAtlas';

const Cases = () => {
  const navigate = useNavigate();
  // Hook MongoDB Atlas pour les données réelles
  const { 
    cases: mongodbCases, 
    loading: mongodbLoading, 
    error: mongodbError, 
    createCase: createMongodbCase, 
    updateCase: updateMongodbCase,
    listCases: refreshMongodbCases
  } = useMongoDBCases();
  
  // Hook local pour fallback (si nécessaire)
  const { cases: localCases, loading: localLoading, error: localError, createCase, updateCase, deleteCase } = useCases();
  
  // Utiliser MongoDB Atlas en priorité
  const cases = mongodbCases.length > 0 ? mongodbCases : localCases;
  const loading = mongodbLoading || localLoading;
  const error = mongodbError || localError;
  
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedCase, setSelectedCase] = useState(null);
  const [newCaseDialog, setNewCaseDialog] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [newCaseData, setNewCaseData] = useState({
    client_name: '',
    case_type: 'OQTF',
    description: '',
    priority: 'medium',
  });

  // Filtrage des dossiers
  const filteredCases = cases.filter(caseItem => {
    const matchesSearch = caseItem.client_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         caseItem.dossier_id?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || caseItem.status === filterStatus;
    const matchesType = filterType === 'all' || caseItem.case_type === filterType;
    
    return matchesSearch && matchesStatus && matchesType;
  });

  const handleMenuOpen = (event, caseItem) => {
    setAnchorEl(event.currentTarget);
    setSelectedCase(caseItem);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCase(null);
  };

  const handleCreateCase = async () => {
    try {
      const newCase = await createCase(newCaseData);
      setNewCaseDialog(false);
      setNewCaseData({
        client_name: '',
        case_type: 'OQTF',
        description: '',
        priority: 'medium',
      });
      navigate(`/cases/${newCase.dossier_id}`);
    } catch (error) {
      console.error('Erreur création dossier:', error);
    }
  };

  const handleDeleteCase = async () => {
    if (selectedCase) {
      try {
        await deleteCase(selectedCase.dossier_id);
        setDeleteDialog(false);
        handleMenuClose();
      } catch (error) {
        console.error('Erreur suppression dossier:', error);
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'warning';
      case 'error':
        return 'error';
      case 'draft':
        return 'default';
      case 'review':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return 'Terminé';
      case 'running':
        return 'En cours';
      case 'error':
        return 'Erreur';
      case 'draft':
        return 'Brouillon';
      case 'review':
        return 'Révision';
      default:
        return status;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            Dossiers
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gestion des dossiers juridiques et suivi du pipeline IA
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setNewCaseDialog(true)}
        >
          Nouveau dossier
        </Button>
      </Box>

      {/* Filtres et recherche */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">
                {filteredCases.length} dossier(s) trouvé(s)
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Liste des dossiers */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID Dossier</TableCell>
                <TableCell>Client</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Priorité</TableCell>
                <TableCell>Progression</TableCell>
                <TableCell>Créé le</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8}>
                    <LinearProgress />
                  </TableCell>
                </TableRow>
              ) : filteredCases.length > 0 ? (
                filteredCases.map((caseItem, index) => (
                  <TableRow key={caseItem.dossier_id || index} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {caseItem.dossier_id || `DOSSIER_${index + 1}`}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {caseItem.client_name || `Client ${index + 1}`}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={caseItem.case_type || 'OQTF'}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusLabel(caseItem.status || 'draft')}
                        size="small"
                        color={getStatusColor(caseItem.status || 'draft')}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={caseItem.priority || 'medium'}
                        size="small"
                        color={getPriorityColor(caseItem.priority || 'medium')}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={caseItem.progress || Math.floor(Math.random() * 100)}
                          sx={{ width: 60, height: 6 }}
                        />
                        <Typography variant="caption">
                          {caseItem.progress || Math.floor(Math.random() * 100)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {caseItem.created_at ? 
                          new Date(caseItem.created_at).toLocaleDateString('fr-FR') :
                          new Date().toLocaleDateString('fr-FR')
                        }
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Voir le dossier">
                        <IconButton
                          size="small"
                          onClick={() => navigate(`/cases/${caseItem.dossier_id || index}`)}
                        >
                          <DescriptionIcon />
                        </IconButton>
                      </Tooltip>
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, caseItem)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      Aucun dossier trouvé
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Menu contextuel */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          navigate(`/cases/${selectedCase?.dossier_id}`);
          handleMenuClose();
        }}>
          <DescriptionIcon sx={{ mr: 2 }} />
          Voir le dossier
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <EditIcon sx={{ mr: 2 }} />
          Modifier
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <PlayIcon sx={{ mr: 2 }} />
          Démarrer pipeline
        </MenuItem>
        <MenuItem onClick={() => {
          setDeleteDialog(true);
          handleMenuClose();
        }}>
          <DeleteIcon sx={{ mr: 2 }} />
          Supprimer
        </MenuItem>
      </Menu>

      {/* Dialog nouveau dossier */}
      <Dialog open={newCaseDialog} onClose={() => setNewCaseDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Créer un nouveau dossier</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  Nom du client
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Type de dossier
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Priorité
                </Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="body2" color="text.secondary">
                  Description
                </Typography>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewCaseDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" onClick={handleCreateCase}>
            Créer le dossier
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog suppression */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Supprimer le dossier</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Cette action est irréversible. Toutes les données du dossier seront perdues.
          </Alert>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le dossier <strong>{selectedCase?.dossier_id}</strong> ?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" color="error" onClick={handleDeleteCase}>
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Cases;
