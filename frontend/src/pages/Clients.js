/**
 * Clients - Gestion des clients/justiciables DEFENSEUR-IA
 */

import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Email as EmailIcon,
  LocationOn as LocationIcon,
  MoreVert as MoreVertIcon,
  Phone as PhoneIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  InputAdornment,
  ListItemText,
  Menu,
  MenuItem,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  List,
  ListItem,
  ListItemAvatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import React, { useState } from 'react';
import { useClients } from '../hooks/useAPI';
import { useNotifications } from '../hooks/useNotifications';

const Clients = () => {
  const { clients, _loading, _searchClients, createClient, updateClient, deleteClient } = useClients();
  const { showSuccess, showError, showInfo } = useNotifications();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedClient, setSelectedClient] = useState(null);
  const [newClientDialog, setNewClientDialog] = useState(false);
  const [editClientDialog, setEditClientDialog] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [viewMode, setViewMode] = useState('table'); // 'table' ou 'cards'
  
  const [newClientData, setNewClientData] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    adresse: '',
    nationalite: '',
    situation: '',
    notes: '',
  });

  // Mock clients si pas encore de données du backend
  const mockClients = clients.length > 0 ? clients : [
    {
      id: 1,
      nom: 'Dubois',
      prenom: 'Marie',
      email: 'marie.dubois@email.com',
      telephone: '+33 6 12 34 56 78',
      adresse: '123 Rue de la République, 75001 Paris',
      nationalite: 'Française',
      situation: 'OQTF en cours',
      dossiers_count: 2,
      created_at: '2024-01-15T10:30:00Z',
      last_contact: '2024-01-27T14:25:00Z',
    },
    {
      id: 2,
      nom: 'Benali',
      prenom: 'Ahmed',
      email: 'ahmed.benali@email.com',
      telephone: '+33 7 98 76 54 32',
      adresse: '456 Avenue des Champs, 69000 Lyon',
      nationalite: 'Algérienne',
      situation: 'Demande de titre de séjour',
      dossiers_count: 1,
      created_at: '2024-01-20T15:45:00Z',
      last_contact: '2024-01-26T09:15:00Z',
    },
    {
      id: 3,
      nom: 'Silva',
      prenom: 'Carlos',
      email: 'carlos.silva@email.com',
      telephone: '+33 6 55 44 33 22',
      adresse: '789 Boulevard Saint-Michel, 13000 Marseille',
      nationalite: 'Brésilienne',
      situation: 'Recours administratif',
      dossiers_count: 3,
      created_at: '2024-01-10T08:20:00Z',
      last_contact: '2024-01-25T16:30:00Z',
    },
  ];

  const displayClients = mockClients.filter(client =>
    `${client.prenom} ${client.nom}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
    client.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    client.situation.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleMenuOpen = (event, client) => {
    setAnchorEl(event.currentTarget);
    setSelectedClient(client);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedClient(null);
  };

  const handleCreateClient = async () => {
    if (!newClientData.nom.trim() || !newClientData.prenom.trim()) {
      showError('Veuillez saisir le nom et prénom du client');
      return;
    }

    if (!newClientData.email.trim()) {
      showError('Veuillez saisir l\'adresse email du client');
      return;
    }

    showInfo('Création du client en cours...');
    
    try {
      await createClient(newClientData);
      showSuccess(`Client ${newClientData.prenom} ${newClientData.nom} créé avec succès`);
      setNewClientDialog(false);
      setNewClientData({
        nom: '',
        prenom: '',
        email: '',
        telephone: '',
        adresse: '',
        nationalite: '',
        situation: '',
        notes: '',
      });
    } catch (error) {
      console.error('Erreur création client:', error);
      showError('Erreur lors de la création du client. Veuillez réessayer.');
    }
  };

  const handleEditClient = () => {
    setNewClientData(selectedClient);
    setEditClientDialog(true);
    handleMenuClose();
  };

  const handleUpdateClient = async () => {
    try {
      await updateClient(selectedClient.id, newClientData);
      setEditClientDialog(false);
      setNewClientData({
        nom: '',
        prenom: '',
        email: '',
        telephone: '',
        adresse: '',
        nationalite: '',
        situation: '',
        notes: '',
      });
    } catch (error) {
      console.error('Erreur modification client:', error);
    }
  };

  const handleDeleteClient = async () => {
    if (selectedClient) {
      try {
        await deleteClient(selectedClient.id);
        setDeleteDialog(false);
        handleMenuClose();
      } catch (error) {
        console.error('Erreur suppression client:', error);
      }
    }
  };

  const getInitials = (prenom, nom) => {
    return `${prenom.charAt(0)}${nom.charAt(0)}`.toUpperCase();
  };

  const getSituationColor = (situation) => {
    if (situation.includes('OQTF')) return 'error';
    if (situation.includes('Recours')) return 'warning';
    if (situation.includes('Demande')) return 'info';
    return 'default';
  };

  return (
    <Box>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            Clients
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gestion de la base de données des justiciables
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setNewClientDialog(true)}
        >
          Nouveau client
        </Button>
      </Box>

      {/* Barre de recherche et filtres */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Rechercher par nom, email, situation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Affichage</InputLabel>
                <Select
                  value={viewMode}
                  label="Affichage"
                  onChange={(e) => setViewMode(e.target.value)}
                >
                  <MenuItem value="table">Tableau</MenuItem>
                  <MenuItem value="cards">Cartes</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                {displayClients.length} client(s) trouvé(s)
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Affichage en tableau */}
      {viewMode === 'table' && (
        <Card>
          <CardContent>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Client</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Situation</TableCell>
                  <TableCell>Dossiers</TableCell>
                  <TableCell>Dernier contact</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {displayClients.map((client) => (
                  <TableRow key={client.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          {getInitials(client.prenom, client.nom)}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {client.prenom} {client.nom}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {client.nationalite}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <EmailIcon fontSize="small" color="action" />
                          {client.email}
                        </Typography>
                        <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                          <PhoneIcon fontSize="small" color="action" />
                          {client.telephone}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={client.situation}
                        size="small"
                        color={getSituationColor(client.situation)}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <LocationIcon fontSize="small" color="action" />
                        <Typography variant="body2">
                          {client.dossiers_count} dossier(s)
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(client.last_contact).toLocaleDateString('fr-FR')}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, client)}
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Affichage en cartes */}
      {viewMode === 'cards' && (
        <Grid container spacing={3}>
          {displayClients.map((client) => (
            <Grid item xs={12} sm={6} md={4} key={client.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        {getInitials(client.prenom, client.nom)}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {client.prenom} {client.nom}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {client.nationalite}
                        </Typography>
                      </Box>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, client)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </Box>

                  <Chip
                    label={client.situation}
                    size="small"
                    color={getSituationColor(client.situation)}
                    variant="outlined"
                    sx={{ mb: 2 }}
                  />

                  <List dense>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <EmailIcon fontSize="small" color="action" />
                      </ListItemAvatar>
                      <ListItemText
                        primary={client.email}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <PhoneIcon fontSize="small" color="action" />
                      </ListItemAvatar>
                      <ListItemText
                        primary={client.telephone}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemAvatar>
                        <LocationIcon fontSize="small" color="action" />
                      </ListItemAvatar>
                      <ListItemText
                        primary={`${client.dossiers_count} dossier(s)`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  </List>

                  <Typography variant="caption" color="text.secondary">
                    Dernier contact: {new Date(client.last_contact).toLocaleDateString('fr-FR')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Menu contextuel */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditClient}>
          <EditIcon sx={{ mr: 2 }} />
          Modifier
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <LocationIcon sx={{ mr: 2 }} />
          Voir les dossiers
        </MenuItem>
        <MenuItem onClick={() => {
          setDeleteDialog(true);
          handleMenuClose();
        }}>
          <DeleteIcon sx={{ mr: 2 }} />
          Supprimer
        </MenuItem>
      </Menu>

      {/* Dialog nouveau client */}
      <Dialog open={newClientDialog} onClose={() => setNewClientDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Ajouter un nouveau client</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Prénom"
                  value={newClientData.prenom}
                  onChange={(e) => setNewClientData({ ...newClientData, prenom: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nom"
                  value={newClientData.nom}
                  onChange={(e) => setNewClientData({ ...newClientData, nom: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={newClientData.email}
                  onChange={(e) => setNewClientData({ ...newClientData, email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Téléphone"
                  value={newClientData.telephone}
                  onChange={(e) => setNewClientData({ ...newClientData, telephone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Adresse"
                  value={newClientData.adresse}
                  onChange={(e) => setNewClientData({ ...newClientData, adresse: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nationalité"
                  value={newClientData.nationalite}
                  onChange={(e) => setNewClientData({ ...newClientData, nationalite: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Situation</InputLabel>
                  <Select
                    value={newClientData.situation}
                    label="Situation"
                    onChange={(e) => setNewClientData({ ...newClientData, situation: e.target.value })}
                  >
                    <MenuItem value="OQTF en cours">OQTF en cours</MenuItem>
                    <MenuItem value="Demande de titre de séjour">Demande de titre de séjour</MenuItem>
                    <MenuItem value="Recours administratif">Recours administratif</MenuItem>
                    <MenuItem value="Contentieux">Contentieux</MenuItem>
                    <MenuItem value="Aide juridictionnelle">Aide juridictionnelle</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Notes"
                  value={newClientData.notes}
                  onChange={(e) => setNewClientData({ ...newClientData, notes: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewClientDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" onClick={handleCreateClient}>
            Créer le client
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog modification client */}
      <Dialog open={editClientDialog} onClose={() => setEditClientDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Modifier le client</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Prénom"
                  value={newClientData.prenom}
                  onChange={(e) => setNewClientData({ ...newClientData, prenom: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nom"
                  value={newClientData.nom}
                  onChange={(e) => setNewClientData({ ...newClientData, nom: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={newClientData.email}
                  onChange={(e) => setNewClientData({ ...newClientData, email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Téléphone"
                  value={newClientData.telephone}
                  onChange={(e) => setNewClientData({ ...newClientData, telephone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Adresse"
                  value={newClientData.adresse}
                  onChange={(e) => setNewClientData({ ...newClientData, adresse: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Nationalité"
                  value={newClientData.nationalite}
                  onChange={(e) => setNewClientData({ ...newClientData, nationalite: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Situation</InputLabel>
                  <Select
                    value={newClientData.situation}
                    label="Situation"
                    onChange={(e) => setNewClientData({ ...newClientData, situation: e.target.value })}
                  >
                    <MenuItem value="OQTF en cours">OQTF en cours</MenuItem>
                    <MenuItem value="Demande de titre de séjour">Demande de titre de séjour</MenuItem>
                    <MenuItem value="Recours administratif">Recours administratif</MenuItem>
                    <MenuItem value="Contentieux">Contentieux</MenuItem>
                    <MenuItem value="Aide juridictionnelle">Aide juridictionnelle</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Notes"
                  value={newClientData.notes}
                  onChange={(e) => setNewClientData({ ...newClientData, notes: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditClientDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" onClick={handleUpdateClient}>
            Sauvegarder
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog suppression */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Supprimer le client</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le client <strong>{selectedClient?.prenom} {selectedClient?.nom}</strong> ?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Cette action supprimera également tous les dossiers associés.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" color="error" onClick={handleDeleteClient}>
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Clients;
