import { Link } from 'react-router-dom';
import { CheckCircle2, LockKeyhole, MessageSquareText, ShieldCheck, UsersRound } from 'lucide-react';
import Logo from './Logo';

const POINTS = [
  { icon: MessageSquareText, text: 'Check suspicious messages before you reply' },
  { icon: LockKeyhole, text: 'Inspect links without opening them' },
  { icon: UsersRound, text: 'Alert the right people in your family' },
];

export default function AuthLayout({ title, subtitle, children, footer }) {
  return (
    <div className="flex min-h-screen bg-white">
      <div className="relative hidden w-[46%] flex-col overflow-hidden bg-navy-950 px-12 py-10 text-white lg:flex xl:px-16">
        <div className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-32 -left-20 h-80 w-80 rounded-full bg-sky-500/[0.07] blur-3xl" />
        <div className="relative">
          <Logo to="/" light />
        </div>

        <div className="relative my-auto max-w-md">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.05] px-3 py-1.5 text-[11px] font-medium text-emerald-300">
            <ShieldCheck className="h-3.5 w-3.5" />
            Built for families, not security experts
          </span>
          <h2 className="mt-6 text-3xl font-semibold leading-tight tracking-tight">
            A calmer way to handle suspicious messages.
          </h2>
          <p className="mt-4 text-sm leading-relaxed text-slate-400">
            FamilyShield AI helps you spot common scam patterns, understand what to do next, and keep everyone in the
            loop — in plain language.
          </p>

          <ul className="mt-8 space-y-3.5">
            {POINTS.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3 text-sm text-slate-300">
                <span className="grid h-8 w-8 place-items-center rounded-lg bg-white/[0.07] text-emerald-400">
                  <Icon className="h-4 w-4" strokeWidth={1.8} />
                </span>
                {text}
              </li>
            ))}
          </ul>
        </div>

        <div className="relative flex items-start gap-2 border-t border-white/10 pt-5 text-[11px] leading-relaxed text-slate-500">
          <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          Detection is advisory, not a guarantee. Always verify unusual requests independently.
        </div>
      </div>

      <div className="flex flex-1 flex-col px-5 py-6 sm:px-10 lg:px-14">
        <div className="flex justify-between lg:justify-end">
          <div className="lg:hidden"><Logo to="/" /></div>
          <Link to="/" className="text-xs font-medium text-slate-500 transition hover:text-slate-900">
            Back to home
          </Link>
        </div>

        <div className="mx-auto flex w-full max-w-[400px] flex-1 flex-col justify-center py-10">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{title}</h1>
          <p className="mt-2 text-sm leading-relaxed text-slate-500">{subtitle}</p>
          <div className="mt-8">{children}</div>
          <div className="mt-8 text-center text-xs text-slate-500">{footer}</div>
        </div>
      </div>
    </div>
  );
}
