/**
 * Audit Logs Page
 * Displays security event history with filtering options
 */
'use client';

import { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Select,
  Tag,
  Badge,
  Space,
  Button,
  Alert,
  Spin,
  message,
} from 'antd';
import {
  HistoryOutlined,
  FilterOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { securityAPI, type AuditLog } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import Link from 'next/link';

const { Option } = Select;

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [days, setDays] = useState<number>(30);
  const [limit, setLimit] = useState<number>(50);

  useEffect(() => {
    loadLogs();
  }, [category, days, limit]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await securityAPI.getAuditLogs(limit, category, days);
      setLogs(data);
    } catch (error: any) {
      message.error('Failed to load audit logs');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Export logs to CSV
  const handleExportCSV = () => {
    if (logs.length === 0) {
      message.warning('No logs to export');
      return;
    }

    const headers = ['ID', 'Event Type', 'Category', 'Description', 'IP Address', 'Success', 'Timestamp'];
    const rows = logs.map(log => [
      log.id,
      log.event_type,
      log.category,
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
    message.success('Audit logs exported successfully');
  };

  // Get event type badge color
  const getEventTypeColor = (eventType: string): string => {
    if (eventType.includes('success')) return 'success';
    if (eventType.includes('failed')) return 'error';
    if (eventType.includes('enabled')) return 'blue';
    if (eventType.includes('disabled')) return 'orange';
    if (eventType.includes('logout')) return 'default';
    return 'default';
  };

  // Get category badge color
  const getCategoryColor = (category: string): string => {
    switch (category) {
      case 'auth':
        return 'blue';
      case 'security':
        return 'green';
      case 'profile':
        return 'purple';
      case 'admin':
        return 'red';
      default:
        return 'default';
    }
  };

  // Table columns
  const columns: ColumnsType<AuditLog> = [
    {
      title: 'Event Type',
      dataIndex: 'event_type',
      key: 'event_type',
      width: 200,
      render: (eventType: string) => (
        <Tag color={getEventTypeColor(eventType)}>
          {eventType.replace(/_/g, ' ').toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category: string) => (
        <Tag color={getCategoryColor(category)}>
          {category.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (description: string | null) => (
        <span className="text-gray-700">{description || '—'}</span>
      ),
    },
    {
      title: 'IP Address',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
      render: (ip: string | null) => (
        <span className="font-mono text-sm text-gray-600">{ip || '—'}</span>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'success',
      key: 'success',
      width: 100,
      align: 'center',
      render: (success: boolean) => (
        <Badge
          status={success ? 'success' : 'error'}
          text={success ? 'Success' : 'Failed'}
        />
      ),
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string) => (
        <span className="text-sm text-gray-600">{formatDate(timestamp)}</span>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-3">
            <HistoryOutlined />
            Security Activity Log
          </h1>
          <p className="text-gray-600 mt-2">
            View detailed history of all security-related events on your account
          </p>
        </div>

        <Card>
          {/* Filters */}
          <div className="mb-6">
            <div className="flex items-center gap-4 mb-4">
              <FilterOutlined className="text-lg text-gray-500" />
              <span className="font-semibold">Filters:</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <Select
                  size="large"
                  style={{ width: '100%' }}
                  placeholder="All categories"
                  value={category}
                  onChange={setCategory}
                  allowClear
                >
                  <Option value="auth">Authentication</Option>
                  <Option value="security">Security</Option>
                  <Option value="profile">Profile</Option>
                  <Option value="admin">Admin</Option>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Time Period
                </label>
                <Select
                  size="large"
                  style={{ width: '100%' }}
                  value={days}
                  onChange={setDays}
                >
                  <Option value={7}>Last 7 days</Option>
                  <Option value={30}>Last 30 days</Option>
                  <Option value={90}>Last 90 days</Option>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Results Limit
                </label>
                <Select
                  size="large"
                  style={{ width: '100%' }}
                  value={limit}
                  onChange={setLimit}
                >
                  <Option value={25}>25 entries</Option>
                  <Option value={50}>50 entries</Option>
                  <Option value={100}>100 entries</Option>
                  <Option value={250}>250 entries</Option>
                </Select>
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <Button
                icon={<ReloadOutlined />}
                onClick={loadLogs}
                loading={loading}
              >
                Refresh
              </Button>
              <Button
                icon={<DownloadOutlined />}
                onClick={handleExportCSV}
                disabled={logs.length === 0}
              >
                Export CSV
              </Button>
            </div>
          </div>

          <Alert
            message="Security Activity Monitoring"
            description="All login attempts, 2FA events, profile changes, and security modifications are logged here for your review."
            type="info"
            showIcon
            className="mb-4"
          />

          {/* Table */}
          {loading ? (
            <div className="text-center py-12">
              <Spin size="large" />
              <p className="text-gray-500 mt-4">Loading audit logs...</p>
            </div>
          ) : (
            <>
              <Table
                columns={columns}
                dataSource={logs}
                rowKey="id"
                pagination={{
                  pageSize: 20,
                  showTotal: (total) => `Total ${total} events`,
                  showSizeChanger: false,
                }}
                locale={{
                  emptyText: (
                    <div className="py-12">
                      <HistoryOutlined className="text-6xl text-gray-300 mb-4" />
                      <p className="text-gray-500">No audit logs found</p>
                      <p className="text-sm text-gray-400 mt-2">
                        Try adjusting your filters or time period
                      </p>
                    </div>
                  ),
                }}
                scroll={{ x: 'max-content' }}
              />

              {logs.length > 0 && (
                <div className="mt-4 text-center text-sm text-gray-500">
                  Showing {logs.length} of {logs.length} events
                  {category && ` in category: ${category}`}
                  {` from the last ${days} days`}
                </div>
              )}
            </>
          )}
        </Card>

        {/* Legend */}
        <Card className="mt-6">
          <h3 className="font-semibold mb-3">Event Categories</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <Tag color="blue" className="mb-2">AUTH</Tag>
              <p className="text-sm text-gray-600">
                Login, logout, and authentication events
              </p>
            </div>
            <div>
              <Tag color="green" className="mb-2">SECURITY</Tag>
              <p className="text-sm text-gray-600">
                2FA changes, password updates, and security modifications
              </p>
            </div>
            <div>
              <Tag color="purple" className="mb-2">PROFILE</Tag>
              <p className="text-sm text-gray-600">
                Profile changes, settings updates
              </p>
            </div>
            <div>
              <Tag color="red" className="mb-2">ADMIN</Tag>
              <p className="text-sm text-gray-600">
                Administrative actions and system changes
              </p>
            </div>
          </div>
        </Card>

        <div className="mt-6 text-center">
          <Link href="/settings" className="text-blue-600 hover:underline">
            ← Back to Settings
          </Link>
        </div>
      </div>
    </div>
  );
}
