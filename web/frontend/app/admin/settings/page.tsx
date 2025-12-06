/**
 * Admin Settings - Feature Toggles & System Configuration
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import {
  Settings,
  Sparkles,
  Link2,
  KeyRound,
  Users,
  Globe,
  Shield,
  Save,
  AlertCircle,
  Info,
  CheckCircle2
} from 'lucide-react';

interface FeatureSettings {
  ai_generation_enabled: boolean;
  pluralkit_sync_enabled: boolean;
  oauth_enabled: boolean;
  user_registration_enabled: boolean;
  google_oauth_enabled: boolean;
  github_oauth_enabled: boolean;
  discord_oauth_enabled: boolean;
}

export default function AdminSettingsPage() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const [settings, setSettings] = useState<FeatureSettings>({
    ai_generation_enabled: false,
    pluralkit_sync_enabled: true,
    oauth_enabled: false,
    user_registration_enabled: true,
    google_oauth_enabled: false,
    github_oauth_enabled: false,
    discord_oauth_enabled: false,
  });

  // Load settings from backend
  useEffect(() => {
    const loadSettings = async () => {
      setLoading(true);
      try {
        // TODO: Implement actual API endpoint
        // const response = await fetch('http://localhost:8000/api/admin/settings');
        // const data = await response.json();
        // setSettings(data);

        // Mock data for now
        await new Promise(resolve => setTimeout(resolve, 500));
        // Settings already initialized above
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load settings",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, []);

  const handleToggle = (key: keyof FeatureSettings) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // TODO: Implement actual API endpoint
      // await fetch('http://localhost:8000/api/admin/settings', {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(settings),
      // });

      // Mock save
      await new Promise(resolve => setTimeout(resolve, 1000));

      toast({
        title: "Success",
        description: "Settings saved successfully",
      });
      setHasChanges(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save settings",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">System Settings</h1>
          <p className="text-muted-foreground mt-1">
            Configure feature toggles and system behavior
          </p>
        </div>
        {hasChanges && (
          <Button onClick={handleSave} disabled={saving}>
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        )}
      </div>

      {/* Unsaved Changes Alert */}
      {hasChanges && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            You have unsaved changes. Click "Save Changes" to apply them.
          </AlertDescription>
        </Alert>
      )}

      {/* Core Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Core Features
          </CardTitle>
          <CardDescription>
            Enable or disable main system features
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* AI Generation */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="h-4 w-4 text-purple-600" />
                <Label htmlFor="ai-generation" className="font-semibold">
                  AI Generation
                </Label>
                <Badge variant="secondary" className="text-xs">
                  GPU Required
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Enable AI-powered message generation via offsite GPU. Users can use AI to generate responses in chat.
                Disable this if you don't have GPU access configured.
              </p>
            </div>
            <Switch
              id="ai-generation"
              checked={settings.ai_generation_enabled}
              onCheckedChange={() => handleToggle('ai_generation_enabled')}
              disabled={loading}
            />
          </div>

          <Separator />

          {/* PluralKit Sync */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Link2 className="h-4 w-4 text-blue-600" />
                <Label htmlFor="pluralkit-sync" className="font-semibold">
                  PluralKit Integration
                </Label>
                <Badge variant="outline" className="text-xs">
                  Recommended
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Allow users to sync their PluralKit system members. Disable this if you don't want PluralKit integration
                or if the API is experiencing issues.
              </p>
            </div>
            <Switch
              id="pluralkit-sync"
              checked={settings.pluralkit_sync_enabled}
              onCheckedChange={() => handleToggle('pluralkit_sync_enabled')}
              disabled={loading}
            />
          </div>

          <Separator />

          {/* User Registration */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Users className="h-4 w-4 text-green-600" />
                <Label htmlFor="user-registration" className="font-semibold">
                  User Registration
                </Label>
              </div>
              <p className="text-sm text-muted-foreground">
                Allow new users to create accounts. Disable this to make the system invite-only or during maintenance.
              </p>
            </div>
            <Switch
              id="user-registration"
              checked={settings.user_registration_enabled}
              onCheckedChange={() => handleToggle('user_registration_enabled')}
              disabled={loading}
            />
          </div>
        </CardContent>
      </Card>

      {/* OAuth Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <KeyRound className="h-5 w-5" />
            OAuth Authentication
          </CardTitle>
          <CardDescription>
            Configure third-party login providers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Master OAuth Toggle */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Globe className="h-4 w-4 text-primary" />
                <Label htmlFor="oauth-master" className="font-semibold">
                  OAuth Login
                </Label>
                <Badge variant="secondary" className="text-xs">
                  Master Toggle
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Enable third-party authentication providers. Individual providers can be configured below.
              </p>
            </div>
            <Switch
              id="oauth-master"
              checked={settings.oauth_enabled}
              onCheckedChange={() => handleToggle('oauth_enabled')}
              disabled={loading}
            />
          </div>

          {settings.oauth_enabled && (
            <>
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  OAuth providers require client IDs and secrets to be configured in the backend environment variables.
                </AlertDescription>
              </Alert>

              <Separator />

              {/* Google OAuth */}
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="h-4 w-4 rounded-full bg-red-500" />
                    <Label htmlFor="google-oauth" className="font-semibold">
                      Google OAuth
                    </Label>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Allow users to sign in with their Google account
                  </p>
                </div>
                <Switch
                  id="google-oauth"
                  checked={settings.google_oauth_enabled}
                  onCheckedChange={() => handleToggle('google_oauth_enabled')}
                  disabled={loading || !settings.oauth_enabled}
                />
              </div>

              <Separator />

              {/* GitHub OAuth */}
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="h-4 w-4 rounded-full bg-gray-800 dark:bg-gray-200" />
                    <Label htmlFor="github-oauth" className="font-semibold">
                      GitHub OAuth
                    </Label>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Allow users to sign in with their GitHub account
                  </p>
                </div>
                <Switch
                  id="github-oauth"
                  checked={settings.github_oauth_enabled}
                  onCheckedChange={() => handleToggle('github_oauth_enabled')}
                  disabled={loading || !settings.oauth_enabled}
                />
              </div>

              <Separator />

              {/* Discord OAuth */}
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="h-4 w-4 rounded-full bg-indigo-500" />
                    <Label htmlFor="discord-oauth" className="font-semibold">
                      Discord OAuth
                    </Label>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Allow users to sign in with their Discord account
                  </p>
                </div>
                <Switch
                  id="discord-oauth"
                  checked={settings.discord_oauth_enabled}
                  onCheckedChange={() => handleToggle('discord_oauth_enabled')}
                  disabled={loading || !settings.oauth_enabled}
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Security Notice */}
      <Card className="border-yellow-600/50 bg-yellow-50 dark:bg-yellow-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
            <Shield className="h-5 w-5" />
            Security Notice
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-yellow-800 dark:text-yellow-200">
          <div className="flex items-start gap-2">
            <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <p>Changes to these settings take effect immediately for all users.</p>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <p>Disabling features will not affect existing data, only prevent new usage.</p>
          </div>
          <div className="flex items-start gap-2">
            <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <p>OAuth configuration changes require backend environment variables to be set.</p>
          </div>
        </CardContent>
      </Card>

      {/* Save Button (Bottom) */}
      {hasChanges && (
        <div className="flex justify-end">
          <Button onClick={handleSave} disabled={saving} size="lg">
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save All Changes'}
          </Button>
        </div>
      )}
    </div>
  );
}
