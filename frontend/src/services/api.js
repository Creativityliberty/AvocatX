/**
 * Service API pour la communication avec le backend DEFENSEUR-IA
 */

import axios from 'axios';

// Configuration de base
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour les erreurs
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// ===== DOSSIERS (CASES) =====

export const casesAPI = {
  // Créer un nouveau dossier (MongoDB Atlas)
  create: async (caseData) => {
    const response = await api.post('/api/v1/mongodb/cases', caseData);
    return response.data;
  },

  // Récupérer tous les dossiers (MongoDB Atlas)
  getAll: async () => {
    const response = await api.get('/api/v1/mongodb/cases');
    return response.data;
  },

  // Récupérer un dossier spécifique (MongoDB Atlas)
  getById: async (dossierId) => {
    const response = await api.get(`/api/v1/mongodb/cases/${dossierId}`);
    return response.data;
  },

  // Mettre à jour un dossier (MongoDB Atlas)
  update: async (dossierId, updates) => {
    const response = await api.put(`/api/v1/mongodb/cases/${dossierId}`, updates);
    return response.data;
  },

  // Supprimer un dossier (MongoDB Atlas)
  delete: async (dossierId) => {
    const response = await api.delete(`/api/v1/mongodb/cases/${dossierId}`);
    return response.data;
  },
};

// ===== PIPELINE IA =====

export const pipelineAPI = {
  // Démarrer le pipeline pour un dossier
  start: async (dossierId, config = {}) => {
    const response = await api.post(`/api/pipeline/${dossierId}/start`, config);
    return response.data;
  },

  // Arrêter le pipeline
  stop: async (dossierId) => {
    const response = await api.post(`/api/pipeline/${dossierId}/stop`);
    return response.data;
  },

  // Récupérer le statut du pipeline
  getStatus: async (dossierId) => {
    const response = await api.get(`/api/pipeline/${dossierId}/status`);
    return response.data;
  },

  // Récupérer les logs du pipeline
  getLogs: async (dossierId) => {
    const response = await api.get(`/api/pipeline/${dossierId}/logs`);
    return response.data;
  },

  // Récupérer les résultats du pipeline
  getResults: async (dossierId) => {
    const response = await api.get(`/api/pipeline/${dossierId}/results`);
    return response.data;
  },
};

// ===== UPLOAD DE FICHIERS =====

export const uploadAPI = {
  // Upload de fichiers (pièces justificatives)
  uploadFiles: async (dossierId, files, onProgress = null) => {
    const formData = new FormData();
    
    // Ajouter les fichiers
    files.forEach((file, index) => {
      formData.append(`files`, file);
    });
    
    formData.append('dossier_id', dossierId);

    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  },

  // Upload audio pour transcription
  uploadAudio: async (dossierId, audioFile, onProgress = null) => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('dossier_id', dossierId);

    const response = await api.post('/api/upload/audio', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    return response.data;
  },

  // Récupérer les fichiers d'un dossier
  getFiles: async (dossierId) => {
    const response = await api.get(`/api/upload/${dossierId}/files`);
    return response.data;
  },

  // Supprimer un fichier
  deleteFile: async (dossierId, filename) => {
    const response = await api.delete(`/api/upload/${dossierId}/files/${filename}`);
    return response.data;
  },
};

// ===== CLIENTS =====

