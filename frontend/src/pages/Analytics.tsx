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
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area
} from 'recharts';
import { getAnalytics } from '../services/api';
import { MetricCard } from '../components/ui/MetricCard';
import {
  DollarSign,
  PieChart as PieIcon,
  TrendingUp,
  ShoppingBag,
  Users,
  AlertTriangle,
  Calendar,
  Layers,
  ArrowUpRight,
  ShieldCheck
} from 'lucide-react';

export const Analytics: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'all' | 'sales' | 'customers' | 'inventory'>('all');

  useEffect(() => {
    getAnalytics()
      .then((res) => setData(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="text-neutral-400 text-sm flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-[#22D3EE] border-t-transparent rounded-full animate-spin" />
          <span>Loading Sharma General Store business intelligence...</span>
        </div>
      </div>
    );
  }

  const { sales_analytics, customer_analytics, inventory_analytics, expenses_breakdown } = data;
  const COLORS = ['#22D3EE', '#818CF8', '#22C55E', '#F59E0B', '#EC4899', '#A855F7'];

  return (
    <div className="p-8 space-y-8 w-full">
      {/* Page Title & Tab Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Business Intelligence & Analytics</h2>
          <p className="text-sm text-neutral-400 mt-1">
            Real-time Kirana retail metrics derived directly from verified transactional records.
          </p>
        </div>

        {/* Tab Switcher Pills */}
        <div className="flex items-center gap-1.5 p-1 bg-[#111111] border border-white/[0.08] rounded-xl self-start sm:self-center">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
              activeTab === 'all'
                ? 'bg-[#22D3EE] text-black font-semibold shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            All Metrics
          </button>
          <button
            onClick={() => setActiveTab('sales')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
              activeTab === 'sales'
                ? 'bg-[#22D3EE] text-black font-semibold shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            30-Day Sales Trend
          </button>
          <button
            onClick={() => setActiveTab('customers')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
              activeTab === 'customers'
                ? 'bg-[#22D3EE] text-black font-semibold shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Customer Cohorts
          </button>
          <button
            onClick={() => setActiveTab('inventory')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
              activeTab === 'inventory'
                ? 'bg-[#22D3EE] text-black font-semibold shadow-sm'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            Inventory Health
          </button>
        </div>
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

      {/* 30-Day Sales & Profit Area Chart (Shown on 'all' or 'sales' tabs) */}
      {(activeTab === 'all' || activeTab === 'sales') && sales_analytics.daily_trends && (
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
            <div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-[#22D3EE]" />
                <h3 className="text-base font-semibold text-white">30-Day Daily Sales & Profit Trajectory</h3>
              </div>
              <p className="text-xs text-neutral-400 mt-0.5">
                Daily turnover and gross margin progression across Ranchi store operations
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-sm bg-[#22D3EE]" />
                <span className="text-neutral-300">Daily Sales</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-sm bg-[#818CF8]" />
                <span className="text-neutral-300">Gross Margin</span>
              </div>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sales_analytics.daily_trends}>
                <defs>
                  <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22D3EE" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#22D3EE" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="profitGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#818CF8" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#818CF8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#71717A" fontSize={11} tickLine={false} />
                <YAxis stroke="#71717A" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#171717', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="sales" name="Sales (₹)" stroke="#22D3EE" fillOpacity={1} fill="url(#salesGrad)" />
                <Area type="monotone" dataKey="profit" name="Profit (₹)" stroke="#818CF8" fillOpacity={1} fill="url(#profitGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Category Performance & Operating Expenses (Shown on 'all' or 'sales' tabs) */}
      {(activeTab === 'all' || activeTab === 'sales') && (
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
      )}

      {/* Customer Intelligence & Retention Tab */}
      {(activeTab === 'all' || activeTab === 'customers') && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 rounded-xl bg-[#111111] border border-white/[0.08]">
              <span className="text-xs text-neutral-400">Total Customer Base</span>
              <p className="text-2xl font-bold text-white mt-1">{customer_analytics.total_customers}</p>
              <span className="text-[11px] text-neutral-500">Harmu Road, Doranda, Lalpur & Kokar</span>
            </div>
            <div className="p-5 rounded-xl bg-[#111111] border border-white/[0.08]">
              <span className="text-xs text-neutral-400">Average Order Value (AOV)</span>
              <p className="text-2xl font-bold text-[#22D3EE] mt-1">₹{customer_analytics.average_aov}</p>
              <span className="text-[11px] text-neutral-500">Basket size across 320 transactions</span>
            </div>
            <div className="p-5 rounded-xl bg-[#111111] border border-amber-500/20 bg-amber-500/5">
              <span className="text-xs text-amber-400">Dormant & At-Risk Customers</span>
              <p className="text-2xl font-bold text-amber-400 mt-1">
                {customer_analytics.inactive_count + customer_analytics.at_risk_count}
              </p>
              <span className="text-[11px] text-amber-400/80">Opportunity for WhatsApp reactivation</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Customer Segments Breakdown */}
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

            {/* Inactive Dormant Customers Table */}
            <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
              <h3 className="text-base font-semibold text-white mb-1">Dormant Customer Reactivation Targets</h3>
              <p className="text-xs text-neutral-400 mb-4">Customers with &gt;30 days since last purchase</p>
              <div className="space-y-2.5">
                {customer_analytics.inactive_sample && customer_analytics.inactive_sample.map((c: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-[#171717] border border-white/[0.04]">
                    <div>
                      <p className="text-xs font-semibold text-white">{c.customer_name}</p>
                      <span className="text-[11px] text-neutral-400">{c.area} • Last seen {c.last_purchase_date}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-semibold text-[#22D3EE]">AOV: ₹{c.average_order_value}</span>
                      <p className="text-[10px] text-neutral-400">{c.preferred_category}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Inventory Health & Stock Risk Tab */}
      {(activeTab === 'all' || activeTab === 'inventory') && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 rounded-xl bg-[#111111] border border-white/[0.08]">
              <span className="text-xs text-neutral-400">Total Catalog Products</span>
              <p className="text-2xl font-bold text-white mt-1">{inventory_analytics.total_products}</p>
              <span className="text-[11px] text-neutral-500">Across 6 grocery categories</span>
            </div>
            <div className="p-5 rounded-xl bg-[#111111] border border-red-500/20 bg-red-500/5">
              <span className="text-xs text-red-400">Low Stock Reorder Alerts</span>
              <p className="text-2xl font-bold text-red-400 mt-1">{inventory_analytics.low_stock_count}</p>
              <span className="text-[11px] text-red-400/80">Stock level strictly below safety threshold</span>
            </div>
            <div className="p-5 rounded-xl bg-[#111111] border border-amber-500/20 bg-amber-500/5">
              <span className="text-xs text-amber-400">Expiring Soon Products</span>
              <p className="text-2xl font-bold text-amber-400 mt-1">{inventory_analytics.expiring_soon_count}</p>
              <span className="text-[11px] text-amber-400/80">Within 7 days of expiry date</span>
            </div>
          </div>

          {/* Low Stock Items Detail */}
          {inventory_analytics.low_stock_items && inventory_analytics.low_stock_items.length > 0 && (
            <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <h3 className="text-base font-semibold text-white">Critical Stock Refill Priorities</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {inventory_analytics.low_stock_items.map((item: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-[#171717] border border-red-500/20 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-white">{item.product_name}</p>
                      <span className="text-[11px] text-neutral-400">{item.category} • Cost: ₹{item.cost_price} / Sell: ₹{item.selling_price}</span>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-red-500/20 text-red-400 border border-red-500/30">
                          {item.current_stock} Units Left (Min: {item.minimum_stock})
                        </span>
                        <span className="text-[10px] text-neutral-500">Exp: {item.expiry_date}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-bold text-[#22D3EE]">+{item.margin_pct}%</span>
                      <p className="text-[10px] text-neutral-400">Gross Margin</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Top Velocity Products Table (Always shown at bottom of 'all' or 'sales') */}
      {(activeTab === 'all' || activeTab === 'sales') && (
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6">
          <h3 className="text-base font-semibold text-white mb-4">High Velocity Top Products</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {sales_analytics.top_products.map((p: any, idx: number) => (
              <div key={idx} className="p-4 rounded-lg bg-[#171717] border border-white/[0.04]">
                <p className="text-xs font-semibold text-white truncate" title={p.product_name}>{p.product_name}</p>
                <span className="text-[10px] text-neutral-400 block mt-0.5">{p.category}</span>
                <div className="mt-3 pt-2 border-t border-white/[0.05] flex items-center justify-between">
                  <span className="text-xs font-bold text-[#22D3EE]">₹{p.total_sales.toLocaleString('en-IN')}</span>
                  <span className="text-[10px] text-[#22C55E]">+{p.units_sold} sold</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
