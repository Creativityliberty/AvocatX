import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Paper,
    TextField,
    IconButton,
    Typography,
    List,
    ListItem,
    ListItemText,
    Avatar,
    Chip,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    LinearProgress,
    Alert,
    Divider,
    Menu,
    MenuItem,
    Tooltip,
    Badge
} from '@mui/material';
import {
    Send,
    AttachFile,
    SmartToy,
    Person,
    PlayArrow,
    Pause,
    Stop,
    History,
    Settings,
    Help,
    Upload,
    Description,
    AudioFile,
    Image,
    Email,
    Delete,
    MoreVert
} from '@mui/icons-material';

const ChatInterface = ({ onFlowCreate, onFlowUpdate }) => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [showUploadDialog, setShowUploadDialog] = useState(false);
    const [activeFlows, setActiveFlows] = useState([]);
    const [menuAnchor, setMenuAnchor] = useState(null);
    const [selectedFlow, setSelectedFlow] = useState(null);
    
    const messagesEndRef = useRef(null);
    const fileInputRef = useRef(null);
    const userId = 'user_001'; // En production, récupérer depuis l'auth

    // Scroll automatique vers le bas
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initialisation avec message de bienvenue
    useEffect(() => {
        setMessages([{
            id: 'welcome',
            type: 'system',
            content: `Bonjour ! Je suis votre assistant IA DEFENSEUR-IA. 

Je peux vous aider à :
• Analyser vos documents juridiques
• Créer des dossiers OQTF
• Rechercher de la jurisprudence
• Gérer vos flux de traitement

Commandes disponibles :
/help - Afficher l'aide
/analyse - Analyser vos documents
/status - Voir l'état des flux
/historique - Afficher l'historique

Vous pouvez aussi me parler naturellement ou glisser-déposer des documents.`,
            timestamp: new Date().toISOString()
        }]);
    }, []);

    // Simulation d'appel API au ChatOrchestrator
    const sendMessageToOrchestrator = async (message, attachments = null) => {
        try {
            // En production, remplacer par un vrai appel API
            const response = await fetch('/api/chat/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    user_id: userId,
                    attachments
                })
            });

            if (!response.ok) {
                throw new Error('Erreur réseau');
            }

            return await response.json();
        } catch (error) {
            // Simulation de réponse pour la démo
            console.log('Mode démo - simulation de réponse');
            return simulateOrchestratorResponse(message, attachments);
        }
    };

    // Simulation de réponse du ChatOrchestrator pour la démo
    const simulateOrchestratorResponse = (message, attachments) => {
        const lowerMessage = message.toLowerCase();
        
        if (message.startsWith('/help')) {
            return {
                response: `Commandes disponibles:
/status [flow_id]    - Affiche le statut du système
/start               - Démarre un nouveau flux
/analyse             - Démarre l'analyse des documents
/resultats [flow_id] - Affiche les résultats
/historique          - Affiche l'historique
/help                - Affiche cette aide

Vous pouvez aussi utiliser le langage naturel:
"Analyser mes documents"
"Voir les résultats"
"Afficher l'historique"`,
                status: 'success'
            };
        }
        
        if (message.startsWith('/analyse') || lowerMessage.includes('analys')) {
            const flowId = `flow_${Date.now()}`;
            setTimeout(() => {
                setActiveFlows(prev => [...prev, {
                    id: flowId,
                    status: 'running',
                    documents: uploadedFiles.length,
                    progress: 0
                }]);
                simulateFlowProgress(flowId);
            }, 1000);
            
            return {
                response: `Analyse démarrée pour ${uploadedFiles.length} document(s). ID du flux: ${flowId}`,
                status: 'success',
                flow_id: flowId,
                documents_count: uploadedFiles.length
            };
        }
        
        if (message.startsWith('/status')) {
            return {
                response: `État du système:
• Flux actifs: ${activeFlows.length}
• Documents en attente: ${uploadedFiles.length}
• Agents disponibles: 12/12`,
                status: 'success'
            };
        }
        
        if (message.startsWith('/historique')) {
            return {
                response: `Historique des analyses:
• 2025-01-27 17:30 - flow_001 - completed (3 docs)
• 2025-01-27 16:45 - flow_002 - completed (1 doc)
• 2025-01-27 15:20 - flow_003 - error (2 docs)`,
                status: 'success'
            };
        }
        
        return {
            response: `J'ai bien reçu votre message: "${message}". 
            
Pour une analyse de documents, utilisez /analyse ou uploadez vos fichiers.
Pour voir les commandes disponibles, tapez /help.`,
            status: 'success'
        };
    };

    // Simulation de progression d'un flux
    const simulateFlowProgress = (flowId) => {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                setActiveFlows(prev => prev.map(flow => 
                    flow.id === flowId 
                        ? { ...flow, status: 'completed', progress: 100 }
                        : flow
                ));
                
                // Ajouter message de completion
                setMessages(prev => [...prev, {
                    id: `completion_${Date.now()}`,
                    type: 'system',
                    content: `✅ Analyse terminée pour le flux ${flowId}. Utilisez /resultats ${flowId} pour voir les résultats.`,
                    timestamp: new Date().toISOString()
                }]);
            } else {
                setActiveFlows(prev => prev.map(flow => 
                    flow.id === flowId 
                        ? { ...flow, progress: Math.min(progress, 100) }
                        : flow
                ));
            }
        }, 1000);
    };

    // Envoi de message
    const handleSendMessage = async () => {
        if (!inputMessage.trim() && uploadedFiles.length === 0) return;

        const userMessage = {
            id: `user_${Date.now()}`,
            type: 'user',
            content: inputMessage,
            timestamp: new Date().toISOString(),
            attachments: uploadedFiles.length > 0 ? [...uploadedFiles] : null
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);

        try {
            const response = await sendMessageToOrchestrator(
                inputMessage, 
                uploadedFiles.length > 0 ? uploadedFiles : null
            );

            const botMessage = {
                id: `bot_${Date.now()}`,
                type: 'bot',
                content: response.response,
                timestamp: new Date().toISOString(),
                status: response.status,
                metadata: {
                    flow_id: response.flow_id,
                    documents_count: response.documents_count
                }
            };

            setMessages(prev => [...prev, botMessage]);

            // Callback pour notifier le parent si un flux est créé
            if (response.flow_id && onFlowCreate) {
                onFlowCreate({
                    id: response.flow_id,
                    status: 'running',
                    documents: uploadedFiles
                });
            }

        } catch (error) {
            const errorMessage = {
                id: `error_${Date.now()}`,
                type: 'error',
                content: `Erreur: ${error.message}`,
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            setInputMessage('');
            setUploadedFiles([]);
        }
    };

    // Gestion de l'upload de fichiers
    const handleFileUpload = (event) => {
        const files = Array.from(event.target.files);
        const newFiles = files.map(file => ({
            id: `file_${Date.now()}_${Math.random()}`,
            name: file.name,
            size: file.size,
            type: getFileType(file.name),
            file: file
        }));
        
        setUploadedFiles(prev => [...prev, ...newFiles]);
        setShowUploadDialog(false);
    };

    // Détection du type de fichier
    const getFileType = (filename) => {
        const ext = filename.toLowerCase().split('.').pop();
        if (['pdf'].includes(ext)) return 'pdf';
        if (['mp3', 'wav', 'm4a', 'ogg'].includes(ext)) return 'audio';
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) return 'image';
        if (['txt', 'doc', 'docx'].includes(ext)) return 'text';
        if (['eml', 'msg'].includes(ext)) return 'email';
        return 'text';
    };

    // Icône selon le type de fichier
    const getFileIcon = (type) => {
        switch (type) {
            case 'pdf': return <Description color="error" />;
            case 'audio': return <AudioFile color="primary" />;
            case 'image': return <Image color="success" />;
            case 'email': return <Email color="info" />;
            default: return <Description />;
        }
    };

    // Suppression d'un fichier uploadé
    const removeFile = (fileId) => {
        setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
    };

    // Gestion des commandes rapides
    const handleQuickCommand = (command) => {
        setInputMessage(command);
        setMenuAnchor(null);
    };

    // Rendu d'un message
    const renderMessage = (message) => {
        const isUser = message.type === 'user';
        const isSystem = message.type === 'system';
        const isError = message.type === 'error';

        return (
            <ListItem
                key={message.id}
                sx={{
                    flexDirection: 'column',
                    alignItems: isUser ? 'flex-end' : 'flex-start',
                    py: 1
                }}
            >
                <Box
                    sx={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        flexDirection: isUser ? 'row-reverse' : 'row',
                        gap: 1,
                        maxWidth: '80%'
                    }}
                >
                    <Avatar
                        sx={{
                            bgcolor: isUser ? 'primary.main' : isSystem ? 'info.main' : isError ? 'error.main' : 'secondary.main',
                            width: 32,
                            height: 32
                        }}
                    >
                        {isUser ? <Person /> : <SmartToy />}
                    </Avatar>
                    
                    <Paper
                        elevation={1}
                        sx={{
                            p: 2,
                            bgcolor: isUser ? 'primary.50' : isError ? 'error.50' : 'grey.50',
                            borderRadius: 2,
                            whiteSpace: 'pre-wrap'
                        }}
                    >
                        <Typography variant="body2">
                            {message.content}
                        </Typography>
                        
                        {message.attachments && (
                            <Box sx={{ mt: 1 }}>
                                {message.attachments.map(file => (
                                    <Chip
                                        key={file.id}
                                        icon={getFileIcon(file.type)}
                                        label={file.name}
                                        size="small"
                                        sx={{ mr: 0.5, mb: 0.5 }}
                                    />
                                ))}
                            </Box>
                        )}
                        
                        {message.metadata?.flow_id && (
                            <Chip
                                label={`Flow: ${message.metadata.flow_id}`}
                                size="small"
                                color="primary"
                                sx={{ mt: 1 }}
                            />
                        )}
                    </Paper>
                </Box>
                
                <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 0.5, alignSelf: isUser ? 'flex-end' : 'flex-start' }}
                >
                    {new Date(message.timestamp).toLocaleTimeString()}
                </Typography>
            </ListItem>
        );
    };

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <Paper elevation={1} sx={{ p: 2, borderRadius: 0 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                            <SmartToy />
                        </Avatar>
                        <Box>
                            <Typography variant="h6">DEFENSEUR-IA Assistant</Typography>
                            <Typography variant="caption" color="text.secondary">
                                Pipeline juridique intelligent
                            </Typography>
                        </Box>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Commandes rapides">
                            <IconButton
                                onClick={(e) => setMenuAnchor(e.currentTarget)}
                            >
                                <MoreVert />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Box>
                
                {/* Flux actifs */}
                {activeFlows.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                            Flux actifs ({activeFlows.length})
                        </Typography>
                        {activeFlows.map(flow => (
                            <Box key={flow.id} sx={{ mb: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                    <Chip
                                        label={flow.id}
                                        size="small"
                                        color={flow.status === 'completed' ? 'success' : 'primary'}
                                    />
                                    <Typography variant="caption">
                                        {flow.documents} doc(s) - {flow.status}
                                    </Typography>
                                </Box>
                                {flow.status === 'running' && (
                                    <LinearProgress
                                        variant="determinate"
                                        value={flow.progress}
                                        sx={{ height: 4, borderRadius: 2 }}
                                    />
                                )}
                            </Box>
                        ))}
                    </Box>
                )}
            </Paper>

            {/* Messages */}
            <Box sx={{ flex: 1, overflow: 'auto', bgcolor: 'grey.50' }}>
                <List sx={{ p: 1 }}>
                    {messages.map(renderMessage)}
                    {isLoading && (
                        <ListItem sx={{ justifyContent: 'center' }}>
                            <LinearProgress sx={{ width: '50%' }} />
                        </ListItem>
                    )}
                    <div ref={messagesEndRef} />
                </List>
            </Box>

            {/* Fichiers uploadés */}
            {uploadedFiles.length > 0 && (
                <Paper elevation={1} sx={{ p: 2, borderRadius: 0 }}>
                    <Typography variant="subtitle2" gutterBottom>
                        Documents à analyser ({uploadedFiles.length})
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {uploadedFiles.map(file => (
                            <Chip
                                key={file.id}
                                icon={getFileIcon(file.type)}
                                label={file.name}
                                onDelete={() => removeFile(file.id)}
                                deleteIcon={<Delete />}
                                size="small"
                            />
                        ))}
                    </Box>
                </Paper>
            )}

            {/* Zone de saisie */}
            <Paper elevation={2} sx={{ p: 2, borderRadius: 0 }}>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
                    <Tooltip title="Joindre des fichiers">
                        <IconButton
                            onClick={() => setShowUploadDialog(true)}
                            color="primary"
                        >
                            <AttachFile />
                        </IconButton>
                    </Tooltip>
                    
                    <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        placeholder="Tapez votre message ou une commande (/help pour l'aide)..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSendMessage();
                            }
                        }}
                        disabled={isLoading}
                        variant="outlined"
                        size="small"
                    />
                    
                    <Tooltip title="Envoyer">
                        <IconButton
                            onClick={handleSendMessage}
                            disabled={isLoading || (!inputMessage.trim() && uploadedFiles.length === 0)}
                            color="primary"
                        >
                            <Send />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Paper>

            {/* Menu des commandes rapides */}
            <Menu
                anchorEl={menuAnchor}
                open={Boolean(menuAnchor)}
                onClose={() => setMenuAnchor(null)}
            >
                <MenuItem onClick={() => handleQuickCommand('/help')}>
                    <Help sx={{ mr: 1 }} /> Aide
                </MenuItem>
                <MenuItem onClick={() => handleQuickCommand('/status')}>
                    <Settings sx={{ mr: 1 }} /> Statut
                </MenuItem>
                <MenuItem onClick={() => handleQuickCommand('/analyse')}>
                    <PlayArrow sx={{ mr: 1 }} /> Analyser
                </MenuItem>
                <MenuItem onClick={() => handleQuickCommand('/historique')}>
                    <History sx={{ mr: 1 }} /> Historique
                </MenuItem>
            </Menu>

            {/* Dialog d'upload */}
            <Dialog
                open={showUploadDialog}
                onClose={() => setShowUploadDialog(false)}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>Joindre des documents</DialogTitle>
                <DialogContent>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                        Sélectionnez les documents à analyser (PDF, audio, images, emails...)
                    </Typography>
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                        accept=".pdf,.mp3,.wav,.m4a,.ogg,.jpg,.jpeg,.png,.gif,.bmp,.txt,.doc,.docx,.eml,.msg"
                    />
                    <Button
                        variant="outlined"
                        startIcon={<Upload />}
                        onClick={() => fileInputRef.current?.click()}
                        fullWidth
                        sx={{ mt: 2 }}
                    >
                        Choisir des fichiers
                    </Button>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setShowUploadDialog(false)}>
                        Fermer
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ChatInterface;
