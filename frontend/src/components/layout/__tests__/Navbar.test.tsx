import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { Navbar } from '../Navbar';
import { useAuthStore } from '@/stores/authStore';

function renderNavbar() {
  return render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>,
  );
}

describe('Navbar - INFR-01', () => {
  beforeEach(() => {
    useAuthStore.setState({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  });

  it('displays "HotelBook" logo text', () => {
    renderNavbar();
    expect(screen.getByText('HotelBook')).toBeInTheDocument();
  });

  it('renders navigation links for Search and Pricing', () => {
    renderNavbar();
    expect(screen.getByText('Search')).toBeInTheDocument();
    expect(screen.getByText('Pricing')).toBeInTheDocument();
  });

  it('shows login button when not authenticated', () => {
    renderNavbar();
    expect(screen.getByText('Log In')).toBeInTheDocument();
  });

  it('shows "My Bookings" link when authenticated', () => {
    useAuthStore.setState({
      token: 'test-token',
      user: {
        id: '1',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        role: 'guest',
        is_active: true,
        created_at: '2026-01-01',
      },
      isAuthenticated: true,
    });
    renderNavbar();
    const myBookingsLinks = screen.getAllByText('My Bookings');
    expect(myBookingsLinks.length).toBeGreaterThan(0);
  });

  it('has z-50 class on the header for proper stacking', () => {
    renderNavbar();
    const header = screen.getByRole('banner');
    expect(header.className).toContain('z-50');
  });
});
