import React from 'react';
import { Play, RotateCcw, AlertOctagon, MapPin } from 'lucide-react';
import { StatusBadge } from '../ui/StatusBadge';

interface HeaderProps {
  pageTitle: string;
  workerStatus: string;
  onStartWorker: () => void;
  onTriggerFailure: () => void;
  onReset: () => void;
  isLoading?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  pageTitle,
  workerStatus,
  onStartWorker,
  onTriggerFailure,
  onReset,
  isLoading = false,
}) => {
  return (
    <header className="h-16 bg-[#050505]/80 backdrop-blur-md border-b border-white/[0.08] px-8 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-white tracking-tight">{pageTitle}</h1>
        <div className="h-4 w-[1px] bg-neutral-800" />
        <div className="flex items-center gap-1.5 text-xs text-neutral-400">
          <MapPin className="w-3.5 h-3.5 text-[#22D3EE]" />
          <span>Sharma General Store, Ranchi</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Worker Status Badge */}
        <div className="flex items-center gap-2 mr-2">
          <span className="text-xs text-neutral-400">Worker Status:</span>
          <StatusBadge status={workerStatus} size="sm" />
        </div>

        {/* Demo trigger failure button */}
        <button
          onClick={onTriggerFailure}
          title="Set Butter Cost ₹60 > Sell ₹55 to test negative-margin rejection"
          className="px-3 py-1.5 rounded-lg border border-red-500/20 bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-medium flex items-center gap-1.5 transition-all"
        >
          <AlertOctagon className="w-3.5 h-3.5" />
          <span>Demo Failure</span>
        </button>

        {/* Reset button */}
        <button
          onClick={onReset}
          title="Reset synthetic data to baseline ₹8,000"
          className="px-3 py-1.5 rounded-lg border border-white/[0.08] bg-[#111111] hover:bg-neutral-800 text-neutral-300 text-xs font-medium flex items-center gap-1.5 transition-all"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset</span>
        </button>

        {/* Primary Start AI Worker button */}
        <button
          onClick={onStartWorker}
          disabled={isLoading || workerStatus === 'EXECUTING'}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md ${
            isLoading || workerStatus === 'EXECUTING'
              ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
              : 'bg-[#22D3EE] hover:bg-[#06b6d4] text-black shadow-[#22D3EE]/20 hover:shadow-[#22D3EE]/30'
          }`}
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isLoading ? 'Executing...' : 'Start AI Worker'}</span>
        </button>
      </div>
    </header>
  );
};
