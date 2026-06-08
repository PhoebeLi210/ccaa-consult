import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card, Table, Tag, Space, Button, message, Spin, Statistic, Row, Col,
  Checkbox, Tooltip, Badge, Empty
} from 'antd';
import {
  FileTextOutlined, DownloadOutlined, ArrowLeftOutlined,
  SafetyOutlined, ToolOutlined, FireOutlined, BuildOutlined
} from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { generateFileList, FileListItem, FileListResponse } from '@/api';

/** 文件清单页面 */
const FileListPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isMobile } = useResponsive();

  const [loading, setLoading] = useState(false);
  const [fileData, setFileData] = useState<FileListResponse | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  /** 加载文件清单 */
  const loadFileList = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      // 从localStorage获取项目信息
      const projectStr = localStorage.getItem(`project_${id}`);
      const project = projectStr ? JSON.parse(projectStr) : {};

      const data = await generateFileList({
        industry_code: project.industryCode || 'property_management',
        company_info: {
          company_name: project.companyName || '示例公司',
          company_code: project.companyCode || 'XXX',
          industry: project.industry || '物业管理',
        },
        include_equipment: true,
        include_emergency_plans: true,
      });
      setFileData(data);
    } catch (err) {
      message.error('加载文件清单失败');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadFileList();
  }, [loadFileList]);

  /** 获取分类图标 */
  const getCategoryIcon = (category: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      manual: <FileTextOutlined />,
      procedure: <FileTextOutlined />,
      regulation: <SafetyOutlined />,
      instruction: <ToolOutlined />,
      form: <FileTextOutlined />,
      plan: <FireOutlined />,
      equipment_op: <ToolOutlined />,
      emergency_plan: <FireOutlined />,
    };
    return iconMap[category] || <FileTextOutlined />;
  };

  /** 获取分类标签 */
  const getCategoryTag = (category: string) => {
    const tagMap: Record<string, { text: string; color: string }> = {
      manual: { text: '手册', color: 'blue' },
      procedure: { text: '程序', color: 'cyan' },
      regulation: { text: '制度', color: 'purple' },
      instruction: { text: '规程', color: 'orange' },
      form: { text: '记录', color: 'green' },
      plan: { text: '预案', color: 'red' },
      equipment_op: { text: '设备', color: 'geekblue' },
      emergency_plan: { text: '应急', color: 'volcano' },
    };
    const tag = tagMap[category] || { text: category, color: 'default' };
    return <Tag color={tag.color}>{tag.text}</Tag>;
  };

  /** 表格列定义 */
  const columns = [
    {
      title: '文件编号',
      dataIndex: 'file_code',
      key: 'file_code',
      width: 100,
      render: (code: string) => <code style={{ fontSize: 12 }}>{code}</code>,
    },
    {
      title: '文件名称',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (name: string, record: FileListItem) => (
        <Space>
          {getCategoryIcon(record.category)}
          <span>{name}</span>
          {record.is_industry_specific && (
            <Tooltip title="行业特有文件">
              <Badge color="gold" />
            </Tooltip>
          )}
          {record.is_dynamic && (
            <Tooltip title="动态生成文件">
              <Badge color="green" />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: '层级',
      dataIndex: 'file_level',
      key: 'file_level',
      width: 80,
      render: (level: string) => {
        const colors: Record<string, string> = {
          A: 'blue',
          B: 'cyan',
          C: 'purple',
          D: 'green',
        };
        return <Tag color={colors[level] || 'default'}>{level}级</Tag>;
      },
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (category: string) => getCategoryTag(category),
    },
    {
      title: 'ISO条款',
      dataIndex: 'iso_clause',
      key: 'iso_clause',
      width: 100,
      render: (clause: string | null) => clause || '-',
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <Spin size="large" tip="加载文件清单..." />
      </div>
    );
  }

  return (
    <div>
      {/* 顶部操作栏 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
            返回
          </Button>
          <h2 style={{ margin: 0 }}>文件清单</h2>
          {fileData && (
            <Tag color="blue">{fileData.industry_name}</Tag>
          )}
        </Space>
        <Space>
          <Button type="primary" icon={<DownloadOutlined />}>
            导出清单
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      {fileData && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Card>
              <Statistic title="总文件数" value={fileData.total_count} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="一级文件" value={fileData.level_counts.A || 0} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="二级文件" value={fileData.level_counts.B || 0} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="三级文件" value={fileData.level_counts.C || 0} />
            </Card>
          </Col>
        </Row>
      )}

      {/* 文件列表 */}
      <Card>
        {fileData ? (
          <Table
            dataSource={fileData.files}
            columns={columns}
            rowKey="file_code"
            pagination={{ pageSize: 20 }}
            size="small"
            rowSelection={{
              selectedRowKeys: selectedFiles,
              onChange: (keys) => setSelectedFiles(keys as string[]),
            }}
          />
        ) : (
          <Empty description="暂无文件清单数据" />
        )}
      </Card>
    </div>
  );
};

export default FileListPage;
