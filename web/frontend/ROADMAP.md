# Plural Chat - Complete Project Roadmap

**Project**: Plural Chat - Community Platform
**Vision**: Community without corporation - self-hosted, plural-friendly chat & community hub
**Current Phase**: Local Development & Testing
**Last Updated**: 2025-11-09

---

## 🎯 Project Vision

### Core Mission
Build a self-hosted community platform that:
- ✅ Supports plural systems (all origins, no gatekeeping)
- ✅ Supports roleplayers and other identity expressions
- ✅ Provides infrastructure for non-profit organizations
- ✅ Is truly community-owned (no corporate overlords)
- ✅ Is open source and forkable
- ✅ Values accessibility and user-friendliness

### Long-term Vision
**Phase 1 (Current):** Plural Chat - Core messaging system
**Phase 2:** Community features - Forums, profiles, resources
**Phase 3:** Non-profit integration - Events, volunteers, donations
**Phase 4:** Full community hub - Blog, resource library, member directory

**Philosophy**: "Don't be an asshole, and we're cool" - Inclusive, supportive, drama-free.

---

## ✅ Completed Work

### UI Migration (100% COMPLETE!)
- ✅ All pages converted from Ant Design to shadcn/ui
- ✅ Login page converted
- ✅ Signup page converted
- ✅ Settings page completely rewritten (1072 lines!)
- ✅ Security/2FA page converted (665 lines!)
- ✅ Admin panel built from scratch (4 pages + layout)
- ✅ Ant Design completely removed (66 packages removed)
- ✅ Zero security vulnerabilities
- ✅ Toast notification system working
- ✅ Dark mode fully supported

### Admin Panel (COMPLETE!)
Built from scratch with shadcn/ui:
- ✅ `/admin` - Dashboard with system health monitoring
- ✅ `/admin/users` - User management (enable/disable, admin roles)
- ✅ `/admin/settings` - Feature toggles (AI, PluralKit, OAuth)
- ✅ `/admin/audit-logs` - Security event logging & export
- ✅ Responsive sidebar navigation with mobile support
- ✅ All working with mock data, ready for backend integration

---

## 🚧 Current Status: Local Development

### What Works Right Now
- ✅ Dev environment (`./dev.sh` runs both frontend + backend)
- ✅ Login/Signup with 2FA support
- ✅ User settings (profile, password, theme)
- ✅ Member management UI (needs backend fixes)
- ✅ Admin panel UI (mock data, needs real APIs)
- ✅ Audit logs (already connected to backend!)
- ✅ Beautiful, consistent shadcn/ui design

### What Needs Work
- 🔧 Backend API integration for admin panel
- 🔧 PluralKit sync (currently broken)
- 🔧 Members Dashboard application system
- 🔧 OAuth implementation
- 🔧 Email verification (optional, configurable)

---

## 📋 Roadmap by Phase

### Phase 1: Core Chat Platform (IN PROGRESS)

#### 1.1 Backend Integration (NEXT PRIORITY)
**Goal**: Connect admin panel to real APIs

**Backend Endpoints Needed:**
```
Admin Dashboard:
- GET /api/admin/health         # System health check
- GET /api/admin/stats          # User/channel/message counts

Feature Toggles:
- GET /api/admin/settings       # Get current feature flags
- PUT /api/admin/settings       # Save feature flags

User Management:
- GET /api/admin/users          # List all users
- POST /api/admin/users/:id/toggle-active
- POST /api/admin/users/:id/toggle-admin

Audit Logs:
- Already working via securityAPI.getAuditLogs() ✅
```

**Tasks:**
- [ ] Implement admin health check endpoint
- [ ] Implement admin stats endpoint
- [ ] Implement feature toggles storage (database)
- [ ] Implement user management endpoints
- [ ] Add `is_admin` role checking in admin layout
- [ ] Test all admin features with real data

**Priority**: 🔴 Critical (before Railway deployment)

---

#### 1.2 Core Chat UI Improvements (BEFORE RAILWAY)
**Goal**: Add essential chat features that users expect

**User Menu (Discord-style):**
- [ ] Replace simple settings cog with user menu button
- [ ] Show avatar + username as clickable button
- [ ] Dropdown menu with:
  - Profile/Settings
  - Activity Log
  - **LOGOUT BUTTON** (kinda important lol!)
  - Theme toggle (quick access)
