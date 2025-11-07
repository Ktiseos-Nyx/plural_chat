/**
 * Sidebar showing all members with avatars
 */
'use client';

import { useStore } from '@/lib/store';
import { Avatar, Button, Tooltip } from 'antd';
import { PlusOutlined, ReloadOutlined, UserOutlined } from '@ant-design/icons';
import { authAPI } from '@/lib/api';
import { useState } from 'react';

export default function MemberSidebar() {
  const { members, selectedMember, setSelectedMember, sidebarOpen } = useStore();
  const [syncing, setSyncing] = useState(false);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await authAPI.syncFromPluralKit();
      window.location.reload(); // Reload to fetch new members
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setSyncing(false);
    }
  };

  if (!sidebarOpen) return null;

  return (
    <div className="w-64 border-r border-gray-200 bg-white flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold mb-3">Members</h2>
        <div className="flex gap-2">
          <Tooltip title="Sync from PluralKit">
            <Button
              icon={<ReloadOutlined />}
              onClick={handleSync}
              loading={syncing}
              style={{ flex: 1 }}
            >
              Sync
            </Button>
          </Tooltip>
          <Tooltip title="Add Member">
            <Button
              icon={<PlusOutlined />}
              type="primary"
              onClick={() => {
                // TODO: Open add member dialog
              }}
            />
          </Tooltip>
        </div>
      </div>

      {/* Member List */}
      <div className="flex-1 overflow-y-auto">
        {members.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <UserOutlined style={{ fontSize: 32, marginBottom: 8 }} />
            <p className="text-sm">No members yet</p>
            <p className="text-xs">Sync from PluralKit or add manually</p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {members.map((member) => (
              <button
                key={member.id}
                onClick={() => setSelectedMember(member)}
                className={`w-full p-3 rounded-lg flex items-center gap-3 hover:bg-gray-50 transition-colors ${
                  selectedMember?.id === member.id
                    ? 'bg-blue-50 border border-blue-200'
                    : ''
                }`}
              >
                <Avatar
                  src={member.avatar_path ? `/api/avatars/${member.avatar_path}` : undefined}
                  style={{
                    backgroundColor: member.color || '#6c757d',
                  }}
                  size={40}
                >
                  {member.name.charAt(0).toUpperCase()}
                </Avatar>
                <div className="flex-1 text-left overflow-hidden">
                  <div className="font-medium text-sm truncate">
                    {member.name}
                  </div>
                  {member.pronouns && (
                    <div className="text-xs text-gray-500 truncate">
                      {member.pronouns}
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
