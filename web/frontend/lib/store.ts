/**
 * Global state management with Zustand
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Channel } from './api';

export interface Member {
  id: number;
  name: string;
  pronouns?: string;
  color?: string;
  avatar_path?: string;
  description?: string;
  pk_id?: string;
  proxy_tags?: string;
}

export interface Message {
  id: number;
  user_id: number;
  member_id?: number;
  channel_id?: number;
  user: User;
  member?: Member;
  content: string;
  timestamp: string;
}

export interface User {
  id: number;
  username: string;
  email?: string;
  system_name?: string;
  theme_color?: string;
  avatar_path?: string;
  created_at: string;
  last_sync?: string;
  last_login?: string;
  totp_enabled: boolean;
}

interface AppState {
  // User & Auth
  user: User | null;
  setUser: (user: User | null) => void;

  // Members
  members: Member[];
  setMembers: (members: Member[]) => void;
  selectedMember: Member | null;
  setSelectedMember: (member: Member | null) => void;

  // Channels
  channels: Channel[];
  setChannels: (channels: Channel[]) => void;
  selectedChannel: Channel | null;
  setSelectedChannel: (channel: Channel | null) => void;
  addChannel: (channel: Channel) => void;
  updateChannel: (id: number, updates: Partial<Channel>) => void;
  deleteChannel: (id: number) => void;

  // Messages
  messages: Message[];
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;

  // UI State
  sidebarOpen: boolean;
  toggleSidebar: () => void;

  // WebSocket connection status
  connected: boolean;
  setConnected: (connected: boolean) => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // User & Auth
      user: null,
      setUser: (user) => set({ user }),

      // Members
      members: [],
      setMembers: (members) => set({ members }),
      selectedMember: null,
      setSelectedMember: (member) => set({ selectedMember: member }),

      // Channels
      channels: [],
      setChannels: (channels) => set({ channels }),
      selectedChannel: null,
      setSelectedChannel: (channel) => set({ selectedChannel: channel }),
      addChannel: (channel) =>
        set((state) => ({ channels: [...state.channels, channel] })),
      updateChannel: (id, updates) =>
        set((state) => ({
          channels: state.channels.map((ch) =>
            ch.id === id ? { ...ch, ...updates } : ch
          ),
        })),
      deleteChannel: (id) =>
        set((state) => ({
          channels: state.channels.filter((ch) => ch.id !== id),
          selectedChannel:
            state.selectedChannel?.id === id ? null : state.selectedChannel,
        })),

      // Messages
      messages: [],
      setMessages: (messages) => set({ messages }),
      addMessage: (message) =>
        set((state) => ({ messages: [...state.messages, message] })),

      // UI State
      sidebarOpen: true,
      toggleSidebar: () =>
        set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      // WebSocket
      connected: false,
      setConnected: (connected) => set({ connected }),
    }),
    {
      name: 'plural-chat-storage',
      partialize: (state) => ({
        user: state.user,
        sidebarOpen: state.sidebarOpen,
        selectedChannel: state.selectedChannel,
      }),
    }
  )
);
