import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  Target,
  Users,
  Wallet,
  ArrowRight,
  ShieldAlert,
  Bot,
  Activity,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import { MetricCard } from '../components/ui/MetricCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { DailyBriefingCard } from '../components/ui/DailyBriefingCard';
import { BusinessOverview, AgentInfo, AuditLog } from '../types';
import { getOverview, getAgentsStatus, getAuditLogs } from '../services/api';
import { useLanguage } from '../contexts/LanguageContext';

export const Overview: React.FC<{ onStartWorker: () => void }> = ({ onStartWorker }) => {
  const { language } = useLanguage();
  const [overview, setOverview] = useState<BusinessOverview | null>(null);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [ov, ag, lg] = await Promise.all([
        getOverview(),
        getAgentsStatus(),
        getAuditLogs()
      ]);
      setOverview(ov);
      setAgents(ag.agents || []);
      setLogs(lg.slice(0, 5));
    } catch (err) {
      console.error('Error fetching overview data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3500);
    return () => clearInterval(interval);
  }, []);

  if (loading && !overview) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center gap-3 text-neutral-400">
          <Activity className="w-5 h-5 animate-spin text-[#22D3EE]" />
          <span>Loading Sharma General Store intelligence...</span>
        </div>
      </div>
    );
  }

  if (!overview) return null;

  const isSimulated = overview.simulated_net_income > overview.initial_net_income;

  return (
    <div className="p-8 space-y-8 w-full">
      {/* Welcome Hero Banner */}
      <div className="bg-gradient-to-r from-[#111111] via-[#141414] to-[#0A0A0A] border border-white/[0.08] rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-full bg-[#22D3EE]/5 blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#22D3EE]/10 text-[#22D3EE] border border-[#22D3EE]/20 flex items-center gap-1.5">
                <Sparkles className="w-3 h-3" /> Autonomous Kirana Partner
              </span>
              <span className="text-xs text-neutral-500">• Ranchi, Jharkhand</span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">
              {language === 'hi' ? 'नमस्ते, शर्मा जी!' : 'Good Evening, Sharma Ji!'}
            </h2>
            <p className="text-neutral-400 text-sm mt-1 max-w-xl">
              {language === 'hi'
                ? 'आपका ऑटोनॉमस ग्रोथ मैनेजर सक्रिय है। लक्ष्य: इन्वेंटरी सुधार और ग्राहकों की वापसी द्वारा मासिक शुद्ध मुनाफे को ₹8,000 से ₹10,000 (+25% वृद्धि) तक ले जाना।'
                : 'Your autonomous growth manager is active. Goal: Bridge monthly net income from ₹8,000 to ₹10,000 (+25% growth) via inventory optimisation and customer reactivation.'}
            </p>
          </div>

          <div className="flex items-center gap-3 self-start md:self-center">
            <button
              onClick={onStartWorker}
              className="px-5 py-2.5 rounded-xl bg-[#22D3EE] hover:bg-[#06b6d4] text-black font-semibold text-sm flex items-center gap-2 shadow-lg shadow-[#22D3EE]/20 transition-all cursor-pointer"
            >
              <Bot className="w-4 h-4" />
              <span>{language === 'hi' ? 'ग्रोथ चक्र शुरू करें' : 'Launch Growth Cycle'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* AI Daily Business Briefing */}
      <DailyBriefingCard />

      {/* 4 Primary Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Baseline Net Income"
          value={`₹${overview.initial_net_income.toLocaleString('en-IN')}`}
          subtitle="Calculated from 320 Kirana transactions"
          icon={Wallet}
          accentColor="cyan"
        />
        <MetricCard
          title="Target Net Income"
          value={`₹${overview.target_net_income.toLocaleString('en-IN')}`}
          subtitle="Monthly milestone (+₹2,000)"
          icon={Target}
          trend="+25.0%"
          trendPositive={true}
          accentColor="indigo"
        />
        <MetricCard
          title="Income Gap"
          value={`₹${overview.income_gap.toLocaleString('en-IN')}`}
          subtitle={overview.income_gap === 0 ? "Target Achieved!" : "Remaining opportunity"}
          icon={TrendingUp}
          accentColor="amber"
        />
        <MetricCard
          title="Synthetic Customers"
          value={overview.total_customers}
          subtitle="120 customers across Ranchi localities"
          icon={Users}
          accentColor="green"
        />
      </div>

      {/* Goal Progress & Simulated Income Card */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-semibold text-white">Target Income Progression</h3>
              {isSimulated && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-[#22C55E]/15 text-[#22C55E] border border-[#22C55E]/30">
                  Simulated Outcome
                </span>
              )}
            </div>
            <p className="text-xs text-neutral-400 mt-1">
              ₹{overview.initial_net_income.toLocaleString('en-IN')} Baseline → ₹{overview.target_net_income.toLocaleString('en-IN')} Monthly Goal
            </p>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white tracking-tight">
              ₹{overview.simulated_net_income.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
            <span className="text-xs text-[#22C55E] font-medium">
              +{overview.simulated_improvement.toLocaleString('en-IN', { maximumFractionDigits: 0 })} simulated
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-[#1A1A1A] h-3 rounded-full overflow-hidden p-0.5 border border-white/[0.04]">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#22D3EE] to-[#818CF8] transition-all duration-700"
            style={{ width: `${Math.min(100, Math.max(10, overview.percentage_achieved))}%` }}
          />
        </div>

        <div className="flex justify-between items-center text-xs text-neutral-400 mt-2">
          <span>₹8,000 (Baseline)</span>
          <span className="font-semibold text-white">{overview.percentage_achieved}% Achieved</span>
          <span>₹10,000 (Target)</span>
        </div>
      </div>

      {/* Financial Waterfall Breakdown */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
        <h3 className="text-base font-semibold text-white mb-1">Financial Reconciliation</h3>
        <p className="text-xs text-neutral-400 mb-6">
          Deterministic calculation derived strictly from atomic transactional records.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
          <div className="p-4 rounded-lg bg-[#171717] border border-white/[0.05]">
            <span className="text-xs text-neutral-400 font-medium">Revenue</span>
            <p className="text-lg font-bold text-white mt-1">₹{overview.revenue.toLocaleString('en-IN')}</p>
            <span className="text-[10px] text-neutral-500">320 Transactions</span>
          </div>

          <div className="p-4 rounded-lg bg-[#171717] border border-white/[0.05]">
            <span className="text-xs text-neutral-400 font-medium">COGS</span>
            <p className="text-lg font-bold text-neutral-300 mt-1">-₹{overview.cogs.toLocaleString('en-IN')}</p>
            <span className="text-[10px] text-neutral-500">Cost of Goods</span>
          </div>

          <div className="p-4 rounded-lg bg-[#171717] border border-white/[0.05]">
            <span className="text-xs text-neutral-400 font-medium">Gross Profit</span>
            <p className="text-lg font-bold text-[#22D3EE] mt-1">₹{overview.gross_profit.toLocaleString('en-IN')}</p>
            <span className="text-[10px] text-neutral-500">20.0% Gross Margin</span>
          </div>

          <div className="p-4 rounded-lg bg-[#171717] border border-white/[0.05]">
            <span className="text-xs text-neutral-400 font-medium">Operating Exp.</span>
            <p className="text-lg font-bold text-[#F59E0B] mt-1">-₹{overview.operating_expenses.toLocaleString('en-IN')}</p>
            <span className="text-[10px] text-neutral-500">Rent, Power, Help</span>
          </div>

          <div className="p-4 rounded-lg bg-[#171717] border border-[#22C55E]/20 col-span-2 md:col-span-1 bg-[#22C55E]/5">
            <span className="text-xs text-[#22C55E] font-semibold">Net Income</span>
            <p className="text-lg font-bold text-[#22C55E] mt-1">₹{overview.current_net_income.toLocaleString('en-IN')}</p>
            <span className="text-[10px] text-[#22C55E]/80">Initial Net Profit</span>
          </div>
        </div>
      </div>

      {/* Agents Status Overview Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-white">Specialized AI Agents Team</h3>
          <span className="text-xs text-neutral-400">6 Specialized Kirana Agents</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="bg-[#111111] border border-white/[0.08] rounded-xl p-5 hover:border-white/[0.15] transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-sm text-white">{agent.name}</span>
                <StatusBadge status={agent.status} size="sm" />
              </div>
              <p className="text-xs font-medium text-[#22D3EE] mb-2">{agent.role}</p>
              <p className="text-xs text-neutral-400 line-clamp-2 leading-relaxed">
                {agent.responsibility}
              </p>
              <div className="mt-3 pt-3 border-t border-white/[0.05] flex items-center justify-between text-[11px] text-neutral-500">
                <span>Recent Activity:</span>
                <span className="text-neutral-400 truncate max-w-[150px]">{agent.last_action}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity Timeline Snippet */}
      {logs.length > 0 && (
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
          <h3 className="text-base font-semibold text-white mb-4">Recent Autonomous Events</h3>
          <div className="space-y-3">
            {logs.map((log) => (
              <div key={log.id} className="flex items-start gap-3 text-xs">
                <div className="w-2 h-2 rounded-full bg-[#22D3EE] mt-1.5 flex-shrink-0" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{log.agent_name}</span>
                    <span className="text-neutral-500">•</span>
                    <span className="text-neutral-400 font-mono text-[10px]">{log.event_type}</span>
                  </div>
                  <p className="text-neutral-300 mt-0.5">{log.details}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
