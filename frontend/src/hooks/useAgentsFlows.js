import { useState, useEffect, useCallback } from 'react';
import { agentsFlowsAPI } from '../services/api';

/**
 * Hook personnalisé pour la gestion des agents et flows DEFENSEUR-IA
 */
export const useAgentsFlows = () => {
  const [agentsStatus, setAgentsStatus] = useState([]);
  const [flowLogs, setFlowLogs] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsConnection, setWsConnection] = useState(null);

  // Récupérer le statut des agents
  const fetchAgentsStatus = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await agentsFlowsAPI.getAgentsStatus();
      setAgentsStatus(response.agents || []);
      setError(null);
    } catch (err) {
      console.error('Erreur lors de la récupération du statut des agents:', err);
      setError('Impossible de récupérer le statut des agents');
      // Fallback avec données mock
      setAgentsStatus(getMockAgentsData());
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Récupérer les logs de flows
  const fetchFlowLogs = useCallback(async () => {
    try {
      const response = await agentsFlowsAPI.getFlowLogs();
      setFlowLogs(response.flows || []);
    } catch (err) {
      console.error('Erreur lors de la récupération des logs:', err);
      // Fallback avec données mock
      setFlowLogs(getMockFlowLogs());
    }
  }, []);

  // Récupérer les métriques
  const fetchMetrics = useCallback(async () => {
    try {
      const response = await agentsFlowsAPI.getMetrics();
      setMetrics(response || {});
    } catch (err) {
      console.error('Erreur lors de la récupération des métriques:', err);
      setMetrics(getMockMetrics());
    }
  }, []);

  // Connexion WebSocket pour le temps réel
  const connectWebSocket = useCallback(() => {
    try {
      const wsUrl = agentsFlowsAPI.getWebSocketUrl();
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connecté pour les agents/flows');
        setWsConnection(ws);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          switch (data.type) {
            case 'agent_status_update':
              setAgentsStatus(prev => 
                prev.map(agent => 
                  agent.id === data.agent_id 
                    ? { ...agent, ...data.status }
                    : agent
                )
              );
              break;
              
            case 'flow_update':
              setFlowLogs(prev => 
                prev.map(flow => 
                  flow.id === data.flow_id 
                    ? { ...flow, ...data.update }
                    : flow
                )
              );
              break;
              
            case 'metrics_update':
              setMetrics(prev => ({ ...prev, ...data.metrics }));
              break;
              
            default:
              console.log('Message WebSocket non géré:', data);
          }
        } catch (err) {
          console.error('Erreur parsing WebSocket:', err);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket fermé, tentative de reconnexion...');
        setWsConnection(null);
        // Reconnexion automatique après 3 secondes
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error('Erreur WebSocket:', error);
      };

    } catch (err) {
      console.error('Impossible de se connecter au WebSocket:', err);
    }
  }, []);

  // Actions sur les flows
  const pauseFlow = useCallback(async (flowId) => {
    try {
      await agentsFlowsAPI.pauseFlow(flowId);
      await fetchFlowLogs(); // Rafraîchir les logs
    } catch (err) {
      console.error('Erreur lors de la pause du flow:', err);
      throw err;
    }
  }, [fetchFlowLogs]);

  const resumeFlow = useCallback(async (flowId) => {
    try {
      await agentsFlowsAPI.resumeFlow(flowId);
      await fetchFlowLogs();
    } catch (err) {
      console.error('Erreur lors de la reprise du flow:', err);
      throw err;
    }
  }, [fetchFlowLogs]);

  const cancelFlow = useCallback(async (flowId) => {
    try {
      await agentsFlowsAPI.cancelFlow(flowId);
      await fetchFlowLogs();
    } catch (err) {
      console.error('Erreur lors de l\'annulation du flow:', err);
      throw err;
    }
  }, [fetchFlowLogs]);

  // Rafraîchir toutes les données
  const refreshAll = useCallback(async () => {
    await Promise.all([
      fetchAgentsStatus(),
      fetchFlowLogs(),
      fetchMetrics()
    ]);
  }, [fetchAgentsStatus, fetchFlowLogs, fetchMetrics]);

  // Initialisation
  useEffect(() => {
    refreshAll();
    connectWebSocket();

    // Nettoyage
    return () => {
      if (wsConnection) {
        wsConnection.close();
      }
    };
  }, [refreshAll, connectWebSocket, wsConnection]);

  // Rafraîchissement périodique (toutes les 30 secondes)
  useEffect(() => {
    const interval = setInterval(refreshAll, 30000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  return {
    agentsStatus,
    flowLogs,
    metrics,
    isLoading,
    error,
    wsConnection: !!wsConnection,
    actions: {
      pauseFlow,
      resumeFlow,
      cancelFlow,
      refreshAll,
      fetchAgentsStatus,
      fetchFlowLogs,
      fetchMetrics
    }
  };
};

// Données mock pour fallback
const getMockAgentsData = () => [
  {
    id: '00',
    name: 'Écouteur',
    emoji: '🎤',
    description: 'Speech-to-Text',
    status: 'active',
    color: 'success.light',
    lastExecution: new Date().toISOString(),
    executionTime: '2.3s',
    successRate: 98.5,
    totalExecutions: 1247
  },
  {
    id: '01',
    name: 'Cadreur Juridique',
    emoji: '⚖️',
    description: 'Analyse juridique Légifrance',
    status: 'active',
    color: 'primary.light',
    lastExecution: new Date(Date.now() - 60000).toISOString(),
    executionTime: '4.7s',
    successRate: 96.2,
    totalExecutions: 1198
  },
  // ... autres agents
];

const getMockFlowLogs = () => [
  {
    id: 'flow_001',
    caseId: 'dossier_17591da5',
    caseName: 'Ahmed Benali - OQTF',
    startTime: new Date(Date.now() - 300000).toISOString(),
    endTime: new Date().toISOString(),
    status: 'completed',
    totalDuration: '5m 27s',
    steps: [
      { agentId: '00', status: 'completed', duration: '2.3s', timestamp: '03:00:00' },
      { agentId: '01', status: 'completed', duration: '4.7s', timestamp: '03:00:03' },
      // ... autres étapes
    ]
  }
];

const getMockMetrics = () => ({
  totalFlows: 1247,
  activeFlows: 3,
  completedFlows: 1244,
  averageExecutionTime: '4m 32s',
  successRate: 96.8,
  agentsHealth: 'excellent'
});

export default useAgentsFlows;