export const clientsAPI = {
  // Créer un nouveau client
  create: async (clientData) => {
    const response = await api.post('/api/clients', clientData);
    return response.data;
  },

  // Récupérer tous les clients
  getAll: async () => {
    const response = await api.get('/api/clients');
    return response.data;
  },

  // Récupérer un client spécifique
  getById: async (clientId) => {
    const response = await api.get(`/api/clients/${clientId}`);
    return response.data;
  },

  // Mettre à jour un client
  update: async (clientId, updates) => {
    const response = await api.put(`/api/clients/${clientId}`, updates);
    return response.data;
  },

  // Supprimer un client
  delete: async (clientId) => {
    const response = await api.delete(`/api/clients/${clientId}`);
    return response.data;
  },

  // Rechercher des clients
  search: async (query) => {
    const response = await api.get(`/api/clients/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },
};

// ===== RENDEZ-VOUS =====

export const appointmentsAPI = {
  // Créer un nouveau rendez-vous
  create: async (appointmentData) => {
    const response = await api.post('/api/appointments', appointmentData);
    return response.data;
  },

  // Récupérer tous les rendez-vous
  getAll: async () => {
    const response = await api.get('/api/appointments');
    return response.data;
  },

  // Récupérer les rendez-vous par période
  getByDateRange: async (startDate, endDate) => {
    const response = await api.get(`/api/appointments?start=${startDate}&end=${endDate}`);
    return response.data;
  },

  // Mettre à jour un rendez-vous
  update: async (appointmentId, updates) => {
    const response = await api.put(`/api/appointments/${appointmentId}`, updates);
    return response.data;
  },

  // Supprimer un rendez-vous
  delete: async (appointmentId) => {
    const response = await api.delete(`/api/appointments/${appointmentId}`);
    return response.data;
  },
};

// ===== DOCUMENTS GÉNÉRÉS =====

export const documentsAPI = {
  // Récupérer les documents générés pour un dossier
  getByCase: async (dossierId) => {
    const response = await api.get(`/api/documents/${dossierId}`);
    return response.data;
  },

  // Télécharger un document
  download: async (dossierId, documentType) => {
    const response = await api.get(`/api/documents/${dossierId}/${documentType}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Régénérer un document
  regenerate: async (dossierId, documentType) => {
    const response = await api.post(`/api/documents/${dossierId}/${documentType}/regenerate`);
    return response.data;
  },
};

// ===== STATISTIQUES =====

export const statsAPI = {
  // Récupérer les statistiques générales
  getOverview: async () => {
    const response = await api.get('/api/v1/stats/overview');
    return response.data;
  },

  // Récupérer les statistiques du pipeline
  getPipelineStats: async () => {
    const response = await api.get('/api/v1/stats/pipeline');
    return response.data;
  },

  // Récupérer les statistiques par période
  getByPeriod: async (period = '30d') => {
    const response = await api.get(`/api/v1/stats/period/${period}`);
    return response.data;
  },
};

// ===== AGENTS & FLOWS =====

export const agentsFlowsAPI = {
  // Récupérer le statut de tous les agents
  getAgentsStatus: async () => {
    const response = await api.get('/api/v1/flow/agents-status');
    return response.data;
  },

  // Récupérer les logs des flows
  getFlowLogs: async () => {
    const response = await api.get('/api/v1/flow/logs');
    return response.data;
  },

  // Récupérer les métriques des agents et flows
  getMetrics: async () => {
    const response = await api.get('/api/v1/flow/metrics');
    return response.data;
  },

  // Actions sur les flows
  pauseFlow: async (flowId) => {
    const response = await api.post(`/api/v1/flow/${flowId}/pause`);
    return response.data;
  },

  resumeFlow: async (flowId) => {
    const response = await api.post(`/api/v1/flow/${flowId}/resume`);
    return response.data;
  },

  cancelFlow: async (flowId) => {
    const response = await api.post(`/api/v1/flow/${flowId}/cancel`);
    return response.data;
  },

  // WebSocket pour le temps réel
  getWebSocketUrl: () => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = API_BASE_URL.replace(/^https?:\/\//, '');
    return `${wsProtocol}//${wsHost}/api/v1/flow/ws`;
  },
};

// ===== MONGODB ATLAS =====

export const mongodbAPI = {
  // Vérification de santé MongoDB Atlas
  health: async () => {
    const response = await api.get('/api/v1/mongodb/health');
    return response.data;
  },

  // Statistiques MongoDB Atlas
  stats: async () => {
    const response = await api.get('/api/v1/mongodb/stats');
    return response.data;
  },

  // Gestion des dossiers MongoDB Atlas
  cases: {
    // Créer un nouveau dossier dans MongoDB Atlas
    create: async (caseData) => {
      const response = await api.post('/api/v1/mongodb/cases', caseData);
      return response.data;
    },

    // Récupérer un dossier par ID depuis MongoDB Atlas
    getById: async (dossierId) => {
      const response = await api.get(`/api/v1/mongodb/cases/${dossierId}`);
      return response.data;
    },

    // Mettre à jour un dossier dans MongoDB Atlas
    update: async (dossierId, updates) => {
      const response = await api.put(`/api/v1/mongodb/cases/${dossierId}`, updates);
      return response.data;
    },

    // Lister les dossiers avec pagination
    list: async (params = {}) => {
      const { skip = 0, limit = 10, status, created_by } = params;
      const queryParams = new URLSearchParams({ skip, limit });
      if (status) queryParams.append('status', status);
      if (created_by) queryParams.append('created_by', created_by);
      
      const response = await api.get(`/api/v1/mongodb/cases?${queryParams}`);
      return response.data;
    }
  },

  // Gestion des documents MongoDB Atlas
  documents: {
    // Stocker les métadonnées d'un document
    store: async (documentData) => {
      const response = await api.post('/api/v1/mongodb/documents', documentData);
      return response.data;
    },

    // Récupérer tous les documents d'un dossier
    getByCase: async (dossierId) => {
      const response = await api.get(`/api/v1/mongodb/documents/${dossierId}`);
      return response.data;
    }
  },

  // Gestion des exécutions de pipeline MongoDB Atlas
  pipeline: {
    // Stocker une exécution de pipeline
    store: async (pipelineData) => {
      const response = await api.post('/api/v1/mongodb/pipeline/runs', pipelineData);
      return response.data;
    },

    // Récupérer une exécution de pipeline
    getRun: async (flowId) => {
      const response = await api.get(`/api/v1/mongodb/pipeline/runs/${flowId}`);
      return response.data;
    },

    // Mettre à jour une exécution de pipeline
    updateRun: async (flowId, updates) => {
      const response = await api.put(`/api/v1/mongodb/pipeline/runs/${flowId}`, updates);
      return response.data;
    }
  }
};

// ===== WEBSOCKET POUR LE MONITORING TEMPS RÉEL =====

export class WebSocketManager {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws';
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connecté');
        this.reconnectAttempts = 0;
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data.type, data);
        } catch (error) {
          console.error('Erreur parsing WebSocket message:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket fermé');
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('Erreur WebSocket:', error);
      };
      
    } catch (error) {
      console.error('Erreur connexion WebSocket:', error);
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Tentative de reconnexion ${this.reconnectAttempts}...`);
        this.connect();
      }, 2000 * this.reconnectAttempts);
    }
  }

  subscribe(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  unsubscribe(eventType, callback) {
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  notifyListeners(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Erreur dans callback WebSocket:', error);
        }
      });
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Instance globale du WebSocket
export const wsManager = new WebSocketManager();

export default api;
