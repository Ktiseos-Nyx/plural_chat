/**
 * API client for backend communication
 */
import axios from 'axios';
import type { Member, Message, User } from './store';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('pk_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: async (pkToken: string) => {
    const response = await api.post<User>('/auth/login', { pk_token: pkToken });
    localStorage.setItem('pk_token', pkToken);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('pk_token');
  },

  verifyToken: async () => {
    const response = await api.get<User>('/auth/verify');
    return response.data;
  },

  syncFromPluralKit: async () => {
    const response = await api.post('/auth/sync-pluralkit');
    return response.data;
  },
};

// Members API
export const membersAPI = {
  getAll: async () => {
    const response = await api.get<Member[]>('/members');
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<Member>(`/members/${id}`);
    return response.data;
  },

  create: async (member: Omit<Member, 'id'>) => {
    const response = await api.post<Member>('/members', member);
    return response.data;
  },

  update: async (id: number, member: Partial<Member>) => {
    const response = await api.patch<Member>(`/members/${id}`, member);
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/members/${id}`);
  },
};

// Messages API
export const messagesAPI = {
  getRecent: async (limit = 50) => {
    const response = await api.get<Message[]>(`/messages?limit=${limit}`);
    return response.data;
  },

  send: async (memberId: number, content: string) => {
    const response = await api.post<Message>('/messages', {
      member_id: memberId,
      content,
    });
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/messages/${id}`);
  },
};

// Export default API instance
export default api;
