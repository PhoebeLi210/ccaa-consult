import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  List,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Drawer,
  Avatar,
  Typography,
  Select,
  Descriptions,
  Empty,
  Tabs,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TeamOutlined,
  UserAddOutlined,
  SettingOutlined,
  UserOutlined,
} from '@ant-design/icons';
import {
  getMyTeams,
  getTeamDetail,
  createTeam,
  updateTeam,
  deleteTeam,
  inviteTeamMember,
  updateMemberRole,
  removeTeamMember,
  getMyPermissions,
  type Team,
  type TeamMember,
  type TeamRole,
} from '../../api';
import styles from './style.module.css';

const { TextArea } = Input;
const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

/** 角色配置 */
const ROLE_CONFIG: Record<TeamRole, { label: string; color: string; description: string }> = {
  owner: { label: '所有者', color: 'gold', description: '拥有所有权限' },
  admin: { label: '管理员', color: 'red', description: '可管理团队和成员' },
  member: { label: '成员', color: 'blue', description: '可编辑文档' },
  viewer: { label: '观察者', color: 'default', description: '仅可查看' },
};

/**
 * 团队协作页面 - V1.3
 */
const TeamPage: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTeam, setEditingTeam] = useState<Team | null>(null);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [myPermissions, setMyPermissions] = useState<Record<string, boolean> | null>(null);
  const [inviteModalVisible, setInviteModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [inviteForm] = Form.useForm();

  // 加载团队列表
  const loadTeams = async () => {
    setLoading(true);
    try {
      const data = await getMyTeams();
      setTeams(data);
    } catch (error) {
      message.error('加载团队列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTeams();
  }, []);

  // 打开创建/编辑模态框
  const openModal = (team?: Team) => {
    if (team) {
      setEditingTeam(team);
      form.setFieldsValue({
        name: team.name,
        description: team.description,
      });
    } else {
      setEditingTeam(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 保存团队
  const handleSave = async (values: any) => {
    try {
      if (editingTeam) {
        await updateTeam(editingTeam.team_id, values);
        message.success('团队更新成功');
      } else {
        await createTeam(values);
        message.success('团队创建成功');
      }
      setModalVisible(false);
      loadTeams();
    } catch (error) {
      message.error('保存失败');
    }
  };

  // 删除团队
  const handleDelete = async (teamId: string) => {
    try {
      await deleteTeam(teamId);
      message.success('团队删除成功');
      loadTeams();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 查看团队详情
  const handleViewDetail = async (team: Team) => {
    setSelectedTeam(team);
    setDetailDrawerVisible(true);
    try {
      const [detailData, permissionsData] = await Promise.all([
        getTeamDetail(team.team_id),
        getMyPermissions(team.team_id),
      ]);
      setMembers(detailData.members);
      setMyPermissions(permissionsData as unknown as Record<string, boolean>);
    } catch (error) {
      message.error('加载团队详情失败');
    }
  };

  // 邀请成员
  const handleInvite = async (values: { email: string; role: TeamRole }) => {
    if (!selectedTeam) return;
    try {
      await inviteTeamMember(selectedTeam.team_id, values);
      message.success('邀请已发送');
      setInviteModalVisible(false);
      inviteForm.resetFields();
      // 刷新成员列表
      const detailData = await getTeamDetail(selectedTeam.team_id);
      setMembers(detailData.members);
    } catch (error) {
      message.error('邀请失败');
    }
  };

  // 更新成员角色
  const handleUpdateRole = async (user_id: string, role: TeamRole) => {
    if (!selectedTeam) return;
    try {
      await updateMemberRole(selectedTeam.team_id, user_id, role);
      message.success('角色更新成功');
      // 刷新成员列表
      const detailData = await getTeamDetail(selectedTeam.team_id);
      setMembers(detailData.members);
    } catch (error) {
      message.error('更新失败');
    }
  };

  // 移除成员
  const handleRemoveMember = async (user_id: string) => {
    if (!selectedTeam) return;
    try {
      await removeTeamMember(selectedTeam.team_id, user_id);
      message.success('成员已移除');
      setMembers(members.filter((m) => m.user_id !== user_id));
    } catch (error) {
      message.error('移除失败');
    }
  };

  // 检查权限
  const hasPermission = (permission: string) => {
    return myPermissions?.[permission] || false;
  };

  return (
    <div className={styles.container}>
      <Card
        title={
          <Space>
            <TeamOutlined />
            <span>我的团队</span>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>
            创建团队
          </Button>
        }
      >
        {teams.length === 0 ? (
          <Empty description="暂无团队，创建一个新团队开始协作吧" />
        ) : (
          <List
            grid={{ gutter: 16, xs: 1, sm: 2, lg: 3 }}
            dataSource={teams}
            loading={loading}
            renderItem={(team) => (
              <List.Item>
                <Card
                  hoverable
                  className={styles.teamCard}
                  onClick={() => handleViewDetail(team)}
                  actions={[
                    <Button
                      key="edit"
                      type="text"
                      icon={<EditOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        openModal(team);
                      }}
                    >
                      编辑
                    </Button>,
                    <Popconfirm
                      key="delete"
                      title="确认删除"
                      description="删除后无法恢复，是否继续？"
                      onConfirm={(e) => {
                        e?.stopPropagation();
                        handleDelete(team.team_id);
                      }}
                      okText="删除"
                      cancelText="取消"
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={(e) => e.stopPropagation()}
                      >
                        删除
                      </Button>
                    </Popconfirm>,
                  ]}
                >
                  <Card.Meta
                    avatar={
                      <Avatar
                        size={48}
                        style={{ backgroundColor: '#1890ff' }}
                        icon={<TeamOutlined />}
                      />
                    }
                    title={team.name}
                    description={
                      <Space direction="vertical" size={0}>
                        <Text type="secondary" ellipsis>
                          {team.description || '无描述'}
                        </Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          创建于 {new Date(team.created_at).toLocaleDateString()}
                        </Text>
                      </Space>
                    }
                  />
                </Card>
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* 创建/编辑模态框 */}
      <Modal
        title={editingTeam ? '编辑团队' : '创建团队'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
        width={500}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item
            name="name"
            label="团队名称"
            rules={[{ required: true, message: '请输入团队名称' }]}
          >
            <Input placeholder="例如：质量管理咨询团队" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="团队描述（可选）" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 团队详情抽屉 */}
      <Drawer
        title={selectedTeam?.name}
        placement="right"
        width={700}
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
        extra={
          hasPermission('can_invite_member') && (
            <Button
              type="primary"
              icon={<UserAddOutlined />}
              onClick={() => setInviteModalVisible(true)}
            >
              邀请成员
            </Button>
          )
        }
      >
        <Tabs defaultActiveKey="members">
          <TabPane tab="成员管理" key="members">
            <List
              dataSource={members}
              renderItem={(member) => (
                <List.Item
                  actions={[
                    hasPermission('can_manage_team') && member.role !== 'owner' && (
                      <Select
                        key="role"
                        value={member.role}
                        style={{ width: 100 }}
                        onChange={(value) => handleUpdateRole(member.user_id, value)}
                        disabled={!hasPermission('can_manage_team')}
                      >
                        {Object.entries(ROLE_CONFIG).map(([role, config]) => (
                          <Option key={role} value={role}>
                            {config.label}
                          </Option>
                        ))}
                      </Select>
                    ),
                    hasPermission('can_remove_member') &&
                      member.role !== 'owner' &&
                      member.user_id !== selectedTeam?.owner_id && (
                        <Popconfirm
                          key="remove"
                          title="确认移除"
                          description="确定要移除此成员吗？"
                          onConfirm={() => handleRemoveMember(member.user_id)}
                          okText="移除"
                          cancelText="取消"
                        >
                          <Button type="text" danger>
                            移除
                          </Button>
                        </Popconfirm>
                      ),
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={<UserOutlined />} />}
                    title={
                      <Space>
                        <Text>{member.user_id}</Text>
                        <Tag color={ROLE_CONFIG[member.role].color}>
                          {ROLE_CONFIG[member.role].label}
                        </Tag>
                        {member.user_id === selectedTeam?.owner_id && (
                          <Tag color="gold">创建者</Tag>
                        )}
                      </Space>
                    }
                    description={ROLE_CONFIG[member.role].description}
                  />
                </List.Item>
              )}
            />
          </TabPane>

          <TabPane tab="权限说明" key="permissions">
            <Descriptions bordered column={1}>
              <Descriptions.Item label="所有者">
                拥有团队的所有权限，包括删除团队、管理成员、分配项目等
              </Descriptions.Item>
              <Descriptions.Item label="管理员">
                可以邀请成员、管理项目、编辑文档，但不能删除团队
              </Descriptions.Item>
              <Descriptions.Item label="成员">
                可以编辑和查看文档，参与项目协作
              </Descriptions.Item>
              <Descriptions.Item label="观察者">
                只能查看文档和项目，不能进行编辑
              </Descriptions.Item>
            </Descriptions>

            {myPermissions && (
              <>
                <Title level={5} style={{ marginTop: 24 }}>
                  我的权限
                </Title>
                <Space wrap>
                  {Object.entries(myPermissions).map(([key, value]) => (
                    <Tag key={key} color={value ? 'success' : 'default'}>
                      {key}: {value ? '是' : '否'}
                    </Tag>
                  ))}
                </Space>
              </>
            )}
          </TabPane>
        </Tabs>
      </Drawer>

      {/* 邀请成员模态框 */}
      <Modal
        title="邀请成员"
        open={inviteModalVisible}
        onOk={() => inviteForm.submit()}
        onCancel={() => {
          setInviteModalVisible(false);
          inviteForm.resetFields();
        }}
        width={400}
      >
        <Form form={inviteForm} layout="vertical" onFinish={handleInvite}>
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="成员邮箱地址" />
          </Form.Item>

          <Form.Item
            name="role"
            label="角色"
            initialValue="member"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select placeholder="选择角色">
              {Object.entries(ROLE_CONFIG).map(([role, config]) => (
                <Option key={role} value={role}>
                  <Space direction="vertical" size={0}>
                    <Text>{config.label}</Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {config.description}
                    </Text>
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TeamPage;
