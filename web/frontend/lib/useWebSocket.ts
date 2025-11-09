/**
 * WebSocket hook for real-time chat updates
 */
import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { useStore } from './store';
import type { Message } from './store';
import type { Channel } from './api';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000';

export function useWebSocket() {
  const socketRef = useRef<Socket | null>(null);
  const { addMessage, setConnected, addChannel, updateChannel, deleteChannel, addOnlineUser, removeOnlineUser } = useStore();

  useEffect(() => {
    const token = localStorage.getItem('pk_token');
    if (!token) return;

    // Initialize socket connection
    socketRef.current = io(WS_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
    });

    const socket = socketRef.current;

    // Connection events
    socket.on('connect', () => {
      console.log('WebSocket connected');
      setConnected(true);
    });

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    });

    socket.on('error', (error: any) => {
      console.error('WebSocket error:', error);
    });

    // Message events
    socket.on('message', (message: Message) => {
      console.log('New message received:', message);
      addMessage(message);
    });

    socket.on('member_update', (member: any) => {
      console.log('Member updated:', member);
      // Could trigger a member refresh here
    });

    // Channel events
    socket.on('channel_created', (channel: Channel) => {
      console.log('Channel created:', channel);
      addChannel(channel);
    });

    socket.on('channel_updated', (channel: Channel) => {
      console.log('Channel updated:', channel);
      updateChannel(channel.id, channel);
    });

    socket.on('channel_deleted', (data: { id: number }) => {
      console.log('Channel deleted:', data.id);
      deleteChannel(data.id);
    });

    // User presence events
    socket.on('user_online', async (data: { user_id: number }) => {
      console.log('User came online:', data.user_id);
      // Fetch user details and add to online users
      try {
        const response = await fetch(`http://localhost:8000/users/online`);
        const onlineUsers = await response.json();
        const user = onlineUsers.find((u: any) => u.id === data.user_id);
        if (user) {
          addOnlineUser(user);
        }
      } catch (error) {
        console.error('Error fetching online user:', error);
      }
    });

    socket.on('user_offline', (data: { user_id: number }) => {
      console.log('User went offline:', data.user_id);
      removeOnlineUser(data.user_id);
    });

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, [addMessage, setConnected, addChannel, updateChannel, deleteChannel, addOnlineUser, removeOnlineUser]);

  return {
    sendMessage: (content: string, memberId: number) => {
      if (socketRef.current) {
        socketRef.current.emit('send_message', { content, member_id: memberId });
      }
    },
  };
}
