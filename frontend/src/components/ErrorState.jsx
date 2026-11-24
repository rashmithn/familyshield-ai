import { AlertTriangle, RotateCw } from 'lucide-react';
import { getErrorMessage } from '../utils/format';

export default function ErrorState({ error, title = 'We could not load this', onRetry, message }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <span className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-red-50 text-red-600">
        <AlertTriangle className="h-6 w-6" strokeWidth={1.8} />
      </span>
      <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
      <p className="mt-1.5 max-w-md text-sm leading-relaxed text-slate-500">
        {message || getErrorMessage(error)}
      </p>
      {onRetry && (
        <button type="button" className="fs-btn-secondary mt-5" onClick={onRetry}>
          <RotateCw className="h-4 w-4" />
          Try again
        </button>
      )}
    </div>
  );
}
