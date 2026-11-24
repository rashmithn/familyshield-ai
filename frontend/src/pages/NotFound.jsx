import { Link } from 'react-router-dom';
import { ArrowLeft, Compass } from 'lucide-react';
import Logo from '../components/Logo';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <header className="px-6 py-6 sm:px-10"><Logo /></header>
      <main className="flex flex-1 flex-col items-center justify-center px-6 pb-20 text-center">
        <span className="grid h-14 w-14 place-items-center rounded-2xl bg-slate-100 text-slate-500">
          <Compass className="h-7 w-7" strokeWidth={1.7} />
        </span>
        <p className="mt-6 text-[11px] font-semibold uppercase tracking-[0.16em] text-emerald-600">404</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">We could not find that page</h1>
        <p className="mt-2 max-w-sm text-sm leading-relaxed text-slate-500">
          The link may have changed, or the page may no longer exist.
        </p>
        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Link to="/" className="fs-btn-primary"><ArrowLeft className="h-4 w-4" /> Back to home</Link>
          <Link to="/app" className="fs-btn-secondary">Go to my workspace</Link>
        </div>
      </main>
    </div>
  );
}
