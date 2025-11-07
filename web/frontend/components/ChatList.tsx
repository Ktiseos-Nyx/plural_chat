/**
 * Chat list component displaying all messages
 */
'use client';

import { useEffect, useRef } from 'react';
import { useStore } from '@/lib/store';
import ChatMessage from './ChatMessage';

export default function ChatList() {
  const { messages } = useStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto p-4 space-y-4"
      style={{
        background: 'var(--lobe-chat-bg, #f8f9fa)',
        height: 'calc(100vh - 200px)',
      }}
    >
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2">No messages yet</p>
            <p className="text-sm">
              Select a member and start chatting!
            </p>
          </div>
        </div>
      ) : (
        messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))
      )}
    </div>
  );
}
