import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle, RefreshCw, ArrowRight, Check, Wrench } from 'lucide-react';
import { getFailures, updateProductPrice, startWorker, resolveFailure, resolveAllFailures } from '../services/api';
import { FailureRecord } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';

export const FailureMonitoring: React.FC = () => {
  const [failures, setFailures] = useState<FailureRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [isResolving, setIsResolving] = useState(false);
  const [resolvingId, setResolvingId] = useState<number | null>(null);

  const fetchFailuresList = async () => {
    try {
      const data = await getFailures();
      setFailures(data || []);
    } catch (err) {
      console.error('Error fetching failures:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFailuresList();
    const interval = setInterval(fetchFailuresList, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleFixButterAndResume = async () => {
    setIsResolving(true);
    try {
      // Correct Butter price back to healthy margin (Cost 245, Sell 275)
      await updateProductPrice('PROD003', 245.0, 275.0);
      // Resolve any existing failure records
      await resolveAllFailures();
      // Restart worker to revalidate and progress
      await startWorker(10000.0);
      await fetchFailuresList();
    } catch (err) {
      console.error('Resolution failed:', err);
    } finally {
      setIsResolving(false);
    }
  };

  const handleResolveSingle = async (id: number) => {
    setResolvingId(id);
    try {
      await resolveFailure(id);
      await fetchFailuresList();
    } catch (err) {
      console.error('Failed to resolve failure record:', err);
    } finally {
      setResolvingId(null);
    }
  };

  const handleResolveAll = async () => {
    setIsResolving(true);
    try {
      await resolveAllFailures();
      await fetchFailuresList();
    } catch (err) {
      console.error('Failed to resolve all failures:', err);
    } finally {
      setIsResolving(false);
    }
  };

  return (
    <div className="p-8 space-y-6 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <h2 className="text-xl font-bold text-white tracking-tight">Failure Monitoring & Safety Guardrails</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Supervised fault isolation, financial policy violations, and bounded recovery workflows.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {failures.some(f => f.recovery_status !== 'RESOLVED') && (
            <button
              onClick={handleResolveAll}
              disabled={isResolving}
              className="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-medium flex items-center gap-1.5 cursor-pointer transition-all"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Resolve All</span>
            </button>
          )}

          <button
            onClick={fetchFailuresList}
            className="px-3 py-1.5 rounded-lg bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-xs text-neutral-300 flex items-center gap-1.5 cursor-pointer transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Hero Failure Case Inspection */}
      <div className="bg-[#111111] border border-red-500/20 rounded-xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/30">
                Guardrail Enforced
              </span>
              <span className="text-xs text-neutral-400 font-mono">FINANCIAL_GATEKEEPER</span>
            </div>
            <h3 className="text-lg font-bold text-white">Negative Gross Margin Auto-Rejection</h3>
            <p className="text-xs text-neutral-300 leading-relaxed max-w-2xl">
              When a promotional bundle incorporates a product with negative margin (e.g. Amul Butter @ Cost ₹60.00 &gt; Sell ₹55.00), the Finance Agent strictly halts execution. The Supervisor isolates the failure and alerts human management for price rectification.
            </p>
          </div>

          <button
            onClick={handleFixButterAndResume}
            disabled={isResolving}
            className="px-5 py-2.5 rounded-xl bg-white hover:bg-neutral-200 text-black text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all shadow-md self-start md:self-center"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isResolving ? 'animate-spin' : ''}`} />
            <span>{isResolving ? 'Rectifying & Revalidating...' : 'Rectify Price & Revalidate'}</span>
          </button>
        </div>
      </div>

      {/* Failure Records Table */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-white">Logged Failures & Violations</h3>

        {failures.length === 0 ? (
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-10 text-center text-neutral-400">
            <CheckCircle className="w-8 h-8 text-[#22C55E] mx-auto mb-2 opacity-70" />
            <p className="text-sm font-semibold text-white">No Logged Failures</p>
            <span className="text-xs text-neutral-500">
              Click "Demo Failure" in the top bar to simulate the negative-margin Butter scenario.
            </span>
          </div>
        ) : (
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#171717] border-b border-white/[0.08] text-neutral-400 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-3 px-4">Task ID</th>
                    <th className="py-3 px-4">Detecting Agent</th>
                    <th className="py-3 px-4">Violation / Root Cause</th>
                    <th className="py-3 px-4">Error Description</th>
                    <th className="py-3 px-4">Retries</th>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.05] text-neutral-300">
                  {failures.map((f) => (
                    <tr key={f.id} className="hover:bg-white/[0.02]">
                      <td className="py-3.5 px-4 font-mono font-medium text-white">{f.task_id}</td>
                      <td className="py-3.5 px-4 text-neutral-300">{f.agent_name}</td>
                      <td className="py-3.5 px-4">
                        <span className="text-red-400 font-mono text-[11px] px-2 py-0.5 rounded bg-red-500/10 border border-red-500/20">
                          {f.root_cause}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-neutral-300 max-w-xs truncate" title={f.error_description}>
                        {f.error_description}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-neutral-400">{f.retry_count}</td>
                      <td className="py-3.5 px-4 text-neutral-500 font-mono text-[11px]">
                        {f.timestamp ? new Date(f.timestamp).toLocaleTimeString() : 'Recent'}
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={f.recovery_status} size="sm" />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {f.recovery_status !== 'RESOLVED' ? (
                          <button
                            onClick={() => handleResolveSingle(f.id)}
                            disabled={resolvingId === f.id}
                            className="px-2.5 py-1 rounded bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-emerald-400 hover:text-emerald-300 text-[11px] inline-flex items-center gap-1 cursor-pointer"
                          >
                            <Check className="w-3 h-3" />
                            <span>{resolvingId === f.id ? 'Resolving...' : 'Resolve'}</span>
                          </button>
                        ) : (
                          <span className="text-[11px] text-neutral-500">Fixed</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
