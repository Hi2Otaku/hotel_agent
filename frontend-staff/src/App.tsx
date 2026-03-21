import { Routes, Route, Navigate } from 'react-router';
import { useAuthStore } from '@/stores/authStore';
import { AppLayout } from '@/components/layout/AppLayout';
import LoginPage from '@/pages/LoginPage';
import type { ReactNode } from 'react';

function ProtectedRoute({ children }: { children: ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function PlaceholderPage({ name }: { name: string }) {
  return (
    <div className="text-slate-100 text-xl font-semibold">{name}</div>
  );
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
        <Route index element={<PlaceholderPage name="Overview" />} />
        <Route path="reservations" element={<PlaceholderPage name="Reservations" />} />
        <Route path="check-in-out" element={<PlaceholderPage name="Check-in / Check-out" />} />
        <Route path="room-status" element={<PlaceholderPage name="Room Status" />} />
        <Route path="guests" element={<PlaceholderPage name="Guests" />} />
        <Route path="reports" element={<PlaceholderPage name="Reports - Coming in Phase 7" />} />
      </Route>
    </Routes>
  );
}
