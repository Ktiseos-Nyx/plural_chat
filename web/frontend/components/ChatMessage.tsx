/**
 * Chat message bubble component
 * Modern chat UI with member colors and avatars
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
  const memberColor = member.color || '#6366f1';

  return (
    <div className="group flex gap-3 px-4 py-2 hover:bg-gray-50/50 transition-colors">
      {/* Avatar */}
      <div className="flex-shrink-0 pt-0.5">
        {member.avatar_path ? (
          <AntAvatar
            src={`/api/avatars/${member.avatar_path}`}
            alt={member.name}
            size={40}
            className="ring-2 ring-gray-100"
          />
        ) : (
          <AntAvatar
            style={{
              backgroundColor: memberColor,
              fontSize: '16px',
              fontWeight: 600,
            }}
            size={40}
            className="ring-2 ring-gray-100"
          >
            {member.name.charAt(0).toUpperCase()}
          </AntAvatar>
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        {/* Header with name and timestamp */}
        <div className="flex items-baseline gap-2 mb-1">
          <span
            style={{ color: memberColor }}
            className="font-semibold text-[15px] hover:underline cursor-pointer"
          >
            {member.name}
          </span>
          {member.pronouns && (
            <span className="text-xs text-gray-500 font-normal">
              ({member.pronouns})
            </span>
          )}
          <span className="text-xs text-gray-400 font-normal">
            {timeString}
          </span>
        </div>

        {/* Message text */}
        <div className="text-[15px] text-gray-900 leading-relaxed break-words">
          {content}
        </div>
      </div>
    </div>
  );
}
