/**
 * Login page for PluralKit token authentication
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input, Button, Card, Alert } from 'antd';
import { LockOutlined, LinkOutlined } from '@ant-design/icons';
import { authAPI } from '@/lib/api';
import { useStore } from '@/lib/store';

export default function LoginPage() {
  const [token, setToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();
  const { setUser } = useStore();

  const handleLogin = async () => {
    if (!token.trim()) {
      setError('Please enter your PluralKit API token');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const user = await authAPI.login(token);
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
            Connect with your PluralKit system
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

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              PluralKit API Token
            </label>
            <Input.Password
              size="large"
              prefix={<LockOutlined />}
              placeholder="Enter your PluralKit API token"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              onPressEnter={handleLogin}
            />
          </div>

          <Button
            type="primary"
            size="large"
            block
            loading={loading}
            onClick={handleLogin}
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
      </Card>
    </div>
  );
}
