# shadcn/ui Chat Interface Components

This document describes the shadcn/ui-based chat interface components built for Plural Chat.

## 🎨 Component Architecture

All components are built on top of shadcn/ui base components using Radix UI primitives and styled with Tailwind CSS.

### Base Components (`components/ui/`)

These are standard shadcn/ui components:

#### `avatar.tsx`
- **Purpose**: Display user/member avatars with fallback initials
- **Primitives**: `@radix-ui/react-avatar`
- **Features**: Image loading, fallback text, customizable size
- **Usage**:
  ```tsx
  <Avatar>
    <AvatarImage src="/path/to/image.jpg" alt="Name" />
    <AvatarFallback>AB</AvatarFallback>
  </Avatar>
  ```

#### `button.tsx`
- **Purpose**: Clickable buttons with variants
- **Variants**: default, destructive, outline, secondary, ghost, link
- **Sizes**: default, sm, lg, icon
- **Usage**:
  ```tsx
  <Button variant="outline" size="sm">Click me</Button>
  ```

#### `input.tsx`
- **Purpose**: Text input fields
- **Features**: Focus states, disabled states, validation support
- **Usage**:
  ```tsx
  <Input placeholder="Type here..." />
  ```

#### `scroll-area.tsx`
- **Purpose**: Scrollable containers with custom scrollbars
- **Primitives**: `@radix-ui/react-scroll-area`
- **Features**: Custom styled scrollbars, smooth scrolling
- **Usage**:
  ```tsx
  <ScrollArea className="h-96">
    {/* Long content */}
  </ScrollArea>
  ```

#### `separator.tsx`
- **Purpose**: Visual dividers
- **Primitives**: `@radix-ui/react-separator`
- **Orientations**: horizontal, vertical
- **Usage**:
  ```tsx
  <Separator />
  ```

#### `tooltip.tsx`
- **Purpose**: Contextual information on hover
- **Primitives**: `@radix-ui/react-tooltip`
- **Features**: Customizable side, delay, animations
- **Usage**:
  ```tsx
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger>Hover me</TooltipTrigger>
      <TooltipContent>Info here</TooltipContent>
    </Tooltip>
  </TooltipProvider>
  ```

---

## 💬 Chat Interface Components

These are custom components built specifically for Plural Chat:

### `chat-message.tsx`
**Purpose**: Display individual chat messages with member info

**Props**:
- `message: Message` - Message object with member, content, timestamp
- `className?: string` - Optional styling

**Features**:
- Member avatar with fallback initials
- Member name with custom color
- Pronouns display
- Timestamp formatting (relative and absolute)
- Hover tooltips showing full member info
- Responsive layout

**Usage**:
```tsx
<ChatMessage message={messageObj} />
```

**Component location**: `/web/frontend/components/ui/chat-message.tsx:15`

---

### `chat-input.tsx`
**Purpose**: Message input area with auto-resize and member indicator

**Props**:
- `currentMember?: Member | null` - Currently selected member
- `onSend: (message: string) => void` - Callback when sending message
- `onMemberSwitch?: (member: Member) => void` - Optional member switch callback
- `placeholder?: string` - Input placeholder text
- `className?: string` - Optional styling

**Features**:
- Auto-resizing textarea (max 200px height)
- Current member indicator with color coding
- Send button (disabled when no member selected)
- Keyboard shortcuts:
  - `Enter` to send
  - `Shift + Enter` for new line
- Visual keyboard hints
- Disabled state when no member selected

**Usage**:
```tsx
<ChatInput
  currentMember={selectedMember}
  onSend={handleSend}
  placeholder="Type a message..."
/>
```

**Component location**: `/web/frontend/components/ui/chat-input.tsx:14`

---

### `chat-list.tsx`
**Purpose**: Scrollable list of messages with date separators

**Props**:
- `messages: Message[]` - Array of message objects
- `className?: string` - Optional styling

**Features**:
- Auto-scroll to bottom on new messages
- Date-based message grouping
- Smart date separators (Today, Yesterday, formatted dates)
- Empty state message
- Smooth scrolling
- Optimized re-rendering with memoization

**Usage**:
```tsx
<ChatList messages={messagesArray} />
```

**Component location**: `/web/frontend/components/ui/chat-list.tsx:11`

---

### `member-sidebar.tsx`
**Purpose**: Sidebar for browsing and selecting members

**Props**:
- `members: Member[]` - Array of member objects
- `selectedMember?: Member | null` - Currently selected member
- `onSelectMember: (member: Member) => void` - Callback when member selected
- `onAddMember?: () => void` - Optional callback for adding new member
- `className?: string` - Optional styling

**Features**:
- Search/filter members by name, pronouns, or description
- Member avatars with color-coded fallbacks
- Selected member highlight with color indicator
- Member count display
- Hover tooltips with full member details
- Keyboard navigation support
- Empty state handling
- Responsive design

**Usage**:
```tsx
<MemberSidebar
  members={membersArray}
  selectedMember={currentMember}
  onSelectMember={handleSelect}
  onAddMember={handleAdd}
/>
```

**Component location**: `/web/frontend/components/ui/member-sidebar.tsx:13`

---

