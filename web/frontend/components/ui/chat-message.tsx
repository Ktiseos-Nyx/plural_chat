"use client"

import * as React from "react"
import { format } from "date-fns"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import type { Message } from "@/lib/store"

interface ChatMessageProps {
  message: Message
  className?: string
}

export function ChatMessage({ message, className }: ChatMessageProps) {
  const { member, content, timestamp } = message

  // Format timestamp
  const timeString = format(new Date(timestamp), "h:mm a")
  const fullTimeString = format(new Date(timestamp), "PPP 'at' p")

  // Get member color or use default
  const memberColor = member.color || "hsl(var(--primary))"

  // Get initials for avatar fallback
  const initials = member.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  return (
    <div
      className={cn(
        "group flex gap-3 px-4 py-2.5 hover:bg-accent/50 transition-colors",
        className
      )}
    >
      {/* Avatar */}
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex-shrink-0 pt-0.5">
              <Avatar className="h-10 w-10 ring-2 ring-border">
                {member.avatar_path ? (
                  <AvatarImage
                    src={`/api/avatars/${member.avatar_path}`}
                    alt={member.name}
                  />
                ) : null}
                <AvatarFallback
                  style={{ backgroundColor: memberColor }}
                  className="text-white font-semibold"
                >
                  {initials}
                </AvatarFallback>
              </Avatar>
            </div>
          </TooltipTrigger>
          <TooltipContent side="right" className="max-w-xs">
            <div className="space-y-1">
              <p className="font-semibold">{member.name}</p>
              {member.pronouns && (
                <p className="text-xs text-muted-foreground">
                  {member.pronouns}
                </p>
              )}
              {member.description && (
                <p className="text-xs">{member.description}</p>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        {/* Header with name and timestamp */}
        <div className="flex items-baseline gap-2 mb-1">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <span
                  style={{ color: memberColor }}
                  className="font-semibold text-[15px] hover:underline cursor-pointer"
                >
                  {member.name}
                </span>
              </TooltipTrigger>
              <TooltipContent>
                <p className="text-xs">{fullTimeString}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {member.pronouns && (
            <span className="text-xs text-muted-foreground font-normal">
              ({member.pronouns})
            </span>
          )}

          <span className="text-xs text-muted-foreground font-normal">
            {timeString}
          </span>
        </div>

        {/* Message text */}
        <div className="text-[15px] text-foreground leading-relaxed break-words whitespace-pre-wrap">
          {content}
        </div>
      </div>
    </div>
  )
}
