import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: string;
  trendPositive?: boolean;
  accentColor?: 'cyan' | 'indigo' | 'green' | 'amber' | 'red';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendPositive = true,
  accentColor = 'cyan',
}) => {
  const accentGlow = {
    cyan: 'hover:border-[#22D3EE]/30',
    indigo: 'hover:border-[#818CF8]/30',
    green: 'hover:border-[#22C55E]/30',
    amber: 'hover:border-[#F59E0B]/30',
    red: 'hover:border-[#EF4444]/30',
  }[accentColor];

  const iconColor = {
    cyan: 'text-[#22D3EE] bg-[#22D3EE]/10',
    indigo: 'text-[#818CF8] bg-[#818CF8]/10',
    green: 'text-[#22C55E] bg-[#22C55E]/10',
    amber: 'text-[#F59E0B] bg-[#F59E0B]/10',
    red: 'text-[#EF4444] bg-[#EF4444]/10',
  }[accentColor];

  return (
    <div
      className={`bg-[#111111] border border-white/[0.08] rounded-xl p-5 transition-all duration-200 ${accentGlow}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-neutral-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2 rounded-lg ${iconColor}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-white tracking-tight">
          {value}
        </span>
        {trend && (
          <span
            className={`text-xs font-medium ${
              trendPositive ? 'text-[#22C55E]' : 'text-[#EF4444]'
            }`}
          >
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-1.5 text-xs text-neutral-500 font-normal">
          {subtitle}
        </p>
      )}
    </div>
  );
};
