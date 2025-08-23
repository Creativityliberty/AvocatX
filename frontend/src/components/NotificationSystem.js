/**
 * NotificationSystem - Système de notifications pour feedback utilisateur
 */

import React from 'react';
import {
  Snackbar,
  Alert,
  Box,
  Slide,
} from '@mui/material';
import { useNotifications } from '../hooks/useNotifications';

const SlideTransition = (props) => {
  return <Slide {...props} direction="left" />;
};

const NotificationSystem = () => {
  const { notifications, removeNotification } = useNotifications();

  return (
    <Box sx={{ position: 'fixed', top: 80, right: 16, zIndex: 9999 }}>
      {notifications.map((notification, index) => (
        <Snackbar
          key={notification.id}
          open={true}
          autoHideDuration={4000}
          onClose={() => removeNotification(notification.id)}
          TransitionComponent={SlideTransition}
          sx={{ 
            position: 'relative',
            mb: index > 0 ? 1 : 0,
            display: 'block'
          }}
        >
          <Alert
            onClose={() => removeNotification(notification.id)}
            severity={notification.type}
            variant="filled"
            sx={{ minWidth: 300 }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};

export default NotificationSystem;
