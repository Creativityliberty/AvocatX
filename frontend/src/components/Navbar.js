/**
 * Navbar - Barre de navigation supérieure DEFENSEUR-IA
 */

import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Chip,
  TextField,
  InputAdornment,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountIcon,
  Gavel as GavelIcon,
  WifiOff as OfflineIcon,
  Wifi as OnlineIcon,
} from '@mui/icons-material';
import { useBackendStatus } from '../hooks/useBackendStatus';

const Navbar = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const { isConnected, isChecking, backendInfo } = useBackendStatus();

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationsOpen = (event) => {
    setNotificationsAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setNotificationsAnchor(null);
  };

  const handleSearch = (event) => {
    if (event.key === 'Enter') {
      // Logique de recherche globale
      console.log('Recherche:', searchQuery);
    }
  };

  // Notifications mockées
  const notifications = [
    { id: 1, message: 'Pipeline terminé pour DOSSIER_20240127_142530', time: '2 min', type: 'success' },
    { id: 2, message: 'Nouveau client ajouté: Marie Dubois', time: '15 min', type: 'info' },
    { id: 3, message: 'Erreur OCR sur document_scan_001.pdf', time: '1h', type: 'error' },
  ];

  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        backgroundColor: 'background.paper',
        borderBottom: '1px solid',
        borderBottomColor: 'divider',
        color: 'text.primary'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', px: 3 }}>
        {/* Logo et titre */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <GavelIcon sx={{ color: 'primary.main', fontSize: 28 }} />
          <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
            DEFENSEUR-IA
          </Typography>
          
          {/* Statut de connexion */}
          <Chip
            icon={isConnected ? <OnlineIcon /> : <OfflineIcon />}
            label={isChecking ? 'Vérification...' : (isConnected ? 'En ligne' : 'Hors ligne')}
            size="small"
            color={isConnected ? 'success' : 'error'}
            variant="outlined"
          />
        </Box>

        {/* Barre de recherche */}
        <Box sx={{ flexGrow: 1, maxWidth: 400, mx: 4 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Rechercher dossiers, clients, documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleSearch}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'background.default',
                borderRadius: 2,
              }
            }}
          />
        </Box>

        {/* Actions utilisateur */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton
              color="inherit"
              onClick={handleNotificationsOpen}
              sx={{ color: 'text.secondary' }}
            >
              <Badge badgeContent={notifications.length} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Paramètres */}
          <Tooltip title="Paramètres">
            <IconButton
              color="inherit"
              sx={{ color: 'text.secondary' }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>

          {/* Profil utilisateur */}
          <Tooltip title="Profil">
            <IconButton
              onClick={handleProfileMenuOpen}
              sx={{ ml: 1 }}
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                A
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>

        {/* Menu profil */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={handleMenuClose}>
            <AccountIcon sx={{ mr: 2 }} />
            Mon Profil
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <SettingsIcon sx={{ mr: 2 }} />
            Paramètres
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            Déconnexion
          </MenuItem>
        </Menu>

        {/* Menu notifications */}
        <Menu
          anchorEl={notificationsAnchor}
          open={Boolean(notificationsAnchor)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          PaperProps={{
            sx: { width: 320, maxHeight: 400 }
          }}
        >
          <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="h6">Notifications</Typography>
          </Box>
          {notifications.map((notification) => (
            <MenuItem key={notification.id} onClick={handleMenuClose}>
              <Box sx={{ width: '100%' }}>
                <Typography variant="body2" sx={{ mb: 0.5 }}>
                  {notification.message}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  il y a {notification.time}
                </Typography>
              </Box>
            </MenuItem>
          ))}
          {notifications.length === 0 && (
            <MenuItem disabled>
              <Typography variant="body2" color="text.secondary">
                Aucune notification
              </Typography>
            </MenuItem>
          )}
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
