import React, { useEffect, useState } from 'react';
import { History, Filter, ArrowUpRight, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { getExecutions, getWorkerStatus } from '../services/api';
import { ExecutionRecord, TaskRecord } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';

export const ExecutionHistory: React.FC = () => {
  const [executions, setExecutions] = useState<ExecutionRecord[]>([]);
  const [selectedExec, setSelectedExec] = useState<string | null>(null);
  const [tasks, setTasks] = useState<TaskRecord[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getExecutions()
      .then(async (data) => {
        setExecutions(data || []);
        if (data && data.length > 0) {
          const firstId = data[0].execution_id;
          setSelectedExec(firstId);
          const st = await getWorkerStatus(firstId);
          setTasks(st.tasks || []);
        }
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectExec = async (execId: string) => {
    setSelectedExec(execId);
    try {
      const st = await getWorkerStatus(execId);
      setTasks(st.tasks || []);
    } catch (err) {
      console.error(err);
    }
  };

  const filters = ['ALL', 'COMPLETED', 'FAILED', 'REJECTED', 'WAITING_APPROVAL', 'PENDING'];

  const filteredTasks = tasks.filter(t => {
    if (statusFilter === 'ALL') return true;
    return t.status === statusFilter;
  });

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <History className="w-5 h-5 text-[#22D3EE]" />
          <h2 className="text-xl font-bold text-white tracking-tight">Execution Audit Trail</h2>
        </div>
        <p className="text-sm text-neutral-400">
          Persistent SQLite execution history, task status checkpoints, approval logs, and financial outcomes.
        </p>
      </div>

      {/* Execution Runs Selector */}
      {executions.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          <span className="text-xs text-neutral-500 mr-1">Execution Runs:</span>
          {executions.map((ex) => (
            <button
              key={ex.execution_id}
              onClick={() => handleSelectExec(ex.execution_id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all flex items-center gap-2 cursor-pointer ${
                selectedExec === ex.execution_id
                  ? 'bg-[#171717] border border-[#22D3EE] text-white shadow-sm'
                  : 'bg-[#111111] border border-white/[0.06] text-neutral-400 hover:text-white'
              }`}
            >
              <span>{ex.execution_id}</span>
              <StatusBadge status={ex.status} size="sm" />
            </button>
          ))}
        </div>
      )}

      {/* Status Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto">
        <Filter className="w-3.5 h-3.5 text-neutral-500 mr-1" />
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setStatusFilter(f)}
            className={`px-3 py-1 rounded-md text-xs font-medium cursor-pointer transition-all ${
              statusFilter === f
                ? 'bg-white text-black font-semibold'
                : 'bg-[#111111] text-neutral-400 hover:text-white border border-white/[0.06]'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Tasks History Table */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#171717] border-b border-white/[0.08] text-neutral-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Task ID & Description</th>
                <th className="py-3 px-4">Assigned Agent</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Expected Profit</th>
                <th className="py-3 px-4">Simulated Impact</th>
                <th className="py-3 px-4">Approval Req.</th>
                <th className="py-3 px-4">Execution Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05] text-neutral-300">
              {filteredTasks.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-neutral-500">
                    No task records match filter '{statusFilter}'
                  </td>
                </tr>
              ) : (
                filteredTasks.map((t) => (
                  <tr key={t.task_id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-medium text-white max-w-sm">
                      <span className="font-semibold block">{t.task_name}</span>
                      <span className="text-[10px] text-neutral-500 font-mono">{t.task_id}</span>
                      {t.execution_result && (
                        <p className="text-[11px] text-neutral-400 mt-0.5 line-clamp-1">{t.execution_result}</p>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-neutral-400">{t.assigned_agent}</td>
                    <td className="py-3.5 px-4">
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                        t.priority === 'HIGH' ? 'bg-red-500/10 text-red-400' : 'bg-neutral-800 text-neutral-300'
                      }`}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono font-medium">₹{t.expected_impact.toFixed(2)}</td>
                    <td className="py-3.5 px-4 font-mono font-bold text-[#22C55E]">
                      {t.simulated_impact > 0 ? `+₹${t.simulated_impact.toFixed(2)}` : '₹0.00'}
                    </td>
                    <td className="py-3.5 px-4">
                      {t.approval_required ? (
                        <span className="text-[11px] text-[#F59E0B]">Required</span>
                      ) : (
                        <span className="text-[11px] text-neutral-500">Automated</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={t.status} size="sm" />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
