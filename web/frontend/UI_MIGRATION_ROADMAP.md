# UI Migration Roadmap: Ant Design → shadcn/ui

**Project**: Plural Chat Web Frontend
**Goal**: Migrate all UI components from Ant Design to shadcn/ui for consistency
**Status**: 🟡 In Progress
**Last Updated**: 2025-11-09

---

## 📋 Overview

The frontend currently has a **hybrid UI approach** that needs to be unified:
- ✅ **Main Chat Interface**: Already using shadcn/ui (correct!)
- ❌ **Settings Pages**: Using Ant Design (needs conversion)
- ❌ **Login/Auth Pages**: Using Ant Design (needs conversion)
- ❌ **Admin Panel**: Doesn't exist yet (needs to be built with shadcn/ui)

---

## ✅ Completed Work

### Phase 1: Setup & Infrastructure
- [x] Installed all required shadcn/ui components:
  - `card`, `tabs`, `form`, `dialog`, `table`, `alert`, `badge`
  - `dropdown-menu`, `label`, `textarea`, `select`, `switch`, `checkbox`
  - `toast`, `sonner` (for notifications)
- [x] Added `Toaster` component to root layout
- [x] Removed Ant Design `ConfigProvider` from layout
- [x] Set up toast notification system (`useToast` hook)

### Phase 2: Page Conversions
- [x] **Login Page** (`/app/login/page.tsx`)
  - Converted all Ant Design components to shadcn/ui
  - Replaced `Input`, `Button`, `Card`, `Alert` with shadcn versions
  - Updated icons from `@ant-design/icons` to `lucide-react`
  - Improved form accessibility with proper labels
  - Enhanced password input with icon positioning

- [x] **Main Settings Page** (`/app/settings/page.tsx`)
  - **MAJOR REWRITE** (998 lines → 1072 lines with shadcn/ui)
  - Converted from Ant Design `Tabs`, `Card`, `Form`, `Modal` to shadcn equivalents
  - Replaced `message.success/error` with `toast()` notifications
  - Converted `Upload` component to native HTML file input
  - Migrated all form controls to shadcn `Input`, `Label`, `Textarea`
  - Replaced `Modal` with shadcn `Dialog` for member add/edit
  - Updated `Tag` components to shadcn `Badge`
  - All four tabs working:
    - Profile (avatar, username, email, theme color, password change)
    - Members (create, edit, delete members with proxy tags)
    - Security (links to 2FA and audit logs)
    - Activity (link to full audit log)

---

## 🚧 Work In Progress

Currently working on documenting the roadmap!

---

## 📝 Remaining Work

### Phase 3: Settings Subpages (LOWER PRIORITY)
- [ ] **Security Settings Page** (`/app/settings/security/page.tsx`)
  - Convert 2FA setup/disable forms
  - Replace Ant Design `Modal`, `QRCode`, `Input` components
  - Update backup code display
  - Estimated: ~300-400 lines

- [ ] **~~Audit Logs in User Settings~~** ❌ DEPRECATED
  - **DECISION**: Move audit logs to admin panel instead
  - User settings shouldn't have audit logs - admin only feature
  - Delete `/app/settings/audit-logs/page.tsx` or move to admin

- [ ] **Members of System Panel** (User Settings)
  - Add dedicated view showing all members belonging to user's system
  - Separate from main "Members" tab (which is for managing)
  - View-only panel for quick reference
  - Estimated: ~150 lines
  - **Note**: Not urgent, can be added later

### Phase 4: Admin Panel (🔥 HIGH PRIORITY - Build from Scratch)
All admin pages need to be created using shadcn/ui. Reference: https://ui.shadcn.com/

**GOAL**: Get basic framework working ASAP, add features incrementally later

#### Stage 4A: Core Admin Framework (DO FIRST!)
- [ ] **Admin Layout** (`/app/admin/layout.tsx`)
  - Admin sidebar navigation
  - Auth check (admin-only access)
  - Breadcrumb navigation
  - Estimated: ~150 lines

- [ ] **Admin Dashboard** (`/app/admin/page.tsx`) - MVP VERSION
  - **System Health Cards**:
    - Server status (online/offline)
    - Database connection status
    - API response time
    - Active WebSocket connections
  - **Quick Stats**: Total users, active channels, messages today
  - **Recent Activity**: Last 10 admin actions
  - **Quick Actions**: Links to other admin pages
  - Estimated: ~250 lines
  - **Goal**: Just get it WORKING, make it pretty later

