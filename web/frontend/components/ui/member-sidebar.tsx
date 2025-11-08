"use client"

import * as React from "react"
import { User, Plus, Search } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import type { Member } from "@/lib/store"

interface MemberSidebarProps {
  members: Member[]
  selectedMember?: Member | null
  onSelectMember: (member: Member) => void
  className?: string
}

export function MemberSidebar({
  members,
  selectedMember,
  onSelectMember,
  className,
}: MemberSidebarProps) {
  const [searchQuery, setSearchQuery] = React.useState("")

  // Filter members based on search
  const filteredMembers = React.useMemo(() => {
    if (!searchQuery.trim()) return members
    const query = searchQuery.toLowerCase()
    return members.filter(
      (member) =>
        member.name.toLowerCase().includes(query) ||
        member.pronouns?.toLowerCase().includes(query) ||
        member.description?.toLowerCase().includes(query)
    )
  }, [members, searchQuery])

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
    <div className={cn("flex flex-col h-full bg-background border-r", className)}>
      {/* Header */}
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <User className="h-5 w-5" />
            Members
          </h2>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search members..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8"
          />
        </div>
      </div>

      {/* Member count */}
      <div className="px-4 py-2 text-xs text-muted-foreground">
        {filteredMembers.length} {filteredMembers.length === 1 ? "member" : "members"}
        {searchQuery && ` (filtered from ${members.length})`}
      </div>

      <Separator />

      {/* Member list */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {filteredMembers.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground text-sm">
              {searchQuery ? "No members found" : "No members yet"}
            </div>
          ) : (
            filteredMembers.map((member) => {
              const isSelected = selectedMember?.id === member.id
              const memberColor = member.color || "hsl(var(--primary))"
              const initials = getInitials(member.name)

              return (
                <TooltipProvider key={member.id}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => onSelectMember(member)}
                        className={cn(
                          "w-full flex items-center gap-3 p-3 rounded-md",
                          "hover:bg-accent transition-colors text-left",
                          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                          isSelected && "bg-accent"
                        )}
                        style={
                          isSelected
                            ? { borderLeft: `3px solid ${memberColor}` }
                            : undefined
                        }
                      >
                        {/* Avatar */}
                        <Avatar className="h-10 w-10 ring-2 ring-border flex-shrink-0">
                          {member.avatar_path ? (
                            <AvatarImage
                              src={`/api/avatars/${member.avatar_path}`}
                              alt={member.name}
                            />
                          ) : null}
                          <AvatarFallback
                            style={{ backgroundColor: memberColor }}
                            className="text-white font-semibold text-sm"
                          >
                            {initials}
                          </AvatarFallback>
                        </Avatar>

                        {/* Member info */}
                        <div className="flex-1 min-w-0">
                          <div
                            className="font-semibold text-sm truncate"
                            style={{ color: memberColor }}
                          >
                            {member.name}
                          </div>
                          {member.pronouns && (
                            <div className="text-xs text-muted-foreground truncate">
                              {member.pronouns}
                            </div>
                          )}
                        </div>
                      </button>
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
                        {member.proxy_tags && (
                          <p className="text-xs font-mono text-muted-foreground">
                            Proxy: {member.proxy_tags}
                          </p>
                        )}
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              )
            })
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
