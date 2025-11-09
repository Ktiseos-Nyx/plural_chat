/**
 * Main settings page with tabs for Profile, Security, and Audit Logs
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Tabs, Input, Button, Form, message, Alert, Upload, Modal, Tag, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined, SafetyOutlined, HistoryOutlined, LinkOutlined, SyncOutlined, BgColorsOutlined, CameraOutlined, TeamOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
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
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [memberModalOpen, setMemberModalOpen] = useState(false);
  const [memberForm] = Form.useForm();
  const [proxyTags, setProxyTags] = useState<Array<{prefix: string, suffix: string}>>([{ prefix: '', suffix: '' }]);
  const [memberAvatarFile, setMemberAvatarFile] = useState<File | null>(null);
  const [memberAvatarPreview, setMemberAvatarPreview] = useState<string | null>(null);

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

  const handleAddMember = () => {
    setEditingMember(null);
    setProxyTags([{ prefix: '', suffix: '' }]);
    setMemberAvatarFile(null);
    setMemberAvatarPreview(null);
    memberForm.resetFields();
    setMemberModalOpen(true);
  };

  const handleEditMember = (member: Member) => {
    setEditingMember(member);
    memberForm.setFieldsValue({
      name: member.name,
      pronouns: member.pronouns || '',
      color: member.color || '#6c757d',
      description: member.description || '',
    });

    // Set avatar preview if exists
    if (member.avatar_path) {
      setMemberAvatarPreview(`http://localhost:8000${member.avatar_path}`);
    } else {
      setMemberAvatarPreview(null);
    }
    setMemberAvatarFile(null);

    // Parse existing proxy tags
    if (member.proxy_tags) {
      try {
        const parsed = JSON.parse(member.proxy_tags);
        setProxyTags(parsed.length > 0 ? parsed : [{ prefix: '', suffix: '' }]);
      } catch {
        setProxyTags([{ prefix: '', suffix: '' }]);
      }
    } else {
      setProxyTags([{ prefix: '', suffix: '' }]);
    }

    setMemberModalOpen(true);
  };

  const handleMemberAvatarChange = (file: File) => {
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

    setMemberAvatarFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setMemberAvatarPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    return false; // Prevent automatic upload
  };

  const handleDeleteMember = async (memberId: number, memberName: string) => {
    if (!confirm(`Delete member "${memberName}"? This cannot be undone.`)) {
      return;
    }

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

  const handleMemberSubmit = async (values: any) => {
    setMembersLoading(true);
    try {
      // Filter out empty proxy tags
      const validProxyTags = proxyTags.filter(
        tag => tag.prefix.trim() !== '' || tag.suffix.trim() !== ''
      );

      const memberData = {
        name: values.name,
        pronouns: values.pronouns || undefined,
        color: values.color || '#6c757d',
        description: values.description || undefined,
        proxy_tags: validProxyTags.length > 0 ? JSON.stringify(validProxyTags) : undefined,
      };

      let memberId: number;
      if (editingMember) {
        await membersAPI.update(editingMember.id, memberData);
        memberId = editingMember.id;
        message.success('Member updated successfully');
      } else {
        const newMember = await membersAPI.create(memberData);
        memberId = newMember.id;
        message.success('Member created successfully');
      }

      // Upload avatar if selected
      if (memberAvatarFile) {
        await membersAPI.uploadAvatar(memberId, memberAvatarFile);
        setMemberAvatarFile(null);
      }

      setMemberModalOpen(false);
      memberForm.resetFields();
      setProxyTags([{ prefix: '', suffix: '' }]);
      setMemberAvatarPreview(null);
      await loadMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to save member');
    } finally {
      setMembersLoading(false);
    }
  };

  const addProxyTag = () => {
    setProxyTags([...proxyTags, { prefix: '', suffix: '' }]);
  };

  const removeProxyTag = (index: number) => {
    if (proxyTags.length > 1) {
      setProxyTags(proxyTags.filter((_, i) => i !== index));
    }
  };

  const updateProxyTag = (index: number, field: 'prefix' | 'suffix', value: string) => {
    const newTags = [...proxyTags];
    newTags[index][field] = value;
    setProxyTags(newTags);
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
                  </div>
                ),
              },
              {
                key: 'members',
                label: (
                  <span>
                    <TeamOutlined /> Members
                  </span>
                ),
                children: (
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <h2 className="text-xl font-semibold">Your Members</h2>
                      <Button
                        type="primary"
                        icon={<PlusOutlined />}
                        onClick={handleAddMember}
                        size="large"
                      >
                        Add Member
                      </Button>
                    </div>

                    <Alert
                      message="What are members?"
                      description="Members allow you to chat as different personas, characters, or system members. You can use proxy tags (like 'text: message') to automatically send messages as a specific member. This is optional - you can always chat as yourself!"
                      type="info"
                      showIcon
                    />

                    {/* Members List */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {membersLoading && members.length === 0 && (
                        <Card>
                          <p className="text-gray-500">Loading members...</p>
                        </Card>
                      )}

                      {!membersLoading && members.length === 0 && (
                        <Card className="col-span-full">
                          <div className="text-center py-12">
                            <UserOutlined className="text-6xl text-gray-400 mb-4" />
                            <h3 className="text-xl font-semibold mb-2">No members yet</h3>
                            <p className="text-gray-600 mb-4">
                              Create your first member to get started!
                            </p>
                            <Button
                              type="primary"
                              size="large"
                              icon={<PlusOutlined />}
                              onClick={handleAddMember}
                            >
                              Add Your First Member
                            </Button>
                          </div>
                        </Card>
                      )}

                      {members.map((member) => {
                        let proxyTagsList: Array<{prefix: string, suffix: string}> = [];
                        if (member.proxy_tags) {
                          try {
                            proxyTagsList = JSON.parse(member.proxy_tags);
                          } catch {}
                        }

                        return (
                          <Card
                            key={member.id}
                            className="hover:shadow-lg transition-shadow"
                          >
                            <div className="flex items-start gap-3 mb-3">
                              {member.avatar_path ? (
                                <div className="w-12 h-12 rounded-full overflow-hidden flex-shrink-0">
                                  <img
                                    src={`http://localhost:8000${member.avatar_path}`}
                                    alt={member.name}
                                    className="w-full h-full object-cover"
                                  />
                                </div>
                              ) : (
                                <div
                                  className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                                  style={{ backgroundColor: member.color || '#6c757d' }}
                                >
                                  {member.name.charAt(0).toUpperCase()}
                                </div>
                              )}
                              <div className="flex-1 min-w-0">
                                <h3 className="font-bold text-base truncate">{member.name}</h3>
                                {member.pronouns && (
                                  <p className="text-sm text-gray-600">{member.pronouns}</p>
                                )}
                              </div>
                            </div>

                            {member.description && (
                              <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                                {member.description}
                              </p>
                            )}

                            {proxyTagsList.length > 0 && (
                              <div className="mb-3 pb-3 border-t pt-3">
                                <p className="text-xs font-semibold text-gray-600 mb-2">
                                  Proxy Tags:
                                </p>
                                <div className="flex flex-wrap gap-1">
                                  {proxyTagsList.map((tag, idx) => (
                                    <Tag key={idx} color="blue" className="text-xs">
                                      {tag.prefix || ''}text{tag.suffix || ''}
                                    </Tag>
                                  ))}
                                </div>
                              </div>
                            )}

                            <div className="flex gap-2">
                              <Button
                                type="default"
                                icon={<EditOutlined />}
                                onClick={() => handleEditMember(member)}
                                block
                              >
                                Edit
                              </Button>
                              <Button
                                danger
                                icon={<DeleteOutlined />}
                                onClick={() => handleDeleteMember(member.id, member.name)}
                                block
                              >
                                Delete
                              </Button>
                            </div>
                          </Card>
                        );
                      })}
                    </div>

                    {/* PluralKit Integration Section */}
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

      {/* Member Add/Edit Modal */}
      <Modal
        title={editingMember ? 'Edit Member' : 'Add New Member'}
        open={memberModalOpen}
        onCancel={() => setMemberModalOpen(false)}
        footer={null}
        width={700}
      >
        <Form
          form={memberForm}
          layout="vertical"
          onFinish={handleMemberSubmit}
          className="mt-4"
          initialValues={{
            color: '#6c757d'
          }}
        >
          <Form.Item
            label="Name"
            name="name"
            rules={[{ required: true, message: 'Please enter a name' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Member name"
              size="large"
            />
          </Form.Item>

          {/* Avatar Upload */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3">Avatar (Optional)</label>
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                {memberAvatarPreview ? (
                  <img src={memberAvatarPreview} alt="Avatar" className="w-full h-full object-cover" />
                ) : (
                  <UserOutlined className="text-3xl text-gray-400" />
                )}
              </div>
              <Upload
                accept="image/jpeg,image/png,image/gif,image/webp"
                beforeUpload={handleMemberAvatarChange}
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

          <Form.Item
            label="Pronouns (Optional)"
            name="pronouns"
          >
            <Input
              placeholder="e.g., they/them, he/him, she/her"
              size="large"
            />
          </Form.Item>

          <Form.Item
            label="Description (Optional)"
            name="description"
          >
            <Input.TextArea
              placeholder="Brief description of this member..."
              rows={3}
              size="large"
            />
          </Form.Item>

          <Form.Item label="Color">
            <div className="flex gap-2">
              <Form.Item name="color" noStyle>
                <Input
                  placeholder="#6c757d"
                  size="large"
                  style={{ flex: 1 }}
                />
              </Form.Item>
              <input
                type="color"
                value={memberForm.getFieldValue('color') || '#6c757d'}
                onChange={(e) => memberForm.setFieldValue('color', e.target.value)}
                className="w-12 h-10 rounded border cursor-pointer"
              />
            </div>
          </Form.Item>

          <Divider />

          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="font-semibold text-base">Proxy Tags (Optional)</h3>
                <p className="text-sm text-gray-600">
                  Automatically send messages as this member using proxy tags
                </p>
              </div>
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={addProxyTag}
                size="small"
              >
                Add Tag
              </Button>
            </div>

            <Alert
              message="How proxy tags work"
              description={
                <div className="text-sm">
                  <p className="mb-2">
                    Proxy tags let you send messages as this member automatically. For example:
                  </p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>
                      <code>text:</code> hello → sends "hello" as this member
                    </li>
                    <li>
                      <code>:text</code> hello → sends "hello" as this member
                    </li>
                    <li>
                      <code>{'{{'}}</code> hello <code>{'}}'}</code> → sends "hello" as this member
                    </li>
                  </ul>
                </div>
              }
              type="info"
              showIcon
              icon={<LinkOutlined />}
              className="mb-3"
            />

            <Space direction="vertical" style={{ width: '100%' }} size="small">
              {proxyTags.map((tag, index) => (
                <div key={index} className="flex gap-2 items-center">
                  <Input
                    placeholder="Prefix (e.g., 'text:')"
                    value={tag.prefix}
                    onChange={(e) => updateProxyTag(index, 'prefix', e.target.value)}
                    style={{ flex: 1 }}
                  />
                  <span className="text-gray-500">message</span>
                  <Input
                    placeholder="Suffix (e.g., ':text')"
                    value={tag.suffix}
                    onChange={(e) => updateProxyTag(index, 'suffix', e.target.value)}
                    style={{ flex: 1 }}
                  />
                  {proxyTags.length > 1 && (
                    <Button
                      danger
                      type="text"
                      icon={<DeleteOutlined />}
                      onClick={() => removeProxyTag(index)}
                    />
                  )}
                </div>
              ))}
            </Space>
          </div>

          <Form.Item className="mb-0 mt-6">
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={membersLoading}
                size="large"
              >
                {editingMember ? 'Update Member' : 'Create Member'}
              </Button>
              <Button
                onClick={() => setMemberModalOpen(false)}
                size="large"
              >
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
