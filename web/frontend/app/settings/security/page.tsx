/**
 * 2FA Security Settings Page
 * Allows users to enable/disable TOTP-based two-factor authentication
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { securityAPI } from '@/lib/api';
import { copyToClipboard } from '@/lib/utils';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import {
  Shield,
  ShieldCheck,
  ShieldOff,
  Key,
  Copy,
  Download,
  CheckCircle2,
  XCircle,
  Info,
  AlertCircle,
  Lock
} from 'lucide-react';

interface TOTPSetup {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

export default function SecuritySettingsPage() {
  const router = useRouter();
  const { toast } = useToast();

  // 2FA status
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [backupCodesRemaining, setBackupCodesRemaining] = useState(0);
  const [loading, setLoading] = useState(true);

  // Setup flow
  const [showSetupModal, setShowSetupModal] = useState(false);
  const [setupData, setSetupData] = useState<TOTPSetup | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [setupLoading, setSetupLoading] = useState(false);

  // Disable flow
  const [showDisableModal, setShowDisableModal] = useState(false);
  const [disablePassword, setDisablePassword] = useState('');
  const [disableTotpCode, setDisableTotpCode] = useState('');
  const [disableLoading, setDisableLoading] = useState(false);

  // Regenerate backup codes
  const [showRegenerateModal, setShowRegenerateModal] = useState(false);
  const [regenerateCode, setRegenerateCode] = useState('');
  const [newBackupCodes, setNewBackupCodes] = useState<string[]>([]);
  const [regenerateLoading, setRegenerateLoading] = useState(false);

  // Load 2FA status on mount
  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const status = await securityAPI.get2FAStatus();
      setIs2FAEnabled(status.enabled);
      setBackupCodesRemaining(status.backup_codes_remaining);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load 2FA status",
        variant: "destructive",
      });
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Start 2FA setup
  const handleStartSetup = async () => {
    setSetupLoading(true);
    try {
      const data = await securityAPI.setup2FA();
      setSetupData(data);
      setShowSetupModal(true);
      toast({
        title: "QR Code Ready",
        description: "Scan the QR code with your authenticator app",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to start 2FA setup',
        variant: "destructive",
      });
    } finally {
      setSetupLoading(false);
    }
  };

  // Enable 2FA
  const handleEnable2FA = async () => {
    if (!verificationCode.trim()) {
      toast({
        title: "Error",
        description: "Please enter the verification code",
        variant: "destructive",
      });
      return;
    }

    setSetupLoading(true);
    try {
      const response = await securityAPI.enable2FA(verificationCode.trim());
      if (response.success) {
        toast({
          title: "Success",
          description: "2FA enabled successfully!",
        });
        setShowSetupModal(false);
        setVerificationCode('');
        setSetupData(null);
        await loadStatus();
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to enable 2FA',
        variant: "destructive",
      });
    } finally {
      setSetupLoading(false);
    }
  };

  // Disable 2FA
  const handleDisable2FA = async () => {
    if (!disablePassword.trim() && !disableTotpCode.trim()) {
      toast({
        title: "Error",
        description: "Please enter your password or TOTP code",
        variant: "destructive",
      });
      return;
    }

    setDisableLoading(true);
    try {
      const response = await securityAPI.disable2FA(
        disablePassword.trim() || undefined,
        disableTotpCode.trim() || undefined
      );
      if (response.success) {
        toast({
          title: "Success",
          description: "2FA disabled successfully",
        });
        setShowDisableModal(false);
        setDisablePassword('');
        setDisableTotpCode('');
        await loadStatus();
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to disable 2FA',
        variant: "destructive",
      });
    } finally {
      setDisableLoading(false);
    }
  };

  // Regenerate backup codes
  const handleRegenerateBackupCodes = async () => {
    if (!regenerateCode.trim()) {
      toast({
        title: "Error",
        description: "Please enter your authenticator code",
        variant: "destructive",
      });
      return;
    }

    setRegenerateLoading(true);
    try {
      const response = await securityAPI.regenerateBackupCodes(regenerateCode.trim());
      if (response.success && response.backup_codes) {
        setNewBackupCodes(response.backup_codes);
        toast({
          title: "Success",
          description: "Backup codes regenerated successfully",
        });
        await loadStatus();
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to regenerate backup codes',
        variant: "destructive",
      });
    } finally {
      setRegenerateLoading(false);
    }
  };

  // Copy backup codes to clipboard
  const handleCopyBackupCodes = async (codes: string[]) => {
    const text = codes.join('\n');
    const success = await copyToClipboard(text);
    if (success) {
      toast({
        title: "Success",
        description: "Backup codes copied to clipboard",
      });
    } else {
      toast({
        title: "Error",
        description: "Failed to copy to clipboard",
        variant: "destructive",
      });
    }
  };

  // Download backup codes as text file
  const handleDownloadBackupCodes = (codes: string[]) => {
    const text = codes.join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plural-chat-backup-codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast({
      title: "Success",
      description: "Backup codes downloaded",
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <Shield className="h-12 w-12 animate-pulse mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading security settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Security Settings</h1>
          <p className="text-muted-foreground mt-2">Manage two-factor authentication and security</p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-blue-600" />
                  Two-Factor Authentication
                </CardTitle>
                <CardDescription className="mt-1">
                  Add an extra layer of security to your account
                </CardDescription>
              </div>
              <div>
                {is2FAEnabled ? (
                  <Badge variant="default" className="bg-green-600 gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    Enabled
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="gap-1">
                    <XCircle className="h-3 w-3" />
                    Disabled
                  </Badge>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                2FA adds an extra layer of security by requiring a code from your authenticator app (like Google Authenticator or Authy) in addition to your password when logging in.
              </AlertDescription>
            </Alert>

            <Separator />

            {/* If 2FA is disabled - show enable option */}
            {!is2FAEnabled && (
              <div className="text-center py-8">
                <ShieldOff className="h-16 w-16 text-blue-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Enable Two-Factor Authentication</h3>
                <p className="text-muted-foreground mb-6">
                  Protect your account with TOTP-based authentication
                </p>
                <Button
                  onClick={handleStartSetup}
                  disabled={setupLoading}
                >
                  <Shield className="h-4 w-4 mr-2" />
                  {setupLoading ? 'Setting up...' : 'Enable 2FA'}
                </Button>
              </div>
            )}

            {/* If 2FA is enabled - show management options */}
            {is2FAEnabled && (
              <div className="space-y-4">
                <Card className="bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800">
                  <CardContent className="pt-6">
                    <div className="flex items-center gap-3">
                      <CheckCircle2 className="h-8 w-8 text-green-600" />
                      <div>
                        <h3 className="text-lg font-semibold text-green-900 dark:text-green-100">
                          Two-Factor Authentication is Active
                        </h3>
                        <p className="text-green-700 dark:text-green-300">
                          Your account is protected with TOTP-based authentication
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-muted/50">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold mb-1 flex items-center gap-2">
                          <Key className="h-5 w-5" />
                          Backup Codes
                        </h3>
                        <p className="text-muted-foreground">
                          {backupCodesRemaining} backup code{backupCodesRemaining !== 1 ? 's' : ''} remaining
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => setShowRegenerateModal(true)}
                      >
                        Regenerate Codes
                      </Button>
                    </div>
                    {backupCodesRemaining < 3 && (
                      <Alert variant="destructive" className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          You're running low on backup codes. Consider regenerating them.
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>

                <div className="flex justify-center pt-4">
                  <Button
                    variant="destructive"
                    onClick={() => setShowDisableModal(true)}
                  >
                    <ShieldOff className="h-4 w-4 mr-2" />
                    Disable 2FA
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="mt-6 text-center">
          <Link href="/settings" className="text-primary hover:underline">
            ← Back to Settings
          </Link>
        </div>
      </div>

      {/* Setup 2FA Modal */}
      <Dialog open={showSetupModal} onOpenChange={setShowSetupModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Enable Two-Factor Authentication</DialogTitle>
            <DialogDescription>
              Scan the QR code with your authenticator app
            </DialogDescription>
          </DialogHeader>

          {setupData && (
            <div className="space-y-4">
              {/* QR Code */}
              <div className="flex justify-center p-4 bg-white rounded-lg">
                <img
                  src={setupData.qr_code}
                  alt="2FA QR Code"
                  className="w-48 h-48"
                />
              </div>

              {/* Manual Entry */}
              <div className="space-y-2">
                <Label>Or enter this code manually:</Label>
                <div className="flex gap-2">
                  <Input
                    value={setupData.secret}
                    readOnly
                    className="font-mono text-sm"
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => {
                      copyToClipboard(setupData.secret);
                      toast({
                        title: "Copied",
                        description: "Secret key copied to clipboard",
                      });
                    }}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Backup Codes */}
              <div className="space-y-2">
                <Label>Save these backup codes:</Label>
                <div className="bg-muted p-3 rounded-lg font-mono text-sm space-y-1">
                  {setupData.backup_codes.map((code, idx) => (
                    <div key={idx}>{code}</div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopyBackupCodes(setupData.backup_codes)}
                    className="flex-1"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Codes
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownloadBackupCodes(setupData.backup_codes)}
                    className="flex-1"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </div>

              {/* Verification Code */}
              <div className="space-y-2">
                <Label htmlFor="verification-code">Enter verification code:</Label>
                <Input
                  id="verification-code"
                  type="text"
                  placeholder="000000"
                  maxLength={6}
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSetupModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleEnable2FA} disabled={setupLoading}>
              {setupLoading ? 'Enabling...' : 'Enable 2FA'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Disable 2FA Modal */}
      <Dialog open={showDisableModal} onOpenChange={setShowDisableModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Disable Two-Factor Authentication</DialogTitle>
            <DialogDescription>
              Enter your password or authenticator code to disable 2FA
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Disabling 2FA will make your account less secure
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="disable-password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="disable-password"
                  type="password"
                  placeholder="Enter your password"
                  value={disablePassword}
                  onChange={(e) => setDisablePassword(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <p className="text-center text-sm text-muted-foreground">OR</p>

            <div className="space-y-2">
              <Label htmlFor="disable-totp">Authenticator Code</Label>
              <div className="relative">
                <Shield className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="disable-totp"
                  type="text"
                  placeholder="000000"
                  maxLength={6}
                  value={disableTotpCode}
                  onChange={(e) => setDisableTotpCode(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDisableModal(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDisable2FA}
              disabled={disableLoading}
            >
              {disableLoading ? 'Disabling...' : 'Disable 2FA'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Regenerate Backup Codes Modal */}
      <Dialog open={showRegenerateModal} onOpenChange={setShowRegenerateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Regenerate Backup Codes</DialogTitle>
            <DialogDescription>
              This will invalidate your existing backup codes
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {newBackupCodes.length === 0 ? (
              <>
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Enter your authenticator code to generate new backup codes
                  </AlertDescription>
                </Alert>

                <div className="space-y-2">
                  <Label htmlFor="regenerate-code">Authenticator Code</Label>
                  <Input
                    id="regenerate-code"
                    type="text"
                    placeholder="000000"
                    maxLength={6}
                    value={regenerateCode}
                    onChange={(e) => setRegenerateCode(e.target.value)}
                  />
                </div>
              </>
            ) : (
              <>
                <Alert>
                  <CheckCircle2 className="h-4 w-4" />
                  <AlertDescription>
                    New backup codes generated! Save these codes securely.
                  </AlertDescription>
                </Alert>

                <div className="bg-muted p-3 rounded-lg font-mono text-sm space-y-1">
                  {newBackupCodes.map((code, idx) => (
                    <div key={idx}>{code}</div>
                  ))}
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => handleCopyBackupCodes(newBackupCodes)}
                    className="flex-1"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Codes
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleDownloadBackupCodes(newBackupCodes)}
                    className="flex-1"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            {newBackupCodes.length === 0 ? (
              <>
                <Button variant="outline" onClick={() => setShowRegenerateModal(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleRegenerateBackupCodes}
                  disabled={regenerateLoading}
                >
                  {regenerateLoading ? 'Regenerating...' : 'Regenerate Codes'}
                </Button>
              </>
            ) : (
              <Button onClick={() => {
                setShowRegenerateModal(false);
                setNewBackupCodes([]);
                setRegenerateCode('');
              }}>
                Done
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
