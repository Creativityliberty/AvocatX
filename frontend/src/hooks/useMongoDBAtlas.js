/**
 * Hook React pour MongoDB Atlas - DEFENSEUR-IA
 * Gestion des dossiers, documents et pipeline avec la vraie base cloud
 */

import { useState, useEffect, useCallback } from 'react';
import { mongodbAPI } from '../services/api';

export const useMongoDBAtlas = () => {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Vérification de santé MongoDB Atlas
  const checkHealth = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const healthData = await mongodbAPI.health();
      setHealth(healthData);
      return healthData;
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur health check MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Récupération des statistiques MongoDB Atlas
  const getStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const statsData = await mongodbAPI.stats();
      setStats(statsData);
      return statsData;
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur stats MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Initialisation automatique
  useEffect(() => {
    checkHealth();
    getStats();
  }, [checkHealth, getStats]);

  return {
    health,
    stats,
    loading,
    error,
    checkHealth,
    getStats
  };
};

export const useMongoDBCases = () => {
  const [cases, setCases] = useState([]);
  const [currentCase, setCurrentCase] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Créer un nouveau dossier dans MongoDB Atlas
  const createCase = useCallback(async (caseData) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.cases.create(caseData);
      
      if (result.success) {
        console.log('✅ Dossier MongoDB Atlas créé:', result.dossier_id);
        // Recharger la liste des dossiers
        await listCases();
        return result;
      } else {
        throw new Error(result.error || 'Erreur création dossier');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur création dossier MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Récupérer un dossier par ID
  const getCaseById = useCallback(async (dossierId) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.cases.getById(dossierId);
      
      if (result.success) {
        setCurrentCase(result.case);
        return result.case;
      } else {
        throw new Error(result.error || 'Dossier non trouvé');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur récupération dossier MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Lister les dossiers avec pagination
  const listCases = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.cases.list(params);
      
      if (result.success) {
        setCases(result.cases || []);
        return result;
      } else {
        throw new Error(result.error || 'Erreur liste dossiers');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur liste dossiers MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Mettre à jour un dossier
  const updateCase = useCallback(async (dossierId, updates) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.cases.update(dossierId, updates);
      
      if (result.success) {
        console.log('✅ Dossier MongoDB Atlas mis à jour:', dossierId);
        // Recharger le dossier courant si c'est le même
        if (currentCase && currentCase.dossier_id === dossierId) {
          await getCaseById(dossierId);
        }
        // Recharger la liste des dossiers
        await listCases();
        return result;
      } else {
        throw new Error(result.error || 'Erreur mise à jour dossier');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur mise à jour dossier MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [currentCase, getCaseById, listCases]);

  // Initialisation automatique
  useEffect(() => {
    listCases();
  }, [listCases]);

  return {
    cases,
    currentCase,
    loading,
    error,
    createCase,
    getCaseById,
    listCases,
    updateCase,
    setCurrentCase
  };
};

export const useMongoDBDocuments = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Stocker les métadonnées d'un document
  const storeDocument = useCallback(async (documentData) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.documents.store(documentData);
      
      if (result.success) {
        console.log('✅ Document MongoDB Atlas stocké:', result.document_id);
        return result;
      } else {
        throw new Error(result.error || 'Erreur stockage document');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur stockage document MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Récupérer tous les documents d'un dossier
  const getDocumentsByCase = useCallback(async (dossierId) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.documents.getByCase(dossierId);
      
      if (result.success) {
        setDocuments(result.documents || []);
        return result.documents;
      } else {
        throw new Error(result.error || 'Erreur récupération documents');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur récupération documents MongoDB Atlas:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    documents,
    loading,
    error,
    storeDocument,
    getDocumentsByCase,
    setDocuments
  };
};

export const useMongoDBPipeline = () => {
  const [pipelineRuns, setPipelineRuns] = useState([]);
  const [currentRun, setCurrentRun] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Stocker une exécution de pipeline
  const storePipelineRun = useCallback(async (pipelineData) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.pipeline.store(pipelineData);
      
      if (result.success) {
        console.log('✅ Pipeline run MongoDB Atlas stocké:', result.flow_id);
        return result;
      } else {
        throw new Error(result.error || 'Erreur stockage pipeline run');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur stockage pipeline run MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Récupérer une exécution de pipeline
  const getPipelineRun = useCallback(async (flowId) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.pipeline.getRun(flowId);
      
      if (result.success) {
        setCurrentRun(result.pipeline_run);
        return result.pipeline_run;
      } else {
        throw new Error(result.error || 'Pipeline run non trouvé');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur récupération pipeline run MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Mettre à jour une exécution de pipeline
  const updatePipelineRun = useCallback(async (flowId, updates) => {
    try {
      setLoading(true);
      setError(null);
      const result = await mongodbAPI.pipeline.updateRun(flowId, updates);
      
      if (result.success) {
        console.log('✅ Pipeline run MongoDB Atlas mis à jour:', flowId);
        // Recharger le run courant si c'est le même
        if (currentRun && currentRun.flow_id === flowId) {
          await getPipelineRun(flowId);
        }
        return result;
      } else {
        throw new Error(result.error || 'Erreur mise à jour pipeline run');
      }
    } catch (err) {
      setError(err.message);
      console.error('❌ Erreur mise à jour pipeline run MongoDB Atlas:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [currentRun, getPipelineRun]);

  return {
    pipelineRuns,
    currentRun,
    loading,
    error,
    storePipelineRun,
    getPipelineRun,
    updatePipelineRun,
    setCurrentRun
  };
};
