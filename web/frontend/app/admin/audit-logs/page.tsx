/**
 * Admin Audit Logs - Security event history for all users
 */
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import {
  Activity,
  RefreshCw,
  Download,
  Filter,
  CheckCircle2,
  XCircle,
  Shield,
  LogIn,
  LogOut,
  Key,
  UserPlus,
  Settings,
  AlertCircle
} from 'lucide-react';
import { securityAPI, type AuditLog } from '@/lib/api';

export default function AdminAuditLogsPage() {
  const { toast } = useToast();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string>('all');
  const [days, setDays] = useState<number>(30);
  const [limit, setLimit] = useState<number>(50);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await securityAPI.getAuditLogs(
        limit,
        category === 'all' ? undefined : category,
        days
      );
      setLogs(data);
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load audit logs",
        variant: "destructive",
      });
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [category, days, limit]);

  const handleExportCSV = () => {
    if (logs.length === 0) {
      toast({
        title: "No data",
        description: "No logs to export",
        variant: "destructive",
      });
      return;
    }

    const headers = ['ID', 'Event Type', 'Category', 'User ID', 'Description', 'IP Address', 'Success', 'Timestamp'];
    const rows = logs.map(log => [
      log.id,
      log.event_type,
      log.category,
      log.user_id || 'N/A',
      log.description || '',
      log.ip_address || '',
      log.success ? 'Success' : 'Failed',
      log.timestamp,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: "Success",
      description: "Audit logs exported successfully",
    });
  };

  const getEventIcon = (eventType: string) => {
    if (eventType.includes('login')) return <LogIn className="h-4 w-4" />;
    if (eventType.includes('logout')) return <LogOut className="h-4 w-4" />;
    if (eventType.includes('2fa')) return <Shield className="h-4 w-4" />;
    if (eventType.includes('password')) return <Key className="h-4 w-4" />;
    if (eventType.includes('register')) return <UserPlus className="h-4 w-4" />;
    if (eventType.includes('settings')) return <Settings className="h-4 w-4" />;
    return <Activity className="h-4 w-4" />;
  };

  const getEventBadgeVariant = (eventType: string, success: boolean) => {
    if (!success) return "destructive";
    if (eventType.includes('enabled')) return "default";
    if (eventType.includes('disabled')) return "secondary";
    if (eventType.includes('success')) return "default";
    return "outline";
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString()
    };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Audit Logs</h1>
          <p className="text-muted-foreground mt-1">
            Security events and user activity across the entire system
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportCSV} disabled={loading || logs.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button onClick={loadLogs} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
          <CardDescription>
            Filter audit logs by category, time range, and limit
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger id="category">
                  <SelectValue placeholder="All categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="auth">Authentication</SelectItem>
                  <SelectItem value="2fa">Two-Factor Auth</SelectItem>
                  <SelectItem value="profile">Profile Changes</SelectItem>
                  <SelectItem value="security">Security Settings</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="days">Time Range</Label>
              <Select value={days.toString()} onValueChange={(v) => setDays(parseInt(v))}>
                <SelectTrigger id="days">
                  <SelectValue placeholder="Last 30 days" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">Last 7 days</SelectItem>
                  <SelectItem value="30">Last 30 days</SelectItem>
                  <SelectItem value="90">Last 90 days</SelectItem>
                  <SelectItem value="365">Last year</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="limit">Limit</Label>
              <Select value={limit.toString()} onValueChange={(v) => setLimit(parseInt(v))}>
                <SelectTrigger id="limit">
                  <SelectValue placeholder="50 logs" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="50">50 logs</SelectItem>
                  <SelectItem value="100">100 logs</SelectItem>
                  <SelectItem value="250">250 logs</SelectItem>
                  <SelectItem value="500">500 logs</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Events</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{logs.length}</div>
            <p className="text-xs text-muted-foreground">In selected period</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Successful</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {logs.filter(l => l.success).length}
            </div>
            <p className="text-xs text-muted-foreground">
              {logs.length > 0 ? Math.round((logs.filter(l => l.success).length / logs.length) * 100) : 0}% success rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {logs.filter(l => !l.success).length}
            </div>
            <p className="text-xs text-muted-foreground">
              {logs.length > 0 ? Math.round((logs.filter(l => !l.success).length / logs.length) * 100) : 0}% failure rate
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Events</CardTitle>
          <CardDescription>
            Complete security event log for all users
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Event</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>User ID</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Timestamp</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                      Loading audit logs...
                    </TableCell>
                  </TableRow>
                ) : logs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                      <AlertCircle className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No audit logs found</p>
                      <p className="text-sm mt-1">Try adjusting your filters</p>
                    </TableCell>
                  </TableRow>
                ) : (
                  logs.map((log) => {
                    const { date, time } = formatTimestamp(log.timestamp);
                    return (
                      <TableRow key={log.id}>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getEventIcon(log.event_type)}
                            <span className="font-medium">{log.event_type}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{log.category}</Badge>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {log.user_id || '-'}
                        </TableCell>
                        <TableCell className="max-w-xs truncate">
                          {log.description || '-'}
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {log.ip_address || '-'}
                        </TableCell>
                        <TableCell>
                          {log.success ? (
                            <Badge variant="default" className="bg-green-600 gap-1">
                              <CheckCircle2 className="h-3 w-3" />
                              Success
                            </Badge>
                          ) : (
                            <Badge variant="destructive" className="gap-1">
                              <XCircle className="h-3 w-3" />
                              Failed
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div>{date}</div>
                            <div className="text-muted-foreground">{time}</div>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
