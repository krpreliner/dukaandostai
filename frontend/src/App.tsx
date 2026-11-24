import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
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
  '/settings': 'System Settings & Governance',
};

const AppContent: React.FC = () => {
  const location = useLocation();
  const pageTitle = routeTitles[location.pathname] || 'DukaanDost AI';

  const [workerStatus, setWorkerStatus] = useState<string>('IDLE');
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);
  const [isStartingWorker, setIsStartingWorker] = useState(false);

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
    <div className="flex min-h-screen bg-[#050505] text-white">
      {/* Sidebar */}
      <Sidebar pendingApprovalsCount={pendingApprovalsCount} />

      {/* Main Body */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          pageTitle={pageTitle}
          workerStatus={workerStatus}
          onStartWorker={handleStartWorker}
          onTriggerFailure={handleTriggerFailure}
          onReset={handleReset}
          isLoading={isStartingWorker}
        />

        <main className="flex-1 overflow-y-auto">
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
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
};

export default App;
