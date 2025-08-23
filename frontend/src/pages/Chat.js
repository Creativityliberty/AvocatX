import React, { useState } from 'react';
import {
    Box,
    Container,
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    Chip,
    Alert,
    Fab,
    Tooltip
} from '@mui/material';
import {
    Chat as ChatIcon,
    SmartToy,
    Timeline,
    Description,
    Speed
} from '@mui/icons-material';
import ChatInterface from '../components/ChatInterface';

const Chat = () => {
    const [activeFlows, setActiveFlows] = useState([]);
    const [recentActivity, setRecentActivity] = useState([
        {
            id: 1,
            type: 'analysis_completed',
            message: 'Analyse OQTF terminée - 3 documents traités',
            timestamp: '2025-01-27T16:30:00Z',
            flowId: 'flow_001'
        },
        {
            id: 2,
            type: 'document_uploaded',
            message: 'Nouveau document téléchargé: decision_oqtf.pdf',
            timestamp: '2025-01-27T16:15:00Z'
        },
        {
            id: 3,
            type: 'flow_started',
            message: 'Nouveau flux démarré - Analyse juridique',
            timestamp: '2025-01-27T15:45:00Z',
            flowId: 'flow_002'
        }
    ]);

    // Callback quand un nouveau flux est créé
    const handleFlowCreate = (flow) => {
        setActiveFlows(prev => [...prev, flow]);
        setRecentActivity(prev => [{
            id: Date.now(),
            type: 'flow_started',
            message: `Nouveau flux démarré: ${flow.id}`,
            timestamp: new Date().toISOString(),
            flowId: flow.id
        }, ...prev.slice(0, 9)]); // Garder seulement les 10 derniers
    };

    // Callback quand un flux est mis à jour
    const handleFlowUpdate = (flowId, updates) => {
        setActiveFlows(prev => prev.map(flow => 
            flow.id === flowId ? { ...flow, ...updates } : flow
        ));
        
        if (updates.status === 'completed') {
            setRecentActivity(prev => [{
                id: Date.now(),
                type: 'analysis_completed',
                message: `Analyse terminée: ${flowId}`,
                timestamp: new Date().toISOString(),
                flowId: flowId
            }, ...prev.slice(0, 9)]);
        }
    };

    const getActivityIcon = (type) => {
        switch (type) {
            case 'analysis_completed':
                return <Speed color="success" />;
            case 'document_uploaded':
                return <Description color="primary" />;
            case 'flow_started':
                return <Timeline color="info" />;
            default:
                return <SmartToy />;
        }
    };

    const getActivityColor = (type) => {
        switch (type) {
            case 'analysis_completed':
                return 'success';
            case 'document_uploaded':
                return 'primary';
            case 'flow_started':
                return 'info';
            default:
                return 'default';
        }
    };

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            <Grid container spacing={3} sx={{ height: 'calc(100vh - 120px)' }}>
                {/* Interface Chat Principale */}
                <Grid item xs={12} md={8}>
                    <Paper 
                        elevation={2} 
                        sx={{ 
                            height: '100%', 
                            display: 'flex', 
                            flexDirection: 'column',
                            overflow: 'hidden'
                        }}
                    >
                        <ChatInterface
                            onFlowCreate={handleFlowCreate}
                            onFlowUpdate={handleFlowUpdate}
                        />
                    </Paper>
                </Grid>

                {/* Panneau latéral - Monitoring et Activité */}
                <Grid item xs={12} md={4}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
                        
                        {/* Statistiques rapides */}
                        <Paper elevation={1} sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>
                                Vue d'ensemble
                            </Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={6}>
                                    <Card variant="outlined">
                                        <CardContent sx={{ textAlign: 'center', py: 1 }}>
                                            <Typography variant="h4" color="primary">
                                                {activeFlows.length}
                                            </Typography>
                                            <Typography variant="caption">
                                                Flux actifs
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                                <Grid item xs={6}>
                                    <Card variant="outlined">
                                        <CardContent sx={{ textAlign: 'center', py: 1 }}>
                                            <Typography variant="h4" color="success.main">
                                                12
                                            </Typography>
                                            <Typography variant="caption">
                                                Agents prêts
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            </Grid>
                        </Paper>

                        {/* Flux actifs détaillés */}
                        {activeFlows.length > 0 && (
                            <Paper elevation={1} sx={{ p: 2 }}>
                                <Typography variant="h6" gutterBottom>
                                    Flux en cours
                                </Typography>
                                {activeFlows.map(flow => (
                                    <Card key={flow.id} variant="outlined" sx={{ mb: 1 }}>
                                        <CardContent sx={{ py: 1 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                                <Typography variant="subtitle2">
                                                    {flow.id}
                                                </Typography>
                                                <Chip
                                                    label={flow.status}
                                                    size="small"
                                                    color={flow.status === 'completed' ? 'success' : 'primary'}
                                                />
                                            </Box>
                                            <Typography variant="caption" color="text.secondary">
                                                {flow.documents?.length || 0} document(s)
                                            </Typography>
                                        </CardContent>
                                    </Card>
                                ))}
                            </Paper>
                        )}

                        {/* Activité récente */}
                        <Paper elevation={1} sx={{ p: 2, flex: 1, overflow: 'auto' }}>
                            <Typography variant="h6" gutterBottom>
                                Activité récente
                            </Typography>
                            {recentActivity.length === 0 ? (
                                <Alert severity="info">
                                    Aucune activité récente
                                </Alert>
                            ) : (
                                <Box>
                                    {recentActivity.map(activity => (
                                        <Card key={activity.id} variant="outlined" sx={{ mb: 1 }}>
                                            <CardContent sx={{ py: 1 }}>
                                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                                                    {getActivityIcon(activity.type)}
                                                    <Box sx={{ flex: 1 }}>
                                                        <Typography variant="body2">
                                                            {activity.message}
                                                        </Typography>
                                                        <Typography variant="caption" color="text.secondary">
                                                            {new Date(activity.timestamp).toLocaleString()}
                                                        </Typography>
                                                        {activity.flowId && (
                                                            <Chip
                                                                label={activity.flowId}
                                                                size="small"
                                                                color={getActivityColor(activity.type)}
                                                                sx={{ ml: 1, height: 16 }}
                                                            />
                                                        )}
                                                    </Box>
                                                </Box>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </Box>
                            )}
                        </Paper>

                        {/* Aide rapide */}
                        <Paper elevation={1} sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>
                                Aide rapide
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                • Tapez <code>/help</code> pour voir toutes les commandes
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                • Glissez-déposez des fichiers pour les analyser
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                • Utilisez <code>/analyse</code> pour démarrer une analyse
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                • Parlez naturellement à l'assistant IA
                            </Typography>
                        </Paper>
                    </Box>
                </Grid>
            </Grid>

            {/* Bouton flottant pour accès rapide */}
            <Tooltip title="Nouvelle conversation">
                <Fab
                    color="primary"
                    sx={{
                        position: 'fixed',
                        bottom: 16,
                        right: 16,
                        display: { xs: 'flex', md: 'none' } // Visible seulement sur mobile
                    }}
                    onClick={() => window.location.reload()}
                >
                    <ChatIcon />
                </Fab>
            </Tooltip>
        </Container>
    );
};

export default Chat;
