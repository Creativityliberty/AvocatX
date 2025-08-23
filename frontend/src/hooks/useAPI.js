/**
 * Hooks React personnalisés pour l'intégration API DEFENSEUR-IA
 */

import { useState, useEffect, useCallback } from 'react';
import { casesAPI, pipelineAPI, uploadAPI, clientsAPI, appointmentsAPI, statsAPI, wsManager } from '../services/api';

// ===== HOOK POUR LES DOSSIERS =====

export const useCases = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCases = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await casesAPI.getAll();
      // Extraire le tableau cases de la réponse MongoDB Atlas
      const casesArray = data.cases || data || [];
      setCases(Array.isArray(casesArray) ? casesArray : []);
    } catch (err) {
      setError(err.message);
      setCases([]); // Fallback sécurisé
    } finally {
      setLoading(false);
    }
  }, []);

  const createCase = useCallback(async (caseData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await casesAPI.create(caseData);
      // Extraire le dossier créé de la réponse MongoDB Atlas
      const newCase = response.case || response || {};
      
      // Ajouter le nouveau dossier à la liste existante
      setCases(prev => {
        const currentCases = Array.isArray(prev) ? prev : [];
        return [...currentCases, newCase];
      });
      
      return newCase;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateCase = useCallback(async (dossierId, updates) => {
    setLoading(true);
    setError(null);
    try {
      const updatedCase = await casesAPI.update(dossierId, updates);
      setCases(prev => prev.map(c => c.dossier_id === dossierId ? updatedCase : c));
      return updatedCase;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteCase = useCallback(async (dossierId) => {
    setLoading(true);
    setError(null);
    try {
      await casesAPI.delete(dossierId);
      setCases(prev => prev.filter(c => c.dossier_id !== dossierId));
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  return {
    cases,
    loading,
    error,
    fetchCases,
    createCase,
    updateCase,
    deleteCase,
  };
};

// ===== HOOK POUR UN DOSSIER SPÉCIFIQUE =====

export const useCase = (dossierId) => {
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCase = useCallback(async () => {
    if (!dossierId) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await casesAPI.getById(dossierId);
      setCaseData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [dossierId]);

  useEffect(() => {
    fetchCase();
  }, [fetchCase]);

  return {
    caseData,
    loading,
    error,
    refetch: fetchCase,
  };
};

// ===== HOOK POUR LE PIPELINE IA =====

export const usePipeline = (dossierId) => {
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [pipelineLogs, setPipelineLogs] = useState([]);
  const [pipelineResults, setPipelineResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const startPipeline = useCallback(async (config = {}) => {
    setLoading(true);
    setError(null);
    try {
      const result = await pipelineAPI.start(dossierId, config);
      setPipelineStatus(result.status);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [dossierId]);

  const stopPipeline = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await pipelineAPI.stop(dossierId);
      setPipelineStatus(result.status);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [dossierId]);

  const fetchStatus = useCallback(async () => {
    if (!dossierId) return;
    
    try {
      const status = await pipelineAPI.getStatus(dossierId);
      setPipelineStatus(status);
    } catch (err) {
      console.error('Erreur récupération statut pipeline:', err);
    }
  }, [dossierId]);

  const fetchLogs = useCallback(async () => {
    if (!dossierId) return;
    
    try {
      const logs = await pipelineAPI.getLogs(dossierId);
      setPipelineLogs(logs);
    } catch (err) {
      console.error('Erreur récupération logs pipeline:', err);
    }
  }, [dossierId]);

  const fetchResults = useCallback(async () => {
    if (!dossierId) return;
    
    try {
      const results = await pipelineAPI.getResults(dossierId);
      setPipelineResults(results);
    } catch (err) {
      console.error('Erreur récupération résultats pipeline:', err);
    }
  }, [dossierId]);

  // WebSocket pour le monitoring temps réel
  useEffect(() => {
    if (!dossierId) return;

    const handlePipelineUpdate = (data) => {
      if (data.dossier_id === dossierId) {
        setPipelineStatus(data.status);
        if (data.logs) {
          setPipelineLogs(prev => [...prev, ...data.logs]);
        }
      }
    };

    wsManager.subscribe('pipeline_update', handlePipelineUpdate);

    return () => {
      wsManager.unsubscribe('pipeline_update', handlePipelineUpdate);
    };
  }, [dossierId]);

  useEffect(() => {
    fetchStatus();
    fetchLogs();
    fetchResults();
  }, [fetchStatus, fetchLogs, fetchResults]);

  return {
    pipelineStatus,
    pipelineLogs,
    pipelineResults,
    loading,
    error,
    startPipeline,
    stopPipeline,
    fetchStatus,
    fetchLogs,
    fetchResults,
  };
};

// ===== HOOK POUR L'UPLOAD DE FICHIERS =====

export const useFileUpload = (dossierId) => {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);

  const uploadFiles = useCallback(async (files) => {
    setUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const result = await uploadAPI.uploadFiles(
        dossierId,
        files,
        (progress) => setUploadProgress(progress)
      );
      
      setUploadedFiles(prev => [...prev, ...result.files]);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [dossierId]);

  const uploadAudio = useCallback(async (audioFile) => {
    setUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const result = await uploadAPI.uploadAudio(
        dossierId,
        audioFile,
        (progress) => setUploadProgress(progress)
      );
      
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [dossierId]);

  const fetchFiles = useCallback(async () => {
    if (!dossierId) return;
    
    try {
      const files = await uploadAPI.getFiles(dossierId);
      setUploadedFiles(files);
    } catch (err) {
      console.error('Erreur récupération fichiers:', err);
    }
  }, [dossierId]);

  const deleteFile = useCallback(async (filename) => {
    try {
      await uploadAPI.deleteFile(dossierId, filename);
      setUploadedFiles(prev => prev.filter(f => f.filename !== filename));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [dossierId]);

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  return {
    uploadProgress,
    uploading,
    uploadedFiles,
    error,
    uploadFiles,
    uploadAudio,
    fetchFiles,
    deleteFile,
  };
};

// ===== HOOK POUR LES CLIENTS =====

export const useClients = () => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchClients = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await clientsAPI.getAll();
      setClients(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const createClient = useCallback(async (clientData) => {
    setLoading(true);
    setError(null);
    try {
      const newClient = await clientsAPI.create(clientData);
      setClients(prev => [...prev, newClient]);
      return newClient;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateClient = useCallback(async (clientId, updates) => {
    setLoading(true);
    setError(null);
    try {
      const updatedClient = await clientsAPI.update(clientId, updates);
      setClients(prev => prev.map(c => c.id === clientId ? updatedClient : c));
      return updatedClient;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteClient = useCallback(async (clientId) => {
    setLoading(true);
    setError(null);
    try {
      await clientsAPI.delete(clientId);
      setClients(prev => prev.filter(c => c.id !== clientId));
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const searchClients = useCallback(async (query) => {
    setLoading(true);
    setError(null);
    try {
      const results = await clientsAPI.search(query);
      return results;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  return {
    clients,
    loading,
    error,
    fetchClients,
    createClient,
    updateClient,
    deleteClient,
    searchClients,
  };
};

// ===== HOOK POUR LES RENDEZ-VOUS =====

export const useAppointments = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAppointments = useCallback(async (startDate = null, endDate = null) => {
    setLoading(true);
    setError(null);
    try {
      const data = startDate && endDate 
        ? await appointmentsAPI.getByDateRange(startDate, endDate)
        : await appointmentsAPI.getAll();
      setAppointments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const createAppointment = useCallback(async (appointmentData) => {
    setLoading(true);
    setError(null);
    try {
      const newAppointment = await appointmentsAPI.create(appointmentData);
      setAppointments(prev => [...prev, newAppointment]);
      return newAppointment;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateAppointment = useCallback(async (appointmentId, updates) => {
    setLoading(true);
    setError(null);
    try {
      const updatedAppointment = await appointmentsAPI.update(appointmentId, updates);
      setAppointments(prev => prev.map(a => a.id === appointmentId ? updatedAppointment : a));
      return updatedAppointment;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteAppointment = useCallback(async (appointmentId) => {
    setLoading(true);
    setError(null);
    try {
      await appointmentsAPI.delete(appointmentId);
      setAppointments(prev => prev.filter(a => a.id !== appointmentId));
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  return {
    appointments,
    loading,
    error,
    fetchAppointments,
    createAppointment,
    updateAppointment,
    deleteAppointment,
  };
};

// ===== HOOK POUR LES STATISTIQUES =====

export const useStats = () => {
  const [stats, setStats] = useState({
    overview: null,
    pipeline: null,
    period: null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchOverview = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const overview = await statsAPI.getOverview();
      setStats(prev => ({ ...prev, overview }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPipelineStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const pipeline = await statsAPI.getPipelineStats();
      setStats(prev => ({ ...prev, pipeline }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPeriodStats = useCallback(async (period = '30d') => {
    setLoading(true);
    setError(null);
    try {
      const periodData = await statsAPI.getByPeriod(period);
      setStats(prev => ({ ...prev, period: periodData }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOverview();
    fetchPipelineStats();
    fetchPeriodStats();
  }, [fetchOverview, fetchPipelineStats, fetchPeriodStats]);

  return {
    stats,
    loading,
    error,
    fetchOverview,
    fetchPipelineStats,
    fetchPeriodStats,
  };
};

// ===== HOOK POUR LE WEBSOCKET =====

export const useWebSocket = () => {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    wsManager.connect();
    
    const handleOpen = () => setConnected(true);
    const handleClose = () => setConnected(false);
    
    wsManager.subscribe('connection_open', handleOpen);
    wsManager.subscribe('connection_close', handleClose);

    return () => {
      wsManager.unsubscribe('connection_open', handleOpen);
      wsManager.unsubscribe('connection_close', handleClose);
      wsManager.disconnect();
    };
  }, []);

  return {
    connected,
    subscribe: wsManager.subscribe.bind(wsManager),
    unsubscribe: wsManager.unsubscribe.bind(wsManager),
  };
};
