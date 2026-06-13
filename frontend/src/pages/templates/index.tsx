import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Table,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Drawer,
  Timeline,
  Typography,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  HistoryOutlined,
  RollbackOutlined,
  EyeOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import {
  getCustomTemplates,
  getCustomTemplate,
  uploadCustomTemplate,
  updateCustomTemplate,
  updateTemplateContent,
  deleteCustomTemplate,
  getTemplateVersions,
  rollbackTemplate,
  type CustomTemplate,
  type TemplateVersion,
} from '../../api';
import styles from './style.module.css';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

/** 文档类型选项 */
const CATEGORY_OPTIONS = [
  { value: 'manual', label: '管理手册' },
  { value: 'procedure', label: '程序文件' },
  { value: 'record', label: '记录表格' },
  { value: 'instruction', label: '作业指导书' },
  { value: 'form', label: '表单' },
];

/** 状态选项 */
const STATUS_OPTIONS = [
  { value: 'active', label: '启用', color: 'success' },
  { value: 'disabled', label: '禁用', color: 'default' },
  { value: 'archived', label: '归档', color: 'warning' },
];

/**
 * 模板管理页面 - V1.3
 */
const TemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<CustomTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<CustomTemplate | null>(null);
  const [versionDrawerVisible, setVersionDrawerVisible] = useState(false);
  const [versions, setVersions] = useState<TemplateVersion[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<CustomTemplate | null>(null);
  const [previewDrawerVisible, setPreviewDrawerVisible] = useState(false);
  const [previewContent, setPreviewContent] = useState('');
  const [form] = Form.useForm();

  // 加载模板列表
  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await getCustomTemplates();
      setTemplates(data);
    } catch (error) {
      message.error('加载模板列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  // 打开创建/编辑模态框
  const openModal = (template?: CustomTemplate) => {
    if (template) {
      setEditingTemplate(template);
      form.setFieldsValue({
        name: template.name,
        description: template.description,
        category: template.category,
        industry: template.industry,
        status: template.status,
      });
    } else {
      setEditingTemplate(null);
      form.resetFields();
    }
    setModalVisible(true);
  };

  // 保存模板
  const handleSave = async (values: any) => {
    try {
      if (editingTemplate) {
        await updateCustomTemplate(editingTemplate.template_id, values);
        message.success('模板更新成功');
      } else {
        // 新建模板需要内容
        await uploadCustomTemplate({
          ...values,
          content: `# ${values.name}\n\n# 在此处编写模板内容\n# 使用 {{变量名}} 定义变量\n`,
        });
        message.success('模板创建成功');
      }
      setModalVisible(false);
      loadTemplates();
    } catch (error) {
      message.error('保存失败');
    }
  };

  // 删除模板
  const handleDelete = async (template_id: string) => {
    try {
      await deleteCustomTemplate(template_id);
      message.success('模板删除成功');
      loadTemplates();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 查看版本历史
  const handleViewVersions = async (template: CustomTemplate) => {
    setSelectedTemplate(template);
    try {
      const data = await getTemplateVersions(template.template_id);
      setVersions(data);
      setVersionDrawerVisible(true);
    } catch (error) {
      message.error('加载版本历史失败');
    }
  };

  // 回滚版本
  const handleRollback = async (version: string) => {
    if (!selectedTemplate) return;
    try {
      await rollbackTemplate(selectedTemplate.template_id, version);
      message.success(`已回滚到版本 ${version}`);
      setVersionDrawerVisible(false);
      loadTemplates();
    } catch (error) {
      message.error('回滚失败');
    }
  };

  // 预览模板
  const handlePreview = async (template: CustomTemplate) => {
    try {
      const data = await getCustomTemplate(template.template_id);
      setPreviewContent(data.content);
      setSelectedTemplate(template);
      setPreviewDrawerVisible(true);
    } catch (error) {
      message.error('加载模板内容失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: CustomTemplate) => (
        <Space direction="vertical" size={0}>
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.description || '无描述'}
          </Text>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (category: string) => {
        const option = CATEGORY_OPTIONS.find((o) => o.value === category);
        return <Tag>{option?.label || category}</Tag>;
      },
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 80,
      render: (version: string) => <Tag color="blue">v{version}</Tag>,
    },
    {
      title: '变量数',
      dataIndex: 'variables',
      key: 'variables',
      width: 80,
      render: (variables: string[]) => variables?.length || 0,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const option = STATUS_OPTIONS.find((o) => o.value === status);
        return <Tag color={option?.color as any}>{option?.label || status}</Tag>;
      },
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: CustomTemplate) => (
        <Space size="small">
          <Tooltip title="预览">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => handlePreview(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => openModal(record)}
            />
          </Tooltip>
          <Tooltip title="版本历史">
            <Button
              type="text"
              icon={<HistoryOutlined />}
              onClick={() => handleViewVersions(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            description="删除后无法恢复，是否继续？"
            onConfirm={() => handleDelete(record.template_id)}
            okText="删除"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <Card
        title={
          <Space>
            <FileTextOutlined />
            <span>我的模板</span>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>
            新建模板
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={templates}
          rowKey="template_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 创建/编辑模态框 */}
      <Modal
        title={editingTemplate ? '编辑模板' : '新建模板'}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="例如：质量管理手册模板" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="模板描述（可选）" />
          </Form.Item>

          <Form.Item
            name="category"
            label="文档类型"
            rules={[{ required: true, message: '请选择文档类型' }]}
          >
            <Select placeholder="选择文档类型">
              {CATEGORY_OPTIONS.map((opt) => (
                <Option key={opt.value} value={opt.value}>
                  {opt.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="industry" label="适用行业">
            <Input placeholder="例如：制造业（可选）" />
          </Form.Item>

          {editingTemplate && (
            <Form.Item name="status" label="状态">
              <Select placeholder="选择状态">
                {STATUS_OPTIONS.map((opt) => (
                  <Option key={opt.value} value={opt.value}>
                    {opt.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          )}
        </Form>
      </Modal>

      {/* 版本历史抽屉 */}
      <Drawer
        title="版本历史"
        placement="right"
        width={500}
        open={versionDrawerVisible}
        onClose={() => setVersionDrawerVisible(false)}
      >
        <Timeline
          items={versions.map((v, index) => ({
            color: index === 0 ? 'green' : 'gray',
            children: (
              <div className={styles.versionItem}>
                <Space direction="vertical" size={0} style={{ width: '100%' }}>
                  <Space>
                    <Tag color="blue">v{v.version}</Tag>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {new Date(v.updated_at).toLocaleString()}
                    </Text>
                  </Space>
                  {index > 0 && (
                    <Button
                      type="link"
                      size="small"
                      icon={<RollbackOutlined />}
                      onClick={() => handleRollback(v.version)}
                    >
                      回滚到此版本
                    </Button>
                  )}
                </Space>
              </div>
            ),
          }))}
        />
      </Drawer>

      {/* 预览抽屉 */}
      <Drawer
        title={selectedTemplate?.name}
        placement="right"
        width={700}
        open={previewDrawerVisible}
        onClose={() => setPreviewDrawerVisible(false)}
      >
        <pre className={styles.previewContent}>{previewContent}</pre>
      </Drawer>
    </div>
  );
};

export default TemplatesPage;
