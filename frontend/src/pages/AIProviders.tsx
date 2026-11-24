import React, { useEffect, useState } from 'react';
import { Cpu, CheckCircle, XCircle, AlertCircle, RefreshCw, Key, ShieldCheck, Zap, DollarSign } from 'lucide-react';
import { getAIProviders, testProviderConnection, saveProviderSetting, getAIUsageStats } from '../services/api';
import { AIProvider, AIUsageStats } from '../types';

export const AIProviders: React.FC = () => {
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [usage, setUsage] = useState<AIUsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [testingName, setTestingName] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ [key: string]: { status: string; message: string; latency_ms: number } }>({});
  
  // Modal state for configuring key
  const [editingProvider, setEditingProvider] = useState<AIProvider | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [isPrimary, setIsPrimary] = useState(false);
  const [isFallback, setIsFallback] = useState(false);
  const [saving, setSaving] = useState(false);

  const fetchData = async () => {
    try {
      const [provData, usageData] = await Promise.all([
        getAIProviders(),
        getAIUsageStats()
      ]);
      setProviders(provData || []);
      setUsage(usageData || null);
    } catch (err) {
      console.error('Error fetching AI providers:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleTestConnection = async (p: AIProvider) => {
    setTestingName(p.provider_name);
    try {
      const res = await testProviderConnection({ provider_name: p.provider_name, model: p.selected_model });
      setTestResult((prev) => ({
        ...prev,
        [p.provider_name]: {
          status: res.status,
          message: res.message,
          latency_ms: res.latency_ms
        }
      }));
    } catch (err: any) {
      setTestResult((prev) => ({
        ...prev,
        [p.provider_name]: {
          status: 'CONNECTION FAILED',
          message: err.message || 'Network error',
          latency_ms: 0
        }
      }));
    } finally {
      setTestingName(null);
    }
  };

  const openConfigModal = (p: AIProvider) => {
    setEditingProvider(p);
    setSelectedModel(p.selected_model || p.supported_models[0]);
    setIsPrimary(p.is_primary);
    setIsFallback(p.is_fallback);
    setApiKeyInput('');
  };

  const handleSaveConfig = async () => {
    if (!editingProvider) return;
    setSaving(true);
    try {
      await saveProviderSetting({
        provider_name: editingProvider.provider_name,
        model_name: selectedModel,
        is_enabled: true,
        is_primary: isPrimary,
        is_fallback: isFallback,
        api_key: apiKeyInput || undefined
      });
      await fetchData();
      setEditingProvider(null);
    } catch (err) {
      console.error('Save failed:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 space-y-8 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Cpu className="w-5 h-5 text-[#22D3EE]" />
            <h2 className="text-xl font-bold text-white tracking-tight">AI Provider & Routing Management</h2>
          </div>
          <p className="text-sm text-neutral-400">
            Modular multi-provider architecture: OpenAI, Google Gemini, Groq, Ollama, and Deterministic Local Mode.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="self-start sm:self-center px-3 py-1.5 rounded-lg bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-xs text-neutral-300 flex items-center gap-1.5 cursor-pointer transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Status</span>
        </button>
      </div>

      {/* Zero Paid Cost Policy Callout */}
      <div className="bg-[#111111] border border-cyan-500/20 rounded-xl p-5 relative overflow-hidden">
        <div className="flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-[#22D3EE] mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-semibold text-white">Zero-Cost-First Policy Active</h4>
            <p className="text-xs text-neutral-300 mt-1 leading-relaxed">
              DukaanDost AI operates 100% locally in <strong>Deterministic Local Mode</strong> without requiring any paid API keys or subscriptions. If you choose to configure external providers (OpenAI, Gemini, Groq), the system uses an intelligent router with bounded retries, token caps, and automatic fallback to local intelligence if credentials expire or rate limits occur.
            </p>
          </div>
        </div>
      </div>

      {/* Usage & Cost Summary Cards */}
      {usage && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <span className="text-xs text-neutral-400 font-medium">Total AI Executions</span>
            <p className="text-xl font-bold text-white mt-1">{usage.total_requests}</p>
            <span className="text-[11px] text-neutral-500">Autonomous queries routed</span>
          </div>
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <span className="text-xs text-neutral-400 font-medium">Total Tokens Consumed</span>
            <p className="text-xl font-bold text-[#22D3EE] mt-1">{usage.total_tokens.toLocaleString()}</p>
            <span className="text-[11px] text-neutral-500">{usage.total_prompt_tokens} in / {usage.total_completion_tokens} out</span>
          </div>
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <span className="text-xs text-neutral-400 font-medium">Estimated API Cost (USD)</span>
            <p className="text-xl font-bold text-[#22C55E] mt-1">${usage.total_cost_usd.toFixed(4)}</p>
            <span className="text-[11px] text-[#22C55E]/80">Published provider rates</span>
          </div>
          <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-5">
            <span className="text-xs text-neutral-400 font-medium">Average Request Latency</span>
            <p className="text-xl font-bold text-neutral-200 mt-1">{usage.avg_latency_ms} ms</p>
            <span className="text-[11px] text-neutral-500">Fast local & API response</span>
          </div>
        </div>
      )}

      {/* Providers Grid */}
      <div className="space-y-4">
        <h3 className="text-base font-semibold text-white">Configured AI Providers</h3>

        <div className="grid grid-cols-1 gap-4">
          {providers.map((p) => {
            const result = testResult[p.provider_name];
            const currentStatus = result ? result.status : p.status;
            const currentMessage = result ? result.message : p.message;
            const currentLatency = result ? result.latency_ms : p.latency_ms;

            const isVerified = currentStatus === 'CONNECTED AND VERIFIED';
            const isFailed = currentStatus === 'CONNECTION FAILED';

            return (
              <div
                key={p.provider_name}
                className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 relative overflow-hidden"
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <span className="text-sm font-bold text-white capitalize">{p.provider_name}</span>
                      <span className="text-xs font-mono text-[#22D3EE] px-2 py-0.5 rounded bg-[#22D3EE]/10 border border-[#22D3EE]/20">
                        {p.selected_model}
                      </span>
                      {p.is_primary && (
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Primary Provider
                        </span>
                      )}
                      {p.is_fallback && (
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                          Fallback Provider
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-neutral-400">{currentMessage}</p>

                    <div className="flex items-center gap-4 text-xs text-neutral-500">
                      <span>Supported Models: <strong className="text-neutral-300">{p.supported_models.join(', ')}</strong></span>
                      {currentLatency > 0 && (
                        <span>Ping Latency: <strong className="text-neutral-300">{currentLatency} ms</strong></span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 border ${
                      isVerified
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : isFailed
                        ? 'bg-red-500/10 text-red-400 border-red-500/20'
                        : 'bg-neutral-800 text-neutral-400 border-white/[0.08]'
                    }`}>
                      {isVerified ? <CheckCircle className="w-3.5 h-3.5" /> : isFailed ? <XCircle className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                      <span>{currentStatus}</span>
                    </span>

                    <button
                      onClick={() => handleTestConnection(p)}
                      disabled={testingName === p.provider_name}
                      className="px-3 py-1.5 rounded-lg bg-[#171717] hover:bg-neutral-800 border border-white/[0.08] text-xs text-neutral-300 flex items-center gap-1.5 cursor-pointer transition-colors"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${testingName === p.provider_name ? 'animate-spin' : ''}`} />
                      <span>{testingName === p.provider_name ? 'Testing...' : 'Test'}</span>
                    </button>

                    {p.provider_name !== 'deterministic' && (
                      <button
                        onClick={() => openConfigModal(p)}
                        className="px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 text-[#22D3EE] text-xs font-medium flex items-center gap-1.5 cursor-pointer transition-colors"
                      >
                        <Key className="w-3.5 h-3.5" />
                        <span>Configure</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Configuration Modal */}
      {editingProvider && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111111] border border-white/[0.1] rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <div>
              <h3 className="text-base font-semibold text-white capitalize">Configure {editingProvider.provider_name}</h3>
              <p className="text-xs text-neutral-400 mt-1">
                Enter API credentials locally. Keys are securely stored and never committed or exposed in chat.
              </p>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-neutral-400 mb-1 block">Selected Model</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-[#22D3EE]"
                >
                  {editingProvider.supported_models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>

              {editingProvider.provider_name !== 'ollama' && (
                <div>
                  <label className="text-neutral-400 mb-1 block">API Key</label>
                  <input
                    type="password"
                    placeholder="Enter API key..."
                    value={apiKeyInput}
                    onChange={(e) => setApiKeyInput(e.target.value)}
                    className="w-full bg-[#171717] border border-white/[0.08] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-[#22D3EE]"
                  />
                  <span className="text-[10px] text-neutral-500 mt-1 block">
                    Leave blank to retain current environment key if set.
                  </span>
                </div>
              )}

              <div className="space-y-2 pt-2 border-t border-white/[0.06]">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isPrimary}
                    onChange={(e) => {
                      setIsPrimary(e.target.checked);
                      if (e.target.checked) setIsFallback(false);
                    }}
                    className="rounded bg-neutral-800 border-white/[0.1] text-[#22D3EE]"
                  />
                  <span className="text-neutral-300">Set as Primary Provider for Agent Reasoning</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isFallback}
                    onChange={(e) => {
                      setIsFallback(e.target.checked);
                      if (e.target.checked) setIsPrimary(false);
                    }}
                    className="rounded bg-neutral-800 border-white/[0.1] text-[#22D3EE]"
                  />
                  <span className="text-neutral-300">Set as Secondary Fallback Provider</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setEditingProvider(null)}
                className="px-4 py-2 rounded-lg bg-[#171717] hover:bg-neutral-800 text-neutral-300 text-xs font-medium cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveConfig}
                disabled={saving}
                className="px-4 py-2 rounded-lg bg-[#22D3EE] hover:bg-[#06b6d4] text-black text-xs font-semibold cursor-pointer"
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
