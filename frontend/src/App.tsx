import { BrowserRouter, Routes, Route } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PageLayout } from '@/components/layout/PageLayout';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';

import Landing from '@/pages/Landing';
import SearchResults from '@/pages/SearchResults';
import RoomDetail from '@/pages/RoomDetail';
import BookingWizard from '@/pages/BookingWizard';
import PricingCalendar from '@/pages/PricingCalendar';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import PasswordReset from '@/pages/PasswordReset';
import PasswordResetConfirm from '@/pages/PasswordResetConfirm';
import MyBookings from '@/pages/MyBookings';
import BookingDetail from '@/pages/BookingDetail';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export function AppRoutes() {
  return (
    <QueryClientProvider client={queryClient}>
      <PageLayout>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/rooms/:roomTypeId" element={<RoomDetail />} />
          <Route path="/book" element={<BookingWizard />} />
          <Route path="/pricing" element={<PricingCalendar />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/password-reset" element={<PasswordReset />} />
          <Route
            path="/password-reset/confirm"
            element={<PasswordResetConfirm />}
          />
          <Route
            path="/my-bookings"
            element={
              <ProtectedRoute>
                <MyBookings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/my-bookings/:bookingId"
            element={
              <ProtectedRoute>
                <BookingDetail />
              </ProtectedRoute>
            }
          />
        </Routes>
      </PageLayout>
    </QueryClientProvider>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
