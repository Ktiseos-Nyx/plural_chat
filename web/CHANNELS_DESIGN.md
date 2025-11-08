# 🗨️ Channels/Rooms Feature Design

## 📋 Overview

Channels allow users to organize conversations into different topics or contexts, similar to Discord channels. Each channel can contain messages from any system member.

## 🎯 Use Cases

### For Plural Systems:
- **#general** - Day-to-day conversations
- **#memories** - Sharing and documenting memories
- **#planning** - System coordination and planning
- **#journaling** - Private thoughts and reflections
- **#creative** - Writing, art, creative projects
- **#venting** - Safe space for emotions
- **#fronting-log** - Track who's fronting when

### For Roleplayers/Writers:
- **#worldbuilding** - Story development
- **#character-development** - Character conversations
- **#scenes** - Roleplay scenes
- **#ooc** - Out-of-character discussion

### For Everyone:
- **Topic-based organization** - Separate work, personal, hobbies
- **Context switching** - Different channels for different moods/needs
- **Privacy** - Keep certain conversations separate

## 📊 Database Schema

### New Table: `channels`

```sql
CREATE TABLE channels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7),  -- Hex color like #8b5cf6
    emoji VARCHAR(10),  -- Optional emoji icon
    is_default BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    position INTEGER DEFAULT 0,  -- For custom ordering
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, name)  -- Channel names must be unique per user
);

CREATE INDEX idx_channels_user_id ON channels(user_id);
CREATE INDEX idx_channels_is_archived ON channels(is_archived);
```

### Update Table: `messages`

```sql
ALTER TABLE messages ADD COLUMN channel_id INTEGER;
ALTER TABLE messages ADD CONSTRAINT fk_messages_channel
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE SET NULL;

CREATE INDEX idx_messages_channel_id ON messages(channel_id);
```

**Migration Strategy:**
1. Create `channels` table
2. Add `channel_id` column to `messages` table (nullable initially)
3. For each user, create a default "#general" channel
4. Update all existing messages to belong to the default channel
5. Make `channel_id` non-nullable (optional)

## 🏗️ Backend API

### Channel Endpoints

#### `POST /channels/` - Create Channel
```python
{
  "name": "memories",
  "description": "Our shared memories and experiences",
  "color": "#10b981",
  "emoji": "💭"
}
```

**Response:**
```python
{
  "id": 1,
  "user_id": 1,
  "name": "memories",
  "description": "Our shared memories and experiences",
  "color": "#10b981",
  "emoji": "💭",
  "is_default": False,
  "is_archived": False,
  "position": 1,
  "created_at": "2025-01-08T00:00:00Z",
  "message_count": 0
}
```

#### `GET /channels/` - List Channels
Returns all channels for the current user, ordered by `position`.

**Response:**
```python
[
  {
    "id": 1,
    "name": "general",
    "description": "General chat",
    "color": "#6366f1",
    "emoji": "💬",
    "is_default": True,
    "is_archived": False,
    "position": 0,
    "message_count": 152
  },
  {
    "id": 2,
    "name": "memories",
    "description": "Our shared memories",
    "color": "#10b981",
    "emoji": "💭",
    "is_default": False,
    "is_archived": False,
    "position": 1,
    "message_count": 47
  }
]
```

#### `GET /channels/{channel_id}` - Get Channel
Returns a single channel with details.

#### `PATCH /channels/{channel_id}` - Update Channel
```python
{
  "name": "old-memories",
  "description": "Updated description",
  "color": "#8b5cf6"
}
```

#### `DELETE /channels/{channel_id}` - Delete Channel
Deletes a channel. Cannot delete the default channel.

**Options:**
- `?delete_messages=true` - Also delete all messages in the channel
- `?delete_messages=false` (default) - Set message `channel_id` to NULL

#### `POST /channels/{channel_id}/archive` - Archive Channel
Archives a channel (hides from main list but keeps messages).

#### `POST /channels/{channel_id}/unarchive` - Unarchive Channel

#### `POST /channels/reorder` - Reorder Channels
```python
{
  "channel_ids": [1, 3, 2, 4]  // New order
}
```

### Updated Message Endpoints

#### `GET /messages/` - Get Messages
Add `channel_id` query parameter:
```
GET /messages/?channel_id=2&limit=50
```

