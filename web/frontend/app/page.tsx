/**
 * Main chat page - Now with shadcn/ui components and channels!
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { membersAPI, messagesAPI, channelsAPI, type Channel } from '@/lib/api';
import { useWebSocket } from '@/lib/useWebSocket';
import { ChatInterface } from '@/components/ui/chat-interface';
import { ChannelModal } from '@/components/ui/channel-modal';

export default function HomePage() {
  const router = useRouter();
  const {
    user,
    members,
    channels,
    messages,
    onlineUsers,
    selectedMember,
    selectedChannel,
    sidebarOpen,
    setMembers,
    setChannels,
    setMessages,
    setOnlineUsers,
    setSelectedMember,
    setSelectedChannel,
    toggleSidebar,
    addMessage,
    addChannel,
    updateChannel,
    deleteChannel,
  } = useStore();
  const [loading, setLoading] = useState(true);
  const [channelModalOpen, setChannelModalOpen] = useState(false);
  const [editingChannel, setEditingChannel] = useState<Channel | null>(null);

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
        const [membersData, channelsData, onlineUsersRes] = await Promise.all([
          membersAPI.getAll(),
          channelsAPI.getAll(),
          fetch('http://localhost:8000/users/online').then(r => r.json()),
        ]);
        setMembers(membersData);
        setChannels(channelsData);
        setOnlineUsers(onlineUsersRes);

        // Select default channel if not already selected
        if (!selectedChannel && channelsData.length > 0) {
          const defaultChannel = channelsData.find(ch => ch.is_default) || channelsData[0];
          setSelectedChannel(defaultChannel);
        }
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [user, router, setMembers, setChannels, setOnlineUsers, selectedChannel, setSelectedChannel]);

  // Load messages when channel changes
  useEffect(() => {
    const loadMessages = async () => {
      if (!selectedChannel) {
        setMessages([]);
        return;
      }

      try {
        const messagesData = await messagesAPI.getRecent(50, selectedChannel.id);
        setMessages(messagesData);
      } catch (error) {
        console.error('Failed to load messages:', error);
      }
    };

    loadMessages();
  }, [selectedChannel, setMessages]);

  const handleSendMessage = async (content: string) => {
    if (!selectedChannel) return;

    try {
      const message = await messagesAPI.create({
        member_id: selectedMember?.id || undefined,  // Optional - send as member if selected, otherwise as user
        channel_id: selectedChannel.id,
        content,
      });
      addMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };


  const handleAddChannel = () => {
    setEditingChannel(null);
    setChannelModalOpen(true);
  };

  const handleEditChannel = (channel: Channel) => {
    setEditingChannel(channel);
    setChannelModalOpen(true);
  };

  const handleSaveChannel = async (data: {
    name: string;
    description?: string;
    color?: string;
    emoji?: string;
  }) => {
    try {
      if (editingChannel) {
        // Update existing channel
        const updated = await channelsAPI.update(editingChannel.id, data);
        updateChannel(editingChannel.id, updated);
      } else {
        // Create new channel
        const newChannel = await channelsAPI.create(data);
        addChannel(newChannel);
        setSelectedChannel(newChannel);
      }
      setChannelModalOpen(false);
      setEditingChannel(null);
    } catch (error) {
      console.error('Failed to save channel:', error);
      throw error;
    }
  };

  const handleDeleteChannel = async () => {
    if (!editingChannel) return;

    try {
      await channelsAPI.delete(editingChannel.id, false);
      deleteChannel(editingChannel.id);
      setChannelModalOpen(false);
      setEditingChannel(null);
    } catch (error) {
      console.error('Failed to delete channel:', error);
      throw error;
    }
  };

  const handleSettings = () => {
    router.push('/settings');
  };

  const handleMembers = () => {
    router.push('/members');
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
    <>
      <ChatInterface
        members={members}
        channels={channels}
        messages={messages}
        onlineUsers={onlineUsers}
        selectedMember={selectedMember}
        selectedChannel={selectedChannel}
        onSelectMember={setSelectedMember}
        onSelectChannel={setSelectedChannel}
        onSendMessage={handleSendMessage}
        onAddChannel={handleAddChannel}
        onEditChannel={handleEditChannel}
        onSettings={handleSettings}
        onMembers={handleMembers}
        onLogout={handleLogout}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={toggleSidebar}
      />

      <ChannelModal
        channel={editingChannel}
        open={channelModalOpen}
        onClose={() => {
          setChannelModalOpen(false);
          setEditingChannel(null);
        }}
        onSave={handleSaveChannel}
        onDelete={editingChannel ? handleDeleteChannel : undefined}
      />
    </>
  );
}
