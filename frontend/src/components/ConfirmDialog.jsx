import { useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Spinner } from './LoadingState';

export default function ConfirmDialog({
  open,
  title = 'Are you sure?',
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  tone = 'danger',
  loading = false,
  onConfirm,
  onCancel,
}) {
  useEffect(() => {
    if (!open) return undefined;
    const onKeyDown = (event) => {
      if (event.key === 'Escape' && !loading) onCancel?.();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open, loading, onCancel]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-navy-950/50 backdrop-blur-[2px]"
        onClick={() => !loading && onCancel?.()}
        aria-label="Close dialog"
      />
      <div role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" className="relative w-full max-w-md animate-fade-in rounded-2xl bg-white p-6 shadow-pop">
        <div className="flex gap-4">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-red-50 text-red-600">
            <AlertTriangle className="h-5 w-5" />
          </span>
          <div>
            <h2 id="confirm-title" className="text-base font-semibold text-slate-900">{title}</h2>
            {description && <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{description}</p>}
          </div>
        </div>
        <div className="mt-6 flex justify-end gap-2">
          <button type="button" className="fs-btn-secondary" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </button>
          <button
            type="button"
            className={tone === 'danger' ? 'fs-btn-danger' : 'fs-btn-primary'}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading && <Spinner className="h-4 w-4" />}
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