#### `POST /messages/` - Create Message
Add `channel_id` to request body:
```python
{
  "member_id": 1,
  "channel_id": 2,
  "content": "Hello from the memories channel!"
}
```

## 🎨 Frontend Components

### 1. Channel Sidebar Component

**File:** `components/ui/channel-sidebar.tsx`

```tsx
interface ChannelSidebarProps {
  channels: Channel[]
  selectedChannel: Channel | null
  onSelectChannel: (channel: Channel) => void
  onCreateChannel?: () => void
  onEditChannel?: (channel: Channel) => void
  onArchiveChannel?: (channel: Channel) => void
  showArchived?: boolean
}
```

**Features:**
- List of channels with icons/emojis
- Current channel highlighted
- Message count badges
- Create channel button
- Right-click context menu (edit, archive, delete)
- Drag-to-reorder
- Show/hide archived toggle

**UI Layout:**
```
┌─────────────────────┐
│ 💬 Channels        + │
├─────────────────────┤
│ 💬 general     (152)│ <- Default, highlighted
│ 💭 memories     (47)│
│ 📝 planning     (23)│
│ 🎨 creative      (8)│
├─────────────────────┤
│ 📦 Archived      ▼  │
│   📜 old-logs   (99)│
└─────────────────────┘
```

### 2. Channel Header Component

**File:** `components/ui/channel-header.tsx`

Shows current channel info in the chat header:
```tsx
<ChannelHeader
  channel={selectedChannel}
  onEditChannel={() => {}}
  onDeleteChannel={() => {}}
/>
```

**Display:**
```
💭 memories  •  Our shared memories and experiences  •  47 messages
```

### 3. Create/Edit Channel Modal

**File:** `components/ui/channel-modal.tsx`

Form with:
- Channel name (required, unique)
- Description (optional)
- Color picker
- Emoji picker
- Archive toggle
- Delete button (if editing)

### 4. Channel Switcher (Quick Switcher)

**Keyboard shortcut:** `Ctrl+K` or `Cmd+K`

Quick search/filter to switch channels:
```
Type to search channels...
> mem█

Results:
💭 memories
📜 old-memories (archived)
```

## 🗂️ State Management

### Update `lib/store.ts`

```typescript
export interface Channel {
  id: number
  user_id: number
  name: string
  description?: string
  color?: string
  emoji?: string
  is_default: boolean
  is_archived: boolean
  position: number
  created_at: string
  message_count?: number
}

interface AppState {
  // ... existing state

  // Channels
  channels: Channel[]
  setChannels: (channels: Channel[]) => void
  selectedChannel: Channel | null
  setSelectedChannel: (channel: Channel | null) => void
  addChannel: (channel: Channel) => void
  updateChannel: (id: number, updates: Partial<Channel>) => void
  deleteChannel: (id: number) => void
}
```

## 🔄 WebSocket Updates

### Message Event Format

Update WebSocket message events to include channel info:

```typescript
{
  type: "new_message",
  data: {
    id: 123,
    member_id: 5,
    channel_id: 2,  // <- Add this
    content: "Hello!",
    timestamp: "2025-01-08T00:00:00Z",
    member: { ... }
  }
}
```

### Channel Events

New WebSocket events:

```typescript
// Channel created
{
  type: "channel_created",
  data: { id: 3, name: "new-channel", ... }
}

// Channel updated
{
  type: "channel_updated",
  data: { id: 2, name: "updated-name", ... }
}

// Channel deleted
{
  type: "channel_deleted",
  data: { id: 4 }
}
```

## 🎯 UI/UX Features

### Default Channel Behavior
- Every user gets a "#general" channel on signup
- Cannot delete the default channel
- If default is archived, set another channel as default

### Channel Creation Flow
1. Click "+" button in channel sidebar
2. Modal opens with form
3. Name and color required, rest optional
4. On save, channel appears in sidebar
5. Auto-switch to new channel

### Message Filtering
- Messages only show for the selected channel
- Clear visual indicator of current channel
- Unread message badges per channel

### Channel Colors
Channels can have custom colors for visual distinction:
- Applies to channel name in sidebar
- Applies to channel indicator in header
- Default color palette provided

