/**
 * Individual chat message component
 */
'use client';

import { Avatar as AntAvatar } from 'antd';
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
    <div className="flex gap-3 mb-4 p-3 rounded-lg hover:bg-gray-50">
      {member.avatar_path ? (
        <AntAvatar
          src={`/api/avatars/${member.avatar_path}`}
          alt={member.name}
          size={40}
        />
      ) : (
        <AntAvatar
          style={{ backgroundColor: memberColor }}
          size={40}
        >
          {member.name.charAt(0).toUpperCase()}
        </AntAvatar>
      )}
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span style={{ color: memberColor }} className="font-semibold">
            {member.name}
          </span>
          {member.pronouns && (
            <span className="text-gray-500 text-sm">
              ({member.pronouns})
            </span>
          )}
          <span className="text-gray-400 text-sm ml-auto">
            {timeString}
          </span>
        </div>
        <div className="text-gray-800">
          {content}
        </div>
      </div>
    </div>
  );
}
