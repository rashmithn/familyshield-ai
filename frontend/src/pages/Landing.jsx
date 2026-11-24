import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BellRing,
  Check,
  FileSearch,
  GraduationCap,
  Link2,
  LockKeyhole,
  MessageSquareText,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  UsersRound,
} from 'lucide-react';
import Logo from '../components/Logo';
import AdvisoryNote from '../components/AdvisoryNote';

const FEATURES = [
  {
    icon: MessageSquareText,
    title: 'Message scanner',
    text: 'Paste a suspicious message or upload a text file. See the warning signs in plain language, with clear next steps.',
  },
  {
    icon: Link2,
    title: 'Link scanner',
    text: 'Check a link for risky patterns without opening it. We analyze it on our servers — your browser never visits it.',
  },
  {
    icon: BellRing,
    title: 'Family alerts',
    text: 'Share a concerning result with your family so the right person sees it, without forwarding the original message.',
  },
  {
    icon: GraduationCap,
    title: 'Scam awareness',
    text: 'Short, practical guides to common scams, with checklists you can actually use with the people you care about.',
  },
];

const STEPS = [
  {
    icon: FileSearch,
    title: 'Share what you saw',
    text: 'Paste the message or link into the scanner. Nothing needs to be opened or clicked.',
  },
  {
    icon: ScanSearch,
    title: 'Get a clear explanation',
    text: 'We look for known scam patterns and explain what stands out — and what to do about it.',
  },
  {
    icon: UsersRound,
    title: 'Bring in your family',
    text: 'When something looks concerning, send a private alert to the family group you choose.',
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <header className="sticky top-0 z-40 border-b border-line/80 bg-white/90 backdrop-blur-md">
        <div className="mx-auto flex h-[68px] max-w-6xl items-center justify-between px-5 sm:px-8">
          <Logo />
          <nav className="hidden items-center gap-7 text-sm text-slate-600 md:flex" aria-label="Primary">
            <a href="#how-it-works" className="transition hover:text-slate-900">How it works</a>
            <a href="#features" className="transition hover:text-slate-900">Features</a>
            <Link to="/app/awareness" className="transition hover:text-slate-900">Awareness</Link>
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/login" className="fs-btn-ghost hidden sm:inline-flex">Sign in</Link>
            <Link to="/register" className="fs-btn-primary px-3.5 py-2 sm:px-4 sm:py-2.5">
              Get started <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden border-b border-line bg-gradient-to-b from-slate-50 via-white to-white">
          <div className="pointer-events-none absolute -right-40 -top-40 h-[420px] w-[420px] rounded-full bg-emerald-500/[0.07] blur-3xl" />
          <div className="mx-auto grid max-w-6xl gap-12 px-5 py-16 sm:px-8 lg:grid-cols-[1.08fr_0.92fr] lg:py-24">
            <div className="relative">
              <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-[11px] font-semibold text-emerald-700">
                <ShieldCheck className="h-3.5 w-3.5" />
                For parents and families
              </span>
              <h1 className="mt-6 max-w-xl text-4xl font-semibold leading-[1.12] tracking-tight text-navy-900 sm:text-[44px]">
                Check before you click — and help your family stay a step ahead.
              </h1>
              <p className="mt-5 max-w-xl text-[15px] leading-relaxed text-slate-600">
                Suspicious messages are hard to judge when they look urgent. FamilyShield AI helps you spot common
                scam patterns, understand the risk, and share what you found — without opening a dangerous link.
              </p>
              <div className="mt-8 flex flex-wrap items-center gap-3">
                <Link to="/app/scanner" className="fs-btn-primary px-5 py-3 text-[13px]">
                  <ScanSearch className="h-4 w-4" />
                  Scan a suspicious message
                </Link>
                <a href="#how-it-works" className="fs-btn-secondary px-5 py-3 text-[13px]">
                  See how it works
                  <ArrowRight className="h-4 w-4" />
                </a>
              </div>
              <div className="mt-7 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
                <span className="inline-flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-600" /> No link is opened in your browser</span>
                <span className="inline-flex items-center gap-1.5"><Check className="h-3.5 w-3.5 text-emerald-600" /> Explanations in plain language</span>
              </div>
            </div>

            <div className="relative">
              <div className="fs-card relative overflow-hidden p-6 sm:p-7">
                <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-emerald-400 via-emerald-500 to-navy-800" />
                <div className="flex items-center gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-50 text-emerald-600">
                    <Sparkles className="h-5 w-5" strokeWidth={1.8} />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">One calm place for every check</p>
                    <p className="text-xs text-slate-500">Designed for everyday decisions</p>
                  </div>
                </div>
                <div className="mt-6 space-y-3">
                  {[
                    { icon: MessageSquareText, title: 'A message that feels off', text: 'Understand the warning signs and what to do next.' },
                    { icon: LockKeyhole, title: 'A link you do not trust', text: 'See structural clues without visiting the page.' },
                    { icon: BellRing, title: 'A heads-up for your family', text: 'Send a short, safe alert when it matters.' },
                  ].map(({ icon: Icon, title, text }) => (
                    <div key={title} className="flex gap-3 rounded-xl border border-line bg-slate-50/60 p-3.5">
                      <Icon className="mt-0.5 h-[18px] w-[18px] shrink-0 text-navy-700" strokeWidth={1.8} />
                      <div>
                        <p className="text-[13px] font-semibold text-slate-800">{title}</p>
                        <p className="mt-0.5 text-xs leading-relaxed text-slate-500">{text}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 rounded-xl bg-navy-950 px-4 py-3.5">
                  <p className="text-[11px] leading-relaxed text-slate-400">
                    <span className="font-semibold text-emerald-400">Advisory by design.</span> We explain what looks
                    unusual — we never promise that anything is completely safe.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="scroll-mt-20 border-b border-line bg-white py-16 sm:py-20">
          <div className="mx-auto max-w-6xl px-5 sm:px-8">
            <div className="max-w-xl">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-emerald-600">How it works</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">Three simple steps, no technical skills needed</h2>
            </div>
            <div className="mt-10 grid gap-5 md:grid-cols-3">
              {STEPS.map(({ icon: Icon, title, text }, index) => (
                <div key={title} className="fs-card p-6">
                  <div className="flex items-center justify-between">
                    <span className="grid h-10 w-10 place-items-center rounded-xl bg-navy-900/[0.05] text-navy-700">
                      <Icon className="h-5 w-5" strokeWidth={1.8} />
                    </span>
                    <span className="text-xs font-semibold text-slate-300">0{index + 1}</span>
                  </div>
                  <h3 className="mt-5 text-sm font-semibold text-slate-900">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-500">{text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="features" className="scroll-mt-20 bg-canvas py-16 sm:py-20">
          <div className="mx-auto max-w-6xl px-5 sm:px-8">
            <div className="max-w-xl">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-emerald-600">What you get</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">Practical help, right when you need it</h2>
            </div>
            <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {FEATURES.map(({ icon: Icon, title, text }) => (
                <div key={title} className="fs-card p-6 transition hover:-translate-y-0.5 hover:shadow-md">
                  <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-50 text-emerald-700">
                    <Icon className="h-5 w-5" strokeWidth={1.8} />
                  </span>
                  <h3 className="mt-5 text-sm font-semibold text-slate-900">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-500">{text}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-y border-line bg-white py-16">
          <div className="mx-auto grid max-w-6xl gap-10 px-5 sm:px-8 lg:grid-cols-2 lg:items-center">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-emerald-600">Trust &amp; privacy</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">Careful with your information</h2>
              <div className="mt-6 space-y-4">
                {[
                  'Links are analyzed on our servers. We do not open them in your browser.',
                  'Codes, card numbers, and email addresses are redacted from stored excerpts.',
                  'Family data stays inside the family group you choose.',
                ].map((text) => (
                  <div key={text} className="flex items-start gap-3 text-sm leading-relaxed text-slate-600">
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                    {text}
                  </div>
                ))}
              </div>
            </div>
            <AdvisoryNote />
          </div>
        </section>

        <section className="bg-navy-950 py-16">
          <div className="mx-auto flex max-w-6xl flex-col items-start justify-between gap-6 px-5 sm:px-8 md:flex-row md:items-center">
            <div>
              <h2 className="text-xl font-semibold tracking-tight text-white">Have a message that does not feel right?</h2>
              <p className="mt-2 text-sm text-slate-400">Take a minute to check it before you reply or click.</p>
            </div>
            <Link to="/app/scanner" className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-navy-900 transition hover:bg-slate-100">
              <ScanSearch className="h-4 w-4" />
              Scan a suspicious message
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t border-line bg-white py-10">
        <div className="mx-auto max-w-6xl px-5 sm:px-8">
          <div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <Logo />
              <p className="mt-3 max-w-xs text-xs leading-relaxed text-slate-500">
                Simple tools that help families recognize scams and respond with confidence. Detection is advisory,
                not a guarantee.
              </p>
            </div>
            <nav className="flex flex-wrap gap-x-8 gap-y-3 text-xs text-slate-500" aria-label="Footer">
              <Link to="/app/scanner" className="transition hover:text-slate-900">Message scanner</Link>
              <Link to="/app/url-scanner" className="transition hover:text-slate-900">Link scanner</Link>
              <Link to="/app/alerts" className="transition hover:text-slate-900">Family alerts</Link>
              <Link to="/app/awareness" className="transition hover:text-slate-900">Scam awareness</Link>
              <Link to="/login" className="transition hover:text-slate-900">Sign in</Link>
            </nav>
          </div>
          <p className="mt-8 border-t border-line pt-5 text-[11px] text-slate-400">© {new Date().getFullYear()} FamilyShield AI.</p>
        </div>
      </footer>
    </div>
  );
}
