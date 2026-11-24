import React, { useEffect, useState } from 'react';
import { ShieldCheck, Check, X, Clock, AlertTriangle, ArrowRight, History, RefreshCw } from 'lucide-react';
import { getPendingApprovals, getApprovalHistory, approveTask, rejectTask } from '../services/api';
import { PendingApproval } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';

export const Approvals: React.FC = () => {
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [history, setHistory] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchApprovalsData = async () => {
    try {
      const [pendingData, historyData] = await Promise.all([
        getPendingApprovals(),
        getApprovalHistory()
      ]);
      setApprovals(pendingData || []);
      setHistory(historyData || []);
    } catch (err) {
      console.error('Error fetching approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovalsData();
    const interval = setInterval(fetchApprovalsData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (taskId: string, execId?: string) => {
    setActionLoading(taskId);
    try {
      await approveTask(taskId, execId);
      await fetchApprovalsData();
    } catch (err) {
      console.error('Approval failed:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (taskId: string, execId?: string) => {
    setActionLoading(taskId);
    try {
      await rejectTask(taskId, execId);
      await fetchApprovalsData();
    } catch (err) {
      console.error('Rejection failed:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const isInventoryTask = (desc: string) => {
    const d = desc.toLowerCase();
    return d.includes('replenish') || d.includes('reorder') || d.includes('procurement') || d.includes('stock');
  };

  return (
    <div className="p-8 space-y-8 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldCheck className="w-5 h-5 text-[#F59E0B]" />
            <h2 className="text-xl font-bold text-white tracking-tight">Human-in-the-Loop Approval Centre</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Autonomous execution interrupts and requests store owner sign-off for actions exceeding business risk thresholds.
          </p>
        </div>

        <button
          onClick={fetchApprovalsData}
          className="self-start sm:self-center px-3 py-1.5 rounded-lg bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-xs text-neutral-300 flex items-center gap-1.5 cursor-pointer transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Pending Approvals Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#F59E0B]" />
            <h3 className="text-base font-semibold text-white">Pending Approval Requests</h3>
          </div>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/30 font-medium">
            {approvals.length} Action{approvals.length !== 1 ? 's' : ''} Awaiting Review
          </span>
        </div>

        {approvals.length === 0 ? (
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-10 text-center text-neutral-400">
            <ShieldCheck className="w-10 h-10 mx-auto mb-3 text-[#22C55E] opacity-70" />
            <h4 className="text-base font-semibold text-white">No Pending Approval Requests</h4>
            <p className="text-xs text-neutral-500 mt-1">
              All agent tasks are either executing within permitted autonomy or completed.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {approvals.map((req) => {
              const isInv = isInventoryTask(req.action_description);
              return (
                <div
                  key={req.id}
                  className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 relative overflow-hidden"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                    <div className="space-y-3 flex-1">
                      <div className="flex flex-wrap items-center gap-2.5">
                        <span className="text-xs font-mono font-medium text-white px-2 py-0.5 rounded bg-white/[0.06]">
                          {req.task_id}
                        </span>
                        <span className={`text-[11px] font-semibold uppercase px-2 py-0.5 rounded border ${
                          isInv
                            ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                            : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                        }`}>
                          {isInv ? 'Inventory Procurement' : 'Promotional Bundle'}
                        </span>
                        <span className="text-xs text-neutral-400">
                          Requested by: <strong className="text-neutral-200">{req.requesting_agent}</strong>
                        </span>
                      </div>

                      <h4 className="text-base font-semibold text-white">{req.action_description}</h4>

                      {/* Financial Matrix */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#171717] p-3 rounded-lg border border-white/[0.05] text-xs">
                        <div>
                          <span className="text-neutral-500">{isInv ? 'Catalog Cost:' : 'Regular Price:'}</span>
                          <p className="text-white font-medium mt-0.5">₹{req.original_price.toFixed(2)}</p>
                        </div>
                        <div>
                          <span className="text-neutral-500">{isInv ? 'Procurement Outlay:' : 'Combo Price:'}</span>
                          <p className="text-[#22D3EE] font-medium mt-0.5">₹{req.proposed_price.toFixed(2)}</p>
                        </div>
                        <div>
                          <span className="text-neutral-500">Gross Margin:</span>
                          <p className="text-[#22C55E] font-medium mt-0.5">{req.gross_margin_pct.toFixed(2)}%</p>
                        </div>
                        <div>
                          <span className="text-neutral-500">Expected Profit:</span>
                          <p className="text-white font-bold mt-0.5">₹{req.expected_impact.toFixed(2)}</p>
                        </div>
                      </div>

                      <div className="text-xs space-y-1 text-neutral-400">
                        <p><strong className="text-neutral-300">Justification:</strong> {req.justification}</p>
                        <p><strong className="text-neutral-300">Risk Assessment:</strong> {req.risk_assessment}</p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex sm:flex-col gap-2.5 min-w-[140px]">
                      <button
                        onClick={() => handleApprove(req.task_id, req.execution_id)}
                        disabled={actionLoading === req.task_id}
                        className="flex-1 px-4 py-2.5 rounded-lg bg-[#22C55E] hover:bg-[#16a34a] text-black font-semibold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md disabled:opacity-50"
                      >
                        <Check className="w-4 h-4 stroke-[2.5]" />
                        <span>{actionLoading === req.task_id ? 'Resuming...' : 'APPROVE'}</span>
                      </button>

                      <button
                        onClick={() => handleReject(req.task_id, req.execution_id)}
                        disabled={actionLoading === req.task_id}
                        className="flex-1 px-4 py-2.5 rounded-lg border border-red-500/30 bg-red-500/10 hover:bg-red-500/20 text-red-400 font-semibold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-50"
                      >
                        <X className="w-4 h-4 stroke-[2.5]" />
                        <span>REJECT</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Decision History Section */}
      <div className="space-y-4 pt-4 border-t border-white/[0.08]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-[#22D3EE]" />
            <h3 className="text-base font-semibold text-white">Approval Decision History</h3>
          </div>
          <span className="text-xs text-neutral-500 font-mono">
            {history.length} logged record{history.length !== 1 ? 's' : ''}
          </span>
        </div>

        {history.length === 0 ? (
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-8 text-center text-neutral-500 text-xs">
            No decisions logged yet. Decisions made above will persist here.
          </div>
        ) : (
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#171717] border-b border-white/[0.08] text-neutral-400 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-3 px-4">Task ID</th>
                    <th className="py-3 px-4">Action Description</th>
                    <th className="py-3 px-4">Agent</th>
                    <th className="py-3 px-4">Proposed Value</th>
                    <th className="py-3 px-4">Expected Impact</th>
                    <th className="py-3 px-4">Decision</th>
                    <th className="py-3 px-4">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.05] text-neutral-300">
                  {history.map((h) => (
                    <tr key={h.id} className="hover:bg-white/[0.02]">
                      <td className="py-3.5 px-4 font-mono font-medium text-white">{h.task_id}</td>
                      <td className="py-3.5 px-4 max-w-xs truncate">{h.action_description}</td>
                      <td className="py-3.5 px-4 text-neutral-400">{h.requesting_agent}</td>
                      <td className="py-3.5 px-4 font-mono text-[#22D3EE]">₹{h.proposed_price.toFixed(2)}</td>
                      <td className="py-3.5 px-4 font-mono text-[#22C55E]">₹{h.expected_impact.toFixed(2)}</td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${
                          h.status === 'APPROVED'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-red-500/10 text-red-400 border-red-500/20'
                        }`}>
                          {h.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-neutral-500 font-mono text-[11px]">
                        {h.created_at ? new Date(h.created_at).toLocaleTimeString() : 'Recent'}
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
