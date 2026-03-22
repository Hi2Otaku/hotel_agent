import { lazy, Suspense, type ReactNode } from 'react';
import { Routes, Route, Navigate } from 'react-router';
import { useAuthStore } from '@/stores/authStore';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import LoginPage from '@/pages/LoginPage';

const OverviewPage = lazy(() => import('@/pages/OverviewPage'));
const ReservationsPage = lazy(() => import('@/pages/ReservationsPage'));
const CheckInOutPage = lazy(() => import('@/pages/CheckInOutPage'));
const RoomStatusPage = lazy(() => import('@/pages/RoomStatusPage'));
const GuestProfilePage = lazy(() => import('@/pages/GuestProfilePage'));
const ReportsPage = lazy(() => import('@/pages/ReportsPage'));
const ChatPage = lazy(() => import('@/features/chat/ChatPage'));

function ProtectedRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Suspense fallback={<LoadingSpinner />}><OverviewPage /></Suspense>} />
        <Route path="reservations" element={<Suspense fallback={<LoadingSpinner />}><ReservationsPage /></Suspense>} />
        <Route path="check-in-out" element={<Suspense fallback={<LoadingSpinner />}><CheckInOutPage /></Suspense>} />
        <Route path="room-status" element={<Suspense fallback={<LoadingSpinner />}><RoomStatusPage /></Suspense>} />
        <Route path="guests" element={<Suspense fallback={<LoadingSpinner />}><GuestProfilePage /></Suspense>} />
        <Route path="reports" element={<Suspense fallback={<LoadingSpinner />}><ReportsPage /></Suspense>} />
        <Route path="chat" element={<Suspense fallback={<LoadingSpinner />}><ChatPage /></Suspense>} />
      </Route>
    </Routes>
  );
}
