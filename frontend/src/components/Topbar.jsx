import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, ChevronDown, LogOut, Menu, Search, UserRound } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { initials } from '../utils/format';

const TITLES = {
  '/app': 'Overview',
  '/app/scanner': 'Message Scanner',
  '/app/url-scanner': 'URL Scanner',
  '/app/alerts': 'Family Alerts',
  '/app/history': 'Scan History',
  '/app/awareness': 'Scam Awareness',
  '/app/settings': 'Settings',
};

export default function Topbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [query, setQuery] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!menuOpen) return undefined;
    const onPointerDown = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) setMenuOpen(false);
    };
    const onKeyDown = (event) => {
      if (event.key === 'Escape') setMenuOpen(false);
    };
    document.addEventListener('mousedown', onPointerDown);
    window.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('mousedown', onPointerDown);
      window.removeEventListener('keydown', onKeyDown);
    };
  }, [menuOpen]);

  const onSearch = (event) => {
    event.preventDefault();
    const trimmed = query.trim();
    navigate(trimmed ? `/app/history?q=${encodeURIComponent(trimmed)}` : '/app/history');
  };

  return (
    <header className="sticky top-0 z-30 flex h-[68px] items-center gap-3 border-b border-line bg-white/90 px-4 backdrop-blur-md sm:px-6 lg:px-8">
      <button
        type="button"
        onClick={onMenuClick}
        className="rounded-xl p-2 text-slate-600 transition hover:bg-slate-100 lg:hidden"
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="hidden min-w-0 shrink-0 md:block">
        <p className="text-[11px] text-slate-400">Workspace</p>
        <p className="truncate text-sm font-semibold text-slate-900">{TITLES[location.pathname] || 'FamilyShield AI'}</p>
      </div>

      <form onSubmit={onSearch} className="relative ml-auto w-full max-w-sm" role="search">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search your scans…"
          aria-label="Search scans"
          className="fs-input h-10 py-2 pl-9 text-[13px]"
        />
      </form>

      <button
        type="button"
        onClick={() => navigate('/app/alerts')}
        className="relative rounded-xl p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
        aria-label="View family alerts"
      >
        <Bell className="h-5 w-5" strokeWidth={1.8} />
      </button>

      <div className="relative" ref={menuRef}>
        <button
          type="button"
          onClick={() => setMenuOpen((value) => !value)}
          className="flex items-center gap-2 rounded-xl border border-transparent p-1 pr-2 transition hover:border-line hover:bg-slate-50"
          aria-haspopup="menu"
          aria-expanded={menuOpen}
        >
          <span className="grid h-8 w-8 place-items-center rounded-full bg-navy-800 text-[11px] font-semibold text-white">
            {initials(user?.full_name)}
          </span>
          <span className="hidden max-w-[130px] truncate text-[13px] font-medium text-slate-700 sm:block">
            {user?.full_name?.split(' ')[0] || 'Account'}
          </span>
          <ChevronDown className="h-4 w-4 text-slate-400" />
        </button>

        {menuOpen && (
          <div
            role="menu"
            className="absolute right-0 top-[calc(100%+8px)] w-60 animate-fade-in overflow-hidden rounded-2xl border border-line bg-white p-1.5 shadow-pop"
          >
            <div className="border-b border-line px-3 py-3">
              <p className="truncate text-sm font-semibold text-slate-900">{user?.full_name || 'Your account'}</p>
              <p className="truncate text-xs text-slate-500">{user?.email}</p>
            </div>
            <button
              type="button"
              role="menuitem"
              onClick={() => navigate('/app/settings')}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm text-slate-700 transition hover:bg-slate-50"
            >
              <UserRound className="h-4 w-4 text-slate-400" />
              Profile & settings
            </button>
            <button
              type="button"
              role="menuitem"
              onClick={() => navigate('/app/alerts')}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm text-slate-700 transition hover:bg-slate-50"
            >
              <Bell className="h-4 w-4 text-slate-400" />
              Family alerts
            </button>
            <button
              type="button"
              role="menuitem"
              onClick={logout}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-red-600 transition hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
              Log out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
