/**
 * Login page with username/password and 2FA support
 */
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { securityAPI, authAPI } from '@/lib/api';
import { useStore } from '@/lib/store';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Label } from '@/components/ui/label';
import { Lock, User, Shield, AlertCircle } from 'lucide-react';

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
          const userData = await authAPI.verifyToken();
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
          const userData = await authAPI.verifyToken();
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
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold">Plural Chat</CardTitle>
          <CardDescription>
            {requires2FA ? 'Two-Factor Authentication' : 'Sign in to continue'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

        {requires2FA ? (
          // 2FA verification screen
          <div className="space-y-4">
            <div className="text-center">
              <Shield className="h-12 w-12 text-primary mx-auto mb-2" />
              <p className="text-sm text-muted-foreground mb-4">
                Enter your 6-digit code from your authenticator app, or use a backup code.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="totp">Authenticator Code</Label>
              <div className="relative">
                <Shield className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="totp"
                  type="text"
                  placeholder="000000"
                  maxLength={6}
                  value={totpCode}
                  onChange={(e) => {
                    setTotpCode(e.target.value);
                    setBackupCode(''); // Clear backup code
                  }}
                  onKeyDown={(e) => e.key === 'Enter' && handle2FAVerification()}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="text-center text-muted-foreground text-sm">OR</div>

            <div className="space-y-2">
              <Label htmlFor="backup">Backup Code</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="backup"
                  type="text"
                  placeholder="Enter 8-digit backup code"
                  maxLength={8}
                  value={backupCode}
                  onChange={(e) => {
                    setBackupCode(e.target.value);
                    setTotpCode(''); // Clear TOTP code
                  }}
                  onKeyDown={(e) => e.key === 'Enter' && handle2FAVerification()}
                  className="pl-10"
                />
              </div>
            </div>

            <Button
              className="w-full"
              disabled={loading}
              onClick={handle2FAVerification}
            >
              {loading ? 'Verifying...' : 'Verify'}
            </Button>

            <Button
              variant="ghost"
              className="w-full"
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
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleUsernameLogin()}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleUsernameLogin()}
                  className="pl-10"
                />
              </div>
            </div>

            <Button
              className="w-full"
              disabled={loading}
              onClick={handleUsernameLogin}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>

            <div className="text-center text-sm">
              Don't have an account?{' '}
              <Link href="/signup" className="text-primary hover:underline font-medium">
                Sign up
              </Link>
            </div>
          </div>
        )}
        </CardContent>
      </Card>
    </div>
  );
}
