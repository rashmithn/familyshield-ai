import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowRight, CheckCircle2, Eye, EyeOff, LockKeyhole, Mail, UserRound } from 'lucide-react';
import AuthLayout from '../components/AuthLayout';
import { Spinner } from '../components/LoadingState';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/format';

const EMPTY = { full_name: '', email: '', password: '', confirm: '' };

export default function Register() {
  const { register, user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/app';

  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [apiError, setApiError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (!authLoading && user) navigate(from, { replace: true });
  }, [authLoading, user, from, navigate]);

  const update = (field) => (event) => {
    setForm((current) => ({ ...current, [field]: event.target.value }));
    setErrors((current) => ({ ...current, [field]: '' }));
    setApiError('');
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    const nextErrors = {};
    if (!form.full_name.trim()) nextErrors.full_name = 'Enter your name.';
    if (!form.email.trim()) nextErrors.email = 'Enter your email address.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) nextErrors.email = 'Enter a valid email address.';
    if (!form.password) nextErrors.password = 'Choose a password.';
    else if (form.password.length < 8) nextErrors.password = 'Use at least 8 characters.';
    if (!form.confirm) nextErrors.confirm = 'Confirm your password.';
    else if (form.confirm !== form.password) nextErrors.confirm = 'Passwords do not match.';

    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setSubmitting(true);
    setApiError('');
    try {
      await register({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        password: form.password,
      });
      navigate(from, { replace: true });
    } catch (error) {
      setApiError(getErrorMessage(error, 'We could not create your account. Please try again.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start checking suspicious messages and keep your family in the loop."
      footer={
        <>
          Already have an account? <Link to="/login" className="font-semibold text-navy-800 hover:underline">Sign in</Link>
        </>
      }
    >
      <form onSubmit={onSubmit} noValidate className="space-y-4">
        {apiError && (
          <div className="flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 text-sm text-red-700 animate-fade-in" role="alert">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{apiError}</span>
          </div>
        )}

        <div>
          <label htmlFor="full_name" className="fs-label">Your name</label>
          <div className="relative">
            <UserRound className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              id="full_name"
              type="text"
              autoComplete="name"
              value={form.full_name}
              onChange={update('full_name')}
              placeholder="e.g. Ravi Kumar"
              aria-invalid={Boolean(errors.full_name)}
              className={`fs-input pl-10 ${errors.full_name ? 'border-red-300 focus:border-red-400 focus:ring-red-500/10' : ''}`}
            />
          </div>
          {errors.full_name && <p className="mt-1.5 text-xs font-medium text-red-600">{errors.full_name}</p>}
        </div>

        <div>
          <label htmlFor="email" className="fs-label">Email address</label>
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={update('email')}
              placeholder="you@example.com"
              aria-invalid={Boolean(errors.email)}
              className={`fs-input pl-10 ${errors.email ? 'border-red-300 focus:border-red-400 focus:ring-red-500/10' : ''}`}
            />
          </div>
          {errors.email && <p className="mt-1.5 text-xs font-medium text-red-600">{errors.email}</p>}
        </div>

        <div>
          <label htmlFor="password" className="fs-label">Password</label>
          <div className="relative">
            <LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              value={form.password}
              onChange={update('password')}
              placeholder="At least 8 characters"
              aria-invalid={Boolean(errors.password)}
              className={`fs-input pl-10 pr-11 ${errors.password ? 'border-red-300 focus:border-red-400 focus:ring-red-500/10' : ''}`}
            />
            <button
              type="button"
              onClick={() => setShowPassword((value) => !value)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-slate-400 transition hover:text-slate-700"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && <p className="mt-1.5 text-xs font-medium text-red-600">{errors.password}</p>}
        </div>

        <div>
          <label htmlFor="confirm" className="fs-label">Confirm password</label>
          <div className="relative">
            <CheckCircle2 className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              id="confirm"
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              value={form.confirm}
              onChange={update('confirm')}
              placeholder="Repeat your password"
              aria-invalid={Boolean(errors.confirm)}
              className={`fs-input pl-10 ${errors.confirm ? 'border-red-300 focus:border-red-400 focus:ring-red-500/10' : ''}`}
            />
          </div>
          {errors.confirm && <p className="mt-1.5 text-xs font-medium text-red-600">{errors.confirm}</p>}
        </div>

        <button type="submit" className="fs-btn-primary w-full py-3" disabled={submitting || authLoading}>
          {submitting ? <Spinner className="h-4 w-4" /> : null}
          {submitting ? 'Creating account…' : 'Create account'}
          {!submitting && <ArrowRight className="h-4 w-4" />}
        </button>

        <p className="text-center text-[11px] leading-relaxed text-slate-400">
          Detection is advisory, not a guarantee of safety.
        </p>
      </form>
    </AuthLayout>
  );
}
