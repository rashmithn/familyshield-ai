import { useEffect } from 'react';
import { X } from 'lucide-react';
import { scanService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import ErrorState from './ErrorState';
import LoadingState from './LoadingState';
import ScanResult from './ScanResult';

export default function ScanDetailModal({ scanId, initialScan, families = [], onClose, onChanged }) {
  const { data, loading, error, reload } = useFetch(
    () => (initialScan ? Promise.resolve(initialScan) : scanService.get(scanId)),
    [scanId, initialScan],
  );

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === 'Escape') onClose?.();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[60] flex justify-end">
      <button type="button" className="absolute inset-0 bg-navy-950/50 backdrop-blur-[2px]" onClick={onClose} aria-label="Close scan details" />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Scan details"
        className="relative h-full w-full max-w-2xl animate-slide-in overflow-y-auto bg-canvas p-4 shadow-pop fs-scroll sm:p-6"
      >
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-emerald-600">Scan report</p>
            <h2 className="mt-1 text-lg font-semibold text-slate-900">Result details</h2>
          </div>
          <button type="button" onClick={onClose} className="rounded-xl border border-line bg-white p-2 text-slate-500 transition hover:bg-slate-50" aria-label="Close">
            <X className="h-5 w-5" />
          </button>
        </div>

        {loading && <div className="fs-card"><LoadingState label="Fetching scan report…" /></div>}
        {error && !loading && <div className="fs-card"><ErrorState error={error} onRetry={reload} title="Could not load this scan" /></div>}
        {data && !loading && !error && (
          <ScanResult scan={data} families={families} onShared={onChanged} />
        )}
      </div>
    </div>
  );
}
