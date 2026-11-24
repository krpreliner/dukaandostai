import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Overview } from './pages/Overview';
import { AIWorker } from './pages/AIWorker';
import { Analytics } from './pages/Analytics';
import { GrowthStrategies } from './pages/GrowthStrategies';
import { Approvals } from './pages/Approvals';
import { Inventory } from './pages/Inventory';
import { Customers } from './pages/Customers';
import { ExecutionHistory } from './pages/ExecutionHistory';
import { FailureMonitoring } from './pages/FailureMonitoring';
import { Settings } from './pages/Settings';
import { AIProviders } from './pages/AIProviders';
import { TeamManagement } from './pages/TeamManagement';
import { Integrations } from './pages/Integrations';
import { SystemHealthPage } from './pages/SystemHealth';
import { LoginPage } from './pages/Login';
import { AssistantModal } from './components/ui/AssistantModal';
import { Bot, Sparkles } from 'lucide-react';
import { startWorker, triggerDemoFailure, resetDemoData, getOverview, getPendingApprovals } from './services/api';

const routeTitles: Record<string, string> = {
  '/': 'Overview Command Centre',
  '/worker': 'AI Worker Command Centre',
  '/analytics': 'Business Intelligence & Analytics',
  '/strategies': 'Autonomous Growth Strategies',
  '/approvals': 'Human-in-the-Loop Approval Centre',
  '/inventory': 'Inventory Intelligence & Stock Health',
  '/customers': 'Customer Cohorts & Insights',
  '/history': 'Audit & Execution History',
  '/failures': 'Failure Monitoring & Safety Guardrails',
  '/ai-providers': 'AI Providers & Routing Management',
  '/team': 'Team & Store Roles Management',
  '/integrations': 'External Integrations & Connectors',
  '/health': 'System Health & Telemetry',
  '/settings': 'System Settings & Governance',
  '/login': 'Workspace Authentication'
};

const AppContent: React.FC = () => {
  const location = useLocation();
  const pageTitle = routeTitles[location.pathname] || 'DukaanDost AI';
  const { user } = useAuth();

  const [workerStatus, setWorkerStatus] = useState<string>('IDLE');
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);
  const [isStartingWorker, setIsStartingWorker] = useState(false);
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

  const refreshGlobalState = async () => {
    try {
      const [ov, approvals] = await Promise.all([
        getOverview(),
        getPendingApprovals()
      ]);
      setWorkerStatus(ov.worker_status || 'IDLE');
      setPendingApprovalsCount(approvals ? approvals.length : 0);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    refreshGlobalState();
    const interval = setInterval(refreshGlobalState, 3500);
    return () => clearInterval(interval);
  }, []);

  const handleStartWorker = async () => {
    setIsStartingWorker(true);
    try {
      await startWorker(10000.0);
      await refreshGlobalState();
    } catch (err) {
      console.error(err);
    } finally {
      setIsStartingWorker(false);
    }
  };

  const handleTriggerFailure = async () => {
    try {
      await triggerDemoFailure();
      await refreshGlobalState();
      alert('Simulated failure condition activated: Butter cost price ₹60 exceeds selling price ₹55.');
    } catch (err) {
      console.error(err);
    }
  };

  const handleReset = async () => {
    try {
      await resetDemoData();
      await refreshGlobalState();
      window.location.reload();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#050505] text-white">
      {/* Sidebar */}
      <Sidebar pendingApprovalsCount={pendingApprovalsCount} />

      {/* Main Body */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        <Header
          pageTitle={pageTitle}
          workerStatus={workerStatus}
          onStartWorker={handleStartWorker}
          onTriggerFailure={handleTriggerFailure}
          onReset={handleReset}
          onOpenAssistant={() => setIsAssistantOpen(true)}
          isLoading={isStartingWorker}
        />

        <main className="flex-1 overflow-y-auto overflow-x-hidden">
          <Routes>
            <Route path="/" element={<Overview onStartWorker={handleStartWorker} />} />
            <Route path="/worker" element={<AIWorker />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/strategies" element={<GrowthStrategies />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/history" element={<ExecutionHistory />} />
            <Route path="/failures" element={<FailureMonitoring />} />
            <Route path="/ai-providers" element={<AIProviders />} />
            <Route path="/team" element={<TeamManagement />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/health" element={<SystemHealthPage />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/login" element={<LoginPage onLoginSuccess={() => window.location.href = '/'} />} />
          </Routes>
        </main>
      </div>

      {/* Conversational AI Business Partner Slide-over Modal */}
      <AssistantModal
        isOpen={isAssistantOpen}
        onClose={() => setIsAssistantOpen(false)}
      />

      {/* Floating AI Business Assistant Action Button */}
      <button
        onClick={() => setIsAssistantOpen(true)}
        title="Chat with DukaanDost AI Business Partner"
        className="fixed bottom-6 right-6 z-30 px-4 py-3 rounded-full bg-[#22D3EE] hover:bg-[#06b6d4] text-black font-semibold text-xs shadow-xl shadow-[#22D3EE]/25 transition-all hover:scale-105 cursor-pointer flex items-center gap-2 group border border-cyan-300/40"
      >
        <Sparkles className="w-4 h-4 fill-current animate-spin" style={{ animationDuration: '6s' }} />
        <span>Ask DukaanDost AI</span>
      </button>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <LanguageProvider>
          <AppContent />
        </LanguageProvider>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
