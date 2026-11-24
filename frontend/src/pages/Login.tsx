import React, { useState } from 'react';
import { Store, Lock, Mail, User as UserIcon, ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage: React.FC<{ onLoginSuccess: () => void }> = ({ onLoginSuccess }) => {
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);

  // Form states
  const [email, setEmail] = useState('owner@sharmastore.com');
  const [password, setPassword] = useState('SharmaStore2026!');
  const [fullName, setFullName] = useState('Sharma Ji');
  const [storeName, setStoreName] = useState('Sharma General Store');
  const [storeLocation, setStoreLocation] = useState('Ranchi, Jharkhand');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isRegister) {
        await register({
          email,
          password,
          full_name: fullName,
          store_name: storeName,
          store_location: storeLocation
        });
      } else {
        await login(email, password);
      }
      onLoginSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4 relative overflow-hidden select-none">
      {/* Ambient background glows */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#22D3EE]/5 blur-3xl pointer-events-none rounded-full" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#818CF8]/5 blur-3xl pointer-events-none rounded-full" />

      <div className="max-w-md w-full bg-[#111111] border border-white/[0.1] rounded-2xl p-8 relative z-10 shadow-2xl space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#22D3EE] to-[#818CF8] flex items-center justify-center mx-auto shadow-lg shadow-[#22D3EE]/20">
            <Store className="w-6 h-6 text-black stroke-[2.5]" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">DukaanDost AI</h2>
          <p className="text-xs text-neutral-400">
            {isRegister ? 'Set up your autonomous Kirana growth manager' : 'Sign in to Sharma General Store workspace'}
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex bg-[#171717] p-1 rounded-xl border border-white/[0.05] text-xs">
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(null); }}
            className={`flex-1 py-1.5 rounded-lg font-medium transition-colors cursor-pointer ${
              !isRegister ? 'bg-[#22D3EE] text-black font-semibold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(null); }}
            className={`flex-1 py-1.5 rounded-lg font-medium transition-colors cursor-pointer ${
              isRegister ? 'bg-[#22D3EE] text-black font-semibold' : 'text-neutral-400 hover:text-white'
            }`}
          >
            Register Store
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {isRegister && (
            <>
              <div>
                <label className="text-neutral-400 mb-1 block">Full Name</label>
                <div className="relative">
                  <UserIcon className="w-4 h-4 absolute left-3 top-2.5 text-neutral-500" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Sharma Ji"
                    className="w-full bg-[#171717] border border-white/[0.08] rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-[#22D3EE]"
                  />
                </div>
              </div>

              <div>
                <label className="text-neutral-400 mb-1 block">Store Name</label>
                <div className="relative">
                  <Store className="w-4 h-4 absolute left-3 top-2.5 text-neutral-500" />
                  <input
                    type="text"
                    required
                    value={storeName}
                    onChange={(e) => setStoreName(e.target.value)}
                    placeholder="Sharma General Store"
                    className="w-full bg-[#171717] border border-white/[0.08] rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-[#22D3EE]"
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <label className="text-neutral-400 mb-1 block">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-2.5 text-neutral-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="owner@sharmastore.com"
                className="w-full bg-[#171717] border border-white/[0.08] rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-[#22D3EE]"
              />
            </div>
          </div>

          <div>
            <label className="text-neutral-400 mb-1 block">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-2.5 text-neutral-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#171717] border border-white/[0.08] rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-[#22D3EE]"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-[#22D3EE] hover:bg-[#06b6d4] text-black font-semibold text-xs flex items-center justify-center gap-2 cursor-pointer transition-all shadow-md disabled:opacity-50"
          >
            <span>{loading ? 'Authenticating...' : isRegister ? 'Create Account & Store' : 'Sign In to Workspace'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Credentials Helper */}
        <div className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.05] text-[11px] text-neutral-400 space-y-1">
          <span className="font-semibold text-neutral-300 block">Demonstration Credentials:</span>
          <p>Email: <code className="text-[#22D3EE]">owner@sharmastore.com</code></p>
          <p>Password: <code className="text-[#22D3EE]">SharmaStore2026!</code></p>
        </div>
      </div>
    </div>
  );
};
