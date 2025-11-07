/**
 * Message input component with member selector
 */
'use client';

import { useState } from 'react';
import { useStore } from '@/lib/store';
import { messagesAPI } from '@/lib/api';
import { useWebSocket } from '@/lib/useWebSocket';
import { Select, Button, Input } from 'antd';
import { SendOutlined } from '@ant-design/icons';

const { TextArea } = Input;

export default function MessageInput() {
  const [content, setContent] = useState('');
  const [sending, setSending] = useState(false);
  const { members, selectedMember, setSelectedMember } = useStore();

  const handleSend = async () => {
    if (!content.trim() || !selectedMember) return;

    setSending(true);
    try {
      await messagesAPI.send(selectedMember.id, content);
      setContent('');
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 p-4 bg-white">
      <div className="flex items-end gap-3">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 font-medium">
              Sending as:
            </span>
            <Select
              value={selectedMember?.id}
              onChange={(id) => {
                const member = members.find((m) => m.id === id);
                setSelectedMember(member || null);
              }}
              placeholder="Select a member"
              style={{ width: 200 }}
              size="large"
              options={members.map((member) => ({
                value: member.id,
                label: member.name,
              }))}
            />
          </div>
          <TextArea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              selectedMember
                ? `Message as ${selectedMember.name}...`
                : 'Select a member first...'
            }
            disabled={!selectedMember}
            autoSize={{ minRows: 2, maxRows: 6 }}
            size="large"
            style={{ resize: 'none' }}
          />
        </div>
        <Button
          type="primary"
          size="large"
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={!content.trim() || !selectedMember || sending}
          loading={sending}
          style={{ height: '80px' }}
        >
          Send
        </Button>
      </div>
    </div>
  );
}
