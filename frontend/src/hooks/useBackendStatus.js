/**
 * Hook pour vérifier le statut de connexion au backend DEFENSEUR-IA
 */

import { useState, useEffect, useCallback } from 'react';

const BACKEND_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useBackendStatus = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [lastCheck, setLastCheck] = useState(null);
  const [backendInfo, setBackendInfo] = useState(null);

  const checkBackendStatus = useCallback(async () => {
    setIsChecking(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${BACKEND_URL}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        setIsConnected(true);
        setBackendInfo(data);
        setLastCheck(new Date());
      } else {
        setIsConnected(false);
        setBackendInfo(null);
      }
    } catch (error) {
      console.warn('Backend connection check failed:', error);
      setIsConnected(false);
      setBackendInfo(null);
    } finally {
      setIsChecking(false);
      setLastCheck(new Date());
    }
  }, []);

  // Vérification initiale
  useEffect(() => {
    checkBackendStatus();
  }, [checkBackendStatus]);

  // Vérification périodique (toutes les 30 secondes)
  useEffect(() => {
    const interval = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(interval);
  }, [checkBackendStatus]);

  return {
    isConnected,
    isChecking,
    lastCheck,
    backendInfo,
    checkBackendStatus,
    backendUrl: BACKEND_URL
  };
};

export default useBackendStatus;
