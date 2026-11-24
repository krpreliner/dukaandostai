import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle, RefreshCw, ArrowRight, Check, Wrench, Search, Filter, Eye, X, DollarSign } from 'lucide-react';
import { getFailures, updateProductPrice, startWorker, resolveFailure, resolveAllFailures, rectifyFailurePrice } from '../services/api';
import { FailureRecord } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';

export const FailureMonitoring: React.FC = () => {
  const [failures, setFailures] = useState<FailureRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [isResolving, setIsResolving] = useState(false);
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  
  // Search and Filter controls (Section 3-B)
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'UNRESOLVED' | 'RESOLVED'>('ALL');
  
  // Details Modal
  const [selectedFailure, setSelectedFailure] = useState<FailureRecord | null>(null);

  // Rectification Modal
  const [rectifyModalOpen, setRectifyModalOpen] = useState(false);
  const [rectifyTargetFailure, setRectifyTargetFailure] = useState<FailureRecord | null>(null);
  const [newCostPrice, setNewCostPrice] = useState<number>(60.0);
  const [newSellingPrice, setNewSellingPrice] = useState<number>(68.0);
  const [rectifyFeedback, setRectifyFeedback] = useState<string | null>(null);

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

  // Live margin calculations for rectification
  const unitProfit = Math.round((newSellingPrice - newCostPrice) * 100) / 100;
  const marginPct = newSellingPrice > 0 ? Math.round(((newSellingPrice - newCostPrice) / newSellingPrice) * 1000) / 10 : 0;
  const isHealthyMargin = marginPct >= 5.0 && unitProfit > 0;

  const openRectifyModal = (f?: FailureRecord) => {
    const target = f || failures.find(item => item.recovery_status !== 'RESOLVED') || failures[0] || null;
    setRectifyTargetFailure(target);
    setNewCostPrice(60.0);
    setNewSellingPrice(68.0);
    setRectifyFeedback(null);
    setRectifyModalOpen(true);
  };

  const handleExecuteRectify = async () => {
    if (!isHealthyMargin) {
      setRectifyFeedback('Validation Error: Selling price must yield at least +5.0% gross margin over cost price.');
      return;
    }
    setIsResolving(true);
    setRectifyFeedback(null);
    try {
      const targetId = rectifyTargetFailure ? rectifyTargetFailure.id : (failures[0]?.id || 1);
      const res = await rectifyFailurePrice(targetId, {
        product_id: 'PROD003',
        new_cost_price: newCostPrice,
        new_selling_price: newSellingPrice
      });
      setRectifyFeedback(`Success: ${res.message || 'Price rectified and validated!'}`);
      await fetchFailuresList();
      setTimeout(() => {
        setRectifyModalOpen(false);
      }, 1200);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Price rectification failed.';
      setRectifyFeedback(`Error: ${msg}`);
    } finally {
      setIsResolving(false);
    }
  };

  const handleFixButterAndResume = async () => {
    setIsResolving(true);
    try {
      const activeFailure = failures.find(f => f.recovery_status !== 'RESOLVED');
      if (activeFailure) {
        await rectifyFailurePrice(activeFailure.id, {
          product_id: 'PROD003',
          new_cost_price: 60.0,
          new_selling_price: 68.0
        });
      } else {
        await updateProductPrice('PROD003', 60.0, 68.0);
        await resolveAllFailures();
      }
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

  // Filtered and searched failure records
  const filteredFailures = failures.filter(f => {
    const matchesSearch =
      f.task_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.agent_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.root_cause.toLowerCase().includes(searchTerm.toLowerCase()) ||
      f.error_description.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (statusFilter === 'UNRESOLVED') return matchesSearch && f.recovery_status !== 'RESOLVED';
    if (statusFilter === 'RESOLVED') return matchesSearch && f.recovery_status === 'RESOLVED';
    return matchesSearch;
  });

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

          <div className="flex items-center gap-2.5 self-start md:self-center">
            <button
              onClick={() => openRectifyModal()}
              disabled={isResolving}
              className="px-4 py-2.5 rounded-xl bg-white hover:bg-neutral-200 text-black text-xs font-semibold flex items-center gap-2 cursor-pointer transition-all shadow-md"
            >
              <Wrench className="w-3.5 h-3.5" />
              <span>Rectify Price & Revalidate</span>
            </button>
            <button
              onClick={handleFixButterAndResume}
              disabled={isResolving}
              title="Direct auto-fix to Cost ₹60.00 / Sell ₹68.00 and resume AI worker"
              className="px-3.5 py-2.5 rounded-xl bg-[#171717] hover:bg-neutral-800 border border-white/[0.12] text-neutral-200 text-xs font-medium flex items-center gap-1.5 cursor-pointer transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isResolving ? 'animate-spin' : ''}`} />
              <span>{isResolving ? 'Auto-Fixing...' : 'Auto-Fix & Resume'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Failure Records Table Controls */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="text-base font-semibold text-white">
            Logged Failures & Violations ({filteredFailures.length})
          </h3>

          <div className="flex items-center gap-3">
            {/* Status Filter Tabs */}
            <div className="flex items-center bg-[#171717] p-1 rounded-lg border border-white/[0.08] text-xs">
              <button
                onClick={() => setStatusFilter('ALL')}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer font-medium ${
                  statusFilter === 'ALL' ? 'bg-[#22D3EE] text-black shadow-xs' : 'text-neutral-400 hover:text-white'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setStatusFilter('UNRESOLVED')}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer font-medium ${
                  statusFilter === 'UNRESOLVED' ? 'bg-red-500 text-white shadow-xs' : 'text-neutral-400 hover:text-white'
                }`}
              >
                Unresolved
              </button>
              <button
                onClick={() => setStatusFilter('RESOLVED')}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer font-medium ${
                  statusFilter === 'RESOLVED' ? 'bg-emerald-500 text-white shadow-xs' : 'text-neutral-400 hover:text-white'
                }`}
              >
                Resolved
              </button>
            </div>

            {/* Search Input */}
            <div className="relative w-48 sm:w-64">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-neutral-500" />
              <input
                type="text"
                placeholder="Search failures, agents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-[#111111] border border-white/[0.08] rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#22D3EE]"
              />
            </div>
          </div>
        </div>

        {filteredFailures.length === 0 ? (
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-10 text-center text-neutral-400">
            <CheckCircle className="w-8 h-8 text-[#22C55E] mx-auto mb-2 opacity-70" />
            <p className="text-sm font-semibold text-white">No Logged Failures</p>
            <span className="text-xs text-neutral-500">
              {failures.length === 0
                ? 'Click "Demo Failure" in the top bar to simulate the negative-margin Butter scenario.'
                : 'No failure records match your current search/filter.'}
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
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.05] text-neutral-300">
                  {filteredFailures.map((f) => (
                    <tr key={f.id} className="hover:bg-white/[0.02] transition-colors">
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
                      <td className="py-3.5 px-4 text-right space-x-1.5 whitespace-nowrap">
                        <button
                          onClick={() => setSelectedFailure(f)}
                          title="Inspect full audit & failure details"
                          className="px-2 py-1 rounded bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-neutral-300 hover:text-white text-[11px] inline-flex items-center gap-1 cursor-pointer"
                        >
                          <Eye className="w-3 h-3" />
                          <span>Details</span>
                        </button>
                        {f.recovery_status !== 'RESOLVED' ? (
                          <>
                            <button
                              onClick={() => openRectifyModal(f)}
                              title="Rectify product price & revalidate"
                              className="px-2 py-1 rounded bg-white/[0.08] hover:bg-white/[0.15] border border-white/[0.15] text-[#22D3EE] text-[11px] inline-flex items-center gap-1 cursor-pointer font-medium"
                            >
                              <Wrench className="w-3 h-3" />
                              <span>Rectify</span>
                            </button>
                            <button
                              onClick={() => handleResolveSingle(f.id)}
                              disabled={resolvingId === f.id}
                              className="px-2 py-1 rounded bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-emerald-400 hover:text-emerald-300 text-[11px] inline-flex items-center gap-1 cursor-pointer"
                            >
                              <Check className="w-3 h-3" />
                              <span>{resolvingId === f.id ? 'Resolving...' : 'Resolve'}</span>
                            </button>
                          </>
                        ) : (
                          <span className="text-[11px] text-emerald-400 font-medium">Rectified</span>
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

      {/* Details Modal */}
      {selectedFailure && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="bg-[#111111] border border-white/[0.15] rounded-2xl w-full max-w-xl p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-400" />
                <h3 className="text-base font-bold text-white">Failure Record Details #{selectedFailure.id}</h3>
              </div>
              <button
                onClick={() => setSelectedFailure(null)}
                className="p-1 rounded-lg text-neutral-400 hover:text-white hover:bg-white/[0.08] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-[#171717] p-3 rounded-lg border border-white/[0.04]">
                <span className="text-neutral-500">Execution Reference:</span>
                <p className="text-white font-mono font-medium mt-0.5">{selectedFailure.execution_id}</p>
              </div>
              <div className="bg-[#171717] p-3 rounded-lg border border-white/[0.04]">
                <span className="text-neutral-500">Responsible Agent:</span>
                <p className="text-white font-medium mt-0.5">{selectedFailure.agent_name}</p>
              </div>
              <div className="bg-[#171717] p-3 rounded-lg border border-white/[0.04]">
                <span className="text-neutral-500">Violation Category:</span>
                <p className="text-red-400 font-mono font-semibold mt-0.5">{selectedFailure.root_cause}</p>
              </div>
              <div className="bg-[#171717] p-3 rounded-lg border border-white/[0.04]">
                <span className="text-neutral-500">Recovery Status:</span>
                <div className="mt-0.5">
                  <StatusBadge status={selectedFailure.recovery_status} size="sm" />
                </div>
              </div>
            </div>

            <div className="bg-[#171717] p-3 rounded-lg border border-white/[0.04] space-y-1 text-xs">
              <span className="text-neutral-400 font-medium">Rejection Reason & Error Description:</span>
              <p className="text-neutral-200 leading-relaxed font-mono text-[11px]">{selectedFailure.error_description}</p>
            </div>

            <div className="flex items-center justify-between text-xs text-neutral-500 pt-2 border-t border-white/[0.08]">
              <span>Timestamp: {selectedFailure.timestamp ? new Date(selectedFailure.timestamp).toLocaleString() : 'N/A'}</span>
              <span>Retries Attempted: {selectedFailure.retry_count}</span>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setSelectedFailure(null)}
                className="px-4 py-2 rounded-lg bg-[#171717] hover:bg-neutral-800 text-neutral-300 text-xs font-medium cursor-pointer"
              >
                Close
              </button>
              {selectedFailure.recovery_status !== 'RESOLVED' && (
                <button
                  onClick={() => {
                    const target = selectedFailure;
                    setSelectedFailure(null);
                    openRectifyModal(target);
                  }}
                  className="px-4 py-2 rounded-lg bg-white hover:bg-neutral-200 text-black text-xs font-semibold flex items-center gap-1.5 cursor-pointer"
                >
                  <Wrench className="w-3.5 h-3.5" />
                  <span>Rectify Price Now</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Rectify Price & Revalidate Modal (Section 3-C) */}
      {rectifyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="bg-[#111111] border border-white/[0.15] rounded-2xl w-full max-w-lg p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
              <div className="flex items-center gap-2">
                <Wrench className="w-5 h-5 text-[#22D3EE]" />
                <h3 className="text-base font-bold text-white">Rectify Product Price & Revalidate</h3>
              </div>
              <button
                onClick={() => setRectifyModalOpen(false)}
                className="p-1 rounded-lg text-neutral-400 hover:text-white hover:bg-white/[0.08] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-1 text-xs">
              <span className="text-neutral-400">Target Product:</span>
              <p className="text-white font-semibold text-sm">Amul Butter 500g (PROD003)</p>
              <p className="text-neutral-500 text-[11px]">
                Deterministic Finance Agent validates pricing to ensure strictly positive gross margin before unblocking execution.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs pt-1">
              <div className="space-y-1.5">
                <label className="text-neutral-400 font-medium">New Cost Price (₹):</label>
                <input
                  type="number"
                  step="0.5"
                  value={newCostPrice}
                  onChange={(e) => setNewCostPrice(parseFloat(e.target.value) || 0)}
                  className="w-full bg-[#171717] border border-white/[0.1] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-[#22D3EE]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-neutral-400 font-medium">New Selling Price (₹):</label>
                <input
                  type="number"
                  step="0.5"
                  value={newSellingPrice}
                  onChange={(e) => setNewSellingPrice(parseFloat(e.target.value) || 0)}
                  className="w-full bg-[#171717] border border-white/[0.1] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-[#22D3EE]"
                />
              </div>
            </div>

            {/* Live Financial Margin Calculation Preview */}
            <div className={`p-4 rounded-xl border text-xs space-y-2 ${
              isHealthyMargin
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                : 'bg-red-500/10 border-red-500/30 text-red-300'
            }`}>
              <div className="flex items-center justify-between font-semibold">
                <span>Deterministic Margin Preview:</span>
                <span className="font-mono text-sm">{marginPct > 0 ? `+${marginPct}%` : `${marginPct}%`}</span>
              </div>
              <div className="flex items-center justify-between text-[11px] opacity-90">
                <span>Unit Profit: ₹{unitProfit.toFixed(2)}/unit</span>
                <span>Policy Threshold: Min +5.0%</span>
              </div>
              <p className="text-[11px] leading-tight">
                {isHealthyMargin
                  ? '✓ Verified: Proposed price satisfies financial guardrails and yields positive net profit.'
                  : '✕ Rejection Warning: Selling price must exceed cost price by at least +5.0%.'}
              </p>
            </div>

            {rectifyFeedback && (
              <div className={`p-2.5 rounded-lg text-xs font-mono ${
                rectifyFeedback.startsWith('Success') ? 'bg-emerald-500/15 text-emerald-300' : 'bg-red-500/15 text-red-300'
              }`}>
                {rectifyFeedback}
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/[0.08]">
              <button
                onClick={() => setRectifyModalOpen(false)}
                disabled={isResolving}
                className="px-4 py-2 rounded-lg bg-[#171717] hover:bg-neutral-800 text-neutral-300 text-xs font-medium cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleExecuteRectify}
                disabled={isResolving || !isHealthyMargin}
                className={`px-5 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                  isHealthyMargin && !isResolving
                    ? 'bg-[#22D3EE] hover:bg-[#06b6d4] text-black shadow-md'
                    : 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
                }`}
              >
                <Check className="w-3.5 h-3.5" />
                <span>{isResolving ? 'Validating...' : 'Confirm & Revalidate'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