### Keyboard Shortcuts
- `Ctrl/Cmd + K` - Quick channel switcher
- `Alt + ↑/↓` - Navigate channels
- `Ctrl/Cmd + 1-9` - Jump to channels 1-9

## 📱 Mobile Considerations

### Responsive Design
- On mobile: Channels in a slide-out drawer
- Tab bar with channel switcher button
- Swipe between channels
- Long-press for channel options

## 🔒 Permissions & Privacy

### Current Design (Single User)
- All channels belong to the user
- All members can post in all channels
- No cross-user channels (for now)

### Future Multi-User Features
- Shared channels between users
- Channel permissions (read-only, posting rights)
- Private vs public channels

## 🚀 Implementation Plan

### Phase 1: Backend (Estimated: 2-3 hours)
1. ✅ Create Channel model in database.py
2. ✅ Create database migration script
3. ✅ Create channel router with CRUD endpoints
4. ✅ Update message endpoints to filter by channel
5. ✅ Update WebSocket to broadcast channel events
6. ✅ Add channel_id to message creation

### Phase 2: Frontend Components (Estimated: 3-4 hours)
1. ✅ Create ChannelSidebar component
2. ✅ Create ChannelHeader component
3. ✅ Create ChannelModal (create/edit)
4. ✅ Update ChatInterface to include channel sidebar
5. ✅ Add state management for channels

### Phase 3: Integration (Estimated: 1-2 hours)
1. ✅ Update main page to load channels
2. ✅ Filter messages by selected channel
3. ✅ Update WebSocket handlers
4. ✅ Test channel switching
5. ✅ Test message sending to different channels

### Phase 4: Polish (Estimated: 1-2 hours)
1. ✅ Add keyboard shortcuts
2. ✅ Add drag-to-reorder
3. ✅ Add unread badges
4. ✅ Add channel search/quick switcher
5. ✅ Mobile responsive design

## 📚 API Examples

### Full Channel Workflow

```typescript
// 1. Load channels on app start
const channels = await channelsAPI.getAll()
setChannels(channels)
setSelectedChannel(channels.find(c => c.is_default))

// 2. Create a new channel
const newChannel = await channelsAPI.create({
  name: "memories",
  description: "Our shared memories",
  color: "#10b981",
  emoji: "💭"
})
addChannel(newChannel)

// 3. Load messages for a channel
const messages = await messagesAPI.getRecent(50, selectedChannel.id)
setMessages(messages)

// 4. Send message to a channel
const message = await messagesAPI.create({
  member_id: selectedMember.id,
  channel_id: selectedChannel.id,
  content: "Hello!"
})
addMessage(message)

// 5. Switch channels
setSelectedChannel(newChannel)
const newMessages = await messagesAPI.getRecent(50, newChannel.id)
setMessages(newMessages)
```

## 🎨 Visual Design

### Channel Colors
Pre-defined color palette:
- 🔵 Blue: `#3b82f6` - General/default
- 💚 Green: `#10b981` - Memories/positive
- 💛 Yellow: `#f59e0b` - Planning/important
- 💜 Purple: `#8b5cf6` - Creative/fun
- ❤️ Red: `#ef4444` - Venting/emotions
- 🩵 Cyan: `#06b6d4` - Journaling/personal
- 🧡 Orange: `#f97316` - Projects/work
- 🩷 Pink: `#ec4899` - Social/relationships

### Emoji Support
Allow users to pick emojis for channels:
- 💬 General chat
- 💭 Thoughts/memories
- 📝 Notes/planning
- 🎨 Creative
- 🎮 Gaming
- 📚 Learning
- 💼 Work
- ❤️ Relationships

## 🔮 Future Enhancements

### v2.0 Features
- [ ] Channel templates (auto-create common channel sets)
- [ ] Channel categories/folders
- [ ] Channel icons (upload custom images)
- [ ] Channel descriptions in markdown
- [ ] Channel search within messages
- [ ] Pin messages to channels
- [ ] Channel-specific member filters
- [ ] Export channel to file
- [ ] Channel statistics/insights

### Multi-User Features (Future)
- [ ] Shared channels between systems
- [ ] Channel invitations
- [ ] Read/write permissions
- [ ] Channel moderation
- [ ] Muted channels
- [ ] Channel notifications settings

---

**Ready to implement?** Let's start with Phase 1 - the backend! 🚀