- [ ] Matches Discord/familiar chat app UX
- [ ] **NOTE:** Make sure logout actually works and clears auth tokens!

**Typing Indicators:**
- [ ] "So-and-so is typing..." via WebSocket
- [ ] Shimmering text effect (Eleven Labs style, subtle)
- [ ] Show typing users in real-time
- [ ] Clear when user stops typing

**Essential Chat Features:**
- [ ] Message editing (user can edit their own messages)
- [ ] Message deletion (user can delete their own messages)
- [ ] Timestamps on all messages
- [ ] User presence indicators (online/offline/away)
- [ ] Last seen timestamp
- [ ] Mention/ping system (@username notifications)
- [ ] File/image uploads in chat
- [ ] Link previews (unfurl URLs)
- [ ] Code block formatting (```code```)

**Priority**: 🔴 Critical (basic expectations for any chat app)

---

#### 1.3 Moderation System (BEFORE RAILWAY)
**Goal**: Essential moderation tools before opening to public

**REALLY IMPORTANT** - Can't launch without basic moderation!

**Moderator Role:**
- [ ] Add `is_moderator` role to user table (between user and admin)
- [ ] Moderators can:
  - Delete messages (any user)
  - Edit messages (any user, with edit log)
  - Timeout/mute users (temporary)
  - View audit logs (limited to moderation actions)
  - Kick users from channels
- [ ] Admins can assign moderator role in user management

