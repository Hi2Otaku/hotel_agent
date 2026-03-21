import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';

// Mock the API client
vi.mock('@/api/client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

import LoginPage from '@/pages/LoginPage';
import { useAuthStore } from '@/stores/authStore';

function renderLoginPage() {
  return render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    useAuthStore.setState({
      token: null,
      user: null,
      isAuthenticated: false,
    });
  });

  it('renders the Staff Login heading', () => {
    renderLoginPage();
    expect(screen.getByText('Staff Login')).toBeInTheDocument();
  });

  it('renders email and password input fields', () => {
    renderLoginPage();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('renders the sign in button', () => {
    renderLoginPage();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
  });

  it('shows descriptive subtext', () => {
    renderLoginPage();
    expect(screen.getByText('Access the hotel management dashboard')).toBeInTheDocument();
  });

  it('has email placeholder text', () => {
    renderLoginPage();
    expect(screen.getByPlaceholderText('staff@hotelbook.com')).toBeInTheDocument();
  });
});
