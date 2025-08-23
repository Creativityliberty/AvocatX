import {
    Api as ApiIcon,
    CheckCircle as CheckCircleIcon,
    Error as ErrorIcon,
    Info as InfoIcon,
    Refresh as RefreshIcon,
    Security as SecurityIcon,
    Settings as SettingsIcon,
    Speed as SpeedIcon,
    TrendingUp as TrendingUpIcon,
    Warning as WarningIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    Divider,
    IconButton,
    LinearProgress,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LegifranceWidget = ({ 
  size = 'medium', 
  showDetails = true, 
  showActions = true,
  onRefresh = null 
}) => {
  const navigate = useNavigate();
  const [apiStatus, setApiStatus] = useState({
    status: 'connected',
    environment: 'sandbox',
    lastCheck: new Date().toISOString(),
    responseTime: 245,
    quotaUsed: 1247,
    quotaLimit: 10000,
    dailyCalls: 89,
    successRate: 98.5,
    activeScopes: ['openid', 'read:codes', 'read:jurisprudence'],
    connectedAgents: 7,
    totalAgents: 12
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Simulation de récupération du statut API
    const fetchApiStatus = async () => {
      try {
        const response = await fetch('/api/legifrance/status');
        if (response.ok) {
          const data = await response.json();
          setApiStatus(data);
        }
      } catch (error) {
        console.error('Erreur récupération statut API:', error);
        setApiStatus(prev => ({ ...prev, status: 'error' }));
      }
    };

    fetchApiStatus();
    const interval = setInterval(fetchApiStatus, 30000); // Refresh toutes les 30s
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected': return <CheckCircleIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getQuotaColor = (percentage) => {
    if (percentage < 70) return 'success';
    if (percentage < 90) return 'warning';
    return 'error';
  };

  const handleRefresh = async () => {
    setLoading(true);
    try {
      if (onRefresh) {
        await onRefresh();
      } else {
        // Refresh par défaut
        const response = await fetch('/api/legifrance/refresh', { method: 'POST' });
        if (response.ok) {
          const data = await response.json();
          setApiStatus(data);
        }
      }
    } catch (error) {
      console.error('Erreur refresh:', error);
    } finally {
      setLoading(false);
    }
  };

  const quotaPercentage = (apiStatus.quotaUsed / apiStatus.quotaLimit) * 100;

  if (size === 'compact') {
    return (
      <Card sx={{ minWidth: 200 }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <ApiIcon sx={{ mr: 1 }} />
              <Typography variant="body2" fontWeight="medium">
                Légifrance
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getStatusIcon(apiStatus.status)}
              <Chip 
                label={apiStatus.environment} 
                size="small" 
                variant="outlined"
              />
            </Box>
          </Box>
          
          {showDetails && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                {apiStatus.dailyCalls} appels aujourd'hui • {apiStatus.responseTime}ms
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <ApiIcon sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6" component="h3">
              API Légifrance
            </Typography>
          </Box>
          
          {showActions && (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Actualiser le statut">
                <IconButton 
                  size="small" 
                  onClick={handleRefresh}
                  disabled={loading}
                >
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Configuration">
                <IconButton 
                  size="small" 
                  onClick={() => navigate('/api-config')}
                >
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          {getStatusIcon(apiStatus.status)}
          <Chip 
            label={apiStatus.status === 'connected' ? 'Connecté' : 'Déconnecté'} 
            color={getStatusColor(apiStatus.status)}
            size="small"
          />
          <Chip 
            label={apiStatus.environment} 
            size="small" 
            variant="outlined"
          />
        </Box>

        {showDetails && (
          <>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Quota utilisé
                </Typography>
                <Typography variant="body2">
                  {apiStatus.quotaUsed.toLocaleString()} / {apiStatus.quotaLimit.toLocaleString()}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={quotaPercentage}
                color={getQuotaColor(quotaPercentage)}
                sx={{ height: 6, borderRadius: 3 }}
              />
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="primary">
                  {apiStatus.dailyCalls}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Appels/jour
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="success.main">
                  {apiStatus.responseTime}ms
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Temps réponse
                </Typography>
              </Box>
              
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="info.main">
                  {apiStatus.successRate}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Taux succès
                </Typography>
              </Box>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <SecurityIcon sx={{ verticalAlign: 'middle', mr: 0.5, fontSize: 16 }} />
                Scopes actifs ({apiStatus.activeScopes.length})
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {apiStatus.activeScopes.map((scope) => (
                  <Chip 
                    key={scope} 
                    label={scope} 
                    size="small" 
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                <TrendingUpIcon sx={{ verticalAlign: 'middle', mr: 0.5, fontSize: 16 }} />
                Agents connectés
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LinearProgress
                  variant="determinate"
                  value={(apiStatus.connectedAgents / apiStatus.totalAgents) * 100}
                  color="primary"
                  sx={{ flex: 1, height: 6, borderRadius: 3 }}
                />
                <Typography variant="body2">
                  {apiStatus.connectedAgents}/{apiStatus.totalAgents}
                </Typography>
              </Box>
            </Box>

            {apiStatus.status === 'error' && (
              <Alert severity="error" sx={{ mb: 2 }}>
                Erreur de connexion à l'API Légifrance. Vérifiez la configuration.
              </Alert>
            )}

            {apiStatus.status === 'warning' && quotaPercentage > 90 && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                Quota API bientôt atteint ({quotaPercentage.toFixed(1)}%)
              </Alert>
            )}

            {showActions && (
              <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => navigate('/api-monitoring')}
                  startIcon={<SpeedIcon />}
                >
                  Monitoring
                </Button>
                
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => navigate('/legal-search')}
                  startIcon={<ApiIcon />}
                >
                  Recherche
                </Button>
              </Box>
            )}

            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              Dernière vérification: {new Date(apiStatus.lastCheck).toLocaleTimeString('fr-FR')}
            </Typography>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default LegifranceWidget;
