"use client"

import * as React from "react"
import { Menu, Settings, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ChatList } from "@/components/ui/chat-list"
import { ChatInput } from "@/components/ui/chat-input"
import { MemberSidebar } from "@/components/ui/member-sidebar"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import type { Member, Message } from "@/lib/store"

interface ChatInterfaceProps {
  members: Member[]
  messages: Message[]
  selectedMember?: Member | null
  onSelectMember: (member: Member) => void
  onSendMessage: (message: string) => void
  onAddMember?: () => void
  onSettings?: () => void
  onLogout?: () => void
  sidebarOpen?: boolean
  onToggleSidebar?: () => void
  className?: string
}

export function ChatInterface({
  members,
  messages,
  selectedMember,
  onSelectMember,
  onSendMessage,
  onAddMember,
  onSettings,
  onLogout,
  sidebarOpen = true,
  onToggleSidebar,
  className,
}: ChatInterfaceProps) {
  return (
    <div className={cn("flex h-screen bg-background", className)}>
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-80 flex-shrink-0">
          <MemberSidebar
            members={members}
            selectedMember={selectedMember}
            onSelectMember={onSelectMember}
            onAddMember={onAddMember}
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

            {selectedMember ? (
              <div className="flex items-center gap-2">
                <div
                  className="h-2 w-2 rounded-full"
                  style={{
                    backgroundColor: selectedMember.color || "hsl(var(--primary))",
                  }}
                />
                <h1 className="font-semibold text-lg">
                  {selectedMember.name}
                  {selectedMember.pronouns && (
                    <span className="text-sm font-normal text-muted-foreground ml-2">
                      ({selectedMember.pronouns})
                    </span>
                  )}
                </h1>
              </div>
            ) : (
              <h1 className="font-semibold text-lg text-muted-foreground">
                Plural Chat
              </h1>
            )}
          </div>

          <div className="flex items-center gap-2">
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
    </div>
  )
}
