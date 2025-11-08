/**
 * Main chat page - Now with shadcn/ui components!
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { membersAPI, messagesAPI } from '@/lib/api';
import { useWebSocket } from '@/lib/useWebSocket';
import { ChatInterface } from '@/components/ui/chat-interface';

export default function HomePage() {
  const router = useRouter();
  const {
    user,
    members,
    messages,
    selectedMember,
    sidebarOpen,
    setMembers,
    setMessages,
    setSelectedMember,
    toggleSidebar,
    addMessage,
  } = useStore();
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
        const [membersData, messagesData] = await Promise.all([
          membersAPI.getAll(),
          messagesAPI.getRecent(50),
        ]);
        setMembers(membersData);
        setMessages(messagesData);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [user, router, setMembers, setMessages]);

  const handleSendMessage = async (content: string) => {
    if (!selectedMember) return;

    try {
      const message = await messagesAPI.create({
        member_id: selectedMember.id,
        content,
      });
      addMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleAddMember = () => {
    router.push('/settings');
  };

  const handleSettings = () => {
    router.push('/settings');
  };

  const handleLogout = () => {
    // Clear user data and redirect to login
    useStore.getState().setUser(null);
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading Plural Chat...</p>
        </div>
      </div>
    );
  }

  return (
    <ChatInterface
      members={members}
      messages={messages}
      selectedMember={selectedMember}
      onSelectMember={setSelectedMember}
      onSendMessage={handleSendMessage}
      onAddMember={handleAddMember}
      onSettings={handleSettings}
      onLogout={handleLogout}
      sidebarOpen={sidebarOpen}
      onToggleSidebar={toggleSidebar}
    />
  );
}
