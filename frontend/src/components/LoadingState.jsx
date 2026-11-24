import { Loader2 } from 'lucide-react';

export function Spinner({ className = 'h-5 w-5' }) {
  return <Loader2 className={`animate-spin ${className}`} aria-hidden="true" />;
}

export default function LoadingState({ label = 'Loading…', compact = false }) {
  if (compact) {
    return (
      <div className="flex items-center gap-2 py-6 text-sm text-slate-500" role="status">
        <Spinner className="h-4 w-4 text-navy-700" />
        {label}
      </div>
    );
  }

  return (
    <div className="flex min-h-[240px] flex-col items-center justify-center gap-3" role="status">
      <span className="grid h-11 w-11 place-items-center rounded-2xl bg-slate-100">
        <Spinner className="h-5 w-5 text-navy-700" />
      </span>
      <p className="text-sm font-medium text-slate-500">{label}</p>
    </div>
  );
}
