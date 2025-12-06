# Moderation Features Implementation Plan

This document outlines the plan to implement moderation features into the Plural Chat application. The implementation is divided into three phases to ensure a structured and manageable development process.

---

## Phase 1: Foundational Backend & Core Features

This phase focuses on building the essential backend capabilities for banning users and deleting messages.

### 1. Database Model Updates
*   **File:** `web/backend/app/models.py`
*   **Changes:**
    *   **`User` Model:**
        *   Add `is_banned: bool = Column(Boolean, default=False, nullable=False)`
        *   Add `ban_reason: str = Column(String, nullable=True)`
    *   **`Message` Model:**
        *   Add `is_deleted: bool = Column(Boolean, default=False, nullable=False)`
        *   Add `deleted_at: datetime = Column(DateTime, nullable=True)`
        *   Add `deleted_by_id: int = Column(Integer, ForeignKey("users.id"), nullable=True)`
        *   Add a relationship to the deleting user.

### 2. Backend API (New Moderation Router)
*   **File:** `web/backend/app/routers/moderation.py` (New File)
*   **Details:**
    *   Create a new router dedicated to moderation actions.
    *   Protect all endpoints to be admin-only using the `require_admin` dependency.
*   **Endpoints:**
    *   `POST /api/v1/moderation/users/{user_id}/ban`: Sets `is_banned = True` for a user and records the reason.
    *   `POST /api/v1/moderation/users/{user_id}/unban`: Sets `is_banned = False` for a user.
    *   `DELETE /api/v1/moderation/messages/{message_id}`: Sets `is_deleted = True` on a message (soft delete).

### 3. Core Logic Updates
*   **Authentication (`web/backend/app/auth_enhanced.py`):**
    *   Update the login logic to reject access if `user.is_banned` is `True`.
*   **WebSockets (`web/backend/app/websocket.py`):**
    *   Prevent banned users from connecting to the WebSocket or sending messages.
*   **Audit Logging (`web/backend/app/audit.py`):**
    *   Ensure all moderation actions (ban, unban, message delete) are logged in the `AuditLog`.

---

## Phase 2: Frontend Integration

This phase focuses on building the user interface for administrators to use the new moderation tools.

### 1. Admin Panel UI
*   **File:** `web/frontend/app/admin/users/page.tsx`
*   **Changes:**
    *   In the user list, add a "Ban" / "Unban" button next to each user.
    *   Clicking "Ban" should open a modal to enter a `ban_reason`.
*   **New Page:** `web/frontend/app/admin/banned-users/page.tsx`
    *   Create a new page that fetches and displays a list of all banned users, showing their username, ban reason, and the date they were banned.

### 2. In-Chat Moderation UI
*   **File:** `web/frontend/components/ui/chat-message.tsx`
*   **Changes:**
    *   For each message, add a "delete" icon/button that is **only visible** to users with admin privileges.
    *   Clicking the button will call the `DELETE /api/v1/moderation/messages/{message_id}` endpoint.
*   **File:** `web/frontend/components/ui/member-sidebar.tsx` (or user profile pop-up)
    *   When an admin clicks on a user, add a "Ban User" option to the context menu or profile view.

---

## Phase 3: Advanced Features (Future Work)

This phase includes more complex features that can be built upon the foundation from Phases 1 and 2.

### 1. Role-Based Access Control (RBAC)
*   **Goal:** Create a more granular permission system.
*   **Database:**
    *   Create a `Role` model (e.g., "Admin", "Moderator").
    *   Create a `user_roles` association table to link users to roles.
*   **Backend:**
    *   Refactor permission checks (`require_admin`) to be role-based (e.g., `require_role('moderator')`).
*   **Frontend:**
    *   Add a UI in the admin panel to assign roles to users.

### 2. User Reporting System
*   **Goal:** Allow regular users to report messages or users to the moderation team.
*   **Database:**
    *   Create a `Report` model to store report details (reporting user, reported user/message, reason).
*   **Backend & Frontend:**
    *   Implement endpoints and UI for creating, viewing, and managing reports.

### 3. Channel-Specific Moderation
*   **Goal:** Allow moderators to mute or kick users from specific channels without a global ban.
*   **Database:**
    *   Create a `ChannelMute` or similar model to track channel-specific restrictions.
*   **Backend & Frontend:**
    *   Implement the logic and UI for applying and enforcing these restrictions.
