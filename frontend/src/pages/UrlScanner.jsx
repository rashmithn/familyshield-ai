import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, ExternalLink, History, Link2, RotateCcw, ScanLine, ShieldCheck } from 'lucide-react';
import { familyService, scanService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import PageHeader from '../components/PageHeader';
import FamilySelect from '../components/FamilySelect';
import ScanResult from '../components/ScanResult';
import AdvisoryNote from '../components/AdvisoryNote';
import { Spinner } from '../components/LoadingState';
import { getErrorMessage } from '../utils/format';

const MAX_CHARS = 2048;

function normalizeUrl(raw) {
  const trimmed = raw.trim();
  if (!trimmed) return '';
  return /^[a-zA-Z][a-zA-Z\d+.-]*:\/\//.test(trimmed) ? trimmed : `https://${trimmed}`;
}

export default function UrlScanner() {
  const { data: families } = useFetch(familyService.list, []);
  const [url, setUrl] = useState('');
  const [familyId, setFamilyId] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [scanning, setScanning] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    const normalized = normalizeUrl(url);
    if (!normalized) {
      setError('Enter the link you want to check.');
      return;
    }
    if (normalized.length > MAX_CHARS) {
      setError(`Please keep the link under ${MAX_CHARS} characters.`);
      return;
    }
    let parsed;
    try {
      parsed = new URL(normalized);
    } catch {
      setError('That does not look like a valid link. Include an address such as example.com.');
      return;
    }
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      setError('We can only check http and https links.');
      return;
    }

    setUrl(normalized);
    setScanning(true);
    setError('');
    setResult(null);
    try {
      const scan = await scanService.scanUrl({ url: normalized, family_id: familyId || undefined });
      setResult(scan);
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'We could not check that link. Please try again.'));
    } finally {
      setScanning(false);
    }
  };

  const reset = () => {
    setUrl('');
    setFamilyId('');
    setError('');
    setResult(null);
  };

  return (
    <>
      <PageHeader
        eyebrow="Link scanner"
        title="Check a link safely"
        description="Copy the link into the box below. We will examine its structure and known warning signs for you."
        actions={
          <Link to="/app/history?scan_type=url" className="fs-btn-secondary">
            <History className="h-4 w-4" /> Link history
          </Link>
        }
      />

      <div className="mb-5 flex items-start gap-3 rounded-2xl border border-emerald-200 bg-emerald-50/70 px-4 py-3.5">
        <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-700" strokeWidth={1.8} />
        <div>
          <p className="text-[13px] font-semibold text-emerald-900">We analyze the link on our servers — we never open it in your browser.</p>
          <p className="mt-1 text-xs leading-relaxed text-emerald-800/70">
            Nothing is clicked or loaded from the destination page. If a link asks for a password or payment, do not
            enter those details.
          </p>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="fs-card p-5 sm:p-6">
          <form onSubmit={onSubmit} className="space-y-5">
            <div>
              <label htmlFor="url-input" className="fs-label">Link to check</label>
              <div className="relative">
                <Link2 className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  id="url-input"
                  type="text"
                  inputMode="url"
                  autoComplete="off"
                  spellCheck={false}
                  value={url}
                  maxLength={MAX_CHARS}
                  onChange={(event) => {
                    setUrl(event.target.value);
                    setError('');
                  }}
                  placeholder="example.com/offer or https://example.com/offer"
                  className="fs-input pl-10"
                />
              </div>
              <p className="mt-1.5 text-[11px] leading-relaxed text-slate-400">
                If you leave out http:// or https://, we will assume https://.
              </p>
            </div>

            <FamilySelect families={families || []} value={familyId} onChange={setFamilyId} />

            {error && (
              <div className="flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 text-xs leading-relaxed text-red-700" role="alert">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex flex-wrap gap-2 pt-1">
              <button type="submit" className="fs-btn-primary flex-1 sm:flex-none" disabled={scanning}>
                {scanning ? <Spinner className="h-4 w-4" /> : <ScanLine className="h-4 w-4" />}
                {scanning ? 'Checking link…' : 'Check this link'}
              </button>
              {(url || result) && (
                <button type="button" className="fs-btn-secondary" onClick={reset} disabled={scanning}>
                  <RotateCcw className="h-4 w-4" /> Clear
                </button>
              )}
            </div>
          </form>

          <div className="mt-7 rounded-xl border border-line bg-slate-50/60 p-4">
            <p className="text-xs font-semibold text-slate-700">What we look at</p>
            <ul className="mt-2.5 space-y-2 text-xs leading-relaxed text-slate-500">
              <li>• The shape of the web address and its domain</li>
              <li>• Patterns commonly used by scam pages</li>
              <li>• How the result compares with known risky links</li>
            </ul>
            <p className="mt-3 flex items-start gap-1.5 text-[11px] text-slate-400">
              <ExternalLink className="mt-0.5 h-3 w-3 shrink-0" />
              A normal-looking link can still be unsafe — always double-check before entering information.
            </p>
          </div>
        </section>

        <div>
          {scanning && (
            <div className="fs-card flex min-h-[300px] flex-col items-center justify-center gap-3">
              <Spinner className="h-6 w-6 text-navy-700" />
              <p className="text-sm font-medium text-slate-600">Examining the link…</p>
              <p className="text-xs text-slate-400">No page is being opened.</p>
            </div>
          )}

          {!scanning && result && (
            <>
              <ScanResult scan={result} families={families || []} />
              <div className="mt-4 flex justify-end">
                <button type="button" className="fs-btn-secondary" onClick={reset}>
                  <ScanLine className="h-4 w-4" /> Check another link
                </button>
              </div>
            </>
          )}

          {!scanning && !result && (
            <div className="fs-card flex min-h-[300px] flex-col items-center justify-center p-8 text-center">
              <span className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-emerald-50 text-emerald-600">
                <ShieldCheck className="h-6 w-6" strokeWidth={1.8} />
              </span>
              <h2 className="text-sm font-semibold text-slate-900">Your report will appear here</h2>
              <p className="mt-2 max-w-sm text-sm leading-relaxed text-slate-500">
                Add a link and you will see the risk level, the details we checked, and what to do next.
              </p>
              <AdvisoryNote compact className="mt-5" />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
