/**
 * 2FA Security Settings Page
 * Allows users to enable/disable TOTP-based two-factor authentication
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  Button,
  Input,
  Alert,
  Modal,
  message,
  Tag,
  Space,
  Divider,
  Spin,
} from 'antd';
import {
  SafetyOutlined,
  LockOutlined,
  CopyOutlined,
  KeyOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import { securityAPI } from '@/lib/api';
import { copyToClipboard } from '@/lib/utils';
import Link from 'next/link';

interface TOTPSetup {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

export default function SecuritySettingsPage() {
  const router = useRouter();

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
      message.error('Failed to load 2FA status');
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
      message.info('Scan the QR code with your authenticator app');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to start 2FA setup');
    } finally {
      setSetupLoading(false);
    }
  };

  // Enable 2FA
  const handleEnable2FA = async () => {
    if (!verificationCode.trim()) {
      message.error('Please enter the verification code');
      return;
    }

    setSetupLoading(true);
    try {
      const response = await securityAPI.enable2FA(verificationCode.trim());
      if (response.success) {
        message.success('2FA enabled successfully!');
        setShowSetupModal(false);
        setVerificationCode('');
        setSetupData(null);
        await loadStatus(); // Reload status
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to enable 2FA');
    } finally {
      setSetupLoading(false);
    }
  };

  // Disable 2FA
  const handleDisable2FA = async () => {
    if (!disablePassword.trim() && !disableTotpCode.trim()) {
      message.error('Please enter your password or TOTP code');
      return;
    }

    setDisableLoading(true);
    try {
      const response = await securityAPI.disable2FA(
        disablePassword.trim() || undefined,
        disableTotpCode.trim() || undefined
      );
      if (response.success) {
        message.success('2FA disabled successfully');
        setShowDisableModal(false);
        setDisablePassword('');
        setDisableTotpCode('');
        await loadStatus();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to disable 2FA');
    } finally {
      setDisableLoading(false);
    }
  };

  // Regenerate backup codes
  const handleRegenerateBackupCodes = async () => {
    if (!regenerateCode.trim()) {
      message.error('Please enter your authenticator code');
      return;
    }

    setRegenerateLoading(true);
    try {
      const response = await securityAPI.regenerateBackupCodes(regenerateCode.trim());
      if (response.success && response.backup_codes) {
        setNewBackupCodes(response.backup_codes);
        message.success('Backup codes regenerated successfully');
        await loadStatus();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to regenerate backup codes');
    } finally {
      setRegenerateLoading(false);
    }
  };

  // Copy backup codes to clipboard
  const handleCopyBackupCodes = async (codes: string[]) => {
    const text = codes.join('\n');
    const success = await copyToClipboard(text);
    if (success) {
      message.success('Backup codes copied to clipboard');
    } else {
      message.error('Failed to copy to clipboard');
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
    message.success('Backup codes downloaded');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Security Settings</h1>
          <p className="text-gray-600 mt-2">Manage two-factor authentication and security</p>
        </div>

        <Card>
          <div className="space-y-6">
            {/* 2FA Status */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold flex items-center gap-2">
                    <SafetyOutlined className="text-blue-600" />
                    Two-Factor Authentication
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Add an extra layer of security to your account
                  </p>
                </div>
                <div>
                  {is2FAEnabled ? (
                    <Tag icon={<CheckCircleOutlined />} color="success" className="text-base px-4 py-1">
                      Enabled
                    </Tag>
                  ) : (
                    <Tag icon={<CloseCircleOutlined />} color="default" className="text-base px-4 py-1">
                      Disabled
                    </Tag>
                  )}
                </div>
              </div>

              <Alert
                message="What is Two-Factor Authentication?"
                description="2FA adds an extra layer of security by requiring a code from your authenticator app (like Google Authenticator or Authy) in addition to your password when logging in."
                type="info"
                showIcon
                className="mb-4"
              />
            </div>

            <Divider />

            {/* If 2FA is disabled - show enable option */}
            {!is2FAEnabled && (
              <div className="text-center py-8">
                <SafetyOutlined className="text-6xl text-blue-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">Enable Two-Factor Authentication</h3>
                <p className="text-gray-600 mb-6">
                  Protect your account with TOTP-based authentication
                </p>
                <Button
                  type="primary"
                  size="large"
                  icon={<SafetyOutlined />}
                  onClick={handleStartSetup}
                  loading={setupLoading}
                >
                  Enable 2FA
                </Button>
              </div>
            )}

            {/* If 2FA is enabled - show management options */}
            {is2FAEnabled && (
              <div className="space-y-4">
                <Card className="bg-green-50 border-green-200">
                  <div className="flex items-center gap-3">
                    <CheckCircleOutlined className="text-3xl text-green-600" />
                    <div>
                      <h3 className="text-lg font-semibold text-green-900">
                        Two-Factor Authentication is Active
                      </h3>
                      <p className="text-green-700">
                        Your account is protected with TOTP-based authentication
                      </p>
                    </div>
                  </div>
                </Card>

                <Card className="bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold mb-1 flex items-center gap-2">
                        <KeyOutlined />
                        Backup Codes
                      </h3>
                      <p className="text-gray-600">
                        {backupCodesRemaining} backup code{backupCodesRemaining !== 1 ? 's' : ''} remaining
                      </p>
                    </div>
                    <Button
                      icon={<KeyOutlined />}
                      onClick={() => {
                        setShowRegenerateModal(true);
                        setNewBackupCodes([]);
                        setRegenerateCode('');
                      }}
                    >
                      Regenerate Codes
                    </Button>
                  </div>
                  {backupCodesRemaining === 0 && (
                    <Alert
                      message="No backup codes remaining"
                      description="You should regenerate backup codes in case you lose access to your authenticator app."
                      type="warning"
                      showIcon
                      className="mt-4"
                    />
                  )}
                </Card>

                <Card className="bg-red-50 border-red-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-red-900 mb-1">Disable 2FA</h3>
                      <p className="text-red-700">
                        Remove two-factor authentication from your account
                      </p>
                    </div>
                    <Button
                      danger
                      icon={<CloseCircleOutlined />}
                      onClick={() => {
                        setShowDisableModal(true);
                        setDisablePassword('');
                        setDisableTotpCode('');
                      }}
                    >
                      Disable 2FA
                    </Button>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </Card>

        <div className="mt-6 text-center">
          <Link href="/settings" className="text-blue-600 hover:underline">
            ← Back to Settings
          </Link>
        </div>
      </div>

      {/* Setup 2FA Modal */}
      <Modal
        title="Enable Two-Factor Authentication"
        open={showSetupModal}
        onCancel={() => {
          setShowSetupModal(false);
          setSetupData(null);
          setVerificationCode('');
        }}
        footer={null}
        width={600}
      >
        {setupData && (
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-3">Step 1: Scan QR Code</h3>
              <p className="text-gray-600 mb-4">
                Open your authenticator app (Google Authenticator, Authy, etc.) and scan this QR code:
              </p>
              <div className="text-center bg-white p-4 rounded-lg">
                <img
                  src={setupData.qr_code}
                  alt="2FA QR Code"
                  className="mx-auto"
                  style={{ width: 256, height: 256 }}
                />
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3">Step 2: Verify Code</h3>
              <p className="text-gray-600 mb-3">
                Enter the 6-digit code from your authenticator app:
              </p>
              <Input
                size="large"
                prefix={<SafetyOutlined />}
                placeholder="000000"
                maxLength={6}
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                onPressEnter={handleEnable2FA}
              />
            </div>

            <div>
              <h3 className="font-semibold mb-3">Step 3: Save Backup Codes</h3>
              <Alert
                message="Important!"
                description="Save these backup codes in a safe place. You can use them to access your account if you lose your authenticator device."
                type="warning"
                showIcon
                className="mb-3"
              />
              <div className="grid grid-cols-2 gap-2 mb-4">
                {setupData.backup_codes.map((code, i) => (
                  <Tag key={i} className="font-mono text-base py-1 text-center">
                    {code}
                  </Tag>
                ))}
              </div>
              <Space>
                <Button
                  icon={<CopyOutlined />}
                  onClick={() => handleCopyBackupCodes(setupData.backup_codes)}
                >
                  Copy All Codes
                </Button>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownloadBackupCodes(setupData.backup_codes)}
                >
                  Download as File
                </Button>
              </Space>
            </div>

            <Divider />

            <div className="flex justify-end gap-2">
              <Button
                onClick={() => {
                  setShowSetupModal(false);
                  setSetupData(null);
                  setVerificationCode('');
                }}
              >
                Cancel
              </Button>
              <Button
                type="primary"
                onClick={handleEnable2FA}
                loading={setupLoading}
                disabled={verificationCode.length !== 6}
              >
                Enable 2FA
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Disable 2FA Modal */}
      <Modal
        title="Disable Two-Factor Authentication"
        open={showDisableModal}
        onCancel={() => {
          setShowDisableModal(false);
          setDisablePassword('');
          setDisableTotpCode('');
        }}
        footer={null}
      >
        <div className="space-y-4">
          <Alert
            message="Warning"
            description="Disabling 2FA will make your account less secure. You'll only need your password to log in."
            type="warning"
            showIcon
          />

          <div>
            <label className="block text-sm font-medium mb-2">Your Password</label>
            <Input.Password
              size="large"
              prefix={<LockOutlined />}
              placeholder="Enter your password"
              value={disablePassword}
              onChange={(e) => {
                setDisablePassword(e.target.value);
                setDisableTotpCode('');
              }}
            />
          </div>

          <div className="text-center text-gray-500">OR</div>

          <div>
            <label className="block text-sm font-medium mb-2">Authenticator Code</label>
            <Input
              size="large"
              prefix={<SafetyOutlined />}
              placeholder="000000"
              maxLength={6}
              value={disableTotpCode}
              onChange={(e) => {
                setDisableTotpCode(e.target.value);
                setDisablePassword('');
              }}
            />
          </div>

          <div className="flex justify-end gap-2 mt-6">
            <Button
              onClick={() => {
                setShowDisableModal(false);
                setDisablePassword('');
                setDisableTotpCode('');
              }}
            >
              Cancel
            </Button>
            <Button
              danger
              type="primary"
              onClick={handleDisable2FA}
              loading={disableLoading}
            >
              Disable 2FA
            </Button>
          </div>
        </div>
      </Modal>

      {/* Regenerate Backup Codes Modal */}
      <Modal
        title="Regenerate Backup Codes"
        open={showRegenerateModal}
        onCancel={() => {
          setShowRegenerateModal(false);
          setRegenerateCode('');
          setNewBackupCodes([]);
        }}
        footer={null}
      >
        <div className="space-y-4">
          {newBackupCodes.length === 0 ? (
            <>
              <Alert
                message="Warning"
                description="Regenerating backup codes will invalidate all existing codes. Make sure to save the new codes."
                type="warning"
                showIcon
              />

              <div>
                <label className="block text-sm font-medium mb-2">
                  Enter your authenticator code to continue
                </label>
                <Input
                  size="large"
                  prefix={<SafetyOutlined />}
                  placeholder="000000"
                  maxLength={6}
                  value={regenerateCode}
                  onChange={(e) => setRegenerateCode(e.target.value)}
                  onPressEnter={handleRegenerateBackupCodes}
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  onClick={() => {
                    setShowRegenerateModal(false);
                    setRegenerateCode('');
                  }}
                >
                  Cancel
                </Button>
                <Button
                  type="primary"
                  onClick={handleRegenerateBackupCodes}
                  loading={regenerateLoading}
                  disabled={regenerateCode.length !== 6}
                >
                  Regenerate Codes
                </Button>
              </div>
            </>
          ) : (
            <>
              <Alert
                message="New Backup Codes Generated"
                description="Save these codes in a safe place. The old codes are no longer valid."
                type="success"
                showIcon
              />

              <div className="grid grid-cols-2 gap-2">
                {newBackupCodes.map((code, i) => (
                  <Tag key={i} className="font-mono text-base py-1 text-center">
                    {code}
                  </Tag>
                ))}
              </div>

              <Space>
                <Button
                  icon={<CopyOutlined />}
                  onClick={() => handleCopyBackupCodes(newBackupCodes)}
                >
                  Copy All Codes
                </Button>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownloadBackupCodes(newBackupCodes)}
                >
                  Download as File
                </Button>
              </Space>

              <div className="flex justify-end">
                <Button
                  type="primary"
                  onClick={() => {
                    setShowRegenerateModal(false);
                    setRegenerateCode('');
                    setNewBackupCodes([]);
                  }}
                >
                  Done
                </Button>
              </div>
            </>
          )}
        </div>
      </Modal>
    </div>
  );
}
