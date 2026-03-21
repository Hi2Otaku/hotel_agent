import { Outlet, useLocation } from 'react-router';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

const pageTitles: Record<string, string> = {
  '/': 'Overview',
  '/reservations': 'Reservations',
  '/check-in-out': 'Check-in / Check-out',
  '/room-status': 'Room Status',
  '/guests': 'Guests',
  '/reports': 'Reports',
};

export function AppLayout() {
  const location = useLocation();
  const title = pageTitles[location.pathname] ?? 'Dashboard';

  return (
    <div className="flex h-screen bg-[#0F172A]">
      {/* Skip to content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-[#0F766E] focus:px-4 focus:py-2 focus:text-white"
      >
        Skip to content
      </a>

      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar title={title} />

        <main
          id="main-content"
          className="flex-1 overflow-y-auto bg-[#0F172A] p-8"
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}
