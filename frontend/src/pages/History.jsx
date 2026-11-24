import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { AlertCircle, ChevronLeft, ChevronRight, Eye, FilterX, History as HistoryIcon, Search, Trash2 } from 'lucide-react';
import { familyService, scanService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import PageHeader from '../components/PageHeader';
import RiskBadge from '../components/RiskBadge';
import ScanDetailModal from '../components/ScanDetailModal';
import ConfirmDialog from '../components/ConfirmDialog';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import { formatDateTime, getErrorMessage, getRisk } from '../utils/format';

const LIMIT = 10;

function initialParams(search) {
  const query = new URLSearchParams(search);
  return {
    risk_level: query.get('risk_level') || '',
    scan_type: query.get('scan_type') || '',
    search: query.get('q') || '',
    page: 0,
  };
}

export default function History() {
  const location = useLocation();
  const [filters, setFilters] = useState(() => initialParams(location.search));
  const [searchInput, setSearchInput] = useState(filters.search);
  const [selected, setSelected] = useState(null);
  const [toDelete, setToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [actionError, setActionError] = useState('');

  const offset = filters.page * LIMIT;
  const { data, loading, error, reload } = useFetch(
    () =>
      scanService.list({
        risk_level: filters.risk_level,
        scan_type: filters.scan_type,
        search: filters.search,
        limit: LIMIT,
        offset,
      }),
    [filters.risk_level, filters.scan_type, filters.search, offset],
  );
  const { data: families } = useFetch(familyService.list, []);

  useEffect(() => {
    const next = initialParams(location.search);
    setFilters(next);
    setSearchInput(next.search);
  }, [location.search]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setFilters((current) =>
        current.search === searchInput.trim() ? current : { ...current, search: searchInput.trim(), page: 0 },
      );
    }, 300);
    return () => clearTimeout(timeout);
  }, [searchInput]);

  const scans = Array.isArray(data?.items) ? data.items : [];
  const total = data?.total ?? 0;
  const page = data ? Math.floor((data.offset ?? offset) / (data.limit || LIMIT)) : filters.page;
  const pageCount = Math.max(1, Math.ceil(total / (data?.limit || LIMIT)));
  const hasFilters = Boolean(filters.risk_level || filters.scan_type || filters.search);

  useEffect(() => {
    if (data && page > 0 && offset >= total) {
      setFilters((current) => ({ ...current, page: 0 }));
    }
  }, [data, page, offset, total]);

  const clearFilters = () => {
    setFilters({ risk_level: '', scan_type: '', search: '', page: 0 });
    setSearchInput('');
  };

  const confirmDelete = async () => {
    if (!toDelete) return;
    setDeleting(true);
    setActionError('');
    try {
      await scanService.remove(toDelete.id);
      setToDelete(null);
      setSelected(null);
      reload();
    } catch (requestError) {
      setActionError(getErrorMessage(requestError, 'Could not delete that scan.'));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      <PageHeader
        eyebrow="Scan history"
        title="Past checks"
        description="Find a result again, open its full report, or remove a scan you no longer need."
      />

      <section className="fs-card mb-5 p-4 sm:p-5">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[1fr_180px_180px_auto]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search by category or content"
              aria-label="Search scans"
              className="fs-input pl-10 text-[13px]"
            />
          </div>
          <select
            value={filters.risk_level}
            onChange={(event) => setFilters((current) => ({ ...current, risk_level: event.target.value, page: 0 }))}
            aria-label="Filter by risk level"
            className="fs-input text-[13px]"
          >
            <option value="">All risk levels</option>
            <option value="safe">Safe</option>
            <option value="suspicious">Suspicious</option>
            <option value="high_risk">High risk</option>
          </select>
          <select
            value={filters.scan_type}
            onChange={(event) => setFilters((current) => ({ ...current, scan_type: event.target.value, page: 0 }))}
            aria-label="Filter by scan type"
            className="fs-input text-[13px]"
          >
            <option value="">All scan types</option>
            <option value="message">Messages</option>
            <option value="url">Links</option>
          </select>
          <button type="button" onClick={clearFilters} disabled={!hasFilters} className="fs-btn-secondary whitespace-nowrap">
            <FilterX className="h-4 w-4" /> Clear filters
          </button>
        </div>
      </section>

      {actionError && (
        <div className="mb-5 flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 text-xs text-red-700" role="alert">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{actionError}</span>
        </div>
      )}

      {loading ? (
        <div className="fs-card"><LoadingState label="Loading your scans…" /></div>
      ) : error ? (
        <div className="fs-card"><ErrorState error={error} onRetry={reload} title="Could not load scan history" /></div>
      ) : scans.length === 0 ? (
        <div className="fs-card">
          <EmptyState
            icon={HistoryIcon}
            title={hasFilters ? 'No scans match these filters' : 'No scans yet'}
            description={hasFilters ? 'Try a different search or clear the filters to see everything.' : 'Your message and link checks will be listed here.'}
            action={hasFilters ? <button type="button" className="fs-btn-secondary" onClick={clearFilters}>Clear filters</button> : undefined}
          />
        </div>
      ) : (
        <div className="fs-card overflow-hidden">
          <div className="overflow-x-auto fs-scroll">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="border-b border-line bg-slate-50/80">
                <tr className="text-[11px] uppercase tracking-wide text-slate-400">
                  <th className="px-5 py-3 font-medium">Result</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Risk</th>
                  <th className="px-4 py-3 font-medium">Shared</th>
                  <th className="px-4 py-3 font-medium">Checked</th>
                  <th className="px-5 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line/70">
                {scans.map((scan) => (
                  <tr key={scan.id} className="transition hover:bg-slate-50/60">
                    <td className="max-w-[280px] px-5 py-3.5">
                      <p className="truncate font-medium text-slate-800">{scan.category || 'Scan result'}</p>
                      <p className="mt-0.5 truncate text-xs text-slate-400" title={scan.content_excerpt || ''}>
                        {scan.content_excerpt || 'No excerpt available'}
                      </p>
                    </td>
                    <td className="px-4 py-3.5 text-xs capitalize text-slate-600">{scan.scan_type === 'url' ? 'Link' : 'Message'}</td>
                    <td className="px-4 py-3.5"><RiskBadge level={scan.risk_level} /></td>
                    <td className="px-4 py-3.5 text-xs text-slate-500">{scan.is_shared ? 'Yes' : 'No'}</td>
                    <td className="whitespace-nowrap px-4 py-3.5 text-xs text-slate-500">{formatDateTime(scan.created_at)}</td>
                    <td className="whitespace-nowrap px-5 py-3.5 text-right">
                      <button
                        type="button"
                        onClick={() => setSelected({ scanId: scan.id, scan })}
                        className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                        aria-label={`View ${getRisk(scan.risk_level).label} scan from ${formatDateTime(scan.created_at)}`}
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        type="button"
                        onClick={() => setToDelete(scan)}
                        className="rounded-lg p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-600"
                        aria-label="Delete scan"
                        title="Delete scan"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line px-5 py-3.5">
            <p className="text-xs text-slate-500">
              Showing <span className="font-semibold text-slate-700">{total === 0 ? 0 : offset + 1}–{Math.min(offset + scans.length, total)}</span> of{' '}
              <span className="font-semibold text-slate-700">{total}</span> scans
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="fs-btn-secondary px-3 py-1.5 text-xs"
                onClick={() => setFilters((current) => ({ ...current, page: Math.max(0, current.page - 1) }))}
                disabled={page <= 0 || loading}
              >
                <ChevronLeft className="h-4 w-4" /> Previous
              </button>
              <span className="px-1 text-xs text-slate-500 tabular-nums">Page {page + 1} of {pageCount}</span>
              <button
                type="button"
                className="fs-btn-secondary px-3 py-1.5 text-xs"
                onClick={() => setFilters((current) => ({ ...current, page: current.page + 1 }))}
                disabled={page + 1 >= pageCount || loading}
              >
                Next <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {selected && (
        <ScanDetailModal
          scanId={selected.scanId}
          initialScan={selected.scan}
          families={families || []}
          onClose={() => setSelected(null)}
          onChanged={reload}
        />
      )}

      <ConfirmDialog
        open={Boolean(toDelete)}
        title="Delete this scan?"
        description="This removes the scan from your history. Alerts already shared with your family will remain."
        confirmLabel={deleting ? 'Deleting…' : 'Delete scan'}
        loading={deleting}
        onCancel={() => setToDelete(null)}
        onConfirm={confirmDelete}
      />
    </>
  );
}
