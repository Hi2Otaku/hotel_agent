import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the chat hooks
vi.mock('../hooks/useChat', () => ({
  useChat: () => ({
    sendMessage: vi.fn(),
    confirmAction: vi.fn(),
    isStreaming: false,
  }),
}));

vi.mock('../hooks/useConversations', () => ({
  useConversations: () => ({ data: [], isLoading: false }),
  useMessages: () => ({ data: [], isLoading: false }),
  useRenameConversation: () => ({ mutate: vi.fn() }),
  useDeleteConversation: () => ({ mutate: vi.fn() }),
}));

vi.mock('../stores/chatStore', () => ({
  useChatStore: () => ({
    currentConversationId: null,
    messages: [],
    isStreaming: false,
    toolStatuses: [],
    pendingConfirmation: null,
    setCurrentConversation: vi.fn(),
    setMessages: vi.fn(),
    clearChat: vi.fn(),
    setPendingConfirmation: vi.fn(),
  }),
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
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders HB Ops welcome message', () => {
    renderWithProviders(<ChatPage />);
    expect(screen.getByText("Hi! I'm HB Ops")).toBeInTheDocument();
    expect(
      screen.getByText(/check-ins, room status, guest lookups/),
    ).toBeInTheDocument();
  });

  it('renders staff starter chips', () => {
    renderWithProviders(<ChatPage />);
    expect(screen.getByText("Today's check-ins")).toBeInTheDocument();
    expect(screen.getByText('Room status')).toBeInTheDocument();
    expect(screen.getByText('Find guest')).toBeInTheDocument();
    expect(screen.getByText('Occupancy report')).toBeInTheDocument();
  });

  it('renders message input with staff placeholder', () => {
    renderWithProviders(<ChatPage />);
    expect(
      screen.getByPlaceholderText('Ask about reservations, guests, or operations...'),
    ).toBeInTheDocument();
  });

  it('renders send button', () => {
    renderWithProviders(<ChatPage />);
    expect(screen.getByRole('button', { name: 'Send message' })).toBeInTheDocument();
  });

  it('renders new chat button', () => {
    renderWithProviders(<ChatPage />);
    expect(screen.getByText('New Chat')).toBeInTheDocument();
  });
});
