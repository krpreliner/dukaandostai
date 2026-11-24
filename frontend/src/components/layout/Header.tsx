import React from 'react';
import { Play, RotateCcw, AlertOctagon, MapPin, Store, LogOut, ChevronDown, Sparkles } from 'lucide-react';
import { StatusBadge } from '../ui/StatusBadge';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

interface HeaderProps {
  pageTitle: string;
  workerStatus: string;
  onStartWorker: () => void;
  onTriggerFailure: () => void;
  onReset: () => void;
  onOpenAssistant?: () => void;
  isLoading?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  pageTitle,
  workerStatus,
  onStartWorker,
  onTriggerFailure,
  onReset,
  onOpenAssistant,
  isLoading = false,
}) => {
  const { activeStore, stores, switchStore, user, logout } = useAuth();
  const { language, setLanguage } = useLanguage();

  return (
    <header className="h-16 bg-[#050505]/90 backdrop-blur-md border-b border-white/[0.08] px-6 lg:px-8 flex items-center justify-between sticky top-0 z-20 w-full shrink-0 overflow-x-auto overflow-y-hidden">
      <div className="flex items-center gap-3 shrink-0">
        <h1 className="text-sm font-semibold text-white tracking-tight whitespace-nowrap">{pageTitle}</h1>
        <div className="h-4 w-[1px] bg-neutral-800" />
        
        {/* Workspace Selector Dropdown */}
        <div className="flex items-center gap-2 text-xs text-neutral-300 shrink-0">
          <MapPin className="w-3.5 h-3.5 text-[#22D3EE]" />
          <select
            value={activeStore?.store_id || 'STORE_001'}
            onChange={(e) => switchStore(e.target.value)}
            className="bg-[#111111] border border-white/[0.08] text-neutral-200 text-xs rounded-lg px-2 py-1 focus:outline-none focus:border-[#22D3EE] cursor-pointer"
          >
            {stores.map((s) => (
              <option key={s.store_id} value={s.store_id}>
                {s.name} ({s.location})
              </option>
            ))}
          </select>
        </div>

        <div className="h-4 w-[1px] bg-neutral-800" />

        {/* Language Switcher Toggle */}
        <div className="flex items-center p-0.5 bg-[#111111] border border-white/[0.08] rounded-lg text-xs shrink-0">
          <button
            onClick={() => setLanguage('hi')}
            title="हिंदी (Hindi) भाषा चुनें"
            className={`px-2 py-0.5 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
              language === 'hi'
                ? 'bg-[#22D3EE] text-black shadow-xs'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            हिंदी
          </button>
          <button
            onClick={() => setLanguage('en')}
            title="Switch to English"
            className={`px-2 py-0.5 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
              language === 'en'
                ? 'bg-[#22D3EE] text-black shadow-xs'
                : 'text-neutral-400 hover:text-white'
            }`}
          >
            English
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 pl-4">
        {/* Worker Status Badge */}
        <div className="flex items-center gap-1.5 mr-1 shrink-0">
          <span className="text-xs text-neutral-400 hidden xl:inline">Worker:</span>
          <StatusBadge status={workerStatus} size="sm" />
        </div>

        {/* Demo trigger failure button */}
        <button
          onClick={onTriggerFailure}
          title="Set Butter Cost ₹60 > Sell ₹55 to test negative-margin rejection"
          className="px-2.5 py-1.5 rounded-lg border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-medium flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
        >
          <AlertOctagon className="w-3.5 h-3.5" />
          <span>Demo Failure</span>
        </button>

        {/* Reset button */}
        <button
          onClick={onReset}
          title="Reset synthetic data to baseline ₹8,000"
          className="px-2.5 py-1.5 rounded-lg border border-white/[0.08] bg-[#111111] hover:bg-neutral-800 text-neutral-300 text-xs font-medium flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>

        {/* AI Assistant button */}
        {onOpenAssistant && (
          <button
            onClick={onOpenAssistant}
            title="Chat or speak with DukaanDost AI Business Partner"
            className="px-2.5 py-1.5 rounded-lg border border-[#22D3EE]/30 bg-[#22D3EE]/10 hover:bg-[#22D3EE]/20 text-[#22D3EE] text-xs font-medium flex items-center gap-1.5 transition-all cursor-pointer shadow-sm shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Assistant</span>
          </button>
        )}

        {/* Primary Start AI Worker button */}
        <button
          onClick={onStartWorker}
          disabled={isLoading || workerStatus === 'EXECUTING'}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md cursor-pointer shrink-0 ${
            isLoading || workerStatus === 'EXECUTING'
              ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
              : 'bg-[#22D3EE] hover:bg-[#06b6d4] text-black shadow-[#22D3EE]/20 hover:shadow-[#22D3EE]/30'
          }`}
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isLoading ? 'Executing...' : 'Start AI Worker'}</span>
        </button>

        {/* User Badge / Logout */}
        {user && (
          <div className="flex items-center gap-2 pl-2 border-l border-white/[0.08] shrink-0">
            <div className="w-7 h-7 rounded-full bg-[#22D3EE]/15 border border-[#22D3EE]/30 flex items-center justify-center text-[11px] font-bold text-[#22D3EE]">
              {user.full_name.charAt(0)}
            </div>
            <button
              onClick={logout}
              title={`Logged in as ${user.email}. Click to sign out.`}
              className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
