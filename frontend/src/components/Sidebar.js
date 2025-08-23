/**
 * Sidebar - Navigation latérale DEFENSEUR-IA
 */

import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Box,
  Typography,
  Divider,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Folder as FolderIcon,
  People as PeopleIcon,
  Description as DocumentIcon,
  Event as EventIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
  Gavel as GavelIcon,
  AutoAwesome as AIIcon,
  Chat as ChatIcon,
  SmartToy as RobotIcon,
  PlayCircleOutline as PlaygroundIcon,
} from '@mui/icons-material';

const DRAWER_WIDTH = 280;

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    {
      text: 'Tableau de bord',
      icon: <DashboardIcon />,
      path: '/dashboard',
      description: 'Vue d\'ensemble des dossiers'
    },
    {
      text: 'Dossiers',
      icon: <FolderIcon />,
      path: '/cases',
      description: 'Gestion des dossiers juridiques',
      badge: 'Nouveau'
    },
    {
      text: 'Clients',
      icon: <PeopleIcon />,
      path: '/clients',
      description: 'Base de données des justiciables'
    },
    {
      text: 'Documents',
      icon: <DocumentIcon />,
      path: '/documents',
      description: 'Pièces et documents générés'
    },
    {
      text: 'Rendez-vous',
      icon: <EventIcon />,
      path: '/appointments',
      description: 'Calendrier et planification'
    },
    {
      text: 'Pipeline IA',
      icon: <TimelineIcon />,
      path: '/pipeline',
      description: 'Monitoring du traitement IA',
      badge: 'Live'
    },
    {
      text: 'Agents & Flows',
      icon: <RobotIcon />,
      path: '/agents-flows',
      description: 'Monitoring détaillé des 12 agents',
      badge: '🚀'
    },
    {
      text: 'Flow Playground',
      icon: <PlaygroundIcon />,
      path: '/flow-playground',
      description: 'Interface procédurale interactive',
      badge: '🎮'
    },
    {
      text: 'Assistant IA',
      icon: <ChatIcon />,
      path: '/chat',
      description: 'Interface conversationnelle',
      badge: 'Nouveau'
    },
  ];

  const bottomMenuItems = [
    {
      text: 'Paramètres',
      icon: <SettingsIcon />,
      path: '/settings',
      description: 'Configuration système'
    },
  ];

  const handleNavigation = (path) => {
    navigate(path);
  };

  const isActive = (path) => {
    return location.pathname === path || (path === '/dashboard' && location.pathname === '/');
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          backgroundColor: 'background.paper',
          borderRight: '1px solid',
          borderRightColor: 'divider',
        },
      }}
    >
      {/* Header */}
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
          <GavelIcon sx={{ color: 'primary.main', fontSize: 32, mr: 1 }} />
          <AIIcon sx={{ color: 'secondary.main', fontSize: 24 }} />
        </Box>
        <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
          DEFENSEUR-IA
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Assistant juridique intelligent
        </Typography>
      </Box>

      <Divider />

      {/* Navigation principale */}
      <Box sx={{ flexGrow: 1, py: 2 }}>
        <List sx={{ px: 2 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive(item.path) ? 'inherit' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {item.text}
                      </Typography>
                      {item.badge && (
                        <Chip
                          label={item.badge}
                          size="small"
                          color={item.badge === 'Live' ? 'success' : 'secondary'}
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {item.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      <Divider />

      {/* Navigation secondaire */}
      <Box sx={{ py: 2 }}>
        <List sx={{ px: 2 }}>
          {bottomMenuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive(item.path) ? 'inherit' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {item.text}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {item.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Version 1.0.0
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          © 2024 AvocatX
        </Typography>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
