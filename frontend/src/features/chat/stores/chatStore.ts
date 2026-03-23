import { create } from 'zustand';
import type {
  ChatMessage,
  PendingConfirmation,
  ToolStatusState,
} from '../types/chat';

interface ChatState {
  currentConversationId: string | null;
  messages: ChatMessage[];
  isStreaming: boolean;
  toolStatuses: ToolStatusState[];
  pendingConfirmation: PendingConfirmation | null;

  setCurrentConversation: (id: string | null) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  appendToLastMessage: (text: string) => void;
  setStreaming: (streaming: boolean) => void;
  addToolStatus: (status: ToolStatusState) => void;
  updateToolStatus: (
    toolId: string,
    update: Partial<ToolStatusState>,
  ) => void;
  clearToolStatuses: () => void;
  setPendingConfirmation: (
    confirmation: PendingConfirmation | null,
  ) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  currentConversationId: null,
  messages: [],
  isStreaming: false,
  toolStatuses: [],
  pendingConfirmation: null,

  setCurrentConversation: (id) => set({ currentConversationId: id }),

  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  appendToLastMessage: (text) =>
    set((state) => {
      const messages = [...state.messages];
      const last = messages[messages.length - 1];
      if (last && last.role === 'assistant') {
        messages[messages.length - 1] = {
          ...last,
          content: (last.content || '') + text,
        };
      }
      return { messages };
    }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  addToolStatus: (status) =>
    set((state) => ({
      toolStatuses: [...state.toolStatuses, status],
    })),

  updateToolStatus: (toolId, update) =>
    set((state) => ({
      toolStatuses: state.toolStatuses.map((ts) =>
        ts.tool_id === toolId ? { ...ts, ...update } : ts,
      ),
    })),

  clearToolStatuses: () => set({ toolStatuses: [] }),

  setPendingConfirmation: (confirmation) =>
    set({ pendingConfirmation: confirmation }),

  clearChat: () =>
    set({
      currentConversationId: null,
      messages: [],
      isStreaming: false,
      toolStatuses: [],
      pendingConfirmation: null,
    }),
}));