- [ ] **Feature Toggles Panel** (`/app/admin/settings/page.tsx`) - NEW!
  - **Global Feature Flags**:
    - AI Generation (on/off globally)
    - PluralKit Sync (on/off globally)
    - OAuth Login (on/off + provider selection)
    - User Registration (open/closed/invite-only)
  - **Per-Channel Flags** (future):
    - AI generation per channel
    - Custom settings per channel
  - Simple toggle switches with descriptions
  - Save to backend API
  - Estimated: ~200 lines

- [ ] **Audit Logs** (`/app/admin/audit-logs/page.tsx`) - MOVED FROM USER SETTINGS
  - **IMPORTANT**: This should be ADMIN ONLY
  - Table showing all security events across all users
  - Filter by user, action type, date range
  - Convert existing audit-logs from user settings
  - Estimated: ~250 lines

#### Stage 4B: User & Moderation (ADD LATER)
- [ ] **User Management** (`/app/admin/users/page.tsx`)
  - User list table with search/filter
  - User details modal
  - Enable/disable accounts (not delete yet)
  - Role management (admin/user)
  - Estimated: ~350 lines

- [ ] **Moderation Queue** (`/app/admin/moderation/page.tsx`)
  - Flagged messages queue
  - Basic moderation tools
  - User reports
  - Estimated: ~300 lines

#### Stage 4C: Analytics & Maintenance (FUTURE)
- [ ] **Statistics Dashboard** (`/app/admin/stats/page.tsx`)
  - Charts/graphs using recharts or tremor
  - User growth, message activity, channel usage
  - Estimated: ~350 lines

- [ ] **System Maintenance** (`/app/admin/maintenance/page.tsx`)
  - Database cleanup tools
  - Cache management
  - Backup/restore functionality
  - Estimated: ~400 lines

### Phase 5: Cleanup & Testing
- [ ] **Remove Ant Design Dependency**
  - Remove `antd` from `package.json`
  - Remove `@ant-design/icons` from `package.json`
  - Search for any remaining Ant imports: `grep -r "from 'antd'" app/`
  - Run `npm install` to clean up

- [ ] **Testing & Validation**
  - [ ] Test login flow (username/password + 2FA)
  - [ ] Test settings page (all tabs)
  - [ ] Test profile updates (avatar, username, email, theme)
  - [ ] Test password change
  - [ ] Test member CRUD operations
  - [ ] Test PluralKit sync
  - [ ] Test audit logs display
  - [ ] Test 2FA setup/disable
  - [ ] Test all admin panel features
  - [ ] Cross-browser testing (Chrome, Firefox, Safari)
  - [ ] Mobile responsive testing
  - [ ] Dark mode testing (all pages)

---

## 🐛 Known Issues & Missing Features

### Critical Issues Found
1. **PluralKit Sync Not Working**: Integration exists but sync functionality is broken
2. **Members Panel Missing**: No "Members of System" panel in user settings (only in main settings tabs)
3. **Audit Logs Location Wrong**: Should be in admin panel, not user settings
4. **Toast Notifications**: Need to verify toast system works across all pages
5. **Form Validation**: Some Ant Design form validation needs manual conversion
6. **File Upload**: Native file input lacks drag-and-drop (consider adding `react-dropzone`)
7. **Loading States**: Ensure all async operations show proper loading states

### Missing Features (Not in Original Scope)
These might have been missed by WebCLI or not implemented yet:

#### Authentication & Security
- [ ] **Session Management**: No visible session timeout handling
- [ ] **"Remember Me" Option**: Missing on login page
- [ ] **Password Reset Flow**: No forgot password functionality
- [ ] **Email Verification**: No email verification system

#### Settings & Profile
- [ ] **Avatar Cropping**: No image cropping tool for avatars
- [ ] **Profile Deletion**: No account deletion option
- [ ] **Export Data**: No GDPR-compliant data export
- [ ] **Privacy Settings**: No privacy/visibility controls

#### Member Management
- [ ] **Bulk Member Import**: Only PluralKit sync exists
- [ ] **Member Avatar from URL**: Only file upload supported
- [ ] **Member Groups/Categories**: No organization system
- [ ] **Member Search/Filter**: No search in member list

#### Admin Panel (Completely Missing - HIGH PRIORITY!)
WebCLI claimed this existed 5+ times but it doesn't! Admin panel needs:

