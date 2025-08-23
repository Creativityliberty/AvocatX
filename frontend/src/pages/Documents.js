/**
 * Documents - Gestion des documents et pièces DEFENSEUR-IA
 */

import {
    AudioFile as AudioIcon,
    Delete as DeleteIcon,
    Description as DescriptionIcon,
    DescriptionOutlined as DocIcon,
    CloudDownload as DownloadIcon,
    InsertDriveFileOutlined as FileIcon,
    Folder as FolderIcon,
    Image as ImageIcon,
    MoreVert as MoreVertIcon,
    PictureAsPdf as PdfIcon,
    Search as SearchIcon,
    CloudUpload as UploadIcon,
    CloudUpload as CloudUploadIcon,
    VideoFile as VideoIcon
} from '@mui/icons-material';
import {
    Avatar,
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    FormControl,
    Grid,
    IconButton,
    InputAdornment,
    InputLabel,
    LinearProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemSecondaryAction,
    ListItemText,
    Menu,
    MenuItem,
    Select,
    Tab,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Tabs,
    TextField,
    Typography,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import React, { useState } from 'react';
import { useDocuments, useCases } from '../hooks/useAPI';
import { useMongoDBDocuments, useMongoDBCases } from '../hooks/useMongoDBAtlas';
import { useNotifications } from '../hooks/useNotifications';

const Documents = () => {
  const { showSuccess, showError, showInfo } = useNotifications();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterSource, setFilterSource] = useState('all');
  const [anchorEl, setAnchorEl] = useState(null);
  const [_selectedDocument, setSelectedDocument] = useState(null);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Mock documents
  const mockDocuments = [
    {
      id: 1,
      name: 'Passeport_Marie_Dubois.pdf',
      type: 'pdf',
      size: '2.1 MB',
      source: 'uploaded',
      dossier_id: 'DOSSIER_20240127_142530',
      client_name: 'Marie Dubois',
      uploaded_at: '2024-01-27T10:30:00Z',
      category: 'piece_identite',
      status: 'processed',
    },
    {
      id: 2,
      name: 'Recit_narratif_v1.docx',
      type: 'docx',
      size: '856 KB',
      source: 'generated',
      dossier_id: 'DOSSIER_20240127_142530',
      client_name: 'Marie Dubois',
      uploaded_at: '2024-01-27T14:45:00Z',
      category: 'document_genere',
      status: 'ready',
    },
    {
      id: 3,
      name: 'Enregistrement_temoignage.mp3',
      type: 'audio',
      size: '15.3 MB',
      source: 'uploaded',
      dossier_id: 'DOSSIER_20240127_135420',
      client_name: 'Ahmed Benali',
      uploaded_at: '2024-01-27T13:54:00Z',
      category: 'temoignage',
      status: 'transcribed',
    },
    {
      id: 4,
      name: 'Scan_titre_sejour.jpg',
      type: 'image',
      size: '3.7 MB',
      source: 'uploaded',
      dossier_id: 'DOSSIER_20240127_135420',
      client_name: 'Ahmed Benali',
      uploaded_at: '2024-01-27T14:10:00Z',
      category: 'piece_justificative',
      status: 'ocr_processed',
    },
    {
      id: 5,
      name: 'Requete_finale_OQTF.pdf',
      type: 'pdf',
      size: '1.2 MB',
      source: 'generated',
      dossier_id: 'DOSSIER_20240126_091500',
      client_name: 'Carlos Silva',
      uploaded_at: '2024-01-26T16:30:00Z',
      category: 'document_genere',
      status: 'ready',
    },
  ];

  const filteredDocuments = mockDocuments.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.client_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.dossier_id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || doc.type === filterType;
    const matchesSource = filterSource === 'all' || doc.source === filterSource;
    
    return matchesSearch && matchesType && matchesSource;
  });

  const uploadedDocuments = filteredDocuments.filter(doc => doc.source === 'uploaded');
  const generatedDocuments = filteredDocuments.filter(doc => doc.source === 'generated');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleMenuOpen = (event, document) => {
    setAnchorEl(event.currentTarget);
    setSelectedDocument(document);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDocument(null);
  };

  const handleFileUpload = async () => {
    if (selectedFiles.length === 0) {
      showError('Veuillez sélectionner au moins un fichier');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    showInfo(`Upload de ${selectedFiles.length} fichier(s) en cours...`);
    
    try {
      // Simulation upload avec progression réaliste
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 150));
        setUploadProgress(i);
      }
      
      // Simulation de traitement backend
      await new Promise(resolve => setTimeout(resolve, 500));
      
      showSuccess(`${selectedFiles.length} fichier(s) uploadé(s) avec succès`);
      setUploadDialog(false);
      setSelectedFiles([]);
      setUploadProgress(0);
    } catch (error) {
      console.error('Erreur upload:', error);
      showError('Erreur lors de l\'upload des fichiers. Veuillez réessayer.');
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'pdf':
        return <PdfIcon color="error" />;
      case 'image':
      case 'jpg':
      case 'jpeg':
      case 'png':
        return <ImageIcon color="primary" />;
      case 'audio':
      case 'mp3':
      case 'wav':
        return <AudioIcon color="secondary" />;
      case 'video':
      case 'mp4':
      case 'avi':
        return <VideoIcon color="info" />;
      case 'docx':
      case 'doc':
        return <DocIcon color="primary" />;
      default:
        return <FileIcon />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready':
        return 'success';
      case 'processed':
      case 'transcribed':
      case 'ocr_processed':
        return 'info';
      case 'processing':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'ready':
        return 'Prêt';
      case 'processed':
        return 'Traité';
      case 'transcribed':
        return 'Transcrit';
      case 'ocr_processed':
        return 'OCR effectué';
      case 'processing':
        return 'En cours';
      case 'error':
        return 'Erreur';
      default:
        return status;
    }
  };

  const getCategoryLabel = (category) => {
    switch (category) {
      case 'piece_identite':
        return 'Pièce d\'identité';
      case 'piece_justificative':
        return 'Pièce justificative';
      case 'temoignage':
        return 'Témoignage';
      case 'document_genere':
        return 'Document généré';
      default:
        return category;
    }
  };

  return (
    <Box>
      {/* En-tête */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            Documents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gestion des pièces justificatives et documents générés
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<UploadIcon />}
          onClick={() => setUploadDialog(true)}
        >
          Uploader des fichiers
        </Button>
      </Box>

      {/* Statistiques rapides */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'primary.main' }}>
                    {mockDocuments.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total documents
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.light' }}>
                  <DescriptionIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'info.main' }}>
                    {uploadedDocuments.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pièces uploadées
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.light' }}>
                  <UploadIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'success.main' }}>
                    {generatedDocuments.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Documents générés
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.light' }}>
                  <DescriptionIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 600, color: 'warning.main' }}>
                    {mockDocuments.filter(d => d.status === 'processing').length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    En traitement
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.light' }}>
                  <CloudUploadIcon />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filtres et recherche */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Rechercher par nom, client, dossier..."
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
                <InputLabel>Type de fichier</InputLabel>
                <Select
                  value={filterType}
                  label="Type de fichier"
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <MenuItem value="all">Tous les types</MenuItem>
                  <MenuItem value="pdf">PDF</MenuItem>
                  <MenuItem value="image">Images</MenuItem>
                  <MenuItem value="audio">Audio</MenuItem>
                  <MenuItem value="docx">Documents Word</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Source</InputLabel>
                <Select
                  value={filterSource}
                  label="Source"
                  onChange={(e) => setFilterSource(e.target.value)}
                >
                  <MenuItem value="all">Toutes les sources</MenuItem>
                  <MenuItem value="uploaded">Uploadés</MenuItem>
                  <MenuItem value="generated">Générés par IA</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Typography variant="body2" color="text.secondary">
                {filteredDocuments.length} document(s)
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Onglets */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Tous les documents" />
            <Tab label="Pièces uploadées" />
            <Tab label="Documents générés" />
          </Tabs>
        </Box>

        {/* Liste des documents */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Document</TableCell>
                <TableCell>Client / Dossier</TableCell>
                <TableCell>Catégorie</TableCell>
                <TableCell>Taille</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(activeTab === 0 ? filteredDocuments :
                activeTab === 1 ? uploadedDocuments : generatedDocuments)
                .map((document) => (
                <TableRow key={document.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      {getFileIcon(document.type)}
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {document.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {document.type.toUpperCase()}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {document.client_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                        {document.dossier_id}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getCategoryLabel(document.category)}
                      size="small"
                      variant="outlined"
                      color={document.source === 'generated' ? 'secondary' : 'primary'}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {document.size}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(document.status)}
                      size="small"
                      color={getStatusColor(document.status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(document.uploaded_at).toLocaleDateString('fr-FR')}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton size="small">
                      <DescriptionIcon />
                    </IconButton>
                    <IconButton size="small">
                      <DownloadIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, document)}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
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
        <MenuItem onClick={handleMenuClose}>
          <DescriptionIcon sx={{ mr: 2 }} />
          Prévisualiser
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <DownloadIcon sx={{ mr: 2 }} />
          Télécharger
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <FolderIcon sx={{ mr: 2 }} />
          Voir le dossier
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <DeleteIcon sx={{ mr: 2 }} />
          Supprimer
        </MenuItem>
      </Menu>

      {/* Dialog upload */}
      <Dialog open={uploadDialog} onClose={() => setUploadDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Uploader des documents</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Box
              sx={{
                border: '2px dashed',
                borderColor: 'primary.main',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                mb: 3,
                backgroundColor: 'action.hover',
              }}
            >
              <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                Glissez-déposez vos fichiers ici
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                ou cliquez pour sélectionner
              </Typography>
              <input
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png,.docx,.txt,.mp3,.wav,.mp4"
                onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
                style={{ display: 'none' }}
                id="file-upload"
              />
              <label htmlFor="file-upload">
                <Button variant="outlined" component="span">
                  Sélectionner des fichiers
                </Button>
              </label>
            </Box>

            {selectedFiles.length > 0 && (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 2 }}>
                  Fichiers sélectionnés ({selectedFiles.length}):
                </Typography>
                <List>
                  {selectedFiles.map((file, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {getFileIcon(file.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={file.name}
                        secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => {
                            const newFiles = [...selectedFiles];
                            newFiles.splice(index, 1);
                            setSelectedFiles(newFiles);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {uploading && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  Upload en cours... {uploadProgress}%
                </Typography>
                <LinearProgress variant="determinate" value={uploadProgress} />
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialog(false)} disabled={uploading}>
            Annuler
          </Button>
          <Button 
            variant="contained" 
            onClick={handleFileUpload}
            disabled={selectedFiles.length === 0 || uploading}
          >
            Uploader {selectedFiles.length > 0 && `(${selectedFiles.length})`}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Documents;
