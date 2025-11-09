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
  timeout: 10000, // 10 second timeout to prevent hanging
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('pk_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log errors for debugging
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      detail: error.response?.data?.detail
    });

    // Map common errors to user-friendly messages
    const status = error.response?.status;
    const userFriendlyMessages: Record<number, string> = {
      400: 'Invalid request. Please check your input.',
      401: 'Session expired. Please log in again.',
      403: 'You don\'t have permission to do that.',
      404: 'Resource not found.',
      409: 'That name is already taken.',
      500: 'Server error. Please try again later.',
      502: 'Server is temporarily unavailable.',
      503: 'Service unavailable. Please try again later.',
    };

    // Handle network errors
    if (!error.response) {
      error.userMessage = 'Cannot connect to server. Please check if the backend is running.';
      error.message = error.userMessage;
    } else if (status && userFriendlyMessages[status]) {
      error.userMessage = userFriendlyMessages[status];
      // Keep the original error message for debugging, add userMessage for display
    } else {
      error.userMessage = error.response?.data?.detail || error.message;
    }

    return Promise.reject(error);
  }
);

// Types for security endpoints
export interface LoginRequest {
  username: string;
  password: string;
  totp_code?: string;
  backup_code?: string;
}

export interface LoginResponse {
  access_token?: string;
  token_type: string;
  requires_2fa: boolean;
  user_id?: number;
  message?: string;
}

export interface TOTPSetupResponse {
  secret: string;
  qr_code: string;
  backup_codes: string[];
  message: string;
}

export interface AuditLog {
  id: number;
  event_type: string;
  category: string;
  description?: string;
  ip_address?: string;
  success: boolean;
  timestamp: string;
}

// Auth API
export const authAPI = {
  // Legacy PluralKit login (deprecated - use setPKToken instead)
  login: async (pkToken: string) => {
    const response = await api.post<User>('/auth/login', { pk_token: pkToken });
    localStorage.setItem('pk_token', pkToken);
    return response.data;
  },

  // Set PluralKit token for syncing (requires existing authentication)
  setPKToken: async (pkToken: string) => {
    const response = await api.post('/auth/set-pk-token', { pk_token: pkToken });
    return response.data;
  },

  logout: async () => {
    try {
      // Call backend to log the logout event
      await api.post('/auth/logout');
    } catch (error) {
      // Continue with logout even if backend call fails
      console.error('Logout API call failed:', error);
    } finally {
      // Always clear local tokens
      localStorage.removeItem('pk_token');
      localStorage.removeItem('access_token');
    }
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

// Security API (username/password + 2FA)
export const securityAPI = {
  // Register new user
  register: async (data: {
    username: string;
    password: string;
    email?: string;
  }): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/security/register', data);
    return response.data;
  },

  // Login with username/password
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/security/login', data);
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    return response.data;
  },

  // 2FA setup
  setup2FA: async (): Promise<TOTPSetupResponse> => {
    const response = await api.post<TOTPSetupResponse>('/security/2fa/setup');
    return response.data;
  },

  // Enable 2FA
  enable2FA: async (code: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/security/2fa/enable', { code });
    return response.data;
  },

  // Disable 2FA
  disable2FA: async (password?: string, totp_code?: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/security/2fa/disable', { password, totp_code });
    return response.data;
  },

  // Get 2FA status
  get2FAStatus: async (): Promise<{ enabled: boolean; backup_codes_remaining: number }> => {
    const response = await api.get('/security/2fa/status');
    return response.data;
  },

  // Regenerate backup codes
  regenerateBackupCodes: async (code: string): Promise<{ success: boolean; backup_codes: string[]; message: string }> => {
    const response = await api.post('/security/2fa/backup-codes/regenerate', { code });
    return response.data;
  },

  // Get audit logs
  getAuditLogs: async (limit = 50, category?: string, days = 30): Promise<AuditLog[]> => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      days: days.toString(),
    });
    if (category) {
      params.append('category', category);
    }
    const response = await api.get<AuditLog[]>(`/security/audit-logs?${params}`);
    return response.data;
  },

  // Get security logs only
  getSecurityLogs: async (limit = 50): Promise<AuditLog[]> => {
    const response = await api.get<AuditLog[]>(`/security/audit-logs/security?limit=${limit}`);
    return response.data;
  },

  // Change password
  changePassword: async (data: {
    current_password: string;
    new_password: string;
  }): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/security/change-password', data);
    return response.data;
  },

  // Update profile
  updateProfile: async (data: {
    username?: string;
    email?: string;
    theme_color?: string;
  }): Promise<{ success: boolean; message: string }> => {
    const response = await api.patch('/security/profile', data);
    return response.data;
  },

  // Upload avatar
  uploadAvatar: async (file: File): Promise<{ success: boolean; message: string; avatar_path: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/security/profile/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
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

  uploadAvatar: async (memberId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/members/${memberId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Messages API
export const messagesAPI = {
  getRecent: async (limit = 50, channelId?: number) => {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (channelId !== undefined) {
      params.append('channel_id', channelId.toString());
    }
    const response = await api.get<Message[]>(`/messages?${params}`);
    return response.data;
  },

  create: async (data: { member_id?: number; content: string; channel_id?: number }) => {
    const response = await api.post<Message>('/messages', data);
    return response.data;
  },

  send: async (memberId: number | undefined, content: string, channelId?: number) => {
    const response = await api.post<Message>('/messages', {
      member_id: memberId,
      content,
      channel_id: channelId,
    });
    return response.data;
  },

  delete: async (id: number) => {
    await api.delete(`/messages/${id}`);
  },

  // Export chat logs in various formats
  export: async (format: 'json' | 'csv' | 'txt', startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const queryString = params.toString();
    const url = `/messages/export/${format}${queryString ? `?${queryString}` : ''}`;

    const response = await api.get(url, {
      responseType: 'blob',
    });

    // Trigger download
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `plural_chat_export_${Date.now()}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);

    return { success: true, format };
  },
};

// Channels API
export interface Channel {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  color?: string;
  emoji?: string;
  is_default: boolean;
  is_archived: boolean;
  position: number;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export const channelsAPI = {
  getAll: async (includeArchived = false) => {
    const params = includeArchived ? '?include_archived=true' : '';
    const response = await api.get<Channel[]>(`/channels${params}`);
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get<Channel>(`/channels/${id}`);
    return response.data;
  },

  create: async (data: {
    name: string;
    description?: string;
    color?: string;
    emoji?: string;
  }) => {
    const response = await api.post<Channel>('/channels', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Channel>) => {
    const response = await api.patch<Channel>(`/channels/${id}`, data);
    return response.data;
  },

  delete: async (id: number, deleteMessages = false) => {
    await api.delete(`/channels/${id}?delete_messages=${deleteMessages}`);
  },

  archive: async (id: number) => {
    const response = await api.post<Channel>(`/channels/${id}/archive`);
    return response.data;
  },

  unarchive: async (id: number) => {
    const response = await api.post<Channel>(`/channels/${id}/unarchive`);
    return response.data;
  },

  reorder: async (channelIds: number[]) => {
    // Backend expects the array to be sent directly as JSON
    const response = await api.post<Channel[]>('/channels/reorder', channelIds);
    return response.data;
  },
};

// Export default API instance
export default api;
