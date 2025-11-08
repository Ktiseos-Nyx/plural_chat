/**
 * Main settings page with tabs for Profile, Security, and Audit Logs
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Tabs, Input, Button, Form, message, Alert } from 'antd';
import { UserOutlined, LockOutlined, SafetyOutlined, HistoryOutlined, LinkOutlined, SyncOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { authAPI } from '@/lib/api';

export default function SettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<string>('profile');
  const [loading, setLoading] = useState(false);

  // PluralKit sync state
  const [pkToken, setPkToken] = useState('');
  const [pkLoading, setPkLoading] = useState(false);
  const [pkSynced, setPkSynced] = useState(false);

  const handleProfileUpdate = async (values: any) => {
    setLoading(true);
    try {
      // TODO: Implement profile update API call
      message.success('Profile updated successfully');
    } catch (error) {
      message.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (values: any) => {
    setLoading(true);
    try {
      // TODO: Implement password change API call
      message.success('Password changed successfully');
    } catch (error) {
      message.error('Failed to change password');
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
                      <Form
                        layout="vertical"
                        onFinish={handleProfileUpdate}
                        initialValues={{
                          username: '',
                          email: '',
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
