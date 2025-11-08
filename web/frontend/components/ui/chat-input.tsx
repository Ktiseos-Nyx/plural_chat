"use client"

import * as React from "react"
import { Send, AtSign } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { Member } from "@/lib/store"

interface ChatInputProps {
  currentMember?: Member | null
  onSend: (message: string) => void
  onMemberSwitch?: (member: Member) => void
  placeholder?: string
  className?: string
}

export function ChatInput({
  currentMember,
  onSend,
  onMemberSwitch,
  placeholder = "Type a message...",
  className,
}: ChatInputProps) {
  const [message, setMessage] = React.useState("")
  const textareaRef = React.useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && currentMember) {
      onSend(message)
      setMessage("")
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto"
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Auto-resize textarea
  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  const memberColor = currentMember?.color || "hsl(var(--primary))"

  return (
    <div className={cn("border-t bg-background", className)}>
      {/* Current member indicator */}
      {currentMember && (
        <div
          className="px-4 py-2 text-sm border-b bg-muted/30"
          style={{ borderLeftColor: memberColor, borderLeftWidth: 3 }}
        >
          <div className="flex items-center gap-2">
            <AtSign className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium" style={{ color: memberColor }}>
              {currentMember.name}
            </span>
            {currentMember.pronouns && (
              <span className="text-muted-foreground">
                ({currentMember.pronouns})
              </span>
            )}
          </div>
        </div>
      )}

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex items-end gap-2 p-4">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              currentMember
                ? placeholder
                : "Select a member to start chatting..."
            }
            disabled={!currentMember}
            rows={1}
            className={cn(
              "w-full resize-none rounded-md border border-input bg-background px-3 py-2",
              "text-sm ring-offset-background placeholder:text-muted-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "max-h-[200px] overflow-y-auto"
            )}
          />
        </div>

        <Button
          type="submit"
          size="icon"
          disabled={!message.trim() || !currentMember}
          className="flex-shrink-0"
        >
          <Send className="h-4 w-4" />
          <span className="sr-only">Send message</span>
        </Button>
      </form>

      {/* Keyboard hint */}
      <div className="px-4 pb-2 text-xs text-muted-foreground">
        <kbd className="px-1.5 py-0.5 rounded bg-muted font-mono">Enter</kbd> to
        send,{" "}
        <kbd className="px-1.5 py-0.5 rounded bg-muted font-mono">
          Shift + Enter
        </kbd>{" "}
        for new line
      </div>
    </div>
  )
}
