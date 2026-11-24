import { Link } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';

export default function Logo({ to = '/', compact = false, light = false, onClick, className = '' }) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className={`group inline-flex items-center gap-2.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/40 ${className}`}
      aria-label="FamilyShield AI home"
    >
      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-700 text-white shadow-sm transition group-hover:from-emerald-300 group-hover:to-emerald-600">
        <ShieldCheck className="h-5 w-5" strokeWidth={2.2} />
      </span>
      {!compact && (
        <span className={`whitespace-nowrap text-[15px] font-bold tracking-tight ${light ? 'text-white' : 'text-navy-900'}`}>
          FamilyShield <span className={light ? 'text-emerald-300' : 'text-emerald-600'}>AI</span>
        </span>
      )}
    </Link>
  );
}
