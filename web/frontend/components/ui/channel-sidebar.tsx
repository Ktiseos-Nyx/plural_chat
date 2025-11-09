"use client"

import * as React from "react"
import { Hash, Plus, Settings, Archive, ChevronDown, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import type { Channel } from "@/lib/api"

interface ChannelSidebarProps {
  channels: Channel[]
  selectedChannel?: Channel | null
  onSelectChannel: (channel: Channel) => void
  onCreateChannel?: () => void
  onEditChannel?: (channel: Channel) => void
  showArchived?: boolean
  onToggleArchived?: () => void
  className?: string
}

export function ChannelSidebar({
  channels,
  selectedChannel,
  onSelectChannel,
  onCreateChannel,
  onEditChannel,
  showArchived = false,
  onToggleArchived,
  className,
}: ChannelSidebarProps) {
  // Separate active and archived channels
  const activeChannels = React.useMemo(
    () => channels.filter((ch) => !ch.is_archived),
    [channels]
  )

  const archivedChannels = React.useMemo(
    () => channels.filter((ch) => ch.is_archived),
    [channels]
  )

  const renderChannel = (channel: Channel) => {
    const isSelected = selectedChannel?.id === channel.id
    const channelColor = channel.color || "hsl(var(--primary))"
    const emoji = channel.emoji || "💬"

    return (
      <div
        key={channel.id}
        className={cn(
          "w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-sm group",
          "hover:bg-accent transition-colors",
          isSelected && "bg-accent font-medium"
        )}
        style={
          isSelected
            ? { borderLeft: `3px solid ${channelColor}` }
            : undefined
        }
      >
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => onSelectChannel(channel)}
                className="flex items-center gap-2 flex-1 min-w-0 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
              >
                <span className="text-base flex-shrink-0">{emoji}</span>
                <span
                  className="flex-1 truncate"
                  style={isSelected ? { color: channelColor } : undefined}
                >
                  {channel.name}
                </span>
                {channel.message_count !== undefined && channel.message_count > 0 && (
                  <span className="text-xs text-muted-foreground">
                    {channel.message_count}
                  </span>
                )}
              </button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <div className="space-y-1">
                <p className="font-semibold">{emoji} {channel.name}</p>
                {channel.description && (
                  <p className="text-xs">{channel.description}</p>
                )}
                {channel.message_count !== undefined && (
                  <p className="text-xs text-muted-foreground">
                    {channel.message_count} {channel.message_count === 1 ? "message" : "messages"}
                  </p>
                )}
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        {onEditChannel && (
          <Button
            size="icon"
            variant="ghost"
            className="h-6 w-6 opacity-0 group-hover:opacity-100 flex-shrink-0"
            onClick={(e) => {
              e.stopPropagation()
              onEditChannel(channel)
            }}
          >
            <Settings className="h-3 w-3" />
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className={cn("flex flex-col h-full bg-background border-r", className)}>
      {/* Header */}
      <div className="p-3 border-b">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <Hash className="h-4 w-4" />
            Channels
          </h2>
          {onCreateChannel && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button onClick={onCreateChannel} size="icon" variant="ghost" className="h-6 w-6">
                    <Plus className="h-4 w-4" />
                    <span className="sr-only">Create channel</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Create channel</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
      </div>

      {/* Active Channels */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-0.5">
          {activeChannels.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground text-sm">
              No channels yet
            </div>
          ) : (
            activeChannels.map(renderChannel)
          )}
        </div>

        {/* Archived Channels Section */}
        {archivedChannels.length > 0 && (
          <>
            <Separator className="my-2" />
            <div className="px-2">
              <button
                onClick={onToggleArchived}
                className={cn(
                  "w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-sm",
                  "hover:bg-accent transition-colors text-left",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                )}
              >
                {showArchived ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
                <Archive className="h-4 w-4" />
                <span className="flex-1">Archived</span>
                <span className="text-xs text-muted-foreground">
                  {archivedChannels.length}
                </span>
              </button>

              {showArchived && (
                <div className="mt-1 space-y-0.5 pl-2">
                  {archivedChannels.map(renderChannel)}
                </div>
              )}
            </div>
          </>
        )}
      </ScrollArea>
    </div>
  )
}
