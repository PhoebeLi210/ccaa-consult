import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Tag,
  Empty,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  BranchesOutlined,
} from '@ant-design/icons';
import {
  getFlowchartList,
  createFlowchart,
  deleteFlowchart,
  FlowchartInfo,
  CreateFlowchartRequest,
} from '../../api';
import styles from './style.module.css';

/**
 * 流程图管理页面
 * 展示流程图列表，支持创建、编辑、删除流程图
 */
const FlowchartListPage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [flowcharts, setFlowcharts] = useState<FlowchartInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // 获取流程图列表
  const fetchFlowcharts = async () => {
    setLoading(true);
    try {
      const data = await getFlowchartList();
      setFlowcharts(data);
    } catch (error) {
      message.error('获取流程图列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlowcharts();
  }, []);

  // 打开创建弹窗
  const handleCreate = () => {
    form.resetFields();
    setModalVisible(true);
  };

  // 提交创建
  const handleSubmit = async (values: CreateFlowchartRequest) => {
    setSubmitting(true);
    try {
      await createFlowchart(values);
      message.success('创建成功');
      setModalVisible(false);
      fetchFlowcharts();
    } catch (error) {
      message.error('创建失败');
    } finally {
      setSubmitting(false);
    }
  };

  // 编辑流程图
  const handleEdit = (record: FlowchartInfo) => {
    navigate(`/flowcharts/editor?id=${record.id}`);
  };

  // 删除流程图
  const handleDelete = async (id: string) => {
    try {
      await deleteFlowchart(id);
      message.success('删除成功');
      fetchFlowcharts();
    } catch (error) {
      message.error('删除失败');
    }
  };

  // 查看流程图详情
  const handleView = (record: FlowchartInfo) => {
    Modal.info({
      title: record.name,
      width: 600,
      content: (
        <div className={styles.detailContent}>
          <p><strong>描述：</strong>{record.description || '无'}</p>
          <p><strong>节点数：</strong>{record.nodeCount || 0}</p>
          <p><strong>边数：</strong>{record.edgeCount || 0}</p>
          <p><strong>创建时间：</strong>{record.createdAt}</p>
          <p><strong>更新时间：</strong>{record.updatedAt}</p>
          <p><strong>状态：</strong>
            <Tag color={record.status === 'published' ? 'success' : 'default'}>
              {record.status === 'published' ? '已发布' : '草稿'}
            </Tag>
          </p>
        </div>
      ),
    });
  };

  // 表格列定义
  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: FlowchartInfo) => (
        <Space>
          <BranchesOutlined style={{ color: '#1890ff' }} />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: '节点数',
      dataIndex: 'nodeCount',
      key: 'nodeCount',
      width: 100,
      render: (count: number) => count || 0,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'published' ? 'success' : 'default'}>
          {status === 'published' ? '已发布' : '草稿'}
        </Tag>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: unknown, record: FlowchartInfo) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个流程图吗？"
            description="删除后无法恢复"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className={styles.container}>
      <Card
        title="流程图管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            创建流程图
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={flowcharts}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          locale={{
            emptyText: (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无流程图"
              />
            ),
          }}
        />
      </Card>

      {/* 创建流程图弹窗 */}
      <Modal
        title="创建流程图"
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => setModalVisible(false)}
        confirmLoading={submitting}
        okText="创建"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="流程图名称"
            rules={[
              { required: true, message: '请输入流程图名称' },
              { max: 50, message: '名称不能超过50个字符' },
            ]}
          >
            <Input placeholder="请输入流程图名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
            rules={[{ max: 200, message: '描述不能超过200个字符' }]}
          >
            <Input.TextArea
              rows={3}
              placeholder="请输入流程图描述（可选）"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default FlowchartListPage;
