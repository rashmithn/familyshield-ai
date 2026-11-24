import { useState } from 'react';
import {
  AlertCircle,
  BellRing,
  CalendarCheck,
  CheckCircle2,
  ChevronRight,
  UsersRound,
} from 'lucide-react';
import { alertService, familyService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import PageHeader from '../components/PageHeader';
import RiskBadge from '../components/RiskBadge';
import ScanDetailModal from '../components/ScanDetailModal';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import AdvisoryNote from '../components/AdvisoryNote';
import { Spinner } from '../components/LoadingState';
import { formatDate, formatRelative, getErrorMessage, getRisk } from '../utils/format';

const FILTERS = [
  { value: 'all', label: 'All alerts' },
  { value: 'unread', label: 'Unread' },
  { value: 'reviewed', label: 'Reviewed' },
];

const SEVERITY_STYLE = {
  high: 'bg-red-50 text-red-700 ring-red-200',
  medium: 'bg-amber-50 text-amber-700 ring-amber-200',
  low: 'bg-slate-100 text-slate-600 ring-slate-200',
};

export default function Alerts() {
  const [status, setStatus] = useState('all');
  const { data, loading, error, reload } = useFetch(() => alertService.list({ status }), [status]);
  const { data: families } = useFetch(familyService.list, []);
  const [selected, setSelected] = useState(null);
  const [reviewingId, setReviewingId] = useState(null);
  const [actionError, setActionError] = useState('');

  const review = async (alert) => {
    setReviewingId(alert.id);
    setActionError('');
    try {
      await alertService.review(alert.id);
      reload();
    } catch (requestError) {
      setActionError(getErrorMessage(requestError, 'Could not mark that alert as reviewed.'));
    } finally {
      setReviewingId(null);
    }
  };

  const alerts = Array.isArray(data) ? data : [];

  return (
    <>
      <PageHeader
        eyebrow="Family alerts"
        title="Alerts for your family"
        description="Concerning results that were shared with a family group appear here, in one place."
      />

      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-xl border border-line bg-white p-1 shadow-sm" role="group" aria-label="Filter alerts">
          {FILTERS.map((filter) => (
            <button
              key={filter.value}
              type="button"
              onClick={() => {
                setStatus(filter.value);
                setActionError('');
              }}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
                status === filter.value ? 'bg-navy-900 text-white shadow-sm' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
              }`}
              aria-pressed={status === filter.value}
            >
              {filter.label}
            </button>
          ))}
        </div>
        <button type="button" onClick={reload} className="fs-btn-ghost text-xs">
          Refresh
        </button>
      </div>

      {actionError && (
        <div className="mb-5 flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 text-xs text-red-700" role="alert">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      {loading ? (
        <div className="fs-card"><LoadingState label="Loading alerts…" /></div>
      ) : error ? (
        <div className="fs-card"><ErrorState error={error} onRetry={reload} title="Could not load alerts" /></div>
      ) : alerts.length === 0 ? (
        <div className="fs-card">
          <EmptyState
            icon={BellRing}
            title={status === 'unread' ? 'No unread alerts' : status === 'reviewed' ? 'No reviewed alerts' : 'No family alerts yet'}
            description="When a scan is shared with your family and looks suspicious or high risk, an alert will show up here."
          />
        </div>
      ) : (
        <div className="space-y-3.5">
          {alerts.map((alert) => (
            <article key={alert.id} className="fs-card p-5 sm:p-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`fs-badge ${SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.low}`}>
                      {alert.severity ? `${alert.severity} severity` : 'Alert'}
                    </span>
                    <RiskBadge level={alert.risk_level} />
                    {alert.status === 'unread' ? (
                      <span className="fs-badge bg-navy-900/5 text-navy-700 ring-navy-900/10">Unread</span>
                    ) : (
                      <span className="fs-badge bg-slate-100 text-slate-500 ring-slate-200">Reviewed</span>
                    )}
                  </div>

                  <h2 className="mt-3 text-sm font-semibold text-slate-900">{alert.title}</h2>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-600">{alert.summary}</p>

                  <div className="mt-4 flex flex-wrap gap-x-5 gap-y-1.5 text-[11px] text-slate-400">
                    {alert.family_name && (
                      <span className="inline-flex items-center gap-1.5"><UsersRound className="h-3.5 w-3.5" /> {alert.family_name}</span>
                    )}
                    <span className="inline-flex items-center gap-1.5"><BellRing className="h-3.5 w-3.5" /> {formatRelative(alert.created_at)}</span>
                    {alert.reviewed_at && (
                      <span className="inline-flex items-center gap-1.5"><CalendarCheck className="h-3.5 w-3.5" /> Reviewed {formatDate(alert.reviewed_at)}</span>
                    )}
                  </div>
                </div>

                <div className="flex shrink-0 flex-wrap items-center gap-2 sm:w-[200px] sm:flex-col sm:items-stretch">
                  {alert.scan_id && (
                    <button
                      type="button"
                      className="fs-btn-secondary w-full"
                      onClick={() => setSelected({ scanId: alert.scan_id, scan: alert.scan || null })}
                    >
                      View scan <ChevronRight className="h-4 w-4" />
                    </button>
                  )}
                  {alert.status === 'unread' && (
                    <button
                      type="button"
                      className="fs-btn-primary w-full"
                      onClick={() => review(alert)}
                      disabled={reviewingId === alert.id}
                    >
                      {reviewingId === alert.id ? <Spinner className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
                      {reviewingId === alert.id ? 'Updating…' : 'Mark as reviewed'}
                    </button>
                  )}
                </div>
              </div>
              <p className="mt-4 border-t border-line pt-3 text-[11px] text-slate-400">
                {getRisk(alert.risk_level).label} result · Detection is advisory, not a guarantee.
              </p>
            </article>
          ))}
        </div>
      )}

      <AdvisoryNote className="mt-5" />

      {selected && (
        <ScanDetailModal
          scanId={selected.scanId}
          initialScan={selected.scan}
          families={families || []}
          onClose={() => setSelected(null)}
        />
      )}
    </>
  );
}
