/**
 * Main settings page with tabs for Profile, Security, and Audit Logs
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { authAPI, securityAPI, membersAPI, type Member } from '@/lib/api';
import { useStore } from '@/lib/store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { User, Lock, Shield, History, Link2, RefreshCw, Palette, Camera, Users, Plus, Edit, Trash2, AlertCircle, Info, CheckCircle2 } from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';

export default function SettingsPage() {
  const router = useRouter();
  const { user, setUser } = useStore();
  const [activeTab, setActiveTab] = useState<string>('profile');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Members state
  const [members, setMembers] = useState<Member[]>([]);
  const [membersLoading, setMembersLoading] = useState(false);
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [memberModalOpen, setMemberModalOpen] = useState(false);
  const [memberName, setMemberName] = useState('');
  const [memberPronouns, setMemberPronouns] = useState('');
  const [memberColor, setMemberColor] = useState('#6c757d');
  const [memberDescription, setMemberDescription] = useState('');
  const [proxyTags, setProxyTags] = useState<Array<{prefix: string, suffix: string}>>([{ prefix: '', suffix: '' }]);
  const [memberAvatarFile, setMemberAvatarFile] = useState<File | null>(null);
  const [memberAvatarPreview, setMemberAvatarPreview] = useState<string | null>(null);

  // PluralKit sync state
  const [pkToken, setPkToken] = useState('');
  const [pkLoading, setPkLoading] = useState(false);
  const [pkSynced, setPkSynced] = useState(false);

  // Avatar upload state
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  // Profile state
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [themeColor, setThemeColor] = useState('#6c757d');

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Load user data on mount
  useEffect(() => {
    if (!user) {
      router.push('/login');
    } else {
      setUsername(user.username || '');
      setEmail(user.email || '');
      setThemeColor(user.theme_color || '#6c757d');
      if (user.avatar_path) {
        setAvatarPreview(`http://localhost:8000${user.avatar_path}`);
      }
      loadMembers();
    }
  }, [user, router]);

  const loadMembers = async () => {
    setMembersLoading(true);
    try {
      const data = await membersAPI.getAll();
      setMembers(data);
    } catch (error) {
      console.error('Failed to load members:', error);
    } finally {
      setMembersLoading(false);
    }
  };

  const handleAddMember = () => {
    setEditingMember(null);
    setMemberName('');
    setMemberPronouns('');
    setMemberColor('#6c757d');
    setMemberDescription('');
    setProxyTags([{ prefix: '', suffix: '' }]);
    setMemberAvatarFile(null);
    setMemberAvatarPreview(null);
    setMemberModalOpen(true);
  };

  const handleEditMember = (member: Member) => {
    setEditingMember(member);
    setMemberName(member.name);
    setMemberPronouns(member.pronouns || '');
    setMemberColor(member.color || '#6c757d');
    setMemberDescription(member.description || '');

    // Set avatar preview if exists
    if (member.avatar_path) {
      setMemberAvatarPreview(`http://localhost:8000${member.avatar_path}`);
    } else {
      setMemberAvatarPreview(null);
    }
    setMemberAvatarFile(null);

    // Parse existing proxy tags
    if (member.proxy_tags) {
      try {
        const parsed = JSON.parse(member.proxy_tags);
        setProxyTags(parsed.length > 0 ? parsed : [{ prefix: '', suffix: '' }]);
      } catch {
        setProxyTags([{ prefix: '', suffix: '' }]);
      }
    } else {
      setProxyTags([{ prefix: '', suffix: '' }]);
    }

    setMemberModalOpen(true);
  };

  const handleMemberAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast({
        title: "Invalid file type",
        description: "Only JPEG, PNG, GIF, and WebP images are allowed",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "File size must be less than 5MB",
        variant: "destructive",
      });
      return;
    }

    setMemberAvatarFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setMemberAvatarPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleDeleteMember = async (memberId: number, memberName: string) => {
    if (!confirm(`Delete member "${memberName}"? This cannot be undone.`)) {
      return;
    }

    setMembersLoading(true);
    try {
      await membersAPI.delete(memberId);
      toast({
        title: "Member deleted",
        description: "Member deleted successfully",
      });
      await loadMembers();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to delete member',
        variant: "destructive",
      });
    } finally {
      setMembersLoading(false);
    }
  };

  const handleMemberSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!memberName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a member name",
        variant: "destructive",
      });
      return;
    }

    setMembersLoading(true);
    try {
      // Filter out empty proxy tags
      const validProxyTags = proxyTags.filter(
        tag => tag.prefix.trim() !== '' || tag.suffix.trim() !== ''
      );

      const memberData = {
        name: memberName,
        pronouns: memberPronouns || undefined,
        color: memberColor || '#6c757d',
        description: memberDescription || undefined,
        proxy_tags: validProxyTags.length > 0 ? JSON.stringify(validProxyTags) : undefined,
      };

      let memberId: number;
      if (editingMember) {
        await membersAPI.update(editingMember.id, memberData);
        memberId = editingMember.id;
        toast({
          title: "Success",
          description: "Member updated successfully",
        });
      } else {
        const newMember = await membersAPI.create(memberData);
        memberId = newMember.id;
        toast({
          title: "Success",
          description: "Member created successfully",
        });
      }

      // Upload avatar if selected
      if (memberAvatarFile) {
        await membersAPI.uploadAvatar(memberId, memberAvatarFile);
        setMemberAvatarFile(null);
      }

      setMemberModalOpen(false);
      await loadMembers();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to save member',
        variant: "destructive",
      });
    } finally {
      setMembersLoading(false);
    }
  };

  const addProxyTag = () => {
    setProxyTags([...proxyTags, { prefix: '', suffix: '' }]);
  };

  const removeProxyTag = (index: number) => {
    if (proxyTags.length > 1) {
      setProxyTags(proxyTags.filter((_, i) => i !== index));
    }
  };

  const updateProxyTag = (index: number, field: 'prefix' | 'suffix', value: string) => {
    const newTags = [...proxyTags];
    newTags[index][field] = value;
    setProxyTags(newTags);
  };

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Update profile data
      await securityAPI.updateProfile({
        username,
        email: email || undefined,
        theme_color: themeColor,
      });

      // Upload avatar if selected
      if (avatarFile) {
        await securityAPI.uploadAvatar(avatarFile);
        setAvatarFile(null); // Clear after upload
      }

      // Refresh user data
      const userData = await authAPI.verifyToken();
      setUser(userData);

      toast({
        title: "Success",
        description: "Profile updated successfully",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.userMessage || error.response?.data?.detail || 'Failed to update profile',
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast({
        title: "Invalid file type",
        description: "Only JPEG, PNG, GIF, and WebP images are allowed",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "File size must be less than 5MB",
        variant: "destructive",
      });
      return;
    }

    setAvatarFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setAvatarPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }

    if (newPassword.length < 8) {
      toast({
        title: "Error",
        description: "Password must be at least 8 characters",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await securityAPI.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      toast({
        title: "Success",
        description: "Password changed successfully",
      });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to change password',
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePluralKitSync = async () => {
    if (!pkToken.trim()) {
      toast({
        title: "Error",
        description: "Please enter your PluralKit API token",
        variant: "destructive",
      });
      return;
    }

    setPkLoading(true);
    try {
      await authAPI.setPKToken(pkToken);
      toast({
        title: "Success",
        description: "PluralKit members synced successfully!",
      });
      setPkSynced(true);
      setPkToken(''); // Clear token after successful sync
      await loadMembers();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || 'Failed to sync PluralKit members. Please check your token.',
        variant: "destructive",
      });
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
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="profile">
                <User className="h-4 w-4 mr-2" />
                Profile
              </TabsTrigger>
              <TabsTrigger value="members">
                <Users className="h-4 w-4 mr-2" />
                Members
              </TabsTrigger>
              <TabsTrigger value="security">
                <Shield className="h-4 w-4 mr-2" />
                Security
              </TabsTrigger>
              <TabsTrigger value="audit">
                <History className="h-4 w-4 mr-2" />
                Activity
              </TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="space-y-6 p-6">
              <div>
                <h2 className="text-xl font-semibold mb-4">Profile Information</h2>

                {/* Avatar Upload */}
                <div className="mb-6">
                  <Label className="mb-3">Profile Picture</Label>
                  <div className="flex items-center gap-4 mt-3">
                    <div className="w-24 h-24 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                      {avatarPreview ? (
                        <img src={avatarPreview} alt="Avatar" className="w-full h-full object-cover" />
                      ) : (
                        <User className="h-12 w-12 text-gray-400" />
                      )}
                    </div>
                    <div>
                      <input
                        type="file"
                        id="avatar-upload"
                        accept="image/jpeg,image/png,image/gif,image/webp"
                        onChange={handleAvatarChange}
                        className="hidden"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => document.getElementById('avatar-upload')?.click()}
                      >
                        <Camera className="h-4 w-4 mr-2" />
                        Choose Avatar
                      </Button>
                      <div className="text-xs text-muted-foreground mt-1">
                        JPEG, PNG, GIF, WebP (Max 5MB)
                      </div>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleProfileUpdate} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email (Optional)</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="theme-color">Theme Color</Label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Palette className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="theme-color"
                          type="text"
                          value={themeColor}
                          onChange={(e) => setThemeColor(e.target.value)}
                          className="pl-10"
                        />
                      </div>
                      <input
                        type="color"
                        value={themeColor}
                        onChange={(e) => setThemeColor(e.target.value)}
                        className="w-12 h-10 rounded border cursor-pointer"
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Choose a color for your profile theme
                    </p>
                  </div>

                  <Button type="submit" disabled={loading}>
                    {loading ? 'Updating...' : 'Update Profile'}
                  </Button>
                </form>
              </div>

              <Separator />

              <div>
                <h2 className="text-xl font-semibold mb-4">Change Password</h2>
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password">Current Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="current-password"
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        required
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="new-password">New Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="new-password"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                        minLength={8}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm New Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="confirm-password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <Button type="submit" disabled={loading}>
                    {loading ? 'Changing...' : 'Change Password'}
                  </Button>
                </form>
              </div>
            </TabsContent>

            <TabsContent value="members" className="space-y-6 p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Your Members</h2>
                <Button onClick={handleAddMember}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Member
                </Button>
              </div>

              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Members allow you to chat as different personas, characters, or system members. You can use proxy tags (like 'text: message') to automatically send messages as a specific member. This is optional - you can always chat as yourself!
                </AlertDescription>
              </Alert>

              {/* Members List */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {membersLoading && members.length === 0 && (
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-muted-foreground">Loading members...</p>
                    </CardContent>
                  </Card>
                )}

                {!membersLoading && members.length === 0 && (
                  <Card className="col-span-full">
                    <CardContent className="text-center py-12">
                      <User className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-xl font-semibold mb-2">No members yet</h3>
                      <p className="text-muted-foreground mb-4">
                        Create your first member to get started!
                      </p>
                      <Button onClick={handleAddMember}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Your First Member
                      </Button>
                    </CardContent>
                  </Card>
                )}

                {members.map((member) => {
                  let proxyTagsList: Array<{prefix: string, suffix: string}> = [];
                  if (member.proxy_tags) {
                    try {
                      proxyTagsList = JSON.parse(member.proxy_tags);
                    } catch {}
                  }

                  return (
                    <Card key={member.id} className="hover:shadow-lg transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start gap-3 mb-3">
                          {member.avatar_path ? (
                            <div className="w-12 h-12 rounded-full overflow-hidden flex-shrink-0">
                              <img
                                src={`http://localhost:8000${member.avatar_path}`}
                                alt={member.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          ) : (
                            <div
                              className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                              style={{ backgroundColor: member.color || '#6c757d' }}
                            >
                              {member.name.charAt(0).toUpperCase()}
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <h3 className="font-bold text-base truncate">{member.name}</h3>
                            {member.pronouns && (
                              <p className="text-sm text-muted-foreground">{member.pronouns}</p>
                            )}
                          </div>
                        </div>

                        {member.description && (
                          <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                            {member.description}
                          </p>
                        )}

                        {proxyTagsList.length > 0 && (
                          <div className="mb-3 pb-3 border-t pt-3">
                            <p className="text-xs font-semibold text-muted-foreground mb-2">
                              Proxy Tags:
                            </p>
                            <div className="flex flex-wrap gap-1">
                              {proxyTagsList.map((tag, idx) => (
                                <Badge key={idx} variant="secondary">
                                  {tag.prefix || ''}text{tag.suffix || ''}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditMember(member)}
                            className="flex-1"
                          >
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeleteMember(member.id, member.name)}
                            className="flex-1"
                          >
                            <Trash2 className="h-4 w-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* PluralKit Integration Section */}
              <Separator />

              <div>
                <h2 className="text-xl font-semibold mb-4">PluralKit Integration</h2>
                <Alert className="mb-4">
                  <Link2 className="h-4 w-4" />
                  <AlertDescription>
                    Connect your PluralKit account to automatically import your system members into Plural Chat. This allows you to chat as any of your members.
                  </AlertDescription>
                </Alert>

                {pkSynced && (
                  <Alert className="mb-4">
                    <CheckCircle2 className="h-4 w-4" />
                    <AlertDescription>
                      Your PluralKit members have been imported. You can now select them when sending messages.
                    </AlertDescription>
                  </Alert>
                )}

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="pk-token">PluralKit API Token</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="pk-token"
                        type="password"
                        placeholder="Enter your PluralKit API token"
                        value={pkToken}
                        onChange={(e) => setPkToken(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  <Button onClick={handlePluralKitSync} disabled={pkLoading}>
                    <RefreshCw className={`h-4 w-4 mr-2 ${pkLoading ? 'animate-spin' : ''}`} />
                    {pkLoading ? 'Syncing...' : 'Sync Members'}
                  </Button>

                  <Card className="bg-muted/50">
                    <CardContent className="pt-6">
                      <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                        <Link2 className="h-4 w-4" /> How to get your PluralKit token:
                      </h3>
                      <ol className="text-sm space-y-1 list-decimal list-inside text-muted-foreground">
                        <li>
                          Visit{' '}
                          <a
                            href="https://pluralkit.me/dash"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline font-medium text-primary hover:text-primary/80"
                          >
                            pluralkit.me/dash
                          </a>
                        </li>
                        <li>Click "Get API Token"</li>
                        <li>Copy the token and paste it above</li>
                        <li>Click "Sync Members" to import your system</li>
                      </ol>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="security" className="space-y-4 p-6">
              <h2 className="text-xl font-semibold mb-4">Security Settings</h2>

              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription>
                  Add an extra layer of security to your account by enabling two-factor authentication (2FA).
                </AlertDescription>
              </Alert>

              <Card className="bg-muted/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-blue-600" />
                    Two-Factor Authentication (2FA)
                  </CardTitle>
                  <CardDescription>
                    Secure your account with TOTP-based authentication using apps like Google Authenticator or Authy.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/settings/security">
                    <Button>
                      Manage 2FA Settings →
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card className="bg-muted/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <History className="h-5 w-5 text-green-600" />
                    Security Activity
                  </CardTitle>
                  <CardDescription>
                    View your recent security activity and login history.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href="/settings/audit-logs">
                    <Button variant="outline">
                      View Activity Log →
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="audit" className="space-y-4 p-6">
              <h2 className="text-xl font-semibold mb-4">Security Activity</h2>

              <Alert>
                <History className="h-4 w-4" />
                <AlertDescription>
                  View detailed logs of all security-related events on your account.
                </AlertDescription>
              </Alert>

              <Card className="bg-muted/50">
                <CardContent className="text-center py-8">
                  <History className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">View Full Activity Log</h3>
                  <p className="text-muted-foreground mb-4">
                    See all login attempts, 2FA events, and security changes
                  </p>
                  <Link href="/settings/audit-logs">
                    <Button>
                      Open Activity Log →
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </Card>

        <div className="mt-6 text-center">
          <Link href="/" className="text-primary hover:underline">
            ← Back to Chat
          </Link>
        </div>
      </div>

      {/* Member Add/Edit Dialog */}
      <Dialog open={memberModalOpen} onOpenChange={setMemberModalOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingMember ? 'Edit Member' : 'Add New Member'}</DialogTitle>
            <DialogDescription>
              {editingMember ? 'Update member information' : 'Create a new member for your system'}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleMemberSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="member-name">Name *</Label>
              <div className="relative">
                <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="member-name"
                  type="text"
                  placeholder="Member name"
                  value={memberName}
                  onChange={(e) => setMemberName(e.target.value)}
                  required
                  className="pl-10"
                />
              </div>
            </div>

            {/* Avatar Upload */}
            <div>
              <Label className="mb-3">Avatar (Optional)</Label>
              <div className="flex items-center gap-4 mt-3">
                <div className="w-20 h-20 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                  {memberAvatarPreview ? (
                    <img src={memberAvatarPreview} alt="Avatar" className="w-full h-full object-cover" />
                  ) : (
                    <User className="h-10 w-10 text-gray-400" />
                  )}
                </div>
                <div>
                  <input
                    type="file"
                    id="member-avatar-upload"
                    accept="image/jpeg,image/png,image/gif,image/webp"
                    onChange={handleMemberAvatarChange}
                    className="hidden"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => document.getElementById('member-avatar-upload')?.click()}
                  >
                    <Camera className="h-4 w-4 mr-2" />
                    Choose Avatar
                  </Button>
                  <div className="text-xs text-muted-foreground mt-1">
                    JPEG, PNG, GIF, WebP (Max 5MB)
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="member-pronouns">Pronouns (Optional)</Label>
              <Input
                id="member-pronouns"
                type="text"
                placeholder="e.g., they/them, he/him, she/her"
                value={memberPronouns}
                onChange={(e) => setMemberPronouns(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="member-description">Description (Optional)</Label>
              <Textarea
                id="member-description"
                placeholder="Brief description of this member..."
                rows={3}
                value={memberDescription}
                onChange={(e) => setMemberDescription(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="member-color">Color</Label>
              <div className="flex gap-2">
                <Input
                  id="member-color"
                  type="text"
                  value={memberColor}
                  onChange={(e) => setMemberColor(e.target.value)}
                  className="flex-1"
                />
                <input
                  type="color"
                  value={memberColor}
                  onChange={(e) => setMemberColor(e.target.value)}
                  className="w-12 h-10 rounded border cursor-pointer"
                />
              </div>
            </div>

            <Separator />

            <div>
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-base">Proxy Tags (Optional)</h3>
                  <p className="text-sm text-muted-foreground">
                    Automatically send messages as this member using proxy tags
                  </p>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addProxyTag}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add Tag
                </Button>
              </div>

              <Alert className="mb-3">
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <div className="text-sm">
                    <p className="mb-2">
                      Proxy tags let you send messages as this member automatically. For example:
                    </p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>
                        <code>text:</code> hello → sends "hello" as this member
                      </li>
                      <li>
                        <code>:text</code> hello → sends "hello" as this member
                      </li>
                      <li>
                        <code>{'{{'}}</code> hello <code>{'}}'}</code> → sends "hello" as this member
                      </li>
                    </ul>
                  </div>
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                {proxyTags.map((tag, index) => (
                  <div key={index} className="flex gap-2 items-center">
                    <Input
                      placeholder="Prefix (e.g., 'text:')"
                      value={tag.prefix}
                      onChange={(e) => updateProxyTag(index, 'prefix', e.target.value)}
                      className="flex-1"
                    />
                    <span className="text-muted-foreground">message</span>
                    <Input
                      placeholder="Suffix (e.g., ':text')"
                      value={tag.suffix}
                      onChange={(e) => updateProxyTag(index, 'suffix', e.target.value)}
                      className="flex-1"
                    />
                    {proxyTags.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeProxyTag(index)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setMemberModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={membersLoading}>
                {membersLoading ? 'Saving...' : editingMember ? 'Update Member' : 'Create Member'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
