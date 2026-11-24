import React, { useEffect, useState } from 'react';
import { Plug, FileSpreadsheet, CloudSun, MessageSquare, Check, X, AlertTriangle, ArrowRight, Upload, RefreshCw } from 'lucide-react';
import { getIntegrations, toggleIntegration, previewSheetsImport, confirmSheetsImport, getWeatherSignals, getMessagingPreview } from '../services/api';
import { IntegrationItem } from '../types';

export const Integrations: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);
  const [weather, setWeather] = useState<any>(null);
  const [messagingDraft, setMessagingDraft] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Sheets import state
  const [csvText, setCsvText] = useState('');
  const [previewResult, setPreviewResult] = useState<any>(null);
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);

  const fetchData = async () => {
    try {
      const [intData, wData, mData] = await Promise.all([
        getIntegrations(),
        getWeatherSignals(),
        getMessagingPreview()
      ]);
      setIntegrations(intData || []);
      setWeather(wData || null);
      setMessagingDraft(mData || null);
    } catch (err) {
      console.error('Error fetching integrations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggle = async (type: string, current: boolean) => {
    try {
      await toggleIntegration(type, !current);
      await fetchData();
    } catch (err) {
      console.error('Toggle failed:', err);
    }
  };

  const handlePreviewCsv = async () => {
    if (!csvText.trim()) return;
    setImporting(true);
    setPreviewResult(null);
    setImportStatus(null);
    try {
      const res = await previewSheetsImport(csvText);
      setPreviewResult(res);
    } catch (err: any) {
      setPreviewResult({ success: false, error: err.response?.data?.detail || 'CSV preview failed' });
    } finally {
      setImporting(false);
    }
  };

  const handleConfirmImport = async () => {
    if (!previewResult || !previewResult.preview_items) return;
    setImporting(true);
    try {
      const res = await confirmSheetsImport(previewResult.preview_items);
      setImportStatus(res.message);
      setPreviewResult(null);
      setCsvText('');
    } catch (err: any) {
      setImportStatus('Import failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setImporting(false);
    }
  };

  const sampleCsvTemplate = `product_id,product_name,category,cost_price,selling_price,current_stock,supplier_name
PROD101,Fortune Sunlite Sunflower Oil 1L,Staples & Grains,130.0,148.0,40,Fortune Depot Ranchi
PROD102,Tata Salt Vaccum Evaporated 1kg,Staples & Grains,22.0,28.0,60,Tata Consumer Hub`;

  return (
    <div className="p-8 space-y-8 w-full">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Plug className="w-5 h-5 text-[#22D3EE]" />
          <h2 className="text-xl font-bold text-white tracking-tight">External Integrations & Data Connectors</h2>
        </div>
        <p className="text-sm text-neutral-400">
          Modular integration adapters for Google Sheets catalog sync, regional weather signals, and sandboxed customer messaging.
        </p>
      </div>

      {/* Integration Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {integrations.map((item) => (
          <div key={item.id} className="bg-[#111111] border border-white/[0.08] rounded-xl p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold text-white capitalize">{item.integration_type.replace('_', ' ')}</span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${
                  item.is_enabled
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-neutral-800 text-neutral-400 border-white/[0.08]'
                }`}>
                  {item.status}
                </span>
              </div>
              <p className="text-xs text-neutral-400">
                {item.integration_type === 'google_sheets' && 'Catalog CSV/Sheets import with duplicate protection.'}
                {item.integration_type === 'weather' && 'Contextual climate and seasonal demand signals.'}
                {item.integration_type === 'whatsapp' && 'Sandboxed customer promotional draft preview.'}
                {item.integration_type === 'email' && 'Supplier and customer restock notifications.'}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-white/[0.05] flex items-center justify-between">
              <span className="text-[11px] text-neutral-500">Connector State:</span>
              <button
                onClick={() => handleToggle(item.integration_type, item.is_enabled)}
                className={`px-3 py-1 rounded text-xs font-semibold cursor-pointer transition-colors ${
                  item.is_enabled
                    ? 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20'
                    : 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20'
                }`}
              >
                {item.is_enabled ? 'Disable' : 'Enable'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Google Sheets / CSV Import Section */}
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-[#22D3EE]" />
          <h3 className="text-base font-semibold text-white">Google Sheets & CSV Catalog Importer</h3>
        </div>
        <p className="text-xs text-neutral-400">
          Paste CSV rows from Google Sheets. dukaanDost validates schema, checks margins (selling &gt; cost), and identifies duplicate items before committing to the database.
        </p>

        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs text-neutral-400">CSV Input Data</label>
            <button
              onClick={() => setCsvText(sampleCsvTemplate)}
              className="text-[11px] text-[#22D3EE] hover:underline cursor-pointer"
            >
              Load Sample Template
            </button>
          </div>
          <textarea
            rows={5}
            value={csvText}
            onChange={(e) => setCsvText(e.target.value)}
            placeholder="product_id,product_name,category,cost_price,selling_price,current_stock,supplier_name..."
            className="w-full bg-[#171717] border border-white/[0.08] rounded-lg p-3 text-xs font-mono text-white placeholder-neutral-500 focus:outline-none focus:border-[#22D3EE]"
          />
        </div>

        <button
          onClick={handlePreviewCsv}
          disabled={importing || !csvText.trim()}
          className="px-4 py-2 rounded-lg bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold flex items-center gap-2 cursor-pointer transition-colors disabled:opacity-50"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>{importing ? 'Validating Schema...' : 'Preview Import'}</span>
        </button>

        {previewResult && (
          <div className="mt-4 p-4 rounded-lg bg-[#171717] border border-white/[0.08] space-y-3 text-xs">
            {previewResult.success ? (
              <>
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-emerald-400">Validation Passed</span>
                  <span className="text-neutral-400">
                    {previewResult.new_products_count} New Products, {previewResult.updated_products_count} Updates
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-neutral-300">
                    <thead className="text-neutral-500 border-b border-white/[0.06] uppercase text-[10px]">
                      <tr>
                        <th className="py-2">ID</th>
                        <th className="py-2">Name</th>
                        <th className="py-2">Cost</th>
                        <th className="py-2">Sell</th>
                        <th className="py-2">Stock</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/[0.04]">
                      {previewResult.preview_items?.map((it: any) => (
                        <tr key={it.product_id}>
                          <td className="py-1.5 font-mono text-white">{it.product_id}</td>
                          <td className="py-1.5">{it.product_name}</td>
                          <td className="py-1.5 font-mono">₹{it.cost_price}</td>
                          <td className="py-1.5 font-mono text-[#22D3EE]">₹{it.selling_price}</td>
                          <td className="py-1.5 font-mono">{it.current_stock}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <button
                  onClick={handleConfirmImport}
                  disabled={importing}
                  className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-black text-xs font-semibold cursor-pointer"
                >
                  Confirm & Commit to Catalog
                </button>
              </>
            ) : (
              <div className="text-red-400">{previewResult.error}</div>
            )}
          </div>
        )}

        {importStatus && (
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
            {importStatus}
          </div>
        )}
      </div>

      {/* Regional Weather Signals Card */}
      {weather && (
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CloudSun className="w-5 h-5 text-amber-400" />
              <h3 className="text-base font-semibold text-white">Contextual Demand Signals ({weather.city}, {weather.region})</h3>
            </div>
            <span className="text-xs text-neutral-400">{weather.temperature_celsius}°C • {weather.condition}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {weather.contextual_signals?.map((sig: any, idx: number) => (
              <div key={idx} className="p-3 rounded-lg bg-[#171717] border border-white/[0.05]">
                <span className="font-semibold text-[#22D3EE]">{sig.category}</span>
                <p className="text-neutral-300 mt-1 leading-relaxed">{sig.advice}</p>
              </div>
            ))}
          </div>
          <span className="text-[10px] text-neutral-500 block">{weather.disclaimer}</span>
        </div>
      )}

      {/* Sandboxed Messaging Preview */}
      {messagingDraft && (
        <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 space-y-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-[#22C55E]" />
            <h3 className="text-base font-semibold text-white">Customer Messaging Preview (Sandboxed Draft)</h3>
          </div>
          <p className="text-xs text-neutral-400">
            Outreach remains in simulation draft mode to prevent unauthorized message transmission and API charges.
          </p>

          <div className="p-4 rounded-lg bg-[#171717] border border-white/[0.05] space-y-2 text-xs">
            <div>
              <span className="text-neutral-500">English Template:</span>
              <p className="text-white mt-0.5">{messagingDraft.message_en}</p>
            </div>
            <div className="pt-2 border-t border-white/[0.04]">
              <span className="text-neutral-500">Hindi Template:</span>
              <p className="text-white mt-0.5">{messagingDraft.message_hi}</p>
            </div>
          </div>
          <span className="text-[10px] text-neutral-500 block">{messagingDraft.disclaimer}</span>
        </div>
      )}
    </div>
  );
};
