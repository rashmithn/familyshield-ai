import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  FileText,
  History,
  RotateCcw,
  ScanLine,
  ShieldCheck,
  UploadCloud,
} from 'lucide-react';
import { familyService, scanService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import PageHeader from '../components/PageHeader';
import FamilySelect from '../components/FamilySelect';
import ScanResult from '../components/ScanResult';
import AdvisoryNote from '../components/AdvisoryNote';
import { Spinner } from '../components/LoadingState';
import { getErrorMessage } from '../utils/format';

const MAX_CHARS = 20000;

const EXAMPLES = [
  {
    id: 'upi',
    label: 'UPI payment request',
    text:
      'URGENT: Your UPI collect request for Rs 4,999 is pending. Approve it now to avoid a penalty on your account. Share the OTP sent to your phone with our support executive to confirm. Do not call the bank.',
  },
  {
    id: 'otp',
    label: 'OTP / bank alert',
    text:
      'Dear customer, your bank account has been blocked due to suspicious activity. To restore access, reply with your OTP, card number and PIN within 10 minutes. Our manager will help you immediately.',
  },
  {
    id: 'delivery',
    label: 'Delivery fee message',
    text:
      'Your parcel could not be delivered because the delivery charge was not paid. Pay a small fee of Rs 49 using the link below within 2 hours or your package will be returned. Reply with your card details to proceed.',
  },
];

export default function MessageScanner() {
  const { data: families } = useFetch(familyService.list, []);
  const [text, setText] = useState('');
  const [familyId, setFamilyId] = useState('');
  const [fileName, setFileName] = useState('');
  const [fileError, setFileError] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [scanning, setScanning] = useState(false);
  const fileRef = useRef(null);

  const onPickFile = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setFileError('');
    const extension = file.name.split('.').pop()?.toLowerCase();
    if (!['txt', 'eml'].includes(extension)) {
      setFileError('Please choose a .txt or .eml file.');
      event.target.value = '';
      return;
    }
    try {
      const contents = await file.text();
      if (contents.length > MAX_CHARS) {
        setFileError(`That file has ${contents.length.toLocaleString('en-IN')} characters. The limit is 20,000.`);
        event.target.value = '';
        return;
      }
      setText(contents);
      setFileName(file.name);
      setResult(null);
    } catch {
      setFileError('We could not read that file. Please try again or paste the text instead.');
    }
    event.target.value = '';
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    const trimmed = text.trim();
    if (!trimmed) {
      setError('Paste a message or choose a file first.');
      return;
    }
    if (trimmed.length > MAX_CHARS) {
      setError(`Please keep the message under ${MAX_CHARS.toLocaleString('en-IN')} characters.`);
      return;
    }

    setScanning(true);
    setError('');
    setResult(null);
    try {
      const scan = await scanService.scanMessage({ text: trimmed, family_id: familyId || undefined });
      setResult(scan);
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'We could not check that message. Please try again.'));
    } finally {
      setScanning(false);
    }
  };

  const reset = () => {
    setText('');
    setFamilyId('');
    setFileName('');
    setFileError('');
    setError('');
    setResult(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  return (
    <>
      <PageHeader
        eyebrow="Message scanner"
        title="Check a suspicious message"
        description="Paste the message exactly as you received it. We will point out common warning signs and suggest what to do next."
        actions={
          <Link to="/app/history?scan_type=message" className="fs-btn-secondary">
            <History className="h-4 w-4" /> Message history
          </Link>
        }
      />

      <div className="grid gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="fs-card p-5 sm:p-6">
          <form onSubmit={onSubmit} className="space-y-5">
            <div>
              <div className="mb-1.5 flex flex-wrap items-center justify-between gap-2">
                <label htmlFor="message-text" className="fs-label mb-0">Message text</label>
                <span className={`text-[11px] tabular-nums ${text.length > MAX_CHARS * 0.95 ? 'text-amber-600' : 'text-slate-400'}`}>
                  {text.length.toLocaleString('en-IN')} / {MAX_CHARS.toLocaleString('en-IN')}
                </span>
              </div>
              <textarea
                id="message-text"
                className="fs-input min-h-[220px] resize-y leading-relaxed"
                value={text}
                maxLength={MAX_CHARS}
                onChange={(event) => {
                  setText(event.target.value);
                  if (fileName) setFileName('');
                  setError('');
                }}
                placeholder="Paste the message here, including any links or phone numbers…"
              />
              <p className="mt-1.5 text-[11px] leading-relaxed text-slate-400">
                Do not include real passwords or one-time codes. Sensitive details are redacted from stored excerpts.
              </p>
            </div>

            <div>
              <label htmlFor="message-file" className="fs-label">Or upload a file</label>
              <label
                htmlFor="message-file"
                className="flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-slate-300 bg-slate-50/60 px-4 py-3.5 transition hover:border-emerald-400 hover:bg-emerald-50/40"
              >
                <UploadCloud className="h-5 w-5 shrink-0 text-slate-500" strokeWidth={1.8} />
                <span className="min-w-0">
                  <span className="block text-[13px] font-medium text-slate-700">
                    {fileName || 'Choose a .txt or .eml file'}
                  </span>
                  <span className="block text-[11px] text-slate-400">Read on your device — up to 20,000 characters</span>
                </span>
              </label>
              <input
                ref={fileRef}
                id="message-file"
                type="file"
                accept=".txt,.eml,text/plain,message/rfc822"
                onChange={onPickFile}
                className="sr-only"
              />
              {fileError && <p className="mt-2 text-xs font-medium text-red-600">{fileError}</p>}
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
                {scanning ? 'Checking message…' : 'Check this message'}
              </button>
              {(text || result) && (
                <button type="button" className="fs-btn-secondary" onClick={reset} disabled={scanning}>
                  <RotateCcw className="h-4 w-4" /> Clear
                </button>
              )}
            </div>
          </form>

          <div className="mt-7 border-t border-line pt-5">
            <div className="mb-3 flex items-center gap-2">
              <FileText className="h-4 w-4 text-slate-400" />
              <p className="text-xs font-semibold text-slate-700">Try an example</p>
            </div>
            <div className="flex flex-wrap gap-2">
              {EXAMPLES.map((example) => (
                <button
                  key={example.id}
                  type="button"
                  className="rounded-lg border border-line bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
                  onClick={() => {
                    setText(example.text);
                    setFileName('');
                    setFileError('');
                    setError('');
                    setResult(null);
                  }}
                >
                  {example.label}
                </button>
              ))}
            </div>
            <p className="mt-2 text-[11px] text-slate-400">Examples are fictional practice messages.</p>
          </div>
        </section>

        <div>
          {scanning && (
            <div className="fs-card flex min-h-[300px] flex-col items-center justify-center gap-3">
              <Spinner className="h-6 w-6 text-navy-700" />
              <p className="text-sm font-medium text-slate-600">Looking for warning signs…</p>
              <p className="text-xs text-slate-400">This usually takes a few seconds.</p>
            </div>
          )}

          {!scanning && result && (
            <>
              <ScanResult scan={result} families={families || []} />
              <div className="mt-4 flex justify-end">
                <button type="button" className="fs-btn-secondary" onClick={reset}>
                  <ScanLine className="h-4 w-4" /> Check another message
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
                Add a message on the left and we will show the risk level, the clues we noticed, and practical next steps.
              </p>
              <AdvisoryNote compact className="mt-5" />
            </div>
          )}
        </div>
      </div>
    </>
  );
}
