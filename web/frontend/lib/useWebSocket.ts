/**
 * WebSocket hook for real-time chat updates
 */
import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { useStore } from './store';
import type { Message } from './store';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000';

export function useWebSocket() {
  const socketRef = useRef<Socket | null>(null);
  const { addMessage, setConnected } = useStore();

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

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, [addMessage, setConnected]);

  return {
    sendMessage: (content: string, memberId: number) => {
      if (socketRef.current) {
        socketRef.current.emit('send_message', { content, member_id: memberId });
      }
    },
  };
}
