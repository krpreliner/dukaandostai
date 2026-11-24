import React, { useEffect, useState } from 'react';
import { Package, Search, Filter, AlertCircle, Edit2, Check, X } from 'lucide-react';
import { getProducts, updateProductPrice } from '../services/api';
import { Product } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';

export const Inventory: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [editCost, setEditCost] = useState<number>(0);
  const [editSell, setEditSell] = useState<number>(0);

  const fetchProductsList = async () => {
    try {
      const data = await getProducts();
      setProducts(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProductsList();
  }, []);

  const categories = ['ALL', ...Array.from(new Set(products.map(p => p.category)))];
  const statuses = ['ALL', 'HEALTHY', 'LOW STOCK', 'SLOW MOVING', 'EXPIRING SOON', 'NEGATIVE MARGIN'];

  const filtered = products.filter(p => {
    const matchesSearch = p.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          p.product_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = selectedCategory === 'ALL' || p.category === selectedCategory;
    const matchesStatus = selectedStatus === 'ALL' || p.status === selectedStatus;
    return matchesSearch && matchesCat && matchesStatus;
  });

  const startEdit = (p: Product) => {
    setEditingProduct(p);
    setEditCost(p.cost_price);
    setEditSell(p.selling_price);
  };

  const handleSavePrice = async () => {
    if (!editingProduct) return;
    try {
      await updateProductPrice(editingProduct.product_id, editCost, editSell);
      await fetchProductsList();
      setEditingProduct(null);
    } catch (err) {
      console.error('Price update failed:', err);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Package className="w-5 h-5 text-[#22D3EE]" />
            <h2 className="text-xl font-bold text-white tracking-tight">Inventory Intelligence</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Real-time stock levels, margin health, expiry alerts, and supplier traceability across {products.length} catalog items.
          </p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-neutral-500" />
          <input
            type="text"
            placeholder="Search product name or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#111111] border border-white/[0.08] rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-[#22D3EE]"
          />
        </div>

        {/* Category Filter */}
        <div className="relative">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full bg-[#111111] border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-neutral-300 focus:outline-none focus:border-[#22D3EE] appearance-none cursor-pointer"
          >
            {categories.map(c => (
              <option key={c} value={c} className="bg-neutral-900 text-white">
                Category: {c}
              </option>
            ))}
          </select>
        </div>

        {/* Status Filter */}
        <div className="relative">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="w-full bg-[#111111] border border-white/[0.08] rounded-xl px-3 py-2 text-xs text-neutral-300 focus:outline-none focus:border-[#22D3EE] appearance-none cursor-pointer"
          >
            {statuses.map(s => (
              <option key={s} value={s} className="bg-neutral-900 text-white">
                Status: {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#171717] border-b border-white/[0.08] text-neutral-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-3 px-4">Product ID & Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Cost Price</th>
                <th className="py-3 px-4">Selling Price</th>
                <th className="py-3 px-4">Stock / Min</th>
                <th className="py-3 px-4">Monthly Sold</th>
                <th className="py-3 px-4">Margin %</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05] text-neutral-300">
              {filtered.map((p) => {
                const isNeg = p.selling_price < p.cost_price;
                return (
                  <tr key={p.product_id} className={`hover:bg-white/[0.02] transition-colors ${isNeg ? 'bg-red-500/5' : ''}`}>
                    <td className="py-3.5 px-4 font-medium text-white">
                      <div>
                        <span className="font-semibold">{p.product_name}</span>
                        <p className="text-[10px] text-neutral-500 font-mono">{p.product_id} • {p.supplier_name}</p>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-neutral-400">{p.category}</td>
                    <td className="py-3.5 px-4 font-mono">₹{p.cost_price.toFixed(2)}</td>
                    <td className="py-3.5 px-4 font-mono font-semibold text-white">₹{p.selling_price.toFixed(2)}</td>
                    <td className="py-3.5 px-4 font-mono">
                      <span className={p.current_stock <= p.minimum_stock ? 'text-amber-400 font-bold' : ''}>
                        {p.current_stock}
                      </span>
                      <span className="text-neutral-500"> / {p.minimum_stock}</span>
                    </td>
                    <td className="py-3.5 px-4 font-mono">{p.monthly_units_sold}</td>
                    <td className="py-3.5 px-4">
                      <span className={`font-semibold ${isNeg ? 'text-red-400' : 'text-[#22C55E]'}`}>
                        {p.profit_margin.toFixed(1)}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={isNeg ? 'NEGATIVE MARGIN' : p.status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => startEdit(p)}
                        className="px-2.5 py-1 rounded bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-neutral-300 text-[11px] flex items-center gap-1.5 ml-auto cursor-pointer"
                        title="Edit price for failure recovery test"
                      >
                        <Edit2 className="w-3 h-3 text-[#22D3EE]" />
                        <span>Edit</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Price Edit Modal */}
      {editingProduct && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111111] border border-white/[0.1] rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <div>
              <h3 className="text-base font-semibold text-white">Adjust Product Pricing</h3>
              <p className="text-xs text-neutral-400 mt-1">
                {editingProduct.product_name} ({editingProduct.product_id})
              </p>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-neutral-400 mb-1 block">Cost Price (₹)</label>
                <input
                  type="number"
                  value={editCost}
                  onChange={(e) => setEditCost(parseFloat(e.target.value) || 0)}
                  className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-[#22D3EE]"
                />
              </div>

              <div>
                <label className="text-neutral-400 mb-1 block">Selling Price (₹)</label>
                <input
                  type="number"
                  value={editSell}
                  onChange={(e) => setEditSell(parseFloat(e.target.value) || 0)}
                  className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-[#22D3EE]"
                />
              </div>

              {editSell < editCost && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>Warning: Selling price is below cost price! Finance Agent will reject promotions.</span>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setEditingProduct(null)}
                className="px-4 py-2 rounded-lg bg-[#171717] hover:bg-neutral-800 text-neutral-300 text-xs font-medium cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSavePrice}
                className="px-4 py-2 rounded-lg bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold cursor-pointer"
              >
                Save & Update
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
