import { NavLink } from 'react-router-dom';
import {
  Bell,
  GraduationCap,
  History,
  LayoutDashboard,
  Link2,
  MessageSquareText,
  Settings,
  ShieldCheck,
  X,
} from 'lucide-react';
import Logo from './Logo';
import { initials } from '../utils/format';

const NAV_ITEMS = [
  { to: '/app', label: 'Overview', icon: LayoutDashboard, end: true },
  { to: '/app/scanner', label: 'Message Scanner', icon: MessageSquareText },
  { to: '/app/url-scanner', label: 'URL Scanner', icon: Link2 },
  { to: '/app/alerts', label: 'Family Alerts', icon: Bell },
  { to: '/app/history', label: 'Scan History', icon: History },
  { to: '/app/awareness', label: 'Scam Awareness', icon: GraduationCap },
  { to: '/app/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ open, onClose, user }) {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-50 flex w-[268px] flex-col border-r border-white/[0.06] bg-navy-950 transition-transform duration-200 ease-out lg:translate-x-0 ${
        open ? 'translate-x-0 shadow-pop' : '-translate-x-full'
      }`}
      aria-label="Main navigation"
    >
      <div className="flex h-[68px] shrink-0 items-center justify-between border-b border-white/[0.06] px-5">
        <Logo to="/app" light />
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-1.5 text-slate-400 transition hover:bg-white/5 hover:text-white lg:hidden"
          aria-label="Close navigation"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <nav className="fs-scroll flex-1 overflow-y-auto px-3 py-5">
        <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Workspace</p>
        <div className="space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-[13px] font-medium transition-colors ${
                  isActive
                    ? 'bg-white/[0.09] text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)]'
                    : 'text-slate-400 hover:bg-white/[0.05] hover:text-slate-100'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={`h-[18px] w-[18px] shrink-0 ${isActive ? 'text-emerald-400' : ''}`} strokeWidth={1.8} />
                  <span>{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>

      <div className="shrink-0 border-t border-white/[0.06] px-4 py-4">
        <div className="mb-4 flex items-start gap-2 rounded-xl bg-white/[0.04] px-3 py-2.5">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
          <p className="text-[11px] leading-relaxed text-slate-400">
            Detection is advisory, not a guarantee.
          </p>
        </div>
        <div className="flex items-center gap-3 px-1">
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-navy-600 to-navy-700 text-xs font-semibold text-white ring-1 ring-white/10">
            {initials(user?.full_name)}
          </span>
          <div className="min-w-0">
            <p className="truncate text-[13px] font-medium text-slate-100">{user?.full_name || 'Your account'}</p>
            <p className="truncate text-[11px] text-slate-500">{user?.email || ''}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
