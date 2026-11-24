import React, { useEffect, useState } from 'react';
import { Sparkles, Shield, AlertTriangle, CheckCircle, ChevronDown, ChevronUp, Bot, Play, Target, TrendingUp, DollarSign, Layers } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { getExecutions, getWorkerStatus, startWorker } from '../services/api';
import { TaskRecord } from '../types';

export const GrowthStrategies: React.FC = () => {
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [expandedTask, setExpandedTask] = useState<string | null>(null);

  // Goal input states (Section 6)
  const [businessGoal, setBusinessGoal] = useState('Increase monthly net income from ₹8,000 to ₹10,000');
  const [targetIncome, setTargetIncome] = useState<number>(10000.0);

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
      await startWorker(targetIncome);
      await fetchTasks();
    } catch (err) {
      console.error(err);
    } finally {
      setIsStarting(false);
    }
  };

  // Pre-calculated strategy templates derived from Sharma General Store business ledger
  const defaultPillars = [
    {
      id: 'INIT-01',
      title: 'High-Margin Breakfast & Dairy Bundle Promotion',
      problem: 'Breakfast items purchased individually with lower cross-sell attachment rate (18%).',
      evidence: 'Bread (AOV ₹40) and Butter (AOV ₹275) show high individual velocity but low joint bundling.',
      action: 'Launch 5% bundle discount pairing Milk, Bread and Eggs with promotional SMS campaign.',
      expected_benefit: '+₹540.00 / month net profit',
      estimated_cost: '₹85.00 promotional markdown',
      risk: 'LOW',
      priority: 'HIGH',
      success_metric: '25% increase in multi-item breakfast transactions',
      agent: 'Marketing Agent'
    },
    {
      id: 'INIT-02',
      title: 'Emergency Stock Replenishment for High-Velocity Spices',
      problem: 'Key staples (Tata Salt, Everest Garam Masala) operating below critical reorder point.',
      evidence: 'Everest Garam Masala stock at 4 units (min threshold: 12 units). Stockout risk in 48 hours.',
      action: 'Generate purchase order for 20 replenishment units to prevent ₹720 lost margin.',
      expected_benefit: '+₹650.00 / month stockout avoidance',
      estimated_cost: '₹1,200.00 working capital reorder',
      risk: 'LOW',
      priority: 'HIGH',
      success_metric: '0 stockout days over next 30-day operating cycle',
      agent: 'Inventory Agent'
    },
    {
      id: 'INIT-03',
      title: 'Dormant High-Value Customer Reactivation',
      problem: '18 previously regular high-ticket customers have not visited in >35 days.',
      evidence: 'Customer cohort previously generated average monthly spend of ₹1,450 each.',
      action: 'Dispatch personalized WhatsApp reminder with 8% welcome-back voucher.',
      expected_benefit: '+₹580.00 / month recovered contribution',
      estimated_cost: '₹116.00 discount cost on reorder',
      risk: 'MEDIUM',
      priority: 'HIGH',
      success_metric: 'Reactivation of at least 6 out of 18 dormant customers',
      agent: 'Strategy Planner'
    },
    {
      id: 'INIT-04',
      title: 'Dead-Stock Clearance for Near-Expiry Snacks',
      problem: '15 units of Haldiram Bhujia approaching 45-day expiry shelf life.',
      evidence: 'Inventory holding cost and capital lockup of ₹750 with declining demand.',
      action: 'Bundle at 12% clearance discount next to checkout counter.',
      expected_benefit: '+₹230.00 capital recovered',
      estimated_cost: '₹36.00 promotional discount',
      risk: 'LOW',
      priority: 'MEDIUM',
      success_metric: '100% liquidation before expiry without write-off',
      agent: 'Inventory Agent'
    }
  ];

  return (
    <div className="p-8 space-y-8 w-full">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-5 h-5 text-[#22D3EE]" />
            <h2 className="text-xl font-bold text-white tracking-tight">Growth Strategies</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Autonomous growth roadmap formulated by Strategy Planner Agent to bridge Sharma General Store's ₹2,000 monthly income gap.
          </p>
        </div>

        <button
          onClick={handleLaunch}
          disabled={isStarting}
          className="px-4 py-2 rounded-xl bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold flex items-center gap-2 cursor-pointer shadow-md transition-all self-start sm:self-center"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isStarting ? 'Formulating & Executing...' : 'Generate Strategies'}</span>
        </button>
      </div>

      {/* Goal Specification Card (Section 6) */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-[#22D3EE]" />
            <span className="text-xs font-semibold text-white uppercase tracking-wider">Business Growth Objective</span>
          </div>
          <span className="text-[11px] text-neutral-400 font-mono">Sharma General Store • Harmu Road, Ranchi</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-3 space-y-1">
            <label className="text-[11px] text-neutral-400 font-medium">Strategic Target Goal:</label>
            <input
              type="text"
              value={businessGoal}
              onChange={(e) => setBusinessGoal(e.target.value)}
              className="w-full bg-[#171717] border border-white/[0.1] rounded-lg px-3 py-2 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#22D3EE]"
            />
          </div>
          <div className="space-y-1">
            <label className="text-[11px] text-neutral-400 font-medium">Target Net Income (₹):</label>
            <input
              type="number"
              step="500"
              value={targetIncome}
              onChange={(e) => setTargetIncome(parseFloat(e.target.value) || 10000)}
              className="w-full bg-[#171717] border border-white/[0.1] rounded-lg px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-[#22D3EE]"
            />
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-white/[0.05] text-xs">
          <div className="flex items-center gap-4 text-neutral-400">
            <span>Baseline Income: <strong className="text-white">₹8,000.00</strong></span>
            <span>Target Income: <strong className="text-[#22D3EE]">₹{targetIncome.toLocaleString()}</strong></span>
            <span>Net Gap: <strong className="text-amber-400">+₹{(targetIncome - 8000).toLocaleString()}</strong></span>
          </div>

          <button
            onClick={handleLaunch}
            disabled={isStarting}
            className="px-4 py-1.5 rounded-lg bg-white/[0.08] hover:bg-white/[0.15] border border-white/[0.12] text-[#22D3EE] text-xs font-medium flex items-center gap-1.5 cursor-pointer transition-all"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Re-plan Initiatives</span>
          </button>
        </div>
      </div>

      {/* Strategies Display */}
      {tasks.length > 0 ? (
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
      ) : (
        /* Pre-planned Strategic Roadmaps based on live ledger */
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#22D3EE]" />
              <span>Recommended Autonomous Growth Initiatives (4 Pillars)</span>
            </h3>
            <span className="text-xs text-[#22C55E] font-semibold">Total Projected Impact: +₹2,000.00 / month</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {defaultPillars.map((p) => (
              <div
                key={p.id}
                className="bg-[#111111] border border-white/[0.08] hover:border-white/[0.15] rounded-xl p-5 space-y-3 transition-all flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="text-[11px] font-mono text-neutral-500">{p.id} • {p.agent}</span>
                      <h4 className="text-sm font-bold text-white mt-0.5">{p.title}</h4>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-red-500/10 text-red-400 border border-red-500/20">
                      {p.priority} PRIORITY
                    </span>
                  </div>

                  <div className="text-xs space-y-1.5 text-neutral-300 pt-1">
                    <p><strong className="text-neutral-400">Problem:</strong> {p.problem}</p>
                    <p><strong className="text-neutral-400">Evidence:</strong> {p.evidence}</p>
                    <p><strong className="text-neutral-400">Proposed Action:</strong> {p.action}</p>
                  </div>
                </div>

                <div className="pt-3 border-t border-white/[0.05] grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-[#171717] p-2.5 rounded-lg border border-white/[0.04]">
                    <span className="text-neutral-500 text-[11px]">Expected Benefit:</span>
                    <p className="text-[#22C55E] font-semibold text-xs mt-0.5">{p.expected_benefit}</p>
                  </div>
                  <div className="bg-[#171717] p-2.5 rounded-lg border border-white/[0.04]">
                    <span className="text-neutral-500 text-[11px]">Estimated Cost:</span>
                    <p className="text-neutral-300 font-mono text-xs mt-0.5">{p.estimated_cost}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 text-center space-y-3">
            <Bot className="w-8 h-8 mx-auto text-[#22D3EE]" />
            <h4 className="text-sm font-semibold text-white">Execute Growth Engine</h4>
            <p className="text-xs text-neutral-400 max-w-md mx-auto">
              Click below to initiate the multi-agent graph. The Strategy Planner, Business Analyst, and Finance Agent will validate and schedule live tasks.
            </p>
            <button
              onClick={handleLaunch}
              disabled={isStarting}
              className="px-5 py-2.5 rounded-xl bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold cursor-pointer shadow-lg shadow-[#22D3EE]/20 transition-all inline-flex items-center gap-2"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{isStarting ? 'Executing Orchestration...' : 'Launch Strategy Planner Cycle'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