### `chat-interface.tsx`
**Purpose**: Complete chat interface combining all components

**Props**:
- `members: Member[]` - All available members
- `messages: Message[]` - All messages to display
- `selectedMember?: Member | null` - Currently selected member
- `onSelectMember: (member: Member) => void` - Member selection handler
- `onSendMessage: (message: string) => void` - Send message handler
- `onAddMember?: () => void` - Add member handler
- `onSettings?: () => void` - Settings handler
- `onLogout?: () => void` - Logout handler
- `sidebarOpen?: boolean` - Sidebar visibility state
- `onToggleSidebar?: () => void` - Sidebar toggle handler
- `className?: string` - Optional styling

**Features**:
- Complete chat layout (sidebar + main area)
- Top header with current member display
- Toggle sidebar button
- Settings and logout buttons
- Message list area
- Message input area
- Fully responsive
- Handles empty states

**Usage**:
```tsx
<ChatInterface
  members={members}
  messages={messages}
  selectedMember={selectedMember}
  onSelectMember={setSelectedMember}
  onSendMessage={handleSend}
  onAddMember={handleAdd}
  onSettings={handleSettings}
  onLogout={handleLogout}
  sidebarOpen={sidebarOpen}
  onToggleSidebar={toggleSidebar}
/>
```

**Component location**: `/web/frontend/components/ui/chat-interface.tsx:15`

---

## 🎨 Theming

All components use CSS variables defined in `app/globals.css`:

### Color Variables
- `--background` - Main background color
- `--foreground` - Main text color
- `--primary` - Primary brand color
- `--muted` - Muted/subtle color
- `--accent` - Accent/hover color
- `--border` - Border color
- etc.

### Dark Mode
Add `class="dark"` to any parent element to enable dark mode. All components support dark mode automatically.

### Customization
Modify `tailwind.config.ts` to customize:
- Color palette
- Border radius
- Spacing
- Fonts
- Animations

---

## 📦 Dependencies

### Required npm packages:
```json
{
  "@radix-ui/react-avatar": "^1.1.1",
  "@radix-ui/react-scroll-area": "^1.2.0",
  "@radix-ui/react-separator": "^1.1.1",
  "@radix-ui/react-slot": "^1.1.1",
  "@radix-ui/react-tooltip": "^1.1.5",
  "class-variance-authority": "^0.7.1",
  "clsx": "^2.1.1",
  "date-fns": "^4.1.0",
  "lucide-react": "^0.460.0",
  "tailwind-merge": "^2.5.4",
  "tailwindcss-animate": "^1.0.7"
}
```

---

## 🚀 Usage Examples

### Complete Chat Page
See `app/page.tsx` for full implementation example.

### Standalone Components
Import individual components:
```tsx
import { ChatMessage } from '@/components/ui/chat-message'
import { MemberSidebar } from '@/components/ui/member-sidebar'
```

Or import from index:
```tsx
import { ChatMessage, MemberSidebar } from '@/components/ui'
```

---

## 🔧 Development

### Adding New Components
Use the shadcn CLI to add more components:
```bash
npx shadcn@latest add <component-name>
```

### Component Guidelines
1. Use TypeScript for type safety
2. Use `"use client"` directive for interactive components
3. Follow Radix UI patterns for accessibility
4. Use `cn()` utility for className merging
5. Support dark mode via CSS variables
6. Add proper ARIA labels
7. Make components keyboard navigable

---

## 🎯 Benefits Over Ant Design

1. **Smaller Bundle Size**: Tree-shakeable, only import what you use
2. **Better Customization**: Full control over styling with Tailwind
3. **Modern Patterns**: Built with React Server Components in mind
4. **Accessibility**: Radix UI primitives follow WAI-ARIA standards
5. **Type Safety**: Full TypeScript support
6. **Dark Mode**: Built-in dark mode support
7. **Performance**: Optimized with modern React patterns

---

## 📝 Migration Notes

### Old Components → New Components

- `components/ChatMessage.tsx` → `components/ui/chat-message.tsx`
- `components/MessageInput.tsx` → `components/ui/chat-input.tsx`
- `components/ChatList.tsx` → `components/ui/chat-list.tsx`
- `components/MemberSidebar.tsx` → `components/ui/member-sidebar.tsx`

### Main Changes
1. Ant Design components replaced with shadcn/ui
2. Better TypeScript types
3. Improved accessibility
4. Enhanced keyboard navigation
5. Smoother animations
6. Better dark mode support

---

## 🐛 Troubleshooting

### Components not rendering?
- Check that all dependencies are installed: `npm install`
- Verify `tsconfig.json` has correct path aliases
- Ensure `globals.css` is imported in `layout.tsx`

### Styling issues?
- Verify `tailwind.config.ts` includes correct content paths
- Check that Tailwind CSS is properly configured
- Ensure CSS variables are defined in `globals.css`

### TypeScript errors?
- Run `npm install` to install type definitions
- Check that imports match exact file names
- Verify `@/` path alias is working

---

**Created with**: shadcn/ui, Radix UI, Tailwind CSS, TypeScript
**For**: Plural Chat Web Edition
**Last Updated**: 2025-11-07
