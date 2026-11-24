import React, { useEffect, useState } from 'react';
import { Users, Search, ShieldCheck, UserCheck, UserX, Award, AlertCircle } from 'lucide-react';
import { getCustomers } from '../services/api';
import { Customer } from '../types';

export const Customers: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSegment, setSelectedSegment] = useState<string>('ALL');

  useEffect(() => {
    getCustomers()
      .then(res => setCustomers(res || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const segments = ['ALL', 'Active', 'Inactive', 'Frequent', 'High Value', 'At Risk'];

  const filtered = customers.filter(c => {
    const matchesSearch = c.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          c.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          c.area.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeg = selectedSegment === 'ALL' || c.segment === selectedSegment;
    return matchesSearch && matchesSeg;
  });

  // Calculate segment breakdown
  const counts = {
    Active: customers.filter(c => c.segment === 'Active').length,
    Inactive: customers.filter(c => c.segment === 'Inactive').length,
    Frequent: customers.filter(c => c.segment === 'Frequent').length,
    'High Value': customers.filter(c => c.segment === 'High Value').length,
    'At Risk': customers.filter(c => c.segment === 'At Risk').length,
  };

  return (
    <div className="p-8 space-y-6 w-full">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Users className="w-5 h-5 text-[#22D3EE]" />
          <h2 className="text-xl font-bold text-white tracking-tight">Customer Cohorts & Insights</h2>
        </div>
        <p className="text-sm text-neutral-400">
          Synthetic Kirana shopper cohorts segmented by RFM (Recency, Frequency, Monetary) purchase dynamics.
        </p>
      </div>

      {/* Segment Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        <div
          onClick={() => setSelectedSegment('Active')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedSegment === 'Active' ? 'bg-[#171717] border-[#22D3EE]' : 'bg-[#111111] border-white/[0.08] hover:border-white/[0.15]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400">Active</span>
            <UserCheck className="w-4 h-4 text-[#22C55E]" />
          </div>
          <p className="text-xl font-bold text-white mt-2">{counts.Active}</p>
          <span className="text-[10px] text-neutral-500">Regular Kirana footfall</span>
        </div>

        <div
          onClick={() => setSelectedSegment('Inactive')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedSegment === 'Inactive' ? 'bg-[#171717] border-[#22D3EE]' : 'bg-[#111111] border-white/[0.08] hover:border-white/[0.15]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400">Inactive</span>
            <UserX className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-xl font-bold text-amber-400 mt-2">{counts.Inactive}</p>
          <span className="text-[10px] text-neutral-500">&gt;45 days dormant</span>
        </div>

        <div
          onClick={() => setSelectedSegment('Frequent')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedSegment === 'Frequent' ? 'bg-[#171717] border-[#22D3EE]' : 'bg-[#111111] border-white/[0.08] hover:border-white/[0.15]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400">Frequent</span>
            <Users className="w-4 h-4 text-[#22D3EE]" />
          </div>
          <p className="text-xl font-bold text-white mt-2">{counts.Frequent}</p>
          <span className="text-[10px] text-neutral-500">Weekly dairy & staples</span>
        </div>

        <div
          onClick={() => setSelectedSegment('High Value')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedSegment === 'High Value' ? 'bg-[#171717] border-[#22D3EE]' : 'bg-[#111111] border-white/[0.08] hover:border-white/[0.15]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400">High Value</span>
            <Award className="w-4 h-4 text-[#818CF8]" />
          </div>
          <p className="text-xl font-bold text-[#818CF8] mt-2">{counts['High Value']}</p>
          <span className="text-[10px] text-neutral-500">AOV &gt; ₹1,200</span>
        </div>

        <div
          onClick={() => setSelectedSegment('At Risk')}
          className={`p-4 rounded-xl border cursor-pointer transition-all ${
            selectedSegment === 'At Risk' ? 'bg-[#171717] border-[#22D3EE]' : 'bg-[#111111] border-white/[0.08] hover:border-white/[0.15]'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400">At Risk</span>
            <AlertCircle className="w-4 h-4 text-red-400" />
          </div>
          <p className="text-xl font-bold text-red-400 mt-2">{counts['At Risk']}</p>
          <span className="text-[10px] text-neutral-500">Churn risk pool</span>
        </div>
      </div>

      {/* Search and Segment Selector */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-neutral-500" />
          <input
            type="text"
            placeholder="Search by customer name, ID, or Ranchi area..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#111111] border border-white/[0.08] rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#22D3EE]"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {segments.map((seg) => (
            <button
              key={seg}
              onClick={() => setSelectedSegment(seg)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap cursor-pointer ${
                selectedSegment === seg
                  ? 'bg-[#22D3EE] text-black font-semibold'
                  : 'bg-[#111111] text-neutral-400 hover:text-white border border-white/[0.06]'
              }`}
            >
              {seg}
            </button>
          ))}
        </div>
      </div>

      {/* Customer Records Table */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#171717] border-b border-white/[0.08] text-neutral-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Customer ID & Name</th>
                <th className="py-3 px-4">Area (Ranchi)</th>
                <th className="py-3 px-4">Age Group</th>
                <th className="py-3 px-4">Segment</th>
                <th className="py-3 px-4">Total Orders</th>
                <th className="py-3 px-4">Total Spending</th>
                <th className="py-3 px-4">AOV</th>
                <th className="py-3 px-4">Last Visit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05] text-neutral-300">
              {filtered.slice(0, 30).map((c) => (
                <tr key={c.customer_id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="py-3 px-4 font-medium text-white">
                    <div>
                      <span className="font-semibold">{c.customer_name}</span>
                      <p className="text-[10px] text-neutral-500 font-mono">{c.customer_id}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-neutral-400">{c.area}</td>
                  <td className="py-3 px-4 text-neutral-400">{c.age_group}</td>
                  <td className="py-3 px-4">
                    <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${
                      c.segment === 'Active' ? 'bg-[#22C55E]/10 text-[#22C55E] border-[#22C55E]/30' :
                      c.segment === 'Inactive' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                      c.segment === 'High Value' ? 'bg-[#818CF8]/10 text-[#818CF8] border-[#818CF8]/30' :
                      c.segment === 'At Risk' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                      'bg-neutral-800 text-neutral-300 border-neutral-700'
                    }`}>
                      {c.segment}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono">{c.total_orders}</td>
                  <td className="py-3 px-4 font-mono font-semibold text-white">₹{c.total_spending.toLocaleString('en-IN')}</td>
                  <td className="py-3 px-4 font-mono">₹{c.average_order_value.toFixed(0)}</td>
                  <td className="py-3 px-4 text-neutral-400 font-mono text-[11px]">{c.last_purchase_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
