/**
 * Admin Dashboard - System Overview & Health Checks
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Activity,
  Users,
  MessageSquare,
  Server,
  Database,
  Wifi,
  WifiOff,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  Settings,
  Shield,
  RefreshCw
} from 'lucide-react';
import Link from 'next/link';

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  server: boolean;
  database: boolean;
  websocket: boolean;
  apiResponseTime: number;
}

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalChannels: number;
  messagesToday: number;
  totalMembers: number;
}

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState<SystemHealth>({
    status: 'healthy',
    server: true,
    database: true,
    websocket: true,
    apiResponseTime: 0,
  });
  const [stats, setStats] = useState<SystemStats>({
    totalUsers: 0,
    activeUsers: 0,
    totalChannels: 0,
    messagesToday: 0,
    totalMembers: 0,
  });

  const fetchSystemHealth = async () => {
    const startTime = Date.now();
    try {
      // TODO: Implement actual health check API endpoint
      // const response = await fetch('http://localhost:8000/api/admin/health');
      // const data = await response.json();

      // Mock data for now
      await new Promise(resolve => setTimeout(resolve, 500));
      const responseTime = Date.now() - startTime;

      setHealth({
        status: 'healthy',
        server: true,
        database: true,
        websocket: true,
        apiResponseTime: responseTime,
      });
    } catch (error) {
      setHealth({
        status: 'down',
        server: false,
        database: false,
        websocket: false,
        apiResponseTime: 0,
      });
    }
  };

  const fetchSystemStats = async () => {
    try {
      // TODO: Implement actual stats API endpoint
      // const response = await fetch('http://localhost:8000/api/admin/stats');
      // const data = await response.json();

      // Mock data for now
      setStats({
        totalUsers: 42,
        activeUsers: 12,
        totalChannels: 8,
        messagesToday: 156,
        totalMembers: 87,
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchSystemHealth(), fetchSystemStats()]);
      setLoading(false);
    };

    loadData();

    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    await Promise.all([fetchSystemHealth(), fetchSystemStats()]);
    setLoading(false);
  };

  const getStatusColor = () => {
    switch (health.status) {
      case 'healthy':
        return 'text-green-600 dark:text-green-400';
      case 'degraded':
        return 'text-yellow-600 dark:text-yellow-400';
      case 'down':
        return 'text-red-600 dark:text-red-400';
    }
  };

  const getStatusIcon = () => {
    switch (health.status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5" />;
      case 'degraded':
        return <AlertCircle className="h-5 w-5" />;
      case 'down':
        return <XCircle className="h-5 w-5" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            System overview and health monitoring
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* System Status Alert */}
      {health.status !== 'healthy' && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {health.status === 'down'
              ? 'System is experiencing critical issues. Some services may be unavailable.'
              : 'System is degraded. Some features may not work as expected.'}
          </AlertDescription>
        </Alert>
      )}

      {/* System Health Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Server Status</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {health.server ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-xl font-bold">Online</span>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-red-600" />
                  <span className="text-xl font-bold">Offline</span>
                </>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              API Response: {health.apiResponseTime}ms
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {health.database ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-xl font-bold">Connected</span>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-red-600" />
                  <span className="text-xl font-bold">Disconnected</span>
                </>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              PostgreSQL
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">WebSocket</CardTitle>
            {health.websocket ? (
              <Wifi className="h-4 w-4 text-muted-foreground" />
            ) : (
              <WifiOff className="h-4 w-4 text-muted-foreground" />
            )}
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {health.websocket ? (
                <>
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-xl font-bold">Active</span>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-red-600" />
                  <span className="text-xl font-bold">Inactive</span>
                </>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Real-time messaging
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Status</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`flex items-center gap-2 ${getStatusColor()}`}>
              {getStatusIcon()}
              <span className="text-xl font-bold capitalize">{health.status}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Last checked: {new Date().toLocaleTimeString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div>
        <h2 className="text-xl font-semibold mb-4">System Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalUsers}</div>
              <p className="text-xs text-muted-foreground">
                {stats.activeUsers} active now
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Users</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeUsers}</div>
              <p className="text-xs text-muted-foreground">
                Currently online
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Channels</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalChannels}</div>
              <p className="text-xs text-muted-foreground">
                Active channels
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Messages Today</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.messagesToday}</div>
              <p className="text-xs text-muted-foreground">
                Last 24 hours
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Members</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalMembers}</div>
              <p className="text-xs text-muted-foreground">
                Across all users
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/admin/users">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Manage Users
                </CardTitle>
                <CardDescription>
                  View and manage user accounts
                </CardDescription>
              </CardHeader>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/admin/settings">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Feature Toggles
                </CardTitle>
                <CardDescription>
                  Configure system features and settings
                </CardDescription>
              </CardHeader>
            </Link>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/admin/audit-logs">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Audit Logs
                </CardTitle>
                <CardDescription>
                  View security events and user activity
                </CardDescription>
              </CardHeader>
            </Link>
          </Card>
        </div>
      </div>

      {/* Recent Activity (Placeholder) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Recent Admin Actions
          </CardTitle>
          <CardDescription>
            Last 10 administrative actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Activity className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>No recent actions</p>
            <p className="text-sm mt-1">Admin activity will appear here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
