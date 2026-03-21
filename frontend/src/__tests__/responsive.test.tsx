import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { AppRoutes } from '../App';

describe('Responsive Layout - INFR-01', () => {
  it('renders Navbar and Footer on all pages', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppRoutes />
      </MemoryRouter>,
    );
    // Navbar: HotelBook logo
    expect(screen.getByText('HotelBook')).toBeInTheDocument();
    // Footer: Powered by HotelBook
    expect(screen.getByText('Powered by HotelBook')).toBeInTheDocument();
  });

  it('renders layout on search page', () => {
    render(
      <MemoryRouter initialEntries={['/search']}>
        <AppRoutes />
      </MemoryRouter>,
    );
    expect(screen.getByText('HotelBook')).toBeInTheDocument();
    expect(screen.getByText('Modify Search')).toBeInTheDocument();
  });
});