**Core Admin Features (Build First)**:
- [ ] **System Health Dashboard**: Server status, DB health, API response times
- [ ] **Feature Toggles/Settings Panel**:
  - Toggle AI generation on/off (globally or per-channel)
  - Toggle PluralKit sync on/off (globally or per-user)
  - Toggle OAuth providers on/off
  - Other feature flags for future additions
- [ ] **Audit Logs (MOVE FROM USER SETTINGS)**: Should be admin-only, not user-accessible
- [ ] **User Management**: Basic user list, enable/disable accounts
- [ ] **Moderation Queue**: Review flagged content, basic moderation tools

**Future Admin Features (Add Later)**:
- [ ] **User Activity Monitoring**: No real-time user tracking
- [ ] **Content Moderation Tools**: Message deletion/editing
- [ ] **Announcement System**: Admin broadcast feature
- [ ] **System Logs Viewer**: Centralized logging UI
- [ ] **API Key Management**: API token interface
- [ ] **OAuth Provider Management**: Configure OAuth clients
- [ ] **Channel Settings**: Per-channel feature toggles

#### Chat Features (Out of Scope but Notable)
- [ ] **Message Reactions**: Not visible in settings
- [ ] **Notification Preferences**: No granular notification settings
- [ ] **Keyboard Shortcuts**: No shortcut customization

#### Accessibility
- [ ] **Screen Reader Testing**: Needs ARIA label verification
- [ ] **Keyboard Navigation**: Full keyboard-only navigation
- [ ] **Focus Indicators**: Consistent focus styling
- [ ] **High Contrast Mode**: Support for Windows high contrast

---

## 🎯 Priority Levels (UPDATED!)

### 🔴 Critical (Do NOW - Next 20 Minutes!)
1. **Build Admin Panel Framework** (layout + basic dashboard)
2. **Add System Health Check** to admin dashboard
3. **Create Feature Toggles Panel** (AI, PluralKit, OAuth on/off switches)
4. **Move Audit Logs to Admin** (out of user settings)
5. Get it WORKING - polish comes later!

### 🟡 High Priority (Should Have - This Session)
1. **User Management Page** (basic version)
2. **Convert Security Settings** (user settings)
3. **Remove Ant Design Dependency**
4. **Fix PluralKit Sync** (currently broken)
5. Basic testing of admin panel

### 🟢 Medium Priority (Nice to Have - Future Sessions)
1. Statistics dashboard with charts
2. Maintenance page
3. Moderation queue
4. Members of System panel (user settings)
5. OAuth provider management UI

### ⚪ Low Priority (Way Future)
1. Password reset flow
2. Avatar cropping tool
3. Advanced analytics
4. Message reactions in settings
5. Keyboard shortcut customization

---

## 🛠️ Technical Debt

### Code Quality
- [ ] Add TypeScript strict mode compliance
- [ ] Add proper error boundaries
- [ ] Implement consistent loading states
- [ ] Add proper form validation schemas (zod?)
- [ ] Add unit tests for form submissions

### Performance
- [ ] Implement proper code splitting
- [ ] Add image optimization for avatars
- [ ] Lazy load admin panel components
- [ ] Add proper caching strategies

### Documentation
- [ ] Document shadcn/ui component usage patterns
- [ ] Create style guide for consistent UI
- [ ] Document form handling patterns
- [ ] Add JSDoc comments for complex functions

---

## 📦 Dependencies to Add

```bash
# Potential additions for missing features
npm install react-dropzone           # Better file uploads
npm install zod                       # Form validation
npm install react-hook-form          # Better form handling
npm install recharts                 # Charts for admin stats
npm install date-fns                 # Already installed
npm install react-image-crop         # Avatar cropping
```

---

## 🔧 Migration Helpers

### Quick Search Commands
```bash
# Find remaining Ant Design imports
grep -r "from 'antd'" app/

# Find Ant Design icon usage
grep -r "@ant-design/icons" app/

# Check for message.success/error/warning
grep -r "message\." app/

# Find all Form.Item usage
grep -r "Form.Item" app/
```

### Component Mapping Reference

