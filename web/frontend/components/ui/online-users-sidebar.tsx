"use client"

import * as React from "react"
import { Users, Circle } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import type { User } from "@/lib/store"

interface OnlineUsersSidebarProps {
  onlineUsers: User[]
  className?: string
}

export function OnlineUsersSidebar({
  onlineUsers,
  className,
}: OnlineUsersSidebarProps) {
  // Get initials for avatar fallback
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className={cn("flex flex-col h-full bg-background border-l", className)}>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Users className="h-5 w-5" />
            Online Users
          </h2>
          <span className="text-sm text-muted-foreground">
            {onlineUsers.length}
          </span>
        </div>
      </div>

      <Separator />

      {/* User list */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {onlineUsers.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground text-sm">
              No users online
            </div>
          ) : (
            onlineUsers.map((user) => {
              const userColor = user.theme_color || "hsl(var(--primary))"
              const initials = getInitials(user.username)

              return (
                <div
                  key={user.id}
                  className="w-full flex items-center gap-3 p-3 rounded-md hover:bg-accent/50 transition-colors"
                >
                  {/* Avatar with online indicator */}
                  <div className="relative">
                    <Avatar className="h-10 w-10 ring-2 ring-border flex-shrink-0">
                      {user.avatar_path ? (
                        <AvatarImage
                          src={`http://localhost:8000${user.avatar_path}`}
                          alt={user.username}
                        />
                      ) : null}
                      <AvatarFallback
                        style={{ backgroundColor: userColor }}
                        className="text-white font-semibold text-sm"
                      >
                        {initials}
                      </AvatarFallback>
                    </Avatar>
                    {/* Online status indicator */}
                    <Circle
                      className="absolute bottom-0 right-0 h-3 w-3 fill-green-500 text-green-500 ring-2 ring-background"
                    />
                  </div>

                  {/* User info */}
                  <div className="flex-1 min-w-0">
                    <div
                      className="font-semibold text-sm truncate"
                      style={{ color: userColor }}
                    >
                      {user.username}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Online
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
