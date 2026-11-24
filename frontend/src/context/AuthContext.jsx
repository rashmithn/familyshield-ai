import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { authService } from '../api/services';
import { clearSession, getStoredUser, getToken, setStoredUser, setToken } from '../api/client';
import { Loader2 } from 'lucide-react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser());
  const [loading, setLoading] = useState(() => Boolean(getToken()));
  const navigate = useNavigate();

  const updateUser = useCallback((next) => {
    setUser(next);
    setStoredUser(next);
  }, []);

  useEffect(() => {
    const onSessionCleared = () => setUser(null);
    window.addEventListener('fs:session-cleared', onSessionCleared);

    if (!getToken()) {
      setLoading(false);
      return () => window.removeEventListener('fs:session-cleared', onSessionCleared);
    }

    authService
      .me()
      .then(updateUser)
      .catch(() => {
        clearSession();
        setUser(null);
      })
      .finally(() => setLoading(false));

    return () => window.removeEventListener('fs:session-cleared', onSessionCleared);
  }, [updateUser]);

  const login = useCallback(
    async (credentials) => {
      const data = await authService.login(credentials);
      setToken(data.access_token);
      updateUser(data.user);
      return data.user;
    },
    [updateUser],
  );

  const register = useCallback(
    async (payload) => {
      const data = await authService.register(payload);
      setToken(data.access_token);
      updateUser(data.user);
      return data.user;
    },
    [updateUser],
  );

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    navigate('/login', { replace: true });
  }, [navigate]);

  const value = useMemo(
    () => ({ user, loading, login, register, logout, updateUser, isAuthenticated: Boolean(user) }),
    [user, loading, login, register, logout, updateUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>');
  return context;
}

export function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas">
        <div className="flex items-center gap-3 text-sm text-slate-500">
          <Loader2 className="h-5 w-5 animate-spin text-navy-700" />
          Loading your workspace…
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