| Ant Design | shadcn/ui | Notes |
|------------|-----------|-------|
| `Input` | `Input` | Similar API |
| `Button` | `Button` | Different variant names |
| `Card` | `Card` + sub-components | More verbose |
| `Form` | Native forms + `useForm` | Manual validation |
| `Modal` | `Dialog` | Different structure |
| `Alert` | `Alert` | Similar but simpler |
| `Tag` | `Badge` | Different styling |
| `Table` | `Table` | More manual setup |
| `Upload` | Native input or react-dropzone | Custom implementation |
| `message.success()` | `toast()` | Different API |
| `Tabs` | `Tabs` + `TabsList` + `TabsTrigger` | More verbose |

---

## 📚 Resources

- **shadcn/ui Docs**: https://ui.shadcn.com/
- **Lucide React Icons**: https://lucide.dev/
- **Radix UI Primitives**: https://www.radix-ui.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **React Hook Form**: https://react-hook-form.com/

---

## 🤝 Collaboration Notes

### For Other AI Assistants (like Gemini)
When working on this project:
1. **Always use shadcn/ui components** - Check the mapping table above
2. **Use lucide-react for icons** - Not @ant-design/icons
3. **Use toast() for notifications** - Not message.success/error
4. **Follow existing patterns** - Check converted files for examples
5. **Maintain accessibility** - Use proper labels, ARIA attributes
6. **Keep dark mode support** - Test in both light and dark themes

### File Structure for New Admin Pages
```
app/
  admin/
    page.tsx              # Dashboard
    users/
      page.tsx            # User management
    stats/
      page.tsx            # Statistics
    maintenance/
      page.tsx            # System tools
    layout.tsx            # Admin layout (optional)
```

### Coding Standards
- Use TypeScript for all new code
- Use `'use client'` directive for interactive components
- Prefer functional components with hooks
- Use `async/await` for API calls
- Handle errors with try/catch and toast notifications
- Add loading states for all async operations

---

## 🎨 Design Consistency

### Colors
- Primary: `#8b5cf6` (purple)
- Background gradient: `from-purple-50 to-blue-50` (light) / `from-gray-900 to-gray-800` (dark)

### Spacing
- Card padding: `p-6`
- Section spacing: `space-y-6`
- Form field spacing: `space-y-4`

### Typography
- Page title: `text-3xl font-bold`
- Section title: `text-xl font-semibold mb-4`
- Description: `text-muted-foreground`

---

## 📈 Progress Tracker

```
Total Tasks: 13
Completed: 4 (31%)
In Progress: 1 (8%)
Remaining: 8 (61%)

Phase 1 (Setup): ████████████████████ 100%
Phase 2 (Pages): ████████░░░░░░░░░░░░  40%
Phase 3 (Settings): ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4 (Admin): ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5 (Cleanup): ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## 💬 Questions & Decisions

### ✅ Decisions Made
1. **Admin Panel Priority**: Build framework first, features later ✓
2. **Audit Logs Location**: Move to admin panel (not user settings) ✓
3. **Feature Toggles**: Needed for AI, PluralKit, OAuth, etc. ✓
4. **Focus**: Get it WORKING first, make it pretty later ✓

### ❓ Still Need to Decide
1. **Charts Library**: Which for admin stats later? (recharts, chart.js, tremor?)
2. **Form Library**: Stick with native forms or add react-hook-form + zod?
3. **OAuth Providers**: Which to support? (Google, GitHub, Discord?)
4. **Permission System**: Single "admin" role or granular permissions?
5. **Feature Toggle Scope**: Just global or per-user/per-channel too?

---

## 🚀 Next Steps - UPDATED PLAN!

**Immediate (RIGHT NOW - Next 20 mins)**:
1. ✅ Updated roadmap with feedback
2. **Build Admin Panel Structure**:
   - Create `/app/admin/layout.tsx` with nav
   - Build basic dashboard (`/app/admin/page.tsx`)
   - Add system health check cards
   - Get something VISIBLE and WORKING

**Short Term (This Session)**:
1. **Feature Toggles Panel** (`/app/admin/settings/page.tsx`)
   - AI generation on/off
   - PluralKit sync on/off
   - OAuth on/off
2. **Move Audit Logs** to `/app/admin/audit-logs/page.tsx`
3. **Basic User Management** page

**Medium Term (Future Sessions)**:
1. Fix PluralKit sync functionality
2. Convert security settings (2FA page)
3. Add Members of System panel
4. Build out more admin features

**Long Term**:
1. Statistics with charts
2. OAuth integration
3. Moderation tools
4. Testing & polish

---

**Notes**: This roadmap is a living document. Update it as work progresses and new requirements emerge!
