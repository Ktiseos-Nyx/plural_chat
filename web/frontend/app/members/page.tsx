/**
 * Dedicated Members Management Page
 * Full-featured member creation and editing with proxy tags support
 */
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, Form, Input, Button, message, Alert, Upload, Modal, Tag, Space, Divider } from 'antd';
import { UserOutlined, PlusOutlined, DeleteOutlined, EditOutlined, CameraOutlined, LinkOutlined } from '@ant-design/icons';
import Link from 'next/link';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { membersAPI, type Member } from '@/lib/api';
import { useStore } from '@/lib/store';

interface ProxyTag {
  prefix: string;
  suffix: string;
}

export default function MembersPage() {
  const router = useRouter();
  const { user } = useStore();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingMember, setEditingMember] = useState<Member | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  // Proxy tags state for the form
  const [proxyTags, setProxyTags] = useState<ProxyTag[]>([{ prefix: '', suffix: '' }]);

  useEffect(() => {
    if (!user) {
      router.push('/login');
    } else {
      loadMembers();
    }
  }, [user, router]);

  const loadMembers = async () => {
    setLoading(true);
    try {
      const data = await membersAPI.getAll();
      setMembers(data);
    } catch (error) {
      console.error('Failed to load members:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMember = () => {
    setEditingMember(null);
    setProxyTags([{ prefix: '', suffix: '' }]);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEditMember = (member: Member) => {
    setEditingMember(member);
    form.setFieldsValue({
      name: member.name,
      pronouns: member.pronouns || '',
      color: member.color || '#6c757d',
      description: member.description || '',
    });

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

    setIsModalOpen(true);
  };

  const handleDeleteMember = async (memberId: number, memberName: string) => {
    if (!confirm(`Delete member "${memberName}"? This cannot be undone.`)) {
      return;
    }

    setLoading(true);
    try {
      await membersAPI.delete(memberId);
      message.success('Member deleted successfully');
      await loadMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to delete member');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // Filter out empty proxy tags
      const validProxyTags = proxyTags.filter(
        tag => tag.prefix.trim() !== '' || tag.suffix.trim() !== ''
      );

      const memberData = {
        name: values.name,
        pronouns: values.pronouns || undefined,
        color: values.color || '#6c757d',
        description: values.description || undefined,
        proxy_tags: validProxyTags.length > 0 ? JSON.stringify(validProxyTags) : undefined,
      };

      if (editingMember) {
        await membersAPI.update(editingMember.id, memberData);
        message.success('Member updated successfully');
      } else {
        await membersAPI.create(memberData);
        message.success('Member created successfully');
      }

      setIsModalOpen(false);
      form.resetFields();
      setProxyTags([{ prefix: '', suffix: '' }]);
      await loadMembers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to save member');
    } finally {
      setLoading(false);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Members</h1>
            <p className="text-muted-foreground mt-2">
              Manage your system members and proxy tags
            </p>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Button
              type="primary"
              size="large"
              icon={<PlusOutlined />}
              onClick={handleAddMember}
            >
              Add Member
            </Button>
          </div>
        </div>

        <Alert
          message="What are members?"
          description="Members allow you to chat as different personas, characters, or system members. You can use proxy tags (like 'text: message') to automatically send messages as a specific member. This is optional - you can always chat as yourself!"
          type="info"
          showIcon
          className="mb-6"
        />

        {/* Members Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading && members.length === 0 && (
            <Card>
              <p className="text-gray-500">Loading members...</p>
            </Card>
          )}

          {!loading && members.length === 0 && (
            <Card className="col-span-full">
              <div className="text-center py-12">
                <UserOutlined className="text-6xl text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">No members yet</h3>
                <p className="text-gray-600 mb-4">
                  Create your first member to get started!
                </p>
                <Button
                  type="primary"
                  size="large"
                  icon={<PlusOutlined />}
                  onClick={handleAddMember}
                >
                  Add Your First Member
                </Button>
              </div>
            </Card>
          )}

          {members.map((member) => {
            let proxyTagsList: ProxyTag[] = [];
            if (member.proxy_tags) {
              try {
                proxyTagsList = JSON.parse(member.proxy_tags);
              } catch {}
            }

            return (
              <Card
                key={member.id}
                className="hover:shadow-lg transition-shadow"
                actions={[
                  <Button
                    key="edit"
                    type="text"
                    icon={<EditOutlined />}
                    onClick={() => handleEditMember(member)}
                  >
                    Edit
                  </Button>,
                  <Button
                    key="delete"
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDeleteMember(member.id, member.name)}
                  >
                    Delete
                  </Button>,
                ]}
              >
                <div className="flex items-start gap-3 mb-3">
                  <div
                    className="w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-2xl flex-shrink-0"
                    style={{ backgroundColor: member.color || '#6c757d' }}
                  >
                    {member.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-lg truncate">{member.name}</h3>
                    {member.pronouns && (
                      <p className="text-sm text-gray-600">{member.pronouns}</p>
                    )}
                  </div>
                </div>

                {member.description && (
                  <p className="text-sm text-gray-700 mb-3 line-clamp-2">
                    {member.description}
                  </p>
                )}

                {proxyTagsList.length > 0 && (
                  <div className="mt-3 pt-3 border-t">
                    <p className="text-xs font-semibold text-gray-600 mb-2">
                      Proxy Tags:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {proxyTagsList.map((tag, idx) => (
                        <Tag key={idx} color="blue" className="text-xs">
                          {tag.prefix || ''}text{tag.suffix || ''}
                        </Tag>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        {/* Add/Edit Member Modal */}
        <Modal
          title={editingMember ? 'Edit Member' : 'Add New Member'}
          open={isModalOpen}
          onCancel={() => setIsModalOpen(false)}
          footer={null}
          width={700}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            className="mt-4"
            initialValues={{
              color: '#6c757d'
            }}
          >
            <Form.Item
              label="Name"
              name="name"
              rules={[{ required: true, message: 'Please enter a name' }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Member name"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="Pronouns (Optional)"
              name="pronouns"
            >
              <Input
                placeholder="e.g., they/them, he/him, she/her"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="Description (Optional)"
              name="description"
            >
              <Input.TextArea
                placeholder="Brief description of this member..."
                rows={3}
                size="large"
              />
            </Form.Item>

            <Form.Item label="Color">
              <div className="flex gap-2">
                <Form.Item name="color" noStyle>
                  <Input
                    placeholder="#6c757d"
                    size="large"
                    style={{ flex: 1 }}
                  />
                </Form.Item>
                <input
                  type="color"
                  value={form.getFieldValue('color') || '#6c757d'}
                  onChange={(e) => form.setFieldValue('color', e.target.value)}
                  className="w-12 h-10 rounded border cursor-pointer"
                />
              </div>
            </Form.Item>

            <Divider />

            <div className="mb-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-base">Proxy Tags (Optional)</h3>
                  <p className="text-sm text-gray-600">
                    Automatically send messages as this member using proxy tags
                  </p>
                </div>
                <Button
                  type="dashed"
                  icon={<PlusOutlined />}
                  onClick={addProxyTag}
                  size="small"
                >
                  Add Tag
                </Button>
              </div>

              <Alert
                message="How proxy tags work"
                description={
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
                        <code>{{</code> hello <code>}}</code> → sends "hello" as this member
                      </li>
                    </ul>
                  </div>
                }
                type="info"
                showIcon
                icon={<LinkOutlined />}
                className="mb-3"
              />

              <Space direction="vertical" style={{ width: '100%' }} size="small">
                {proxyTags.map((tag, index) => (
                  <div key={index} className="flex gap-2 items-center">
                    <Input
                      placeholder="Prefix (e.g., 'text:')"
                      value={tag.prefix}
                      onChange={(e) => updateProxyTag(index, 'prefix', e.target.value)}
                      style={{ flex: 1 }}
                    />
                    <span className="text-gray-500">message</span>
                    <Input
                      placeholder="Suffix (e.g., ':text')"
                      value={tag.suffix}
                      onChange={(e) => updateProxyTag(index, 'suffix', e.target.value)}
                      style={{ flex: 1 }}
                    />
                    {proxyTags.length > 1 && (
                      <Button
                        danger
                        type="text"
                        icon={<DeleteOutlined />}
                        onClick={() => removeProxyTag(index)}
                      />
                    )}
                  </div>
                ))}
              </Space>
            </div>

            <Form.Item className="mb-0 mt-6">
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  size="large"
                >
                  {editingMember ? 'Update Member' : 'Create Member'}
                </Button>
                <Button
                  onClick={() => setIsModalOpen(false)}
                  size="large"
                >
                  Cancel
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>

        <div className="mt-6 text-center">
          <Link href="/" className="text-blue-600 hover:underline">
            ← Back to Chat
          </Link>
        </div>
      </div>
    </div>
  );
}
