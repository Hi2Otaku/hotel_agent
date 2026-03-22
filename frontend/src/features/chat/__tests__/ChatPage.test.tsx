import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the chat hooks to avoid network calls
vi.mock('../hooks/useChat', () => ({
  useChat: () => ({
    sendMessage: vi.fn(),
    confirmAction: vi.fn(),
    isStreaming: false,
    error: null,
  }),
}));

vi.mock('../hooks/useConversations', () => ({
  useConversations: () => ({ data: [], isLoading: false }),
  useMessages: () => ({ data: undefined, isLoading: false }),
  useRenameConversation: () => ({ mutate: vi.fn() }),
  useDeleteConversation: () => ({ mutate: vi.fn() }),
}));

import ChatPage from '../ChatPage';

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ChatPage', () => {
  it('renders chat layout', () => {
    renderWithProviders(<ChatPage />);
    // The welcome message should be visible since no conversation is active
    expect(
      screen.getByText("Hi! I'm HotelBook Assistant"),
    ).toBeInTheDocument();
  });

  it('shows welcome message with starter chips', () => {
    renderWithProviders(<ChatPage />);
    expect(screen.getByText('Search rooms')).toBeInTheDocument();
    expect(screen.getByText('Check my booking')).toBeInTheDocument();
    expect(screen.getByText('Hotel info')).toBeInTheDocument();
    expect(screen.getByText('Cancellation policy')).toBeInTheDocument();
  });
});
