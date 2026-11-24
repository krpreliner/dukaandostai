import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { getAnalytics } from '../services/api';
import { MetricCard } from '../components/ui/MetricCard';
import { DollarSign, PieChart as PieIcon, TrendingUp, ShoppingBag } from 'lucide-react';

export const Analytics: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalytics()
      .then(res => setData(res))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="text-neutral-400 text-sm">Loading business analytics...</div>
      </div>
    );
  }

  const { sales_analytics, customer_analytics, inventory_analytics, expenses_breakdown } = data;

  const COLORS = ['#22D3EE', '#818CF8', '#22C55E', '#F59E0B', '#EC4899', '#A855F7'];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Business Intelligence & Analytics</h2>
        <p className="text-sm text-neutral-400 mt-1">
          Deep-dive Kirana retail metrics derived directly from verified transactional records.
        </p>
      </div>

      {/* Financial Core Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Monthly Revenue"
          value={`₹${sales_analytics.revenue.toLocaleString('en-IN')}`}
          subtitle="320 synthetic customer transactions"
          icon={DollarSign}
          accentColor="cyan"
        />
        <MetricCard
          title="Gross Profit"
          value={`₹${sales_analytics.gross_profit.toLocaleString('en-IN')}`}
          subtitle={`${sales_analytics.gross_margin_pct}% gross margin`}
          icon={TrendingUp}
          accentColor="green"
        />
        <MetricCard
          title="Operating Expenses"
          value={`₹${sales_analytics.operating_expenses.toLocaleString('en-IN')}`}
          subtitle="Rent, Electricity, Helper wages"
          icon={PieIcon}
          accentColor="amber"
        />
        <MetricCard
          title="Inventory Value"
          value={`₹${inventory_analytics.total_inventory_value.toLocaleString('en-IN')}`}
          subtitle={`${inventory_analytics.total_products} grocery products`}
          icon={ShoppingBag}
          accentColor="indigo"
        />
      </div>

      {/* Category Performance Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-[#111111] border border-white/[0.08] rounded-xl p-6">
          <h3 className="text-base font-semibold text-white mb-1">Category Sales & Profit Breakdown</h3>
          <p className="text-xs text-neutral-400 mb-6">Revenue and gross profit across grocery categories</p>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sales_analytics.category_breakdown}>
                <XAxis dataKey="category" stroke="#71717A" fontSize={11} tickLine={false} />
                <YAxis stroke="#71717A" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#171717', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ fontSize: '12px' }}
                />
                <Bar dataKey="sales" name="Sales (₹)" fill="#22D3EE" radius={[4, 4, 0, 0]} />
                <Bar dataKey="profit" name="Profit (₹)" fill="#818CF8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Expenses Distribution */}
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 flex flex-col">
          <h3 className="text-base font-semibold text-white mb-1">Operating Expenses Breakdown</h3>
          <p className="text-xs text-neutral-400 mb-4">Total: ₹{sales_analytics.operating_expenses.toLocaleString('en-IN')}</p>
          <div className="h-52 w-full my-auto">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={expenses_breakdown}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                >
                  {expenses_breakdown.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#171717', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-1.5 mt-2">
            {expenses_breakdown.map((e: any, idx: number) => (
              <div key={idx} className="flex justify-between items-center text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                  <span className="text-neutral-300">{e.category}</span>
                </div>
                <span className="font-semibold text-white">₹{e.amount}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Selling vs Underperforming Items */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Selling */}
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
          <h3 className="text-base font-semibold text-white mb-4">High Velocity Top Products</h3>
          <div className="space-y-3">
            {sales_analytics.top_products.map((p: any, idx: number) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-[#171717] border border-white/[0.04]">
                <div>
                  <p className="text-xs font-semibold text-white">{p.product_name}</p>
                  <span className="text-[11px] text-neutral-400">{p.category} • {p.units_sold} units sold</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-[#22D3EE]">₹{p.total_sales.toLocaleString('en-IN')}</span>
                  <p className="text-[10px] text-[#22C55E]">₹{p.total_profit} profit</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Customer Segments summary */}
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
          <h3 className="text-base font-semibold text-white mb-4">Customer Base Segmentation</h3>
          <div className="space-y-3">
            {Object.entries(customer_analytics.segments_breakdown).map(([seg, count]: any, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-[#171717] border border-white/[0.04]">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-[#818CF8]" />
                  <span className="text-xs font-medium text-white">{seg}</span>
                </div>
                <span className="text-xs font-semibold text-neutral-300">{count} Customers</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
