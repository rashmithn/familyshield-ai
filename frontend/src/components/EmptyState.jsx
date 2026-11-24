import { Inbox } from 'lucide-react';

export default function EmptyState({ icon: Icon = Inbox, title = 'Nothing here yet', description, action, compact = false }) {
  return (
    <div className={`flex flex-col items-center justify-center text-center ${compact ? 'py-12' : 'py-20'}`}>
      <span className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-slate-100 text-slate-500">
        <Icon className="h-6 w-6" strokeWidth={1.8} />
      </span>
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      {description && <p className="mt-1.5 max-w-sm text-sm leading-relaxed text-slate-500">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
