"use client"

import * as React from "react"
import { Menu, Settings, LogOut, Hash, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ChatList } from "@/components/ui/chat-list"
import { ChatInput } from "@/components/ui/chat-input"
import { MemberSidebar } from "@/components/ui/member-sidebar"
import { ChannelSidebar } from "@/components/ui/channel-sidebar"
import { OnlineUsersSidebar } from "@/components/ui/online-users-sidebar"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import type { Member, Message, User } from "@/lib/store"
import type { Channel } from "@/lib/api"

interface ChatInterfaceProps {
  members: Member[]
  channels: Channel[]
  messages: Message[]
  onlineUsers: User[]
  selectedMember?: Member | null
  selectedChannel?: Channel | null
  onSelectMember: (member: Member) => void
  onSelectChannel: (channel: Channel) => void
  onSendMessage: (message: string) => void
  onAddChannel?: () => void
  onEditChannel?: (channel: Channel) => void
  onSettings?: () => void
  onMembers?: () => void
  onLogout?: () => void
  sidebarOpen?: boolean
  onToggleSidebar?: () => void
  className?: string
}

export function ChatInterface({
  members,
  channels,
  messages,
  onlineUsers,
  selectedMember,
  selectedChannel,
  onSelectMember,
  onSelectChannel,
  onSendMessage,
  onAddChannel,
  onEditChannel,
  onSettings,
  onMembers,
  onLogout,
  sidebarOpen = true,
  onToggleSidebar,
  className,
}: ChatInterfaceProps) {
  const [showArchivedChannels, setShowArchivedChannels] = React.useState(false)

  return (
    <div className={cn("flex h-screen bg-background", className)}>
      {/* Channel Sidebar */}
      {sidebarOpen && (
        <div className="w-60 flex-shrink-0">
          <ChannelSidebar
            channels={channels}
            selectedChannel={selectedChannel}
            onSelectChannel={onSelectChannel}
            onCreateChannel={onAddChannel}
            onEditChannel={onEditChannel}
            showArchived={showArchivedChannels}
            onToggleArchived={() => setShowArchivedChannels(!showArchivedChannels)}
          />
        </div>
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-14 border-b flex items-center justify-between px-4 bg-background">
          <div className="flex items-center gap-3">
            {onToggleSidebar && (
              <Button
                onClick={onToggleSidebar}
                size="icon"
                variant="ghost"
                className="flex-shrink-0"
              >
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle sidebar</span>
              </Button>
            )}

            <div className="flex items-center gap-3">
              {selectedChannel && (
                <div className="flex items-center gap-2">
                  <span className="text-lg">{selectedChannel.emoji || "💬"}</span>
                  <h1
                    className="font-semibold text-lg"
                    style={{ color: selectedChannel.color || undefined }}
                  >
                    {selectedChannel.name}
                  </h1>
                  {selectedChannel.description && (
                    <span className="text-sm text-muted-foreground">
                      • {selectedChannel.description}
                    </span>
                  )}
                </div>
              )}
              {!selectedChannel && (
                <h1 className="font-semibold text-lg text-muted-foreground">
                  Select a channel
                </h1>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {onMembers && (
              <Button onClick={onMembers} size="icon" variant="ghost">
                <Users className="h-5 w-5" />
                <span className="sr-only">Members</span>
              </Button>
            )}
            {onSettings && (
              <Button onClick={onSettings} size="icon" variant="ghost">
                <Settings className="h-5 w-5" />
                <span className="sr-only">Settings</span>
              </Button>
            )}
            {onLogout && (
              <Button onClick={onLogout} size="icon" variant="ghost">
                <LogOut className="h-5 w-5" />
                <span className="sr-only">Logout</span>
              </Button>
            )}
          </div>
        </div>

        {/* Messages area */}
        <ChatList messages={messages} className="flex-1" />

        {/* Input area */}
        <ChatInput
          currentMember={selectedMember}
          onSend={onSendMessage}
        />
      </div>

      {/* Online Users Sidebar - Right side */}
      {sidebarOpen && (
        <div className="w-64 flex-shrink-0">
          <OnlineUsersSidebar onlineUsers={onlineUsers} />
        </div>
      )}
    </div>
  )
}
