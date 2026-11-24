import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import AdvisoryNote from './AdvisoryNote';
import { useAuth } from '../context/AuthContext';

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user } = useAuth();

  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} user={user} />
      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-navy-950/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-label="Close navigation"
        />
      )}

      <div className="lg:pl-[268px]">
        <Topbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <Outlet />
          <div className="mt-10 border-t border-line pt-5">
            <AdvisoryNote compact />
          </div>
        </main>
      </div>
    </div>
  );
}
