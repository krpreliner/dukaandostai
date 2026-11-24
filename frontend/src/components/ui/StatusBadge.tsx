import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const s = status ? status.toUpperCase() : 'UNKNOWN';

  let bg = 'bg-neutral-800/80 text-neutral-300 border-neutral-700';
  let dot = 'bg-neutral-400';

  if (['COMPLETED', 'HEALTHY', 'APPROVED', 'RESOLVED'].includes(s)) {
    bg = 'bg-[#22C55E]/10 text-[#22C55E] border-[#22C55E]/20';
    dot = 'bg-[#22C55E]';
  } else if (['EXECUTING', 'ACTIVE', 'ANALYSING', 'PLANNING'].includes(s)) {
    bg = 'bg-[#22D3EE]/10 text-[#22D3EE] border-[#22D3EE]/30';
    dot = 'bg-[#22D3EE] animate-pulse';
  } else if (['WAITING FOR APPROVAL', 'WAITING_APPROVAL', 'LOW STOCK', 'PENDING'].includes(s)) {
    bg = 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/30';
    dot = 'bg-[#F59E0B]';
  } else if (['FAILED', 'REJECTED', 'NEGATIVE MARGIN', 'UNRESOLVED', 'EXPIRING SOON'].includes(s)) {
    bg = 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/30';
    dot = 'bg-[#EF4444]';
  } else if (['SLOW MOVING', 'REORDER REQUIRED'].includes(s)) {
    bg = 'bg-[#818CF8]/10 text-[#818CF8] border-[#818CF8]/30';
    dot = 'bg-[#818CF8]';
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${bg} ${px}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      <span>{status}</span>
    </span>
  );
};
