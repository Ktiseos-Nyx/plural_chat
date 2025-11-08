"use client"

import * as React from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ChatMessage } from "@/components/ui/chat-message"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"
import type { Message } from "@/lib/store"
import { format, isToday, isYesterday, isSameDay } from "date-fns"

interface ChatListProps {
  messages: Message[]
  className?: string
}

export function ChatList({ messages, className }: ChatListProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  // Group messages by date
  const groupedMessages = React.useMemo(() => {
    const groups: Array<{ date: Date; messages: Message[] }> = []

    messages.forEach((message) => {
      const messageDate = new Date(message.timestamp)
      const lastGroup = groups[groups.length - 1]

      if (!lastGroup || !isSameDay(lastGroup.date, messageDate)) {
        groups.push({
          date: messageDate,
          messages: [message],
        })
      } else {
        lastGroup.messages.push(message)
      }
    })

    return groups
  }, [messages])

  // Format date separator
  const formatDateSeparator = (date: Date) => {
    if (isToday(date)) return "Today"
    if (isYesterday(date)) return "Yesterday"
    return format(date, "MMMM d, yyyy")
  }

  return (
    <ScrollArea className={cn("flex-1", className)}>
      <div ref={scrollRef} className="flex flex-col">
        {groupedMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full p-8">
            <div className="text-center text-muted-foreground">
              <p className="text-lg font-medium mb-2">No messages yet</p>
              <p className="text-sm">Start a conversation!</p>
            </div>
          </div>
        ) : (
          groupedMessages.map((group, groupIndex) => (
            <div key={groupIndex}>
              {/* Date separator */}
              <div className="flex items-center gap-4 px-4 py-4">
                <Separator className="flex-1" />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  {formatDateSeparator(group.date)}
                </span>
                <Separator className="flex-1" />
              </div>

              {/* Messages for this date */}
              {group.messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </div>
          ))
        )}
      </div>
    </ScrollArea>
  )
}
