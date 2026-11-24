import { Info, ShieldCheck } from 'lucide-react';

export default function AdvisoryNote({ compact = false, className = '' }) {
  if (compact) {
    return (
      <p className={`flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-400 ${className}`}>
        <Info className="mt-px h-3.5 w-3.5 shrink-0" />
        Detection is advisory, not a guarantee.
      </p>
    );
  }

  return (
    <div className={`flex items-start gap-3 rounded-xl border border-amber-200/70 bg-amber-50/70 px-4 py-3 ${className}`}>
      <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
      <p className="text-xs leading-relaxed text-amber-900">
        <span className="font-semibold">Detection is advisory, not a guarantee.</span> No tool can prove a message or
        link is completely safe. Stay careful with requests for money, passwords, or one-time codes.
      </p>
    </div>
  );
}
