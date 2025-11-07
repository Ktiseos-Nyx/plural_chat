/**
 * Individual chat message component using LobeHub UI
 */
'use client';

import { ChatItem } from '@lobehub/ui';
import { Avatar } from '@lobehub/ui';
import type { Message } from '@/lib/store';
import { format } from 'date-fns';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const { member, content, timestamp } = message;

  // Format timestamp
  const timeString = format(new Date(timestamp), 'h:mm a');

  // Get member color or use default
  const memberColor = member.color || '#6c757d';

  return (
    <ChatItem
      avatar={
        member.avatar_path ? (
          <Avatar
            src={`/api/avatars/${member.avatar_path}`}
            alt={member.name}
            size={40}
          />
        ) : (
          <Avatar
            alt={member.name}
            background={memberColor}
            size={40}
          >
            {member.name.charAt(0).toUpperCase()}
          </Avatar>
        )
      }
      primary={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: memberColor, fontWeight: 600 }}>
            {member.name}
          </span>
          {member.pronouns && (
            <span style={{ color: '#6c757d', fontSize: '0.85em' }}>
              ({member.pronouns})
            </span>
          )}
          <span style={{ color: '#999', fontSize: '0.85em', marginLeft: 'auto' }}>
            {timeString}
          </span>
        </div>
      }
      text={content}
      placement="left"
      showTitle
      style={{ marginBottom: '16px' }}
    />
  );
}
