import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';

const NewCaseDialog = ({ 
  open, 
  onClose, 
  onSubmit, 
  loading = false 
}) => {
  const [formData, setFormData] = useState({
    nom_justiciable: '',
    type_contentieux: 'OQTF',
    urgence: 'normale',
    description: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Effacer l'erreur si le champ est maintenant valide
    if (errors[field] && value.trim()) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.nom_justiciable.trim()) {
      newErrors.nom_justiciable = 'Le nom du justiciable est requis';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'La description est requise';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleClose = () => {
    // Réinitialiser le formulaire
    setFormData({
      nom_justiciable: '',
      type_contentieux: 'OQTF',
      urgence: 'normale',
      description: ''
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { minHeight: '500px' }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        🆕 Créer un nouveau dossier
      </DialogTitle>
      
      <DialogContent sx={{ pt: 2 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          
          {/* Nom du justiciable */}
          <TextField
            autoFocus
            label="Nom du justiciable *"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.nom_justiciable}
            onChange={(e) => handleChange('nom_justiciable', e.target.value)}
            error={!!errors.nom_justiciable}
            helperText={errors.nom_justiciable}
            placeholder="Ex: Ahmed Benali"
          />
          
          {/* Type de contentieux */}
          <FormControl fullWidth variant="outlined">
            <InputLabel>Type de contentieux</InputLabel>
            <Select
              value={formData.type_contentieux}
              onChange={(e) => handleChange('type_contentieux', e.target.value)}
              label="Type de contentieux"
            >
              <MenuItem value="OQTF">OQTF</MenuItem>
              <MenuItem value="TITRE_SEJOUR">Titre de séjour</MenuItem>
              <MenuItem value="REGROUPEMENT_FAMILIAL">Regroupement familial</MenuItem>
              <MenuItem value="NATURALISATION">Naturalisation</MenuItem>
              <MenuItem value="ASILE">Demande d'asile</MenuItem>
              <MenuItem value="AUTRE">Autre</MenuItem>
            </Select>
          </FormControl>

          {/* Niveau d'urgence */}
          <FormControl fullWidth variant="outlined">
            <InputLabel>Niveau d'urgence</InputLabel>
            <Select
              value={formData.urgence}
              onChange={(e) => handleChange('urgence', e.target.value)}
              label="Niveau d'urgence"
            >
              <MenuItem value="faible">🟢 Faible</MenuItem>
              <MenuItem value="normale">🟡 Normale</MenuItem>
              <MenuItem value="elevee">🟠 Élevée</MenuItem>
              <MenuItem value="critique">🔴 Critique</MenuItem>
            </Select>
          </FormControl>

          {/* Description */}
          <TextField
            label="Description du cas *"
            multiline
            rows={4}
            fullWidth
            variant="outlined"
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            error={!!errors.description}
            helperText={errors.description || "Décrivez brièvement la situation du justiciable..."}
            placeholder="Ex: Demande de régularisation suite à OQTF reçue le 20/07/2025. Situation familiale complexe avec enfants scolarisés."
          />

          {/* Affichage des erreurs globales */}
          {Object.keys(errors).length > 0 && (
            <Alert severity="error">
              Veuillez corriger les erreurs ci-dessus avant de continuer.
            </Alert>
          )}
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 3, pt: 2 }}>
        <Button 
          onClick={handleClose}
          color="inherit"
          disabled={loading}
        >
          Annuler
        </Button>
        <Button 
          onClick={handleSubmit}
          variant="contained"
          color="primary"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Création...' : 'Créer le dossier'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NewCaseDialog;
