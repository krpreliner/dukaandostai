import React, { useEffect, useState } from 'react';
import { Activity, CheckCircle, Database, Server, Cpu, Clock, ShieldCheck, RefreshCw, Search } from 'lucide-react';
import { getSystemHealth, getAuditLogs } from '../services/api';
import { SystemHealth as SystemHealthType, AuditLog } from '../types';

export const SystemHealthPage: React.FC = () => {
  const [health, setHealth] = useState<SystemHealthType | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchData = async () => {
    try {
      const [hData, lData] = await Promise.all([
        getSystemHealth(),
        getAuditLogs()
      ]);
      setHealth(hData || null);
      setLogs(lData || []);
    } catch (err) {
      console.error('Error fetching health:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  const filteredLogs = logs.filter((l) =>
    l.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.agent_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.details.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8 space-y-8 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-5 h-5 text-[#22D3EE]" />
            <h2 className="text-xl font-bold text-white tracking-tight">System Health & Diagnostic Telemetry</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Real-time process telemetry, database connection health, and immutable audit logs.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="self-start sm:self-center px-3 py-1.5 rounded-lg bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-xs text-neutral-300 flex items-center gap-1.5 cursor-pointer transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* Primary Health Metric Cards */}
      {health && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-400 font-medium">Server Health</span>
              <CheckCircle className="w-4 h-4 text-[#22C55E]" />
            </div>
            <p className="text-xl font-bold text-white mt-1">{health.status}</p>
            <span className="text-[11px] text-neutral-500">Env: {health.app_env}</span>
          </div>

          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-400 font-medium">Database Latency</span>
              <Database className="w-4 h-4 text-[#22D3EE]" />
            </div>
            <p className="text-xl font-bold text-[#22D3EE] mt-1">{health.database_latency_ms} ms</p>
            <span className="text-[11px] text-neutral-500">Connected & Verified</span>
          </div>

          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-400 font-medium">Process Memory</span>
              <Server className="w-4 h-4 text-indigo-400" />
            </div>
            <p className="text-xl font-bold text-white mt-1">{health.process_memory_mb} MB</p>
            <span className="text-[11px] text-neutral-500">CPU: {health.process_cpu_pct}%</span>
          </div>

          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-neutral-400 font-medium">System Uptime</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <p className="text-xl font-bold text-white mt-1">{Math.floor(health.uptime_seconds / 60)} min {health.uptime_seconds % 60} s</p>
            <span className="text-[11px] text-neutral-500">Active background daemon</span>
          </div>
        </div>
      )}

      {/* Audit Log Table */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h3 className="text-base font-semibold text-white">Immutable Audit Trail ({filteredLogs.length})</h3>

          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-neutral-500" />
            <input
              type="text"
              placeholder="Search audit events, agents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#111111] border border-white/[0.08] rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#22D3EE]"
            />
          </div>
        </div>

        <div className="bg-[#111111] border border-white/[0.08] rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#171717] border-b border-white/[0.08] text-neutral-400 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="py-3 px-4">Event Type</th>
                  <th className="py-3 px-4">Origin Agent / Actor</th>
                  <th className="py-3 px-4">Details</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.05] text-neutral-300">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-white/[0.02]">
                    <td className="py-3.5 px-4 font-mono font-medium text-white">
                      <span className="px-2 py-0.5 rounded bg-white/[0.05] text-[#22D3EE] border border-white/[0.05]">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-neutral-300">{log.agent_name}</td>
                    <td className="py-3.5 px-4 text-neutral-400 max-w-lg truncate" title={log.details}>
                      {log.details}
                    </td>
                    <td className="py-3.5 px-4 text-neutral-500 font-mono text-[11px]">
                      {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Recent'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
