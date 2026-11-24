import React, { useEffect, useState } from 'react';
import { Sparkles, Shield, AlertTriangle, CheckCircle, ChevronDown, ChevronUp, Bot, Play } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { getExecutions, getWorkerStatus, startWorker } from '../services/api';
import { TaskRecord } from '../types';

export const GrowthStrategies: React.FC = () => {
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [expandedTask, setExpandedTask] = useState<string | null>(null);

  const fetchTasks = async () => {
    try {
      const execs = await getExecutions();
      if (execs && execs.length > 0) {
        const latest = execs[0];
        const st = await getWorkerStatus(latest.execution_id);
        setTasks(st.tasks || []);
      } else {
        setTasks([]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleLaunch = async () => {
    setIsStarting(true);
    try {
      await startWorker(10000.0);
      await fetchTasks();
    } catch (err) {
      console.error(err);
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="p-8 space-y-8 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-4 h-4 text-[#22D3EE]" />
            <h2 className="text-xl font-bold text-white tracking-tight">Growth Strategies</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Autonomous strategy roadmap formulated by Strategy Planner Agent to bridge Sharma General Store's ₹2,000 monthly income gap.
          </p>
        </div>

        {tasks.length === 0 && (
          <button
            onClick={handleLaunch}
            disabled={isStarting}
            className="px-4 py-2 rounded-xl bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold flex items-center gap-2 cursor-pointer shadow-md"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isStarting ? 'Formulating...' : 'Generate Strategies'}</span>
          </button>
        )}
      </div>

      {tasks.length === 0 ? (
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-12 text-center text-neutral-400">
          <Bot className="w-10 h-10 mx-auto mb-3 text-[#22D3EE] opacity-60" />
          <h3 className="text-base font-semibold text-white">No Growth Plan Generated Yet</h3>
          <p className="text-xs text-neutral-500 max-w-md mx-auto mt-1 mb-4">
            The Strategy Planner Agent generates real initiatives once an execution cycle begins. Start the AI Worker to analyze live store records and construct the plan.
          </p>
          <button
            onClick={handleLaunch}
            disabled={isStarting}
            className="px-5 py-2 rounded-xl bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold cursor-pointer transition-all inline-flex items-center gap-2 shadow-lg shadow-[#22D3EE]/20"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Launch Strategy Planner</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {tasks.map((t) => {
            const isExpanded = expandedTask === t.task_id;
            return (
              <div
                key={t.task_id}
                className="bg-[#111111] border border-white/[0.08] hover:border-white/[0.15] rounded-xl p-6 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div>
                      <span className="text-[11px] font-mono text-neutral-500 uppercase tracking-wider">{t.task_id}</span>
                      <h3 className="text-base font-semibold text-white mt-0.5">{t.task_name}</h3>
                    </div>
                    <StatusBadge status={t.status} size="sm" />
                  </div>

                  <div className="flex flex-wrap items-center gap-2 my-3">
                    <span className="text-xs px-2.5 py-1 rounded bg-[#171717] border border-white/[0.06] text-neutral-300 flex items-center gap-1.5">
                      <Bot className="w-3.5 h-3.5 text-[#22D3EE]" />
                      {t.assigned_agent}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded font-medium border ${
                      t.priority === 'HIGH'
                        ? 'bg-red-500/10 text-red-400 border-red-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      {t.priority} Priority
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-neutral-800 text-neutral-400 border border-white/[0.05]">
                      Risk: {t.risk_level}
                    </span>
                    {t.approval_required && (
                      <span className="text-xs px-2 py-0.5 rounded bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20">
                        Sign-off Required
                      </span>
                    )}
                  </div>

                  <div className="bg-[#171717] rounded-lg p-3 border border-white/[0.04] grid grid-cols-2 gap-3 text-xs mb-4">
                    <div>
                      <span className="text-neutral-500">Expected Profit:</span>
                      <p className="text-white font-semibold text-sm mt-0.5">₹{t.expected_impact.toFixed(2)}</p>
                    </div>
                    <div>
                      <span className="text-neutral-500">Simulated Impact:</span>
                      <p className="text-[#22C55E] font-semibold text-sm mt-0.5">
                        {t.simulated_impact > 0 ? `+₹${t.simulated_impact.toFixed(2)}` : 'Pending execution'}
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <button
                    onClick={() => setExpandedTask(isExpanded ? null : t.task_id)}
                    className="w-full pt-3 border-t border-white/[0.05] flex items-center justify-between text-xs text-neutral-400 hover:text-white transition-all cursor-pointer"
                  >
                    <span>{isExpanded ? 'Hide Detailed Reasoning' : 'Inspect Agent Reasoning'}</span>
                    {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {isExpanded && (
                    <div className="mt-3 p-3 bg-black/60 rounded-lg border border-white/[0.05] text-xs text-neutral-300 space-y-2 animate-in fade-in duration-200">
                      <p><strong className="text-white">Execution Result:</strong> {t.execution_result || 'Pending graph execution.'}</p>
                      {t.failure_reason && (
                        <p className="text-red-400"><strong className="text-red-300">Failure / Gatekeeper Reason:</strong> {t.failure_reason}</p>
                      )}
                      <p className="text-neutral-500 text-[11px]">
                        Validated by Finance Agent for non-negative gross margin and 15% discount threshold.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
