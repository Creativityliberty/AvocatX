import {
    Assessment as AssessmentIcon,
    Download as DownloadIcon,
    Refresh as RefreshIcon,
    Speed as SpeedIcon,
    Timeline as TimelineIcon,
    TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import {
    Alert,
    Box,
    Card,
    CardContent,
    Chip,
    FormControl,
    IconButton,
    InputLabel,
    MenuItem,
    Select,
    Tooltip,
    Typography
} from '@mui/material';
import React, { useEffect, useState } from 'react';
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    Tooltip as RechartsTooltip,
    ResponsiveContainer,
    XAxis,
    YAxis
} from 'recharts';

const ApiMetricsChart = ({ 
  type = 'line',
  metric = 'calls',
  timeRange = '24h',
  height = 300,
  showControls = true,
  title = null,
  agentFilter = 'all'
}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState(metric);
  const [selectedTimeRange, setSelectedTimeRange] = useState(timeRange);
  const [selectedAgent, setSelectedAgent] = useState(agentFilter);
  const [chartType, setChartType] = useState(type);

  const metricOptions = [
    { value: 'calls', label: 'Appels API', color: '#2196f3' },
    { value: 'response_time', label: 'Temps de réponse', color: '#4caf50' },
    { value: 'success_rate', label: 'Taux de succès', color: '#ff9800' },
    { value: 'quota_usage', label: 'Utilisation quota', color: '#f44336' },
    { value: 'errors', label: 'Erreurs', color: '#9c27b0' }
  ];

  const timeRangeOptions = [
    { value: '1h', label: 'Dernière heure' },
    { value: '24h', label: 'Dernières 24h' },
    { value: '7d', label: 'Derniers 7 jours' },
    { value: '30d', label: 'Derniers 30 jours' }
  ];

  const chartTypeOptions = [
    { value: 'line', label: 'Courbe', icon: TimelineIcon },
    { value: 'area', label: 'Zone', icon: TrendingUpIcon },
    { value: 'bar', label: 'Barres', icon: AssessmentIcon },
    { value: 'pie', label: 'Camembert', icon: SpeedIcon }
  ];

  const agentOptions = [
    { value: 'all', label: 'Tous les agents' },
    { value: 'cadreur_juridique', label: 'Cadreur Juridique' },
    { value: 'recherche_web', label: 'Recherche Web' },
    { value: 'relecteur_ia_1', label: 'Relecteur IA #1' },
    { value: 'synthese_strategique', label: 'Synthèse Stratégique' },
    { value: 'avocat_ia', label: 'Avocat IA' }
  ];

  useEffect(() => {
    fetchMetricsData();
  }, [selectedMetric, selectedTimeRange, selectedAgent]);

  const fetchMetricsData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/metrics/legifrance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric: selectedMetric,
          timeRange: selectedTimeRange,
          agent: selectedAgent
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setData(result.data || generateMockData());
      } else {
        setData(generateMockData());
      }
    } catch (error) {
      console.error('Erreur récupération métriques:', error);
      setData(generateMockData());
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    const now = new Date();
    const points = selectedTimeRange === '1h' ? 12 : 
                   selectedTimeRange === '24h' ? 24 : 
                   selectedTimeRange === '7d' ? 7 : 30;
    
    const mockData = [];
    for (let i = points - 1; i >= 0; i--) {
      const date = new Date(now);
      
      if (selectedTimeRange === '1h') {
        date.setMinutes(date.getMinutes() - (i * 5));
      } else if (selectedTimeRange === '24h') {
        date.setHours(date.getHours() - i);
      } else if (selectedTimeRange === '7d') {
        date.setDate(date.getDate() - i);
      } else {
        date.setDate(date.getDate() - i);
      }

      let value;
      switch (selectedMetric) {
        case 'calls':
          value = Math.floor(Math.random() * 50) + 10;
          break;
        case 'response_time':
          value = Math.floor(Math.random() * 200) + 100;
          break;
        case 'success_rate':
          value = Math.floor(Math.random() * 10) + 90;
          break;
        case 'quota_usage':
          value = Math.floor(Math.random() * 30) + 40;
          break;
        case 'errors':
          value = Math.floor(Math.random() * 5);
          break;
        default:
          value = Math.floor(Math.random() * 100);
      }

      mockData.push({
        time: selectedTimeRange === '1h' ? date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) :
              selectedTimeRange === '24h' ? date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }) :
              date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }),
        value,
        timestamp: date.toISOString()
      });
    }
    
    return mockData;
  };

  const generatePieData = () => {
    if (selectedAgent !== 'all') return [];
    
    return agentOptions.slice(1).map((agent, index) => ({
      name: agent.label,
      value: Math.floor(Math.random() * 100) + 20,
      color: `hsl(${index * 60}, 70%, 50%)`
    }));
  };

  const exportData = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Temps,Valeur\n"
      + data.map(row => `"${row.time}",${row.value}`).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `metrics_${selectedMetric}_${selectedTimeRange}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getMetricColor = () => {
    const metricConfig = metricOptions.find(m => m.value === selectedMetric);
    return metricConfig ? metricConfig.color : '#2196f3';
  };

  const getMetricLabel = () => {
    const metricConfig = metricOptions.find(m => m.value === selectedMetric);
    return metricConfig ? metricConfig.label : selectedMetric;
  };

  const renderChart = () => {
    if (loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height }}>
          <Typography>Chargement des métriques...</Typography>
        </Box>
      );
    }

    if (data.length === 0) {
      return (
        <Alert severity="info" sx={{ m: 2 }}>
          Aucune donnée disponible pour cette période
        </Alert>
      );
    }

    const chartProps = {
      width: '100%',
      height,
      data: chartType === 'pie' ? generatePieData() : data,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer {...chartProps}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke={getMetricColor()} 
                strokeWidth={2}
                name={getMetricLabel()}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer {...chartProps}>
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke={getMetricColor()} 
                fill={getMetricColor()}
                fillOpacity={0.3}
                name={getMetricLabel()}
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer {...chartProps}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Bar 
                dataKey="value" 
                fill={getMetricColor()}
                name={getMetricLabel()}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        const pieData = generatePieData();
        return (
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <RechartsTooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="h3">
            {title || `Métriques API - ${getMetricLabel()}`}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Actualiser">
              <IconButton size="small" onClick={fetchMetricsData} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Exporter CSV">
              <IconButton size="small" onClick={exportData}>
                <DownloadIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {showControls && (
          <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Métrique</InputLabel>
              <Select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
              >
                {metricOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Période</InputLabel>
              <Select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
              >
                {timeRangeOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Agent</InputLabel>
              <Select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
              >
                {agentOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 100 }}>
              <InputLabel>Type</InputLabel>
              <Select
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
              >
                {chartTypeOptions.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        )}

        {selectedAgent !== 'all' && (
          <Box sx={{ mb: 2 }}>
            <Chip 
              label={`Agent: ${agentOptions.find(a => a.value === selectedAgent)?.label}`}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>
        )}

        <Box sx={{ width: '100%', height }}>
          {renderChart()}
        </Box>

        {data.length > 0 && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Dernière mise à jour: {new Date().toLocaleTimeString('fr-FR')}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Min: {Math.min(...data.map(d => d.value))}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Max: {Math.max(...data.map(d => d.value))}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Moy: {Math.round(data.reduce((sum, d) => sum + d.value, 0) / data.length)}
              </Typography>
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ApiMetricsChart;
