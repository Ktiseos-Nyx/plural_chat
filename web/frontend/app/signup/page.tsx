/**
 * Signup page for new user registration
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Input, Button, Card, Alert } from 'antd';
import { LockOutlined, UserOutlined, MailOutlined } from '@ant-design/icons';
import { securityAPI, authAPI } from '@/lib/api';
import { useStore } from '@/lib/store';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';

export default function SignupPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const router = useRouter();
  const { setUser } = useStore();

  const handleSignup = async () => {
    // Validation
    if (!username.trim() || !password.trim() || !confirmPassword.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    if (username.length < 3) {
      setError('Username must be at least 3 characters long');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (email.trim() && !email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Step 1: Register the user
      await securityAPI.register({
        username: username.trim(),
        password: password.trim(),
        email: email.trim() || undefined,
      });

      setSuccess(true);

      // Step 2: Auto-login the user
      try {
        const loginResponse = await securityAPI.login({
          username: username.trim(),
          password: password.trim(),
        });

        if (loginResponse.access_token) {
          // Fetch user data and set in store
          const userData = await authAPI.verifyToken();
          setUser(userData);

          // Redirect to home page
          setTimeout(() => {
            router.push('/');
          }, 1500);
        } else {
          // Registration succeeded but auto-login failed, redirect to login
          setTimeout(() => {
            router.push('/login');
          }, 2000);
        }
      } catch (loginError) {
        // Registration succeeded but auto-login failed, redirect to login
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        'Registration failed. Username may already be taken.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-4">
        <Card
          style={{ width: '100%', maxWidth: 500 }}
          className="shadow-lg"
        >
          <div className="text-center py-8">
            <div className="text-6xl mb-4">🎉</div>
            <h1 className="text-2xl font-bold mb-2">
              Account Created!
            </h1>
            <p className="text-muted-foreground mb-4">
              Logging you in...
            </p>
          </div>
        </Card>
      </div>
    );
  }

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
            Create Account
          </h1>
          <p className="text-muted-foreground">
            Join Plural Chat to get started
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
            <label className="block text-sm font-medium mb-2">
              Username <span className="text-red-500">*</span>
            </label>
            <Input
              size="large"
              prefix={<UserOutlined />}
              placeholder="Choose a username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onPressEnter={handleSignup}
            />
            <div className="text-xs text-muted-foreground mt-1">
              At least 3 characters
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Email <span className="text-muted-foreground">(optional)</span>
            </label>
            <Input
              size="large"
              prefix={<MailOutlined />}
              placeholder="your.email@example.com"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onPressEnter={handleSignup}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Password <span className="text-red-500">*</span>
            </label>
            <Input.Password
              size="large"
              prefix={<LockOutlined />}
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onPressEnter={handleSignup}
            />
            <div className="text-xs text-muted-foreground mt-1">
              At least 8 characters
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Confirm Password <span className="text-red-500">*</span>
            </label>
            <Input.Password
              size="large"
              prefix={<LockOutlined />}
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              onPressEnter={handleSignup}
            />
          </div>

          <Button
            type="primary"
            size="large"
            block
            loading={loading}
            onClick={handleSignup}
          >
            Create Account
          </Button>

          <div className="text-center text-sm">
            Already have an account?{' '}
            <Link href="/login" className="text-primary hover:underline font-medium">
              Sign in
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
}
