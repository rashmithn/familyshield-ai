import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { ProtectedRoute } from './context/AuthContext';
import AppShell from './components/AppShell';

const Landing = lazy(() => import('./pages/Landing'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const Overview = lazy(() => import('./pages/Overview'));
const MessageScanner = lazy(() => import('./pages/MessageScanner'));
const UrlScanner = lazy(() => import('./pages/UrlScanner'));
const Alerts = lazy(() => import('./pages/Alerts'));
const History = lazy(() => import('./pages/History'));
const Awareness = lazy(() => import('./pages/Awareness'));
const Settings = lazy(() => import('./pages/Settings'));
const NotFound = lazy(() => import('./pages/NotFound'));

function PageFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas">
      <div className="flex items-center gap-3 text-sm text-slate-500">
        <Loader2 className="h-5 w-5 animate-spin text-navy-700" />
        Loading…
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Suspense fallback={<PageFallback />}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route index element={<Overview />} />
          <Route path="scanner" element={<MessageScanner />} />
          <Route path="url-scanner" element={<UrlScanner />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="history" element={<History />} />
          <Route path="awareness" element={<Awareness />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
}
