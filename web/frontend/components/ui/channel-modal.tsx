"use client"

import * as React from "react"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import type { Channel } from "@/lib/api"

interface ChannelModalProps {
  channel?: Channel | null  // If provided, edit mode
  open: boolean
  onClose: () => void
  onSave: (data: {
    name: string
    description?: string
    color?: string
    emoji?: string
  }) => Promise<void>
  onDelete?: () => Promise<void>
}

const DEFAULT_COLORS = [
  { name: "Blue", value: "#3b82f6" },
  { name: "Green", value: "#10b981" },
  { name: "Yellow", value: "#f59e0b" },
  { name: "Purple", value: "#8b5cf6" },
  { name: "Red", value: "#ef4444" },
  { name: "Cyan", value: "#06b6d4" },
  { name: "Orange", value: "#f97316" },
  { name: "Pink", value: "#ec4899" },
]

const DEFAULT_EMOJIS = [
  "💬", "💭", "📝", "🎨", "🎮", "📚", "💼", "❤️",
  "📋", "🔔", "🎉", "⚡", "🔥", "🌟", "💡", "🚀"
]

export function ChannelModal({
  channel,
  open,
  onClose,
  onSave,
  onDelete,
}: ChannelModalProps) {
  const [name, setName] = React.useState(channel?.name || "")
  const [description, setDescription] = React.useState(channel?.description || "")
  const [color, setColor] = React.useState(channel?.color || DEFAULT_COLORS[0].value)
  const [emoji, setEmoji] = React.useState(channel?.emoji || DEFAULT_EMOJIS[0])
  const [loading, setLoading] = React.useState(false)

  // Reset form when channel changes
  React.useEffect(() => {
    setName(channel?.name || "")
    setDescription(channel?.description || "")
    setColor(channel?.color || DEFAULT_COLORS[0].value)
    setEmoji(channel?.emoji || DEFAULT_EMOJIS[0])
  }, [channel])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!name.trim()) return

    setLoading(true)
    try {
      await onSave({
        name: name.trim(),
        description: description.trim() || undefined,
        color,
        emoji,
      })
      onClose()
    } catch (error) {
      console.error("Failed to save channel:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete || !channel) return

    if (confirm(`Are you sure you want to delete #${channel.name}?`)) {
      setLoading(true)
      try {
        await onDelete()
        onClose()
      } catch (error) {
        console.error("Failed to delete channel:", error)
      } finally {
        setLoading(false)
      }
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-background rounded-lg shadow-lg w-full max-w-md p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">
            {channel ? "Edit Channel" : "Create Channel"}
          </h2>
          <Button
            size="icon"
            variant="ghost"
            onClick={onClose}
            disabled={loading}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label htmlFor="name" className="text-sm font-medium block mb-2">
              Channel Name *
            </label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="general"
              required
              disabled={loading}
              maxLength={100}
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="text-sm font-medium block mb-2">
              Description
            </label>
            <Input
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What's this channel for?"
              disabled={loading}
            />
          </div>

          {/* Emoji Picker */}
          <div>
            <label className="text-sm font-medium block mb-2">
              Icon Emoji
            </label>
            <div className="flex flex-wrap gap-2">
              {DEFAULT_EMOJIS.map((e) => (
                <button
                  key={e}
                  type="button"
                  onClick={() => setEmoji(e)}
                  className={cn(
                    "text-2xl p-2 rounded hover:bg-accent transition-colors",
                    emoji === e && "bg-accent ring-2 ring-ring"
                  )}
                  disabled={loading}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>

          {/* Color Picker */}
          <div>
            <label className="text-sm font-medium block mb-2">
              Color
            </label>
            <div className="flex flex-wrap gap-2">
              {DEFAULT_COLORS.map((c) => (
                <button
                  key={c.value}
                  type="button"
                  onClick={() => setColor(c.value)}
                  className={cn(
                    "h-8 w-8 rounded-full transition-transform hover:scale-110",
                    color === c.value && "ring-2 ring-ring ring-offset-2"
                  )}
                  style={{ backgroundColor: c.value }}
                  title={c.name}
                  disabled={loading}
                />
              ))}
            </div>
          </div>

          {/* Preview */}
          <div className="p-3 rounded-md bg-muted">
            <p className="text-xs text-muted-foreground mb-2">Preview:</p>
            <div className="flex items-center gap-2">
              <span className="text-xl">{emoji}</span>
              <span
                className="font-medium"
                style={{ color }}
              >
                {name || "channel-name"}
              </span>
            </div>
            {description && (
              <p className="text-sm text-muted-foreground mt-1">
                {description}
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-between gap-2 pt-2">
            {onDelete && channel && !channel.is_default ? (
              <Button
                type="button"
                variant="destructive"
                onClick={handleDelete}
                disabled={loading}
              >
                Delete
              </Button>
            ) : (
              <div />
            )}

            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading || !name.trim()}>
                {loading ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
