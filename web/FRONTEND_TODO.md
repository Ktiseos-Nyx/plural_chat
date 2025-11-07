# Frontend Development TODO

## ✅ Completed

- ✅ Installed shadcn/ui dependencies (@radix-ui components)
- ✅ Created utility functions (lib/utils.ts)
- ✅ Updated API client with all security endpoints (lib/api.ts)
- ✅ Updated login page with:
  - Username/password login
  - 2FA verification (TOTP + backup codes)
  - PluralKit token login (legacy)
  - Tab-based UI for both methods

## 📋 Remaining Frontend Pages

### 1. Signup Page (`app/signup/page.tsx`)
**NOTE:** Backend signup endpoint needs to be created first!
- Username/password registration
- Email field (optional)
- Password strength indicator
- Terms acceptance checkbox
- Link to login page

**Backend endpoint needed:**
```typescript
POST /security/register
Body: { username, email?, password }
Returns: { user_id, message }
```

### 2. Settings Page (`app/settings/page.tsx`)
Main settings page with tabs:
- **Profile** - Username, email, password change
- **Security** - 2FA setup (link to /settings/security)
- **Audit Logs** - Security history (link to /settings/audit-logs)

### 3. 2FA Setup Page (`app/settings/security/page.tsx`)
- **If 2FA disabled:**
  - Button: "Enable Two-Factor Authentication"
  - Shows QR code when clicked (use `securityAPI.setup2FA()`)
  - Input field to verify first code
  - Display backup codes (copy/download)
  - Confirm button (use `securityAPI.enable2FA(code)`)

- **If 2FA enabled:**
  - Status: "Two-Factor Authentication: Enabled ✓"
  - Backup codes remaining count
  - Button: "Regenerate Backup Codes" (requires TOTP verification)
  - Button: "Disable 2FA" (requires password or TOTP)

**API endpoints available:**
```typescript
securityAPI.setup2FA() // Returns QR code + backup codes
securityAPI.enable2FA(code) // Verify and enable
securityAPI.disable2FA(password?, totp_code?) // Disable
securityAPI.get2FAStatus() // Check status
securityAPI.regenerateBackupCodes(code) // Get new codes
```

### 4. Audit Logs Page (`app/settings/audit-logs/page.tsx`)
Display security event history:
- Table with columns:
  - Event Type (login_success, 2fa_enabled, etc.)
  - Description
  - IP Address
  - Timestamp
  - Success/Failed indicator
- Filter by category dropdown (auth, security, profile)
- Date range selector (last 7/30/90 days)
- Export to CSV button (optional)

**API endpoints available:**
```typescript
securityAPI.getAuditLogs(limit, category?, days)
securityAPI.getSecurityLogs(limit)
```

**Example data:**
```typescript
{
  id: 1,
  event_type: "login_success",
  category: "auth",
  description: "User logged in via password+2fa",
  ip_address: "192.168.1.1",
  success: true,
  timestamp: "2025-01-07T12:34:56"
}
```

## 🎨 UI Components Needed

Use **Ant Design** (already installed) for consistency with existing pages:

### For 2FA Setup:
- `Card` - Container
- `Button` - Actions
- `Input` - Code entry
- `Modal` or `Drawer` - QR code display
- `Alert` - Success/error messages
- `Tag` - Backup codes display
- `Image` - QR code (base64 data URI)

### For Audit Logs:
- `Table` - Main data display
- `Select` - Category filter
- `DatePicker` or `RangePicker` - Date range
- `Tag` - Event type badges
- `Badge` - Success/failed indicators

### Example Components:

**QR Code Display:**
```tsx
<div className="text-center">
  <img
    src={qrCode} // Base64 data URI from API
    alt="2FA QR Code"
    className="mx-auto mb-4"
    style={{ width: 256, height: 256 }}
  />
  <p>Scan with Google Authenticator or Authy</p>
</div>
```

**Backup Codes Display:**
```tsx
<div className="grid grid-cols-2 gap-2">
  {backupCodes.map((code, i) => (
    <Tag key={i} className="font-mono">
      {code}
    </Tag>
  ))}
</div>
<Button onClick={() => copyToClipboard(backupCodes.join('\n'))}>
  Copy All Codes
</Button>
```

**Audit Log Table:**
```tsx
<Table
  columns={[
    { title: 'Event', dataIndex: 'event_type' },
    { title: 'Description', dataIndex: 'description' },
    { title: 'IP Address', dataIndex: 'ip_address' },
    { title: 'Time', dataIndex: 'timestamp', render: formatDate },
    { title: 'Status', dataIndex: 'success', render: (success) => (
      <Badge status={success ? 'success' : 'error'} />
    )}
  ]}
  dataSource={logs}
  pagination={{ pageSize: 20 }}
/>
```

## 🔧 Additional Backend Endpoints Needed

### User Registration
```python
# web/backend/app/routers/security.py

@router.post("/register")
async def register_user(
    username: str,
    password: str,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Validate username/password
    # Check if username exists
    # Hash password
    # Create user
    # Log account creation
    # Return user_id
```

### Password Change
```python
@router.post("/password/change")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify current password
    # Validate new password
    # Update password
    # Log password change
    # Invalidate old sessions?
```

## 📝 Implementation Steps

1. **Create signup endpoint in backend** (if needed)
2. **Build settings page** with tabs
3. **Build 2FA setup page** with QR code display
4. **Build audit logs page** with table
5. **Add navigation** links in main app
6. **Test all flows:**
   - Login with/without 2FA
   - Enable 2FA
   - Login with 2FA
   - Disable 2FA
   - View audit logs
   - Regenerate backup codes
7. **Add error handling** and loading states
8. **Style consistently** with existing pages

## 🚀 Quick Start for Development

```bash
cd web/frontend
npm run dev
```

Visit:
- http://localhost:3000/login - Updated with 2FA
- http://localhost:3000/settings/security - (Create this)
- http://localhost:3000/settings/audit-logs - (Create this)

## 📚 Resources

- **Ant Design Components:** https://ant.design/components/overview/
- **API Client:** `web/frontend/lib/api.ts` (all endpoints ready)
- **Backend Docs:** http://localhost:8000/docs (Swagger UI)
- **2FA Guide:** `/AI_CHARACTERS_GUIDE.md` (for backend reference)

---

**Current Status:** Backend is complete, frontend login page updated with 2FA. Remaining: settings pages and audit logs display.
