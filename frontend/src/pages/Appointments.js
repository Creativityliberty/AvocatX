/**
 * Appointments - Gestion des rendez-vous DEFENSEUR-IA
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
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Paper,
  Divider,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Event as EventIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  LocationOn as LocationIcon,
  VideoCall as VideoCallIcon,
  Phone as PhoneIcon,
  MoreVert as MoreIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Today as TodayIcon,
  CalendarMonth as CalendarIcon,
} from '@mui/icons-material';
import { useAppointments } from '../hooks/useAPI';

const Appointments = () => {
  const { appointments, loading, createAppointment, updateAppointment, deleteAppointment } = useAppointments();
  
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [viewMode, setViewMode] = useState('day'); // 'day', 'week', 'month'
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [newAppointmentDialog, setNewAppointmentDialog] = useState(false);
  const [editAppointmentDialog, setEditAppointmentDialog] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  
  const [newAppointmentData, setNewAppointmentData] = useState({
    client_name: '',
    client_id: '',
    title: '',
    description: '',
    date: '',
    time: '',
    duration: 60,
    type: 'consultation',
    location: 'Bureau',
    status: 'scheduled',
  });

  // Mock appointments si pas encore de données du backend
  const mockAppointments = appointments.length > 0 ? appointments : [
    {
      id: 1,
      client_name: 'Marie Dubois',
      client_id: 1,
      title: 'Consultation OQTF',
      description: 'Première consultation pour dossier OQTF',
      date: '2024-01-27',
      time: '14:00',
      duration: 60,
      type: 'consultation',
      location: 'Bureau',
      status: 'scheduled',
      created_at: '2024-01-25T10:00:00Z',
    },
    {
      id: 2,
      client_name: 'Ahmed Benali',
      client_id: 2,
      title: 'Suivi dossier',
      description: 'Point sur l\'avancement du recours',
      date: '2024-01-27',
      time: '16:30',
      duration: 45,
      type: 'suivi',
      location: 'Visioconférence',
      status: 'scheduled',
      created_at: '2024-01-26T14:30:00Z',
    },
    {
      id: 3,
      client_name: 'Carlos Silva',
      client_id: 3,
      title: 'Signature documents',
      description: 'Signature de la requête finale',
      date: '2024-01-28',
      time: '10:00',
      duration: 30,
      type: 'signature',
      location: 'Bureau',
      status: 'scheduled',
      created_at: '2024-01-26T16:00:00Z',
    },
    {
      id: 4,
      client_name: 'Marie Dubois',
      client_id: 1,
      title: 'Préparation audience',
      description: 'Préparation pour l\'audience du tribunal',
      date: '2024-01-29',
      time: '09:00',
      duration: 90,
      type: 'preparation',
      location: 'Bureau',
      status: 'scheduled',
      created_at: '2024-01-27T08:00:00Z',
    },
  ];

  // Filtrer les rendez-vous par date sélectionnée
  const todayAppointments = mockAppointments.filter(apt => apt.date === selectedDate);
  const upcomingAppointments = mockAppointments.filter(apt => new Date(apt.date) > new Date(selectedDate));

  const handleMenuOpen = (event, appointment) => {
    setAnchorEl(event.currentTarget);
    setSelectedAppointment(appointment);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedAppointment(null);
  };

  const handleCreateAppointment = async () => {
    try {
      await createAppointment(newAppointmentData);
      setNewAppointmentDialog(false);
      setNewAppointmentData({
        client_name: '',
        client_id: '',
        title: '',
        description: '',
        date: '',
        time: '',
        duration: 60,
        type: 'consultation',
        location: 'Bureau',
        status: 'scheduled',
      });
    } catch (error) {
      console.error('Erreur création rendez-vous:', error);
    }
  };

  const handleEditAppointment = () => {
    setNewAppointmentData(selectedAppointment);
    setEditAppointmentDialog(true);
    handleMenuClose();
  };

  const handleUpdateAppointment = async () => {
    try {
      await updateAppointment(selectedAppointment.id, newAppointmentData);
      setEditAppointmentDialog(false);
      setNewAppointmentData({
        client_name: '',
        client_id: '',
        title: '',
        description: '',
        date: '',
        time: '',
        duration: 60,
        type: 'consultation',
        location: 'Bureau',
        status: 'scheduled',
      });
    } catch (error) {
      console.error('Erreur modification rendez-vous:', error);
    }
  };

  const handleDeleteAppointment = async () => {
    if (selectedAppointment) {
      try {
        await deleteAppointment(selectedAppointment.id);
        setDeleteDialog(false);
        handleMenuClose();
      } catch (error) {
        console.error('Erreur suppression rendez-vous:', error);
      }
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'consultation':
        return 'primary';
      case 'suivi':
        return 'info';
      case 'signature':
        return 'success';
      case 'preparation':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'consultation':
        return 'Consultation';
      case 'suivi':
        return 'Suivi';
      case 'signature':
        return 'Signature';
      case 'preparation':
        return 'Préparation';
      default:
        return type;
    }
  };

  const getLocationIcon = (location) => {
    if (location.includes('Visio') || location.includes('Video')) {
      return <VideoCallIcon />;
    }
    if (location.includes('Téléphone')) {
      return <PhoneIcon />;
    }
    return <LocationIcon />;
  };

  return (
    <Box>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            Rendez-vous
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gestion du planning et des consultations clients
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setNewAppointmentDialog(true)}
        >
          Nouveau rendez-vous
        </Button>
      </Box>

      {/* Sélecteur de date et vue */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="date"
                label="Date sélectionnée"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Vue</InputLabel>
                <Select
                  value={viewMode}
                  label="Vue"
                  onChange={(e) => setViewMode(e.target.value)}
                >
                  <MenuItem value="day">Jour</MenuItem>
                  <MenuItem value="week">Semaine</MenuItem>
                  <MenuItem value="month">Mois</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<TodayIcon />}
                  onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
                >
                  Aujourd'hui
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CalendarIcon />}
                >
                  Calendrier
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Rendez-vous du jour */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Rendez-vous du {new Date(selectedDate).toLocaleDateString('fr-FR', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </Typography>

              {todayAppointments.length > 0 ? (
                <List>
                  {todayAppointments
                    .sort((a, b) => a.time.localeCompare(b.time))
                    .map((appointment, index) => (
                    <React.Fragment key={appointment.id}>
                      <ListItem
                        sx={{
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 2,
                          mb: 2,
                          backgroundColor: 'background.paper',
                        }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: `${getTypeColor(appointment.type)}.main` }}>
                            <EventIcon />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                                {appointment.title}
                              </Typography>
                              <Chip
                                label={getTypeLabel(appointment.type)}
                                size="small"
                                color={getTypeColor(appointment.type)}
                                variant="outlined"
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                <PersonIcon fontSize="small" />
                                {appointment.client_name}
                              </Typography>
                              <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                <ScheduleIcon fontSize="small" />
                                {appointment.time} ({appointment.duration} min)
                              </Typography>
                              <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                                {getLocationIcon(appointment.location)}
                                {appointment.location}
                              </Typography>
                              {appointment.description && (
                                <Typography variant="body2" color="text.secondary">
                                  {appointment.description}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                        <IconButton
                          onClick={(e) => handleMenuOpen(e, appointment)}
                        >
                          <MoreIcon />
                        </IconButton>
                      </ListItem>
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Alert severity="info">
                  Aucun rendez-vous prévu pour cette date.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar - Rendez-vous à venir */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                Prochains rendez-vous
              </Typography>

              {upcomingAppointments.length > 0 ? (
                <List dense>
                  {upcomingAppointments
                    .sort((a, b) => new Date(a.date + ' ' + a.time) - new Date(b.date + ' ' + b.time))
                    .slice(0, 5)
                    .map((appointment, index) => (
                    <React.Fragment key={appointment.id}>
                      <ListItem sx={{ px: 0 }}>
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: `${getTypeColor(appointment.type)}.light`, width: 32, height: 32 }}>
                            <EventIcon fontSize="small" />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={appointment.title}
                          secondary={
                            <Box>
                              <Typography variant="caption" color="text.secondary">
                                {appointment.client_name}
                              </Typography>
                              <br />
                              <Typography variant="caption" color="text.secondary">
                                {new Date(appointment.date).toLocaleDateString('fr-FR')} à {appointment.time}
                              </Typography>
                            </Box>
                          }
                          primaryTypographyProps={{ variant: 'body2', fontWeight: 500 }}
                        />
                      </ListItem>
                      {index < upcomingAppointments.slice(0, 5).length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Aucun rendez-vous à venir.
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* Statistiques rapides */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Statistiques
              </Typography>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Aujourd'hui
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {todayAppointments.length} RDV
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Cette semaine
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {mockAppointments.filter(apt => {
                    const aptDate = new Date(apt.date);
                    const today = new Date();
                    const weekStart = new Date(today.setDate(today.getDate() - today.getDay()));
                    const weekEnd = new Date(today.setDate(today.getDate() - today.getDay() + 6));
                    return aptDate >= weekStart && aptDate <= weekEnd;
                  }).length} RDV
                </Typography>
              </Box>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  Total
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {mockAppointments.length} RDV
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Menu contextuel */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEditAppointment}>
          <EditIcon sx={{ mr: 2 }} />
          Modifier
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <VideoCallIcon sx={{ mr: 2 }} />
          Démarrer visio
        </MenuItem>
        <MenuItem onClick={() => {
          setDeleteDialog(true);
          handleMenuClose();
        }}>
          <DeleteIcon sx={{ mr: 2 }} />
          Supprimer
        </MenuItem>
      </Menu>

      {/* Dialog nouveau rendez-vous */}
      <Dialog open={newAppointmentDialog} onClose={() => setNewAppointmentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Nouveau rendez-vous</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Titre"
                  value={newAppointmentData.title}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, title: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Client"
                  value={newAppointmentData.client_name}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, client_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={newAppointmentData.type}
                    label="Type"
                    onChange={(e) => setNewAppointmentData({ ...newAppointmentData, type: e.target.value })}
                  >
                    <MenuItem value="consultation">Consultation</MenuItem>
                    <MenuItem value="suivi">Suivi</MenuItem>
                    <MenuItem value="signature">Signature</MenuItem>
                    <MenuItem value="preparation">Préparation</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="date"
                  label="Date"
                  value={newAppointmentData.date}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="time"
                  label="Heure"
                  value={newAppointmentData.time}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, time: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Durée (min)"
                  value={newAppointmentData.duration}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, duration: parseInt(e.target.value) })}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Lieu</InputLabel>
                  <Select
                    value={newAppointmentData.location}
                    label="Lieu"
                    onChange={(e) => setNewAppointmentData({ ...newAppointmentData, location: e.target.value })}
                  >
                    <MenuItem value="Bureau">Bureau</MenuItem>
                    <MenuItem value="Visioconférence">Visioconférence</MenuItem>
                    <MenuItem value="Téléphone">Téléphone</MenuItem>
                    <MenuItem value="Tribunal">Tribunal</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={newAppointmentData.description}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, description: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewAppointmentDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" onClick={handleCreateAppointment}>
            Créer le rendez-vous
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog modification rendez-vous */}
      <Dialog open={editAppointmentDialog} onClose={() => setEditAppointmentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Modifier le rendez-vous</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Titre"
                  value={newAppointmentData.title}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, title: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Client"
                  value={newAppointmentData.client_name}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, client_name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={newAppointmentData.type}
                    label="Type"
                    onChange={(e) => setNewAppointmentData({ ...newAppointmentData, type: e.target.value })}
                  >
                    <MenuItem value="consultation">Consultation</MenuItem>
                    <MenuItem value="suivi">Suivi</MenuItem>
                    <MenuItem value="signature">Signature</MenuItem>
                    <MenuItem value="preparation">Préparation</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="date"
                  label="Date"
                  value={newAppointmentData.date}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="time"
                  label="Heure"
                  value={newAppointmentData.time}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, time: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  type="number"
                  label="Durée (min)"
                  value={newAppointmentData.duration}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, duration: parseInt(e.target.value) })}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Lieu</InputLabel>
                  <Select
                    value={newAppointmentData.location}
                    label="Lieu"
                    onChange={(e) => setNewAppointmentData({ ...newAppointmentData, location: e.target.value })}
                  >
                    <MenuItem value="Bureau">Bureau</MenuItem>
                    <MenuItem value="Visioconférence">Visioconférence</MenuItem>
                    <MenuItem value="Téléphone">Téléphone</MenuItem>
                    <MenuItem value="Tribunal">Tribunal</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Description"
                  value={newAppointmentData.description}
                  onChange={(e) => setNewAppointmentData({ ...newAppointmentData, description: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditAppointmentDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" onClick={handleUpdateAppointment}>
            Sauvegarder
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog suppression */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Supprimer le rendez-vous</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le rendez-vous <strong>{selectedAppointment?.title}</strong> ?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>
            Annuler
          </Button>
          <Button variant="contained" color="error" onClick={handleDeleteAppointment}>
            Supprimer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Appointments;
