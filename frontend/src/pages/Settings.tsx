import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Shield, Server, RefreshCw, AlertOctagon, CheckCircle2, Award } from 'lucide-react';
import { getEvaluation, resetDemoData, triggerDemoFailure } from '../services/api';
import { EvaluationMetrics } from '../types';

export const Settings: React.FC = () => {
  const [evalData, setEvalData] = useState<EvaluationMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  const fetchEval = async () => {
    try {
      const data = await getEvaluation();
      setEvalData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEval();
  }, []);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  };

  const handleReset = async () => {
    try {
      await resetDemoData();
      await fetchEval();
      showToast('Synthetic database reset to baseline: Net Income ₹8,000.00');
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerFailure = async () => {
    try {
      await triggerDemoFailure();
      await fetchEval();
      showToast('Triggered Butter Cost ₹60 > Sell ₹55 negative margin condition.');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <SettingsIcon className="w-5 h-5 text-[#22D3EE]" />
          <h2 className="text-xl font-bold text-white tracking-tight">System Settings & Governance</h2>
        </div>
        <p className="text-sm text-neutral-400">
          Store governance policies, deterministic financial guardrails, and autonomous system evaluation.
        </p>
      </div>

      {toast && (
        <div className="p-3 rounded-lg bg-[#22C55E]/15 border border-[#22C55E]/30 text-[#22C55E] text-xs font-medium animate-in fade-in">
          {toast}
        </div>
      )}

      {/* Evaluation Scorecard */}
      {evalData && (
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-[#22D3EE]" />
              <h3 className="text-base font-semibold text-white">System Evaluation Scorecard</h3>
            </div>
            <span className="text-xs text-neutral-400">Section 10 & 26 Validation</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-3.5 bg-[#171717] rounded-lg border border-white/[0.05]">
              <span className="text-neutral-400">Task Completion Rate</span>
              <p className="text-lg font-bold text-[#22C55E] mt-1">{evalData.completion_rate_pct}%</p>
              <span className="text-[10px] text-neutral-500">{evalData.completed_tasks} / {evalData.total_tasks} completed</span>
            </div>

            <div className="p-3.5 bg-[#171717] rounded-lg border border-white/[0.05]">
              <span className="text-neutral-400">Recovery Rate</span>
              <p className="text-lg font-bold text-[#22D3EE] mt-1">{evalData.recovery_rate_pct}%</p>
              <span className="text-[10px] text-neutral-500">Fault isolation active</span>
            </div>

            <div className="p-3.5 bg-[#171717] rounded-lg border border-white/[0.05]">
              <span className="text-neutral-400">Income Improvement</span>
              <p className="text-lg font-bold text-white mt-1">+₹{evalData.income_improvement.toLocaleString('en-IN')}</p>
              <span className="text-[10px] text-[#22C55E]">Target: +₹2,000</span>
            </div>

            <div className="p-3.5 bg-[#171717] rounded-lg border border-white/[0.05]">
              <span className="text-neutral-400">Duplicate Prevention</span>
              <p className="text-lg font-bold text-[#22C55E] mt-1">
                {evalData.duplicate_execution_prevented ? 'VERIFIED' : 'ACTIVE'}
              </p>
              <span className="text-[10px] text-neutral-500">Zero duplicate runs</span>
            </div>
          </div>
        </div>
      )}

      {/* Store Profile & Policy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Store Profile */}
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 space-y-4">
          <h3 className="text-base font-semibold text-white">Kirana Store Profile</h3>
          <div className="space-y-3 text-xs">
            <div>
              <span className="text-neutral-500 block mb-1">Business Name</span>
              <input
                type="text"
                disabled
                value="Sharma General Store"
                className="w-full bg-[#171717] border border-white/[0.06] rounded-lg px-3 py-2 text-white font-medium cursor-not-allowed"
              />
            </div>
            <div>
              <span className="text-neutral-500 block mb-1">Location</span>
              <input
                type="text"
                disabled
                value="Ranchi, Jharkhand, India"
                className="w-full bg-[#171717] border border-white/[0.06] rounded-lg px-3 py-2 text-white font-medium cursor-not-allowed"
              />
            </div>
            <div>
              <span className="text-neutral-500 block mb-1">Store Owner</span>
              <input
                type="text"
                disabled
                value="Sharma Ji"
                className="w-full bg-[#171717] border border-white/[0.06] rounded-lg px-3 py-2 text-white font-medium cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* Financial Risk Guardrails */}
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 space-y-4">
          <h3 className="text-base font-semibold text-white">Financial Guardrails</h3>
          <div className="space-y-3 text-xs">
            <div>
              <span className="text-neutral-500 block mb-1">Target Monthly Net Income (₹)</span>
              <input
                type="number"
                disabled
                value="10000"
                className="w-full bg-[#171717] border border-white/[0.06] rounded-lg px-3 py-2 text-white font-mono cursor-not-allowed"
              />
            </div>
            <div>
              <span className="text-neutral-500 block mb-1">Maximum Promotional Discount Allowed (%)</span>
              <input
                type="number"
                disabled
                value="15"
                className="w-full bg-[#171717] border border-white/[0.06] rounded-lg px-3 py-2 text-white font-mono cursor-not-allowed"
              />
            </div>
            <div>
              <span className="text-neutral-500 block mb-1">Negative Margin Guardrail</span>
              <div className="p-2.5 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 text-[#22C55E] flex items-center justify-between">
                <span>Enforced deterministically by Finance Agent</span>
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Execution Mode */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold text-white">AI Engine & Execution Mode</h3>
            <p className="text-xs text-neutral-400 mt-0.5">
              Zero paid API dependency: Local deterministic mode executes fully without OpenAI key.
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-[#22D3EE]/15 text-[#22D3EE] border border-[#22D3EE]/30">
            Deterministic Local Mode
          </span>
        </div>

        <div className="p-4 rounded-lg bg-[#171717] border border-white/[0.05] flex items-center justify-between text-xs">
          <div>
            <span className="font-semibold text-white block">Local Deterministic Engine</span>
            <span className="text-neutral-400 text-[11px]">
              Calculates margins, RFM customer clusters, bundles, and LangGraph checkpoints offline.
            </span>
          </div>
          <span className="text-[#22C55E] font-medium">Active</span>
        </div>
      </div>

      {/* Demo Controls */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
        <h3 className="text-base font-semibold text-white mb-2">Live Demonstration Controls</h3>
        <p className="text-xs text-neutral-400 mb-4">
          Control reproducible scenarios for evaluation and internship review.
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleTriggerFailure}
            className="px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all"
          >
            <AlertOctagon className="w-4 h-4" />
            <span>Trigger Butter Negative-Margin Failure</span>
          </button>

          <button
            onClick={handleReset}
            className="px-4 py-2 rounded-lg bg-[#171717] hover:bg-neutral-800 text-white border border-white/[0.08] text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all"
          >
            <RefreshCw className="w-4 h-4 text-[#22D3EE]" />
            <span>Reset Synthetic Kirana Store Data</span>
          </button>
        </div>
      </div>
    </div>
  );
};
