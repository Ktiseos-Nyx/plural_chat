/**
 * Login page with username/password and 2FA support
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input, Button, Card, Alert } from 'antd';
import { LockOutlined, UserOutlined, SafetyOutlined } from '@ant-design/icons';
import { securityAPI } from '@/lib/api';
import { useStore } from '@/lib/store';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';

export default function LoginPage() {
  // Username/Password login state
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [backupCode, setBackupCode] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);

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
        // Success - verify token and fetch user data
        try {
          const userData = await securityAPI.verifyToken();
          setUser(userData);
          router.push('/');
        } catch (verifyError) {
          setError('Login successful but failed to fetch user data');
        }
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
        // Success - verify token and fetch user data
        try {
          const userData = await securityAPI.verifyToken();
          setUser(userData);
          router.push('/');
        } catch (verifyError) {
          setError('Verification successful but failed to fetch user data');
        }
      } else {
        setError('Verification failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '2FA verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>
      <Card
        style={{ width: '100%', maxWidth: 500 }}
        className="shadow-lg"
      >
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold mb-2">
            Plural Chat
          </h1>
          <p className="text-muted-foreground">
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
              <SafetyOutlined className="text-4xl text-primary mb-2" />
              <p className="mb-4">
                Enter your 6-digit code from your authenticator app, or use a backup code.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
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

            <div className="text-center text-muted-foreground text-sm">OR</div>

            <div>
              <label className="block text-sm font-medium mb-2">
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
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
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
              <label className="block text-sm font-medium mb-2">
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

            <div className="text-center text-sm">
              Don't have an account?{' '}
              <Link href="/signup" className="text-primary hover:underline font-medium">
                Sign up
              </Link>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
