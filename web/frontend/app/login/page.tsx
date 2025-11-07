/**
 * Login page with username/password and 2FA support
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input, Button, Card, Alert, Tabs } from 'antd';
import { LockOutlined, UserOutlined, LinkOutlined, SafetyOutlined } from '@ant-design/icons';
import { authAPI, securityAPI } from '@/lib/api';
import { useStore } from '@/lib/store';
import Link from 'next/link';

export default function LoginPage() {
  const [activeTab, setActiveTab] = useState<string>('username');

  // Username/Password login state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [backupCode, setBackupCode] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);

  // PluralKit login state
  const [pkToken, setPkToken] = useState('');

  // Common state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const { setUser } = useStore();

  // Username/Password login handler
  const handleUsernameLogin = async () => {
    if (!username.trim() || !password.trim()) {
      setError('Please enter username and password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await securityAPI.login({
        username: username.trim(),
        password: password.trim(),
      });

      if (response.requires_2fa) {
        // 2FA required
        setRequires2FA(true);
        setUserId(response.user_id || null);
        setError('');
      } else if (response.access_token) {
        // Success
        router.push('/');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // 2FA verification handler
  const handle2FAVerification = async () => {
    if (!totpCode.trim() && !backupCode.trim()) {
      setError('Please enter a 2FA code or backup code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await securityAPI.login({
        username: username.trim(),
        password: password.trim(),
        totp_code: totpCode.trim() || undefined,
        backup_code: backupCode.trim() || undefined,
      });

      if (response.access_token) {
        // Success
        router.push('/');
      } else {
        setError('Verification failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '2FA verification failed');
    } finally {
      setLoading(false);
    }
  };

  // PluralKit login handler
  const handlePKLogin = async () => {
    if (!pkToken.trim()) {
      setError('Please enter your PluralKit API token');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const user = await authAPI.login(pkToken);
      setUser(user);
      router.push('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your token.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      <Card
        style={{ width: '100%', maxWidth: 500 }}
        className="shadow-lg"
      >
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Plural Chat
          </h1>
          <p className="text-gray-600">
            {requires2FA ? 'Two-Factor Authentication' : 'Sign in to continue'}
          </p>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            closable
            onClose={() => setError('')}
            className="mb-4"
          />
        )}

        {requires2FA ? (
          // 2FA verification screen
          <div className="space-y-4">
            <div className="text-center">
              <SafetyOutlined className="text-4xl text-blue-500 mb-2" />
              <p className="text-gray-700 mb-4">
                Enter your 6-digit code from your authenticator app, or use a backup code.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Authenticator Code
              </label>
              <Input
                size="large"
                prefix={<SafetyOutlined />}
                placeholder="000000"
                maxLength={6}
                value={totpCode}
                onChange={(e) => {
                  setTotpCode(e.target.value);
                  setBackupCode(''); // Clear backup code
                }}
                onPressEnter={handle2FAVerification}
              />
            </div>

            <div className="text-center text-gray-500 text-sm">OR</div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Backup Code
              </label>
              <Input
                size="large"
                prefix={<LockOutlined />}
                placeholder="Enter 8-digit backup code"
                maxLength={8}
                value={backupCode}
                onChange={(e) => {
                  setBackupCode(e.target.value);
                  setTotpCode(''); // Clear TOTP code
                }}
                onPressEnter={handle2FAVerification}
              />
            </div>

            <Button
              type="primary"
              size="large"
              block
              loading={loading}
              onClick={handle2FAVerification}
            >
              Verify
            </Button>

            <Button
              type="link"
              block
              onClick={() => {
                setRequires2FA(false);
                setTotpCode('');
                setBackupCode('');
                setError('');
              }}
            >
              ← Back to login
            </Button>
          </div>
        ) : (
          // Normal login screen
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: 'username',
                label: 'Username/Password',
                children: (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Username
                      </label>
                      <Input
                        size="large"
                        prefix={<UserOutlined />}
                        placeholder="Enter your username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        onPressEnter={handleUsernameLogin}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Password
                      </label>
                      <Input.Password
                        size="large"
                        prefix={<LockOutlined />}
                        placeholder="Enter your password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        onPressEnter={handleUsernameLogin}
                      />
                    </div>

                    <Button
                      type="primary"
                      size="large"
                      block
                      loading={loading}
                      onClick={handleUsernameLogin}
                    >
                      Sign In
                    </Button>

                    <div className="text-center text-sm text-gray-600">
                      Don't have an account?{' '}
                      <Link href="/signup" className="text-blue-600 hover:underline">
                        Sign up
                      </Link>
                    </div>
                  </div>
                ),
              },
              {
                key: 'pluralkit',
                label: 'PluralKit',
                children: (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        PluralKit API Token
                      </label>
                      <Input.Password
                        size="large"
                        prefix={<LockOutlined />}
                        placeholder="Enter your PluralKit API token"
                        value={pkToken}
                        onChange={(e) => setPkToken(e.target.value)}
                        onPressEnter={handlePKLogin}
                      />
                    </div>

                    <Button
                      type="primary"
                      size="large"
                      block
                      loading={loading}
                      onClick={handlePKLogin}
                    >
                      Connect to PluralKit
                    </Button>

                    <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                      <h3 className="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
                        <LinkOutlined /> How to get your token:
                      </h3>
                      <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                        <li>
                          Visit{' '}
                          <a
                            href="https://pluralkit.me/dash"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline font-medium"
                          >
                            pluralkit.me/dash
                          </a>
                        </li>
                        <li>Click "Get API Token"</li>
                        <li>Copy the token and paste it above</li>
                      </ol>
                    </div>
                  </div>
                ),
              },
            ]}
          />
        )}
      </Card>
    </div>
  );
}
