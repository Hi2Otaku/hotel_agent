import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MessageBubble } from '../components/MessageBubble';
import type { ChatMessage } from '../types/chat';

const userMessage: ChatMessage = {
  id: '1',
  role: 'user',
  content: 'Hello there',
  tool_calls: null,
  tool_results: null,
  pending_confirmation: null,
  created_at: new Date().toISOString(),
};

const botMessage: ChatMessage = {
  id: '2',
  role: 'assistant',
  content: '**Bold text** and regular text',
  tool_calls: null,
  tool_results: null,
  pending_confirmation: null,
  created_at: new Date().toISOString(),
};

describe('MessageBubble', () => {
  it('renders user bubble right-aligned', () => {
    const { container } = render(<MessageBubble message={userMessage} />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('flex-row-reverse');
  });

  it('renders bot bubble with markdown', () => {
    render(<MessageBubble message={botMessage} />);
    // react-markdown renders **Bold text** as <strong>
    expect(screen.getByText('Bold text')).toBeInTheDocument();
    const strong = screen.getByText('Bold text');
    expect(strong.tagName).toBe('STRONG');
  });

  it('hides timestamp by default (opacity-0)', () => {
    const { container } = render(<MessageBubble message={userMessage} />);
    const timestamps = container.querySelectorAll('.opacity-0');
    expect(timestamps.length).toBeGreaterThan(0);
  });
});
