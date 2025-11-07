/**
 * Main settings page with tabs for Profile, Security, and Audit Logs
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Tabs, Input, Button, Form, message, Alert } from 'antd';
import { UserOutlined, LockOutlined, SafetyOutlined, HistoryOutlined } from '@ant-design/icons';
import Link from 'next/link';

export default function SettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<string>('profile');
  const [loading, setLoading] = useState(false);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
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
