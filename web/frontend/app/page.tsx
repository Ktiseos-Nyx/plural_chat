/**
 * Main chat page
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { membersAPI, messagesAPI } from '@/lib/api';
import { useWebSocket } from '@/lib/useWebSocket';
import { Button, Badge } from 'antd';
import {
  MenuOutlined,
  CloseOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import MemberSidebar from '@/components/MemberSidebar';
import ChatList from '@/components/ChatList';
import MessageInput from '@/components/MessageInput';

export default function HomePage() {
  const router = useRouter();
  const { user, setMembers, setMessages, sidebarOpen, toggleSidebar, connected } = useStore();
  const [loading, setLoading] = useState(true);

  // Initialize WebSocket
  useWebSocket();

  useEffect(() => {
    // Check auth
    if (!user) {
      router.push('/login');
      return;
    }

    // Load initial data
    const loadData = async () => {
      try {
        const [members, messages] = await Promise.all([
          membersAPI.getAll(),
          messagesAPI.getRecent(50),
        ]);
        setMembers(members);
        setMessages(messages);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [user, router, setMembers, setMessages]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Plural Chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <MemberSidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              type="text"
              icon={sidebarOpen ? <CloseOutlined /> : <MenuOutlined />}
              onClick={toggleSidebar}
            />
            <h1 className="text-xl font-semibold">Plural Chat</h1>
            <Badge
              status={connected ? 'success' : 'default'}
              text={connected ? 'Connected' : 'Disconnected'}
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="text"
              icon={<SettingOutlined />}
              onClick={() => {
                // TODO: Open settings
              }}
            />
          </div>
        </div>

        {/* Chat Area */}
        <ChatList />

        {/* Input */}
        <MessageInput />
      </div>
    </div>
  );
}
