/**
 * Main settings page with tabs for Profile, Security, and Audit Logs
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Tabs, Input, Button, Form, message, Alert, Upload } from 'antd';
import { UserOutlined, LockOutlined, SafetyOutlined, HistoryOutlined, LinkOutlined, SyncOutlined, BgColorsOutlined, CameraOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { authAPI, securityAPI, membersAPI, type Member } from '@/lib/api';
import { useStore } from '@/lib/store';

export default function SettingsPage() {
  const router = useRouter();
  const { user, setUser } = useStore();
  const [activeTab, setActiveTab] = useState<string>('profile');
  const [loading, setLoading] = useState(false);

  // Members state
  const [members, setMembers] = useState<Member[]>([]);
  const [membersLoading, setMembersLoading] = useState(false);

  // PluralKit sync state
  const [pkToken, setPkToken] = useState('');
  const [pkLoading, setPkLoading] = useState(false);
  const [pkSynced, setPkSynced] = useState(false);

  // Avatar upload state
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  // Theme color state
  const [themeColor, setThemeColor] = useState('#6c757d');

  // Load user data on mount
  useEffect(() => {
    if (!user) {
      router.push('/login');
    } else {
      setThemeColor(user.theme_color || '#6c757d');
      if (user.avatar_path) {
        setAvatarPreview(`http://localhost:8000${user.avatar_path}`);
      }
      loadMembers();
    }
  }, [user, router]);

  const loadMembers = async () => {
    setMembersLoading(true);
    try {
      const data = await membersAPI.getAll();
      setMembers(data);
    } catch (error) {
      console.error('Failed to load members:', error);
    } finally {
      setMembersLoading(false);
    }
  };

  const handleAddMember = async (values: any) => {
    setMembersLoading(true);
    try {
      await membersAPI.create({
        name: values.name,
        pronouns: values.pronouns,
        color: values.color || '#6c757d',
      });
      message.success('Member added successfully');
      await loadMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to add member');
    } finally {
      setMembersLoading(false);
    }
  };

  const handleDeleteMember = async (memberId: number) => {
    setMembersLoading(true);
    try {
      await membersAPI.delete(memberId);
      message.success('Member deleted successfully');
      await loadMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to delete member');
    } finally {
      setMembersLoading(false);
    }
  };

  const handleProfileUpdate = async (values: any) => {
    setLoading(true);
    try {
      // Update profile data
      await securityAPI.updateProfile({
        username: values.username,
        email: values.email || undefined,
        theme_color: themeColor,
      });

      // Upload avatar if selected
      if (avatarFile) {
        await securityAPI.uploadAvatar(avatarFile);
        setAvatarFile(null); // Clear after upload
      }

      // Refresh user data
      const userData = await authAPI.verifyToken();
      setUser(userData);

      message.success('Profile updated successfully');
    } catch (error: any) {
      message.error(error.userMessage || error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarChange = (file: File) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      message.error('Only JPEG, PNG, GIF, and WebP images are allowed');
      return false;
    }

    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      message.error('File size must be less than 5MB');
      return false;
    }

    setAvatarFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setAvatarPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    return false; // Prevent automatic upload
  };

  const handlePasswordChange = async (values: any) => {
    setLoading(true);
    try {
      await securityAPI.changePassword({
        current_password: values.current_password,
        new_password: values.new_password,
      });
      message.success('Password changed successfully');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handlePluralKitSync = async () => {
    if (!pkToken.trim()) {
      message.error('Please enter your PluralKit API token');
      return;
    }

    setPkLoading(true);
    try {
      await authAPI.setPKToken(pkToken);
      message.success('PluralKit members synced successfully!');
      setPkSynced(true);
      setPkToken(''); // Clear token after successful sync
    } catch (error: any) {
      message.error(
        error.response?.data?.detail ||
        'Failed to sync PluralKit members. Please check your token.'
      );
    } finally {
      setPkLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Settings</h1>
            <p className="text-muted-foreground mt-2">Manage your account settings and preferences</p>
          </div>
          <ThemeToggle />
        </div>

        <Card>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'profile',
                label: (
                  <span>
                    <UserOutlined /> Profile
                  </span>
                ),
                children: (
                  <div className="space-y-6">
                    <div>
                      <h2 className="text-xl font-semibold mb-4">Profile Information</h2>

                      {/* Avatar Upload */}
                      <div className="mb-6">
                        <label className="block text-sm font-medium mb-3">Profile Picture</label>
                        <div className="flex items-center gap-4">
                          <div className="w-24 h-24 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                            {avatarPreview ? (
                              <img src={avatarPreview} alt="Avatar" className="w-full h-full object-cover" />
                            ) : (
                              <UserOutlined className="text-4xl text-gray-400" />
                            )}
                          </div>
                          <Upload
                            accept="image/jpeg,image/png,image/gif,image/webp"
                            beforeUpload={handleAvatarChange}
                            showUploadList={false}
                            maxCount={1}
                          >
                            <Button icon={<CameraOutlined />} size="large">
                              Choose Avatar
                            </Button>
                          </Upload>
                          <div className="text-xs text-gray-500">
                            JPEG, PNG, GIF, WebP (Max 5MB)
                          </div>
                        </div>
                      </div>

                      <Form
                        layout="vertical"
                        onFinish={handleProfileUpdate}
                        initialValues={{
                          username: user?.username || '',
                          email: user?.email || '',
                        }}
                      >
                        <Form.Item
                          label="Username"
                          name="username"
                          rules={[{ required: true, message: 'Please enter your username' }]}
                        >
                          <Input
                            prefix={<UserOutlined />}
                            placeholder="Enter your username"
                            size="large"
                          />
                        </Form.Item>

                        <Form.Item
                          label="Email (Optional)"
                          name="email"
                          rules={[{ type: 'email', message: 'Please enter a valid email' }]}
                        >
                          <Input
                            type="email"
                            placeholder="Enter your email"
                            size="large"
                          />
                        </Form.Item>

                        {/* Theme Color Picker */}
                        <Form.Item label="Theme Color">
                          <div className="flex gap-2">
                            <Input
                              size="large"
                              prefix={<BgColorsOutlined />}
                              placeholder="#6c757d"
                              value={themeColor}
                              onChange={(e) => setThemeColor(e.target.value)}
                            />
                            <input
                              type="color"
                              value={themeColor}
                              onChange={(e) => setThemeColor(e.target.value)}
                              className="w-12 h-10 rounded border cursor-pointer"
                            />
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Choose a color for your profile theme
                          </div>
                        </Form.Item>

                        <Form.Item>
                          <Button type="primary" htmlType="submit" loading={loading} size="large">
                            Update Profile
                          </Button>
                        </Form.Item>
                      </Form>
                    </div>

                    <div className="border-t pt-6">
                      <h2 className="text-xl font-semibold mb-4">Change Password</h2>
                      <Form layout="vertical" onFinish={handlePasswordChange}>
                        <Form.Item
                          label="Current Password"
                          name="current_password"
                          rules={[{ required: true, message: 'Please enter your current password' }]}
                        >
                          <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="Enter your current password"
                            size="large"
                          />
                        </Form.Item>

                        <Form.Item
                          label="New Password"
                          name="new_password"
                          rules={[
                            { required: true, message: 'Please enter a new password' },
                            { min: 8, message: 'Password must be at least 8 characters' },
                          ]}
                        >
                          <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="Enter new password"
                            size="large"
                          />
                        </Form.Item>

                        <Form.Item
                          label="Confirm New Password"
                          name="confirm_password"
                          dependencies={['new_password']}
                          rules={[
                            { required: true, message: 'Please confirm your password' },
                            ({ getFieldValue }) => ({
                              validator(_, value) {
                                if (!value || getFieldValue('new_password') === value) {
                                  return Promise.resolve();
                                }
                                return Promise.reject(new Error('Passwords do not match'));
                              },
                            }),
                          ]}
                        >
                          <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="Confirm new password"
                            size="large"
                          />
                        </Form.Item>

                        <Form.Item>
                          <Button type="primary" htmlType="submit" loading={loading} size="large">
                            Change Password
                          </Button>
                        </Form.Item>
                      </Form>
                    </div>

                    <div className="border-t pt-6">
                      <h2 className="text-xl font-semibold mb-4">Members</h2>
                      <Alert
                        message="Manage Your Members"
                        description="Create and manage members/personas. You can switch between them when chatting. A default member with your username was created automatically."
                        type="info"
                        showIcon
                        className="mb-4"
                      />

                      {/* Members List */}
                      <div className="space-y-2 mb-4">
                        {membersLoading && <p className="text-gray-500">Loading members...</p>}
                        {!membersLoading && members.length === 0 && (
                          <p className="text-gray-500">No members yet. Add one below!</p>
                        )}
                        {!membersLoading && members.map((member) => (
                          <Card key={member.id} className="bg-gray-50">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <div
                                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                                  style={{ backgroundColor: member.color || '#6c757d' }}
                                >
                                  {member.name.charAt(0).toUpperCase()}
                                </div>
                                <div>
                                  <h4 className="font-semibold">{member.name}</h4>
                                  {member.pronouns && (
                                    <p className="text-sm text-gray-600">{member.pronouns}</p>
                                  )}
                                </div>
                              </div>
                              <Button
                                danger
                                onClick={() => {
                                  if (confirm(`Delete member "${member.name}"?`)) {
                                    handleDeleteMember(member.id);
                                  }
                                }}
                                disabled={membersLoading}
                              >
                                Delete
                              </Button>
                            </div>
                          </Card>
                        ))}
                      </div>

                      {/* Add Member Form */}
                      <Form layout="inline" onFinish={handleAddMember}>
                        <Form.Item
                          name="name"
                          rules={[{ required: true, message: 'Name required' }]}
                        >
                          <Input placeholder="Member name" size="large" />
                        </Form.Item>
                        <Form.Item name="pronouns">
                          <Input placeholder="Pronouns (optional)" size="large" />
                        </Form.Item>
                        <Form.Item name="color">
                          <Input type="color" size="large" defaultValue="#6c757d" />
                        </Form.Item>
                        <Form.Item>
                          <Button type="primary" htmlType="submit" loading={membersLoading} size="large">
                            Add Member
                          </Button>
                        </Form.Item>
                      </Form>
                    </div>

                    <div className="border-t pt-6">
                      <h2 className="text-xl font-semibold mb-4">PluralKit Integration</h2>
                      <Alert
                        message="Sync Your PluralKit Members"
                        description="Connect your PluralKit account to automatically import your system members into Plural Chat. This allows you to chat as any of your members."
                        type="info"
                        showIcon
                        icon={<LinkOutlined />}
                        className="mb-4"
                      />

                      {pkSynced && (
                        <Alert
                          message="Members Synced Successfully!"
                          description="Your PluralKit members have been imported. You can now select them when sending messages."
                          type="success"
                          showIcon
                          closable
                          onClose={() => setPkSynced(false)}
                          className="mb-4"
                        />
                      )}

                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">
                            PluralKit API Token
                          </label>
                          <Input.Password
                            size="large"
                            prefix={<LockOutlined />}
                            placeholder="Enter your PluralKit API token"
                            value={pkToken}
                            onChange={(e) => setPkToken(e.target.value)}
                            onPressEnter={handlePluralKitSync}
                          />
                        </div>

                        <Button
                          type="primary"
                          size="large"
                          icon={<SyncOutlined />}
                          loading={pkLoading}
                          onClick={handlePluralKitSync}
                        >
                          Sync Members
                        </Button>

                        <Card className="bg-muted/50 mt-4">
                          <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                            <LinkOutlined /> How to get your PluralKit token:
                          </h3>
                          <ol className="text-sm space-y-1 list-decimal list-inside text-muted-foreground">
                            <li>
                              Visit{' '}
                              <a
                                href="https://pluralkit.me/dash"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="underline font-medium text-primary"
                              >
                                pluralkit.me/dash
                              </a>
                            </li>
                            <li>Click "Get API Token"</li>
                            <li>Copy the token and paste it above</li>
                            <li>Click "Sync Members" to import your system</li>
                          </ol>
                        </Card>
                      </div>
                    </div>
                  </div>
                ),
              },
              {
                key: 'security',
                label: (
                  <span>
                    <SafetyOutlined /> Security
                  </span>
                ),
                children: (
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold mb-4">Security Settings</h2>

                    <Alert
                      message="Two-Factor Authentication"
                      description="Add an extra layer of security to your account by enabling two-factor authentication (2FA)."
                      type="info"
                      showIcon
                      className="mb-4"
                    />

                    <Card className="bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                            <SafetyOutlined className="text-blue-600" />
                            Two-Factor Authentication (2FA)
                          </h3>
                          <p className="text-gray-600 mb-4">
                            Secure your account with TOTP-based authentication using apps like Google Authenticator or Authy.
                          </p>
                          <Link href="/settings/security">
                            <Button type="primary" size="large">
                              Manage 2FA Settings →
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </Card>

                    <Card className="bg-gray-50 mt-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                            <HistoryOutlined className="text-green-600" />
                            Security Activity
                          </h3>
                          <p className="text-gray-600 mb-4">
                            View your recent security activity and login history.
                          </p>
                          <Link href="/settings/audit-logs">
                            <Button size="large">
                              View Activity Log →
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </Card>
                  </div>
                ),
              },
              {
                key: 'audit',
                label: (
                  <span>
                    <HistoryOutlined /> Activity Log
                  </span>
                ),
                children: (
                  <div className="space-y-4">
                    <h2 className="text-xl font-semibold mb-4">Security Activity</h2>

                    <Alert
                      message="Audit Logs"
                      description="View detailed logs of all security-related events on your account."
                      type="info"
                      showIcon
                      className="mb-4"
                    />

                    <Card className="bg-gray-50">
                      <div className="text-center py-8">
                        <HistoryOutlined className="text-6xl text-gray-400 mb-4" />
                        <h3 className="text-lg font-semibold mb-2">View Full Activity Log</h3>
                        <p className="text-gray-600 mb-4">
                          See all login attempts, 2FA events, and security changes
                        </p>
                        <Link href="/settings/audit-logs">
                          <Button type="primary" size="large">
                            Open Activity Log →
                          </Button>
                        </Link>
                      </div>
                    </Card>
                  </div>
                ),
              },
            ]}
          />
        </Card>

        <div className="mt-6 text-center">
          <Link href="/" className="text-blue-600 hover:underline">
            ← Back to Chat
          </Link>
        </div>
      </div>
    </div>
  );
}
