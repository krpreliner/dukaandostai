import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Bot,
  BarChart3,
  Sparkles,
  ShieldCheck,
  Package,
  Users,
  History,
  AlertTriangle,
  Settings as SettingsIcon,
  Store,
  CheckCircle2,
  Cpu,
  UserCheck,
  Plug,
  Activity
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  pendingApprovalsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ pendingApprovalsCount = 0 }) => {
  const { activeStore } = useAuth();

  const primaryNavItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'AI Worker', path: '/worker', icon: Bot },
    { name: 'Business Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Growth Strategies', path: '/strategies', icon: Sparkles },
    { name: 'Approval Centre', path: '/approvals', icon: ShieldCheck, badge: pendingApprovalsCount },
    { name: 'Inventory Intelligence', path: '/inventory', icon: Package },
    { name: 'Customer Insights', path: '/customers', icon: Users },
    { name: 'Execution History', path: '/history', icon: History },
    { name: 'Failure Monitoring', path: '/failures', icon: AlertTriangle },
  ];

  const enterpriseNavItems = [
    { name: 'AI Providers & Routing', path: '/ai-providers', icon: Cpu },
    { name: 'Team & Store Roles', path: '/team', icon: UserCheck },
    { name: 'External Integrations', path: '/integrations', icon: Plug },
    { name: 'System Health & Audits', path: '/health', icon: Activity },
    { name: 'Settings', path: '/settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 shrink-0 bg-[#0A0A0A] border-r border-white/[0.08] flex flex-col h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-white/[0.08]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#22D3EE] to-[#818CF8] flex items-center justify-center shadow-lg shadow-[#22D3EE]/20">
            <Store className="w-5 h-5 text-black stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-base tracking-tight text-white">DukaanDost</span>
              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-[#22D3EE]/15 text-[#22D3EE] border border-[#22D3EE]/30">AI</span>
            </div>
            <p className="text-[11px] text-neutral-500 font-medium tracking-tight">Autonomous Kirana Partner</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-4 overflow-y-auto">
        <div className="space-y-1">
          <span className="px-3 text-[10px] font-bold uppercase tracking-wider text-neutral-500">
            Core Growth Operations
          </span>
          {primaryNavItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-[#171717] text-white border-l-2 border-[#22D3EE] pl-2.5 shadow-sm'
                    : 'text-neutral-400 hover:text-white hover:bg-neutral-900/60'
                }`
              }
            >
              <div className="flex items-center gap-2.5">
                <item.icon className="w-4 h-4 opacity-80" />
                <span>{item.name}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded-full bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </div>

        <div className="space-y-1 pt-2 border-t border-white/[0.04]">
          <span className="px-3 text-[10px] font-bold uppercase tracking-wider text-neutral-500">
            Enterprise & Platform
          </span>
          {enterpriseNavItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-[#171717] text-white border-l-2 border-[#22D3EE] pl-2.5 shadow-sm'
                    : 'text-neutral-400 hover:text-white hover:bg-neutral-900/60'
                }`
              }
            >
              <div className="flex items-center gap-2.5">
                <item.icon className="w-4 h-4 opacity-80" />
                <span>{item.name}</span>
              </div>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Dynamic Store Workspace Badge */}
      <div className="p-4 border-t border-white/[0.08] bg-[#080808]">
        <div className="bg-[#111111] p-3 rounded-lg border border-white/[0.06]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-white truncate max-w-[140px]">
              {activeStore ? activeStore.name : 'Sharma General Store'}
            </span>
            <span className="flex items-center gap-1 text-[10px] text-[#22C55E]">
              <CheckCircle2 className="w-3 h-3" /> Live
            </span>
          </div>
          <p className="text-[10px] text-neutral-400 mt-0.5 truncate">
            {activeStore ? activeStore.location : 'Ranchi, Jharkhand'}
          </p>
          <div className="mt-2 pt-2 border-t border-white/[0.04] flex items-center justify-between text-[10px]">
            <span className="text-neutral-500">Income Goal:</span>
            <span className="text-[#22D3EE] font-medium">₹8k → ₹10k</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
