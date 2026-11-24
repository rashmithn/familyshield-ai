import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { AlertCircle, ArrowRight, Eye, EyeOff, LockKeyhole, Mail } from 'lucide-react';
import AuthLayout from '../components/AuthLayout';
import { Spinner } from '../components/LoadingState';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/format';

const EMPTY = { email: '', password: '' };

export default function Login() {
  const { login, user, loading: authLoading } = useAuth();
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
    if (!form.email.trim()) nextErrors.email = 'Enter your email address.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) nextErrors.email = 'Enter a valid email address.';
    if (!form.password) nextErrors.password = 'Enter your password.';

    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    setSubmitting(true);
    setApiError('');
    try {
      await login({ email: form.email.trim(), password: form.password });
      navigate(from, { replace: true });
    } catch (error) {
      setApiError(getErrorMessage(error, 'We could not sign you in. Please try again.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to check messages, review alerts, and look after your family."
      footer={
        <>
          New to FamilyShield AI? <Link to="/register" className="font-semibold text-navy-800 hover:underline">Create an account</Link>
        </>
      }
    >
      <form onSubmit={onSubmit} noValidate className="space-y-5">
        {apiError && (
          <div className="flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 text-sm text-red-700 animate-fade-in" role="alert">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{apiError}</span>
          </div>
        )}

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
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="fs-label">Password</label>
          </div>
          <div className="relative">
            <LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              value={form.password}
              onChange={update('password')}
              placeholder="Your password"
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

        <button type="submit" className="fs-btn-primary w-full py-3" disabled={submitting || authLoading}>
          {submitting ? <Spinner className="h-4 w-4" /> : null}
          {submitting ? 'Signing in…' : 'Sign in'}
          {!submitting && <ArrowRight className="h-4 w-4" />}
        </button>

        <p className="text-center text-[11px] leading-relaxed text-slate-400">
          Detection is advisory, not a guarantee of safety.
        </p>
      </form>
    </AuthLayout>
  );
}
