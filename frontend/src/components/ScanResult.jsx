import { useState } from 'react';
import {
  ArrowRight,
  CheckCircle2,
  FileText,
  Link2,
  Send,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';
import { scanService } from '../api/services';
import AdvisoryNote from './AdvisoryNote';
import FamilySelect from './FamilySelect';
import RiskBadge from './RiskBadge';
import ScoreGauge from './ScoreGauge';
import { Spinner } from './LoadingState';
import {
  formatDate,
  formatDetailValue,
  getErrorMessage,
  humanizeKey,
  SEVERITY_STYLES,
  toPercent,
} from '../utils/format';

function DetailGrid({ details = {} }) {
  const entries = Object.entries(details || {});
  if (!entries.length) return null;
  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2">
      {entries.map(([key, value]) => (
        <div key={key} className="min-w-0 border-b border-line/70 pb-2.5">
          <dt className="text-[11px] font-medium uppercase tracking-wide text-slate-400">{humanizeKey(key)}</dt>
          <dd className="mt-0.5 break-words text-[13px] font-medium text-slate-700">{formatDetailValue(value)}</dd>
        </div>
      ))}
    </dl>
  );
}

export default function ScanResult({ scan, families = [], onShared, showShare = true }) {
  const [shareFamily, setShareFamily] = useState(() => {
    const matching = families.find((family) => family.id === scan?.family_id);
    return matching?.id || (families.length === 1 ? families[0].id : '');
  });
  const [sharing, setSharing] = useState(false);
  const [shared, setShared] = useState(false);
  const [shareError, setShareError] = useState('');

  if (!scan) return null;

  const confidence = Number(scan.confidence_score);
  const confidencePercent = Number.isFinite(confidence)
    ? Math.round(confidence <= 1 && confidence > 0 ? confidence * 100 : confidence)
    : null;

  const share = async () => {
    setSharing(true);
    setShareError('');
    try {
      await scanService.share(scan.id, shareFamily ? { family_id: shareFamily } : {});
      setShared(true);
      onShared?.();
    } catch (error) {
      setShareError(getErrorMessage(error));
    } finally {
      setSharing(false);
    }
  };

  return (
    <div className="animate-fade-in space-y-5">
      <div className="fs-card overflow-hidden">
        <div className="border-b border-line bg-gradient-to-r from-slate-50 to-white px-5 py-5 sm:px-6">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-center sm:text-left">
              <ScoreGauge score={scan.risk_score} level={scan.risk_level} />
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <RiskBadge level={scan.risk_level} />
                  <span className="fs-badge bg-slate-100 text-slate-600 ring-slate-200">
                    {scan.scan_type === 'url' ? <Link2 className="h-3 w-3" /> : <FileText className="h-3 w-3" />}
                    {scan.scan_type === 'url' ? 'Link' : 'Message'}
                  </span>
                </div>
                <h2 className="mt-3 text-lg font-semibold tracking-tight text-slate-900">
                  {scan.category || 'Analysis complete'}
                </h2>
                <p className="mt-1 text-xs text-slate-500">Checked {formatDate(scan.created_at, { dateStyle: 'medium', timeStyle: 'short' })}</p>
              </div>
            </div>

            {showShare && (
              <div className="w-full shrink-0 border-t border-line pt-4 sm:w-auto sm:border-l sm:border-t-0 sm:pl-6 sm:pt-0">
                <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">Keep your family informed</p>
                <div className="flex flex-col gap-2 sm:min-w-[230px]">
                  {families.length > 1 && (
                    <FamilySelect
                      families={families}
                      value={shareFamily}
                      onChange={setShareFamily}
                      id={`share-family-${scan.id}`}
                      label="Share with"
                      helper=""
                    />
                  )}
                  <button
                    type="button"
                    className="fs-btn-primary w-full"
                    onClick={share}
                    disabled={sharing || shared || families.length === 0}
                    title={families.length === 0 ? 'Create a family in Settings first' : undefined}
                  >
                    {sharing ? <Spinner className="h-4 w-4" /> : <Send className="h-4 w-4" />}
                    {shared ? 'Shared with family' : 'Share with family'}
                  </button>
                  {families.length === 0 && (
                    <p className="text-xs text-slate-400">Add a family in Settings to share this result.</p>
                  )}
                  {shareError && <p className="text-xs font-medium text-red-600">{shareError}</p>}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6 px-5 py-6 sm:px-6">
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-900">
              <Sparkles className="h-4 w-4 text-emerald-600" />
              What we found
            </h3>
            <p className="text-sm leading-relaxed text-slate-600">{scan.summary || 'No summary was provided for this scan.'}</p>

            {confidencePercent !== null && (
              <div className="mt-4 max-w-sm">
                <div className="mb-1.5 flex justify-between text-xs text-slate-500">
                  <span>Confidence in this assessment</span>
                  <span className="font-semibold text-slate-700 tabular-nums">{toPercent(scan.confidence_score)}</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-navy-700 transition-all duration-500"
                    style={{ width: `${Math.max(0, Math.min(100, confidencePercent))}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {Array.isArray(scan.indicators) && scan.indicators.length > 0 && (
            <div>
              <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
                <ShieldAlert className="h-4 w-4 text-amber-600" />
                Warning signs
              </h3>
              <ul className="space-y-2.5">
                {scan.indicators.map((indicator, index) => (
                  <li key={indicator?.code || `${indicator?.phrase}-${index}`} className="rounded-xl border border-line bg-slate-50/60 px-4 py-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-[13px] font-semibold text-slate-800">
                        {indicator?.label || indicator?.code || 'Indicator'}
                      </span>
                      {indicator?.severity && (
                        <span className={`fs-badge ${SEVERITY_STYLES[indicator.severity] || SEVERITY_STYLES.low}`}>
                          {indicator.severity}
                        </span>
                      )}
                    </div>
                    {indicator?.phrase && (
                      <p className="mt-1 text-xs text-slate-600">
                        Matched text: <span className="font-medium italic">“{indicator.phrase}”</span>
                      </p>
                    )}
                    {indicator?.description && (
                      <p className="mt-1 text-xs leading-relaxed text-slate-500">{indicator.description}</p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {scan.explanation && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-slate-900">Plain-language explanation</h3>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">{scan.explanation}</p>
              <AdvisoryNote compact className="mt-3" />
            </div>
          )}

          {Array.isArray(scan.recommended_actions) && scan.recommended_actions.length > 0 && (
            <div>
              <h3 className="mb-3 text-sm font-semibold text-slate-900">What to do next</h3>
              <ol className="space-y-2">
                {scan.recommended_actions.map((action, index) => (
                  <li key={`${action}-${index}`} className="flex items-start gap-2.5 text-sm text-slate-600">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" strokeWidth={1.9} />
                    <span>{action}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {scan.content_excerpt && (
            <div>
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-900">
                <FileText className="h-4 w-4 text-slate-400" />
                Checked content
              </h3>
              <div className="max-h-48 overflow-auto rounded-xl border border-line bg-slate-50 px-4 py-3 fs-scroll">
                <p className="whitespace-pre-wrap break-words text-[13px] leading-relaxed text-slate-600">
                  {scan.content_excerpt}
                </p>
              </div>
              <p className="mt-1.5 text-[11px] text-slate-400">Sensitive details are redacted from stored excerpts.</p>
            </div>
          )}

          {scan.details && Object.keys(scan.details).length > 0 && (
            <div>
              <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
                <ArrowRight className="h-4 w-4 text-slate-400" />
                {scan.scan_type === 'url' ? 'Link structure' : 'Scan details'}
              </h3>
              <DetailGrid details={scan.details} />
            </div>
          )}

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-line pt-4 text-[11px] text-slate-400">
            <span>Engine: <span className="font-medium text-slate-600">{scan.engine || 'not reported'}</span></span>
            {scan.family_id && <span>Filed under a family</span>}
            {scan.is_shared && <span>Shared with family</span>}
            <span>ID: <span className="font-mono">{scan.id}</span></span>
          </div>
        </div>
      </div>
    </div>
  );
}
