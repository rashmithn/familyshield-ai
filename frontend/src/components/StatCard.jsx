export default function StatCard({ label, value, hint, icon: Icon, tone = 'navy' }) {
  const tones = {
    navy: 'bg-navy-900/5 text-navy-700',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    red: 'bg-red-50 text-red-600',
    slate: 'bg-slate-100 text-slate-600',
  };

  return (
    <div className="fs-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-slate-500">{label}</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900 tabular-nums">{value ?? '—'}</p>
          {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
        </div>
        {Icon && (
          <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ${tones[tone] || tones.navy}`}>
            <Icon className="h-[18px] w-[18px]" strokeWidth={1.9} />
          </span>
        )}
      </div>
    </div>
  );
}
