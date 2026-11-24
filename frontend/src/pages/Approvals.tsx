import React, { useEffect, useState } from 'react';
import { ShieldCheck, Check, X, Clock, AlertTriangle, ArrowRight } from 'lucide-react';
import { getPendingApprovals, approveTask, rejectTask } from '../services/api';
import { PendingApproval } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';

export const Approvals: React.FC = () => {
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchApprovals = async () => {
    try {
      const data = await getPendingApprovals();
      setApprovals(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, []);

  const handleApprove = async (taskId: string, execId?: string) => {
    setActionLoading(taskId);
    try {
      await approveTask(taskId, execId);
      await fetchApprovals();
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
      await fetchApprovals();
    } catch (err) {
      console.error('Rejection failed:', err);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="w-5 h-5 text-[#F59E0B]" />
          <h2 className="text-xl font-bold text-white tracking-tight">Human-in-the-Loop Approval Centre</h2>
        </div>
        <p className="text-sm text-neutral-400">
          The autonomous worker interrupts and requests store owner sign-off for actions exceeding business risk thresholds (e.g., custom discount combos or inventory purchase).
        </p>
      </div>

      {/* Pending Approvals Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold text-white">Pending Approval Requests</h3>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/30 font-medium">
            {approvals.length} Action{approvals.length !== 1 ? 's' : ''} Awaiting Review
          </span>
        </div>

        {approvals.length === 0 ? (
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-12 text-center text-neutral-400">
            <ShieldCheck className="w-10 h-10 mx-auto mb-3 text-[#22C55E] opacity-70" />
            <h4 className="text-base font-semibold text-white">No Pending Approval Requests</h4>
            <p className="text-xs text-neutral-500 mt-1">
              All agent tasks are either executing within permitted autonomy or completed.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {approvals.map((req) => (
              <div
                key={req.id}
                className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 relative overflow-hidden"
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-neutral-400">{req.task_id}</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-white/[0.05] text-neutral-300">
                        Requested by: {req.requesting_agent}
                      </span>
                    </div>

                    <h4 className="text-base font-semibold text-white">{req.action_description}</h4>

                    {/* Financial Matrix */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#171717] p-3 rounded-lg border border-white/[0.05] text-xs">
                      <div>
                        <span className="text-neutral-500">Regular Price:</span>
                        <p className="text-white font-medium mt-0.5">₹{req.original_price.toFixed(2)}</p>
                      </div>
                      <div>
                        <span className="text-neutral-500">Proposed Combo Price:</span>
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
                      className="flex-1 px-4 py-2.5 rounded-lg bg-[#22C55E] hover:bg-[#16a34a] text-black font-semibold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md"
                    >
                      <Check className="w-4 h-4 stroke-[2.5]" />
                      <span>{actionLoading === req.task_id ? 'Resuming...' : 'APPROVE'}</span>
                    </button>

                    <button
                      onClick={() => handleReject(req.task_id, req.execution_id)}
                      disabled={actionLoading === req.task_id}
                      className="flex-1 px-4 py-2.5 rounded-lg border border-red-500/30 bg-red-500/10 hover:bg-red-500/20 text-red-400 font-semibold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer"
                    >
                      <X className="w-4 h-4 stroke-[2.5]" />
                      <span>REJECT</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
