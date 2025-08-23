import { Box } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';

// Components
import FlowMonitor from './components/FlowMonitor';
import MongoDBAtlasTest from './components/MongoDBAtlasTest';
import Navbar from './components/Navbar';
import NotificationSystem from './components/NotificationSystem';
import Sidebar from './components/Sidebar';

// Pages
import AdvancedWebSearch from './pages/AdvancedWebSearch';
import AgentsConfig from './pages/AgentsConfig';
import AgentsFlows from './pages/AgentsFlows';
import Appointments from './pages/Appointments';
import CaseDetail from './pages/CaseDetail';
import Cases from './pages/Cases';
import Chat from './pages/Chat';
import Clients from './pages/Clients';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import FlowPlayground from './pages/FlowPlayground';
import LegalSearch from './pages/LegalSearch';
import LegalValidation from './pages/LegalValidation';
import Pipeline from './pages/Pipeline';
import Settings from './pages/Settings';

// Thème DEFENSEUR-IA
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1565c0', // Bleu juridique professionnel
      light: '#5e92f3',
      dark: '#003c8f',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#f57c00', // Orange pour les accents
      light: '#ffad42',
      dark: '#bb4d00',
      contrastText: '#ffffff',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
    text: {
      primary: '#1a1a1a',
      secondary: '#666666',
    },
    success: {
      main: '#2e7d32',
    },
    warning: {
      main: '#f57c00',
    },
    error: {
      main: '#d32f2f',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
      color: '#1a1a1a',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 500,
      color: '#1a1a1a',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          {/* Sidebar */}
          <Sidebar />
          
          {/* Main Content */}
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            {/* Navbar */}
            <Navbar />
            
            {/* Page Content */}
            <Box sx={{ flexGrow: 1, p: 3, backgroundColor: 'background.default' }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/cases" element={<Cases />} />
                <Route path="/cases/:dossierId" element={<CaseDetail />} />
                <Route path="/clients" element={<Clients />} />
                <Route path="/documents" element={<Documents />} />
                <Route path="/appointments" element={<Appointments />} />
                <Route path="/pipeline" element={<Pipeline />} />
                <Route path="/agents-flows" element={<AgentsFlows />} />
                <Route path="/flow-playground" element={<FlowPlayground />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/legal-search" element={<LegalSearch />} />
                <Route path="/agents-config" element={<AgentsConfig />} />
                <Route path="/legal-validation" element={<LegalValidation />} />
                <Route path="/advanced-web-search" element={<AdvancedWebSearch />} />
                <Route path="/mongodb-test" element={<MongoDBAtlasTest />} />
                <Route path="/flow-monitor" element={<FlowMonitor />} />
              </Routes>
            </Box>
          </Box>
          
          {/* Système de notifications */}
          <NotificationSystem />
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
