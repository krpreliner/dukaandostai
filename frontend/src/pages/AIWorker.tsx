import React, { useState, useEffect } from 'react';
import {
  Play,
  RotateCcw,
  CheckCircle2,
  Clock,
  AlertCircle,
  ShieldCheck,
  Bot,
  Zap,
  Activity,
  Layers
} from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { AgentInfo, AuditLog } from '../types';
import { getAgentsStatus, getAuditLogs, startWorker, getOverview } from '../services/api';

export const AIWorker: React.FC = () => {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [workerStatus, setWorkerStatus] = useState<string>('IDLE');
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [isStarting, setIsStarting] = useState(false);
  const [activeTask, setActiveTask] = useState<string>('No active task');

  const fetchWorkerState = async () => {
    try {
      const [agRes, logsRes, ovRes] = await Promise.all([
        getAgentsStatus(),
        getAuditLogs(),
        getOverview()
      ]);
      setAgents(agRes.agents || []);
      setWorkerStatus(agRes.worker_status || ovRes.worker_status || 'IDLE');
      setAuditLogs(logsRes || []);
    } catch (err) {
      console.error('Error fetching AI worker state:', err);
    }
  };

  useEffect(() => {
    fetchWorkerState();
    // Auto-refresh every 3s to capture real-time graph transitions
    const interval = setInterval(fetchWorkerState, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    setIsStarting(true);
    try {
      await startWorker(10000.0);
      await fetchWorkerState();
    } catch (err) {
      console.error('Error starting worker:', err);
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Command Centre Control Header */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-2xl p-6 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-white tracking-tight">AI Worker Command Centre</h2>
              <StatusBadge status={workerStatus} />
            </div>
            <p className="text-sm text-neutral-400 max-w-2xl">
              Autonomous Kirana orchestrator powered by LangGraph. Monitors business metrics, plans strategy, coordinates 6 specialized agents, and executes within financial guardrails.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleStart}
              disabled={isStarting || workerStatus === 'EXECUTING'}
              className={`px-6 py-3 rounded-xl font-semibold text-sm flex items-center gap-2 transition-all shadow-lg ${
                isStarting || workerStatus === 'EXECUTING'
                  ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
                  : 'bg-[#22D3EE] hover:bg-[#06b6d4] text-black shadow-[#22D3EE]/25 hover:scale-[1.02]'
              }`}
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{isStarting ? 'Initiating LangGraph...' : 'START AI WORKER'}</span>
            </button>
          </div>
        </div>

        {/* Current State Ribbon */}
        <div className="mt-6 pt-5 border-t border-white/[0.06] grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          <div>
            <span className="text-neutral-500">Autonomous Cycle:</span>
            <p className="text-white font-medium mt-0.5">Sharma General Store Growth Sprint</p>
          </div>
          <div>
            <span className="text-neutral-500">Execution Engine:</span>
            <p className="text-[#22D3EE] font-mono mt-0.5">LangGraph • SQLite Persistence</p>
          </div>
          <div>
            <span className="text-neutral-500">Human Sign-off Policy:</span>
            <p className="text-neutral-300 font-medium mt-0.5">Interrupt & Resume Required for Bundles</p>
          </div>
        </div>
      </div>

      {/* 6 Specialized Agents Monitoring Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white">Multi-Agent Coordination Matrix</h3>
            <p className="text-xs text-neutral-400 mt-0.5">Real-time status of each specialized worker agent</p>
          </div>
          <span className="text-xs text-neutral-400">6 Agents Active</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => {
            const isActive = agent.status === 'ACTIVE';
            return (
              <div
                key={agent.id}
                className={`bg-[#111111] rounded-xl p-5 border transition-all duration-200 ${
                  isActive
                    ? 'border-[#22D3EE] shadow-lg shadow-[#22D3EE]/10'
                    : 'border-white/[0.08] hover:border-white/[0.15]'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h4 className="font-semibold text-sm text-white">{agent.name}</h4>
                    <span className="text-[11px] font-medium text-[#22D3EE]">{agent.role}</span>
                  </div>
                  <StatusBadge status={agent.status} size="sm" />
                </div>

                <p className="text-xs text-neutral-400 leading-relaxed min-h-[40px]">
                  {agent.responsibility}
                </p>

                <div className="mt-4 pt-3 border-t border-white/[0.05] space-y-1.5 text-xs">
                  <div className="flex items-center justify-between text-neutral-500">
                    <span>Last Activity:</span>
                    <span className="text-neutral-300 truncate max-w-[180px] font-mono text-[11px]">
                      {agent.last_action}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live Execution Timeline & Audit Log */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-semibold text-white">Live Execution Audit Timeline</h3>
            <p className="text-xs text-neutral-400 mt-0.5">Real-time trace of LangGraph node transitions and agent events</p>
          </div>
          <span className="text-xs text-neutral-500 font-mono">
            {auditLogs.length} Events Logged
          </span>
        </div>

        {auditLogs.length === 0 ? (
          <div className="py-12 text-center text-neutral-500 text-sm">
            <Bot className="w-8 h-8 mx-auto mb-2 opacity-40 text-[#22D3EE]" />
            No events logged yet. Click "START AI WORKER" to begin autonomous execution.
          </div>
        ) : (
          <div className="space-y-4 max-h-[450px] overflow-y-auto pr-2">
            {auditLogs.map((log) => (
              <div
                key={log.id}
                className="p-3.5 rounded-lg bg-[#171717] border border-white/[0.05] hover:border-white/[0.1] transition-all flex items-start gap-4"
              >
                <div className="p-2 rounded-lg bg-black border border-white/[0.06] text-[#22D3EE] mt-0.5">
                  <Activity className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-white">{log.agent_name}</span>
                      <span className="text-neutral-600">•</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/[0.05] text-neutral-300">
                        {log.event_type}
                      </span>
                    </div>
                    {log.timestamp && (
                      <span className="text-[10px] text-neutral-500 font-mono">
                        {log.timestamp.slice(11, 19)}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-neutral-300 leading-relaxed">{log.details}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
