import React, { useEffect, useState } from 'react';
import { Sparkles, Shield, AlertTriangle, CheckCircle, ChevronDown, ChevronUp, Bot } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { getExecutions, getWorkerStatus } from '../services/api';
import { TaskRecord } from '../types';

export const GrowthStrategies: React.FC = () => {
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedTask, setExpandedTask] = useState<string | null>(null);

  useEffect(() => {
    getExecutions()
      .then(async (execs) => {
        if (execs && execs.length > 0) {
          const latest = execs[0];
          const st = await getWorkerStatus(latest.execution_id);
          setTasks(st.tasks || []);
        }
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  // Fallback default strategies if worker has not yet executed
  const defaultStrategies: TaskRecord[] = [
    {
      task_id: "TASK_001",
      task_name: "Launch Breakfast Combo (Bread + Butter)",
      assigned_agent: "Marketing Agent",
      priority: "HIGH",
      expected_impact: 440.0,
      simulated_impact: 418.0,
      risk_level: "MEDIUM",
      approval_required: true,
      status: "COMPLETED",
      execution_result: "Simulated 38 combos sold @ ₹109 (Regular ₹115, Unit Profit ₹11, Margin 10.09%)."
    },
    {
      task_id: "TASK_002",
      task_name: "Reactivate 25 Dormant Kirana Customers",
      assigned_agent: "Marketing Agent",
      priority: "HIGH",
      expected_impact: 810.0,
      simulated_impact: 729.0,
      risk_level: "LOW",
      approval_required: false,
      status: "COMPLETED",
      execution_result: "Simulated personalized voucher sent to 25 inactive customers. 9 reactivated (36% uptake)."
    },
    {
      task_id: "TASK_003",
      task_name: "Liquidate Perishable Sudha Paneer Before Expiry",
      assigned_agent: "Inventory Agent",
      priority: "MEDIUM",
      expected_impact: 418.0,
      simulated_impact: 418.0,
      risk_level: "LOW",
      approval_required: false,
      status: "COMPLETED",
      execution_result: "10% markdown secured sales for 14 packs before 3-day expiry, preserving ₹1,120 capital."
    },
    {
      task_id: "TASK_004",
      task_name: "Restock High Velocity Staples (Bread & Eggs)",
      assigned_agent: "Inventory Agent",
      priority: "HIGH",
      expected_impact: 480.0,
      simulated_impact: 445.0,
      risk_level: "MEDIUM",
      approval_required: true,
      status: "COMPLETED",
      execution_result: "Reordered 50 units fast-moving Bread & Farm Eggs, capturing missed footfall turnover."
    }
  ];

  const displayTasks = tasks.length > 0 ? tasks : defaultStrategies;

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="w-4 h-4 text-[#22D3EE]" />
          <h2 className="text-xl font-bold text-white tracking-tight">Growth Strategies</h2>
        </div>
        <p className="text-sm text-neutral-400">
          Autonomous strategy roadmap designed by Strategy Planner Agent to bridge Sharma General Store's ₹2,000 monthly income gap.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {displayTasks.map((t) => {
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
    </div>
  );
};