**Auto-Moderation (Bot-less):**
- [ ] Regex word filter (like Discord's AutoMod)
- [ ] Configurable banned words/phrases (admin panel)
- [ ] Auto-delete matching messages
- [ ] Auto-timeout repeat offenders
- [ ] Log all auto-mod actions to audit log
- [ ] Whitelist/exemptions for mods/admins

**Report System:**
- [ ] Users can report messages
- [ ] Reports go to moderation queue (`/admin/moderation`)
- [ ] Mods can review and take action
- [ ] Track false reports (prevent abuse)

**Moderation Queue Page (`/admin/moderation`):**
- [ ] Flagged messages (auto-mod + user reports)
- [ ] Quick actions (approve, delete, timeout user)
- [ ] Context (show surrounding messages)
- [ ] Moderation history per user

**Admin Panel Additions:**
- [ ] Moderator management in `/admin/users`
- [ ] Word filter configuration in `/admin/settings`
- [ ] Moderation stats in dashboard

**Priority**: 🔴 Critical (cannot launch publicly without this!)

---

#### 1.4 Members Dashboard Application System (NEW FEATURE)
**Goal**: Opt-in member management to keep UI clean for non-plural users

**Design Philosophy:**
- Neutral language ("Members Dashboard", not "Plural Mode")
- Includes systems AND roleplayers AND anyone else
- Opt-in via simple application (not gatekeeping, just intentional use)
- Admin approval to prevent spam

**Application Flow:**
1. User signs up normally (no member features visible)
2. User sees option: "Request Members Dashboard Access"
3. Application form asks:
   - "Why do you want Members features?" (freeform text)
   - "Do you use PluralKit/Tupperbox?" (optional, helps inform features)
4. Admin reviews in `/admin/member-requests`
5. Admin approves/denies (with optional message)
6. User gets Members tab unlocked in settings

**Messaging Example:**
```
"Members Dashboard Application"

We offer member management tools for systems, roleplayers,
and anyone who needs to manage multiple identities in chat.

This isn't gatekeeping - it's an opt-in feature to keep
our community safe and our UI clean for those who don't need it.

Why would you like access to Members features?
[text box]

Do you use PluralKit or Tupperbox? (optional)
[ ] PluralKit  [ ] Tupperbox  [ ] Other  [ ] None
```

**Backend Tasks:**
- [ ] Add `has_members_access` boolean to user table
- [ ] Add `member_requests` table (user_id, reason, pk_tb_usage, status, created_at)
- [ ] Create `/api/members/request-access` endpoint
- [ ] Create `/api/admin/member-requests` endpoint (list, approve, deny)
- [ ] Conditionally render Members tab based on `user.has_members_access`

**Frontend Tasks:**
- [ ] Create application form component
- [ ] Create `/admin/member-requests` page
- [ ] Add "Request Access" button/card in settings
- [ ] Hide Members tab if user doesn't have access
- [ ] Show friendly message explaining how to request access

**Priority**: 🟡 High (nice QoL feature, not blocking deployment)

---

#### 1.3 Authentication & Security Enhancements

**OAuth Implementation (RECOMMENDED PATH)**

**Why OAuth over Email Verification:**
- ✅ No SMTP setup required
- ✅ One-click signup
- ✅ Email pre-verified by provider
- ✅ Users trust it more
- ✅ Less support burden ("I didn't get the email" etc.)

**OAuth Providers to Support:**
- [ ] Google OAuth (most common)
- [ ] Discord OAuth (fits the community vibe)
- [ ] GitHub OAuth (for devs/tech users)

**Make It Configurable (Open Source Ethos):**
Each instance owner can choose:
- OAuth only (your preference - simple, no SMTP)
- Email verification only (they have SMTP configured)
- Both (maximum flexibility)
- Neither (just username/password, no email required)

**Backend .env Config:**
```env
# Authentication Options (all optional)
OAUTH_ENABLED=true
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
DISCORD_OAUTH_CLIENT_ID=...
DISCORD_OAUTH_CLIENT_SECRET=...
GITHUB_OAUTH_CLIENT_ID=...
GITHUB_OAUTH_CLIENT_SECRET=...

SMTP_ENABLED=false  # Optional email verification
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
```

**Tasks:**
- [ ] Implement Google OAuth (FastAPI)
- [ ] Implement Discord OAuth
- [ ] Implement GitHub OAuth
- [ ] Add OAuth buttons to login/signup pages
- [ ] Make OAuth configurable via admin panel toggles
- [ ] (Optional) Implement email verification with SMTP
- [ ] Make email verification configurable

**Priority**: 🟡 High (before Railway - makes onboarding way easier)

---

#### 1.5 AI Image Generation System (FLESH OUT LATER)
**Goal**: Optional AI image generation via vast.ai GPU rental

**Concept:**
- Hook up a vast.ai GPU instance running A1111/Forge
- Connect via A1111's API (not Gradio UI)
- Handle vast.ai's Cloudflare challenges
- Admin toggle to enable/disable globally
- Per-channel toggle (some channels allow, some don't)
- Usage limits/quotas per user
- Queue system if multiple users generating

**Technical Approach:**
- Backend proxies requests to vast.ai A1111 API
- Store generated images locally or S3
- Track usage/costs
- Handle GPU instance startup/shutdown (vast.ai auto-scaling)
- Cloudflare bypass/handling (vast.ai specific)

**Why vast.ai:**
- Cheap GPU rental (pay per minute)
- A1111/Forge already has API
- Scale up/down based on demand
- No expensive constant GPU costs

**Tasks (WAY LATER):**
- [ ] Research vast.ai API integration
- [ ] Research Cloudflare bypass methods
- [ ] Test A1111 API connection
- [ ] Build backend proxy service
- [ ] Add admin controls for GPU management
- [ ] Add usage tracking/quotas
- [ ] Add generation queue UI
- [ ] Add gallery/history for users

**Priority**: 🟢 Medium (cool feature but not critical - you said "too early")

**Note**: This is documented but NOT prioritized. Get chat working first!

---

#### 1.6 Personal Activity Log (User-Facing)

**Goal**: Give users transparency into their own account activity

**Different from Admin Audit Logs:**
- Admin audit logs = ALL users, security events, admin-only
- Personal activity log = THIS user only, helpful for systems & security

**What to Show:**
- Last login time/IP (security check: "Was this me?")
- Recent password changes
- 2FA enable/disable events
- Member switches (if applicable - helpful for amnesia barriers!)
- Profile updates
- OAuth connections/disconnections

**Use Cases:**
- Systems: "Which member did what yesterday?"
- Security: "I didn't log in from that IP - am I hacked?"
- Transparency: "What data exists about me?"

**Tasks:**
- [ ] Design personal activity log UI (Settings > Activity tab)
- [ ] Create `/api/user/activity` endpoint (filters to current user only)
- [ ] Add member switch tracking (if members enabled)
- [ ] Add pagination/filtering by date range
- [ ] Keep it separate from admin audit logs (different endpoints)

**Priority**: 🟢 Medium (nice feature, not critical for launch)

---

#### 1.5 Bug Fixes & Polish

**Known Issues:**
- [ ] Fix PluralKit sync (currently broken)
- [ ] Test member CRUD operations with backend
- [ ] Verify avatar upload works correctly
- [ ] Test 2FA flow end-to-end
- [ ] Ensure all toast notifications work
- [ ] Mobile responsiveness testing
- [ ] Cross-browser testing

**Priority**: 🔴 Critical (before Railway deployment)

---

### Phase 2: Community Features (FUTURE)

**Goal**: Expand beyond chat into full community platform

**Potential Features (not prioritized yet):**
- [ ] Forums/discussion boards
- [ ] Resource library (files, links, guides)
- [ ] Event calendar
- [ ] Blog/diary system (per-user or community-wide)
- [ ] Member profiles (public-facing)
- [ ] Search functionality
- [ ] Tags/categories for content
- [ ] Polls/voting system

**Fun Social Features ("Fuck it whenever" tier):**

**Music Listening Parties:**
- [ ] Shared music listening (like listen.moe / plug.dj)
- [ ] Users upload their own MP3s (at their own risk - we don't host copyrighted content)
- [ ] Or: YouTube audio embeds (legal! just embedding)
- [ ] DJ queue system
- [ ] Synchronized playback for everyone in channel
- [ ] Chat alongside music
- [ ] "Now Playing" display
- [ ] Volume controls per-user
- [ ] Inspired by Eleven Labs audio UI components

**Watch Nights (YouTube Sync):**
- [ ] Synchronized YouTube video playback
- [ ] Legal (just embedding YouTube player)
- [ ] "Movie night" or "watch party" feature
- [ ] Everyone sees same video at same timestamp
- [ ] Chat alongside video
- [ ] Play/pause synced for all users
- [ ] Queue system for multiple videos

**Notes:**
- These are **legal** (embedding YouTube, users bring their own content)
- Users responsible for what they upload/share
- Terms of service: "Don't upload pirated content" (enforce at admin discretion)
- Could add DMCA takedown system if needed (way later)
- Inspired by old web radio/streaming vibes

**Philosophy**: Build iteratively. Add features when chat is stable and users request them.

**Priority**: ⚪ Low (way down the line - focus on chat first!)

---

### Phase 3: Non-Profit Integration (FUTURE)

**Goal**: Integrate partner's non-profit organization website

**Context:**
- Partner runs a non-profit community organization
- Lost old website (Wix years ago)
- Has Wayback Machine archives to reference
- Wants modern replacement that they control

**Potential Features:**
- [ ] Static informational pages (About, Mission, History)
- [ ] Volunteer management
- [ ] Donation tracking/integration
- [ ] Event management
- [ ] Newsletter/mailing list
- [ ] Resource downloads
- [ ] Photo galleries
- [ ] Contact forms

**Approach:**
- Start with static pages (easy - Next.js makes this trivial)
- Add CMS-like features as needed
- Keep it simple and maintainable
- Professional but with personality

**Priority**: ⚪ Low (after chat is stable and deployed)

---

### Phase 4: Visual Enhancements (WAY FUTURE)

**Goal**: Add "sparkle" and personality without sacrificing professionalism

**Philosophy**:
- Corporate clean = foundation (done! shadcn is perfect)
- Weird touch = layered on top (later, when core works)
- Never sacrifice accessibility for aesthetics

**Ideas from ReactBits/Magic UI:**
- [ ] Hyperspeed text effect for splash page
- [ ] Pill navigation for main chat
- [ ] Profile cards for system members
- [ ] Avatar circles for member lists (`@magicui/avatar-circles`)
- [ ] Changelog template for announcements
- [ ] Background rotation (every 5 minutes)
- [ ] Spotlight cards for featured content
- [ ] Smooth animations (respects `prefers-reduced-motion`)

**Potential Monetization (way down the line):**
- Custom profile gadgets/widgets
- Premium themes
- Advanced member customization
- (Always keep core free and open source!)

**Priority**: ⚪ Low (sparkle comes AFTER stability!)

---

## 🎯 Priorities Summary

### 🔴 Critical (Before Railway Deployment)
**MUST HAVE** - Cannot launch without these!

1. **Backend Integration** - Connect admin panel to real APIs (health, stats, settings, users)
2. **Core Chat UI** - User menu, typing indicators, message edit/delete, timestamps
3. **Moderation System** - Moderator role, word filters, report system, moderation queue
4. **OAuth Implementation** - At least Google OAuth (makes signup way easier)
5. **Admin Role Checking** - Verify `is_admin` before allowing admin panel access
6. **Fix PluralKit Sync** - Currently broken, needs fixing
7. **Bug Fixes & Testing** - Full testing of all features
8. **Security Hardening** - Rate limiting, input validation, SQL injection prevention

**Estimated Time**: 2-4 weeks of solid work

### 🟡 High (Before Public Launch)
**SHOULD HAVE** - Makes the platform actually usable

1. **Members Dashboard Application System** - Opt-in member features
2. **Personal Activity Log** - User transparency & security
3. **Full OAuth Support** - Google, Discord, GitHub
4. **Email Verification** - Optional, configurable (SMTP)
5. **Mobile Optimization** - Touch-friendly, responsive
6. **Documentation** - Setup guide, self-hosting guide, user docs
7. **Terms of Service / Privacy Policy** - Legal stuff
8. **Onboarding Flow** - Welcome tutorial for new users

**Estimated Time**: 1-2 weeks after critical features

### 🟢 Medium (Post-Launch Enhancements)
**NICE TO HAVE** - Quality of life improvements

1. **AI Image Generation** - vast.ai + A1111/Forge integration
2. **Community Features** - Forums, resources, blog/diary
3. **Advanced Admin Tools** - Statistics, analytics, charts
4. **Advanced Moderation** - Appeals system, ban management
5. **Export/Import Tools** - Data portability, backups
6. **Emoji Reactions** - React to messages
7. **Message Search** - Find old messages
8. **Notification Preferences** - Granular control

### ⚪ Low (Future Vision)
**"FUCK IT WHENEVER" TIER** - Fun stuff for way later

1. **Non-profit Website Integration** - Partner's org site
2. **Visual Enhancements** - ReactBits animations, Magic UI sparkle (respects accessibility!)
3. **Music Listening Parties** - Shared music playback, DJ queue
4. **Watch Nights** - Synchronized YouTube viewing
5. **Custom Profile Features** - Themes, badges, customization
6. **Advanced Customization** - Per-user/per-channel everything
7. **Monetization** - Premium features (core always free!)

---

## 🛠️ Technical Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: shadcn/ui (Radix + Tailwind)
- **Icons**: lucide-react
- **State Management**: Zustand
- **Forms**: Native React (consider react-hook-form + zod later)
- **Styling**: Tailwind CSS
- **Theme**: next-themes (dark mode support)
- **Notifications**: shadcn/ui toast + sonner

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (local), PostgreSQL (production)
- **Auth**: JWT tokens + 2FA (TOTP)
- **WebSocket**: Socket.io
- **File Storage**: Local filesystem (later: S3/cloud)

### Deployment
- **Current**: Local development (`./dev.sh`)
- **Planned**: Railway (frontend + backend + database)
- **Future**: Self-hosting guides for community instances

---

## 📚 Documentation Needed

### For Developers
- [ ] Setup guide (local development)
- [ ] Contributing guidelines
- [ ] Code style guide
- [ ] API documentation
- [ ] Component usage patterns

### For Self-Hosters
- [ ] Installation guide
- [ ] Configuration reference (.env variables)
- [ ] OAuth setup guides
- [ ] SMTP setup guide (optional)
- [ ] Backup/restore procedures
- [ ] Troubleshooting common issues

### For Users
- [ ] Getting started guide
- [ ] Member management guide
- [ ] PluralKit sync guide
- [ ] 2FA setup guide
- [ ] FAQ

**Priority**: 🟡 High (needed before open sourcing)

---

## 🎨 Design Philosophy

### Core Principles
1. **Accessibility First**: WCAG compliance, keyboard navigation, screen readers
2. **Clean Foundation**: Professional, usable baseline (shadcn provides this)
3. **Personality Later**: Add "weird touch" without sacrificing usability
4. **Mobile-First**: Responsive design from the start
5. **Dark Mode**: Full support, respects user preferences
6. **Performance**: Fast, lightweight, no bloat
7. **Consistency**: Unified design language across all pages

### Visual Identity
- **Colors**: Purple primary, clean neutrals, semantic colors for states
- **Typography**: Clear hierarchy, readable fonts, proper contrast
- **Spacing**: Generous whitespace, consistent padding/margins
- **Components**: shadcn/ui standard, customized as needed
- **Animations**: Subtle, purposeful, respects `prefers-reduced-motion`

---

## 🤝 Collaboration Strategy

### With Other Developers
- Open source on GitHub (when ready)
- Clear contribution guidelines
- Good documentation
- Welcoming to new contributors
- Credit all contributors

### With AI Assistants
- Use Claude Code (desktop) for deep work
- Use WebCLI for quick iterations
- Use Gemini for alternative approaches
- Provide clear context in prompts
- Verify AI output (you understand the code!)

### With Community
- User feedback drives features
- Transparent roadmap (this document!)
- Regular updates
- Open to suggestions
- "Don't be an asshole" moderation

---

## 🚀 Next Steps

### Immediate (This Week - Local Testing)
- [x] UI migration complete
- [x] Admin panel built
- [x] Dev environment working
- [ ] Test all features locally
- [ ] Document any bugs found
- [ ] Plan backend integration tasks

### Short Term (Next 2-4 Weeks - Backend Integration)
- [ ] Implement admin API endpoints
- [ ] Fix PluralKit sync
- [ ] Add OAuth (at least Google)
- [ ] Implement Members Dashboard application system
- [ ] Add admin role checking
- [ ] Testing and bug fixes

### Medium Term (1-2 Months - Railway Deployment)
- [ ] Deploy to Railway
- [ ] Test in production environment
- [ ] Invite alpha testers
- [ ] Gather feedback
- [ ] Iterate based on real usage
- [ ] Document self-hosting process

### Long Term (3+ Months - Community Growth)
- [ ] Open source release
- [ ] Add community features as requested
- [ ] Integrate non-profit website
- [ ] Add visual enhancements
- [ ] Support multiple self-hosted instances
- [ ] Build the community without corporation

---

## 💬 Notes & Learnings

### Lessons from Dataset Tools
- ✅ Don't add themes before core functionality
- ✅ Finish features before adding sparkle
- ✅ User needs > aesthetic wants
- ✅ Thumbnails and file tree took a year - core first!

### Lessons from WebCLI Hallucinations
- ✅ Verify AI claims (admin panel didn't exist!)
- ✅ But hallucinations can show what SHOULD exist
- ✅ Use them as inspiration, not truth
- ✅ Build what's needed, not what AI assumes

### Why This Tech Stack Works for You
- ✅ HTML/CSS/JS is your native language (design degree!)
- ✅ Can read and understand the code
- ✅ Can spot when AI is wrong
- ✅ Can fix small things yourself
- ✅ Python backend is mostly done, just endpoints
- ✅ Frontend is infinite canvas for creativity

### Community Philosophy
- ✅ Inclusive but not a free-for-all
- ✅ Support all system origins (no gatekeeping)
- ✅ Support roleplayers too (they're valid!)
- ✅ "Don't be an asshole" is the main rule
- ✅ Peer support without forcing agreement
- ✅ Tired of syscourse and drama - just vibe

---

## 🎉 Celebrations & Milestones

- ✅ **2025-11-09**: UI migration 100% complete!
- ✅ **2025-11-09**: Admin panel built from scratch!
- ✅ **2025-11-09**: Ant Design completely removed!
- ✅ **2025-11-09**: Dev environment working perfectly!
- ✅ **2025-11-09**: Comprehensive roadmap created!
- ✅ **2025-11-09**: New dog Baxter joined the family! 🐕

---

## 📝 TL;DR - What's Next?

### Right Now (Local Testing Phase)
- ✅ Framework is DONE and working
- ✅ Just tinker, test, learn the codebase
- ✅ No pressure to build new stuff yet
- ✅ Play with Baxter when code gets boring 😊

### Next Up (Before Railway - 2-4 weeks)
1. **Backend integration** - Connect admin panel to real APIs
2. **Chat UI basics** - User menu, typing indicators, edit/delete
3. **Moderation** - Can't launch without it!
4. **OAuth** - Google login at minimum
5. **Testing** - Make sure it all works

### After Railway (Public Launch)
1. Members Dashboard application system
2. Personal activity log
3. Full documentation
4. Community feedback → iterate

### Way Later (When Stable)
1. Community features (forums, resources)
2. Non-profit website integration
3. AI image generation
4. Music/watch parties
5. ALL THE SPARKLE

---

**This roadmap is a living document. Update as the project evolves!**

**Remember**: "Community without corporation" - build it right, build it ethical, build it together.

**Philosophy**: Core first, features later. Don't be an asshole, and we're cool. ✨

---

*Last updated: 2025-11-09 by Claude Code (with lots of planning spew from the human!)*
*Next review: Before Railway deployment*
*Baxter approves of this roadmap* 🐕
