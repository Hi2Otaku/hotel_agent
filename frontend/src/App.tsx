import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PageLayout } from '@/components/layout/PageLayout';
import { Navbar } from '@/components/layout/Navbar';
import { ProtectedRoute } from '@/components/common/ProtectedRoute';
import { Toaster } from '@/components/ui/sonner';

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

const ChatPage = lazy(() => import('@/features/chat/ChatPage'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

function LoadingSpinner() {
  return (
    <div className="flex h-[calc(100vh-64px)] items-center justify-center">
      <div className="size-8 animate-spin rounded-full border-4 border-slate-200 border-t-[#0F766E]" />
    </div>
  );
}

export function AppRoutes() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        {/* Chat route: own layout (Navbar + no Footer) */}
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <div className="flex min-h-screen flex-col">
                <a
                  href="#main-content"
                  className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:shadow-lg"
                >
                  Skip to main content
                </a>
                <Navbar />
                <main id="main-content" className="pt-16">
                  <Suspense fallback={<LoadingSpinner />}>
                    <ChatPage />
                  </Suspense>
                </main>
                <Toaster position="top-right" richColors closeButton />
              </div>
            </ProtectedRoute>
          }
        />

        {/* All other routes: PageLayout with Footer */}
        <Route
          path="*"
          element={
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
          }
        />
      </Routes>
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
