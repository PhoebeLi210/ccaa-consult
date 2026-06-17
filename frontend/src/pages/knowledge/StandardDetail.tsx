import React, { useState, useEffect } from 'react';
import {
  Card,
  Descriptions,
  Tag,
  Space,
  Button,
  Typography,
  Divider,
  List,
  Tabs,
  Empty,
  Spin,
  Breadcrumb,
  Table,
  Tooltip,
  message,
  Collapse,
  Anchor,
} from 'antd';
import {
  ArrowLeftOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  AuditOutlined,
  FileSearchOutlined,
  LinkOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import {
  getStandardClauseDetail,
  getRelatedKnowledge,
  incrementViewCount,
  type StandardClause,
  type AuditPoint,
  type RecordRequirement,
  type KnowledgeItem,
} from '../../api/knowledge';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

/** 审核方法标签配置 */
const AUDIT_METHOD_CONFIG: Record<string, { label: string; color: string }> = {
  document: { label: '文件审查', color: 'blue' },
  interview: { label: '访谈', color: 'green' },
  observation: { label: '现场观察', color: 'orange' },
};

/** 标准颜色配置 */
const STANDARD_COLORS: Record<string, string> = {
  ISO9001: 'blue',
  ISO14001: 'green',
  ISO45001: 'orange',
};

/**
 * 标准条款详情页组件
 */
const StandardDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  // 状态
  const [loading, setLoading] = useState(true);
  const [clause, setClause] = useState<StandardClause | null>(null);
  const [relatedKnowledge, setRelatedKnowledge] = useState<KnowledgeItem[]>([]);

  // 加载条款详情
  useEffect(() => {
    const loadDetail = async () => {
      if (!id) return;

      setLoading(true);
      try {
        const [clauseData, relatedData] = await Promise.all([
          getStandardClauseDetail(id),
          getRelatedKnowledge(id, 5).catch(() => []),
        ]);

        setClause(clauseData);
        setRelatedKnowledge(relatedData);

        // 增加查看次数
        incrementViewCount(id).catch(() => {});
      } catch (error) {
        message.error('加载条款详情失败');
      } finally {
        setLoading(false);
      }
    };

    loadDetail();
  }, [id]);

  // 返回知识库
  const handleBack = () => {
    navigate('/knowledge');
  };

  // 查看相关条款
  const handleViewRelatedClause = (clauseId: string) => {
    navigate(`/knowledge/standard/${clauseId}`);
  };

  // 渲染要求列表
  const renderRequirements = (requirements: string[]) => {
    if (!requirements || requirements.length === 0) {
      return <Empty description="暂无要求" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    }

    return (
      <List
        dataSource={requirements}
        renderItem={(item, index) => (
          <List.Item style={{ padding: '8px 0', borderBottom: 'none' }}>
            <Space>
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
              <Text>{item}</Text>
            </Space>
          </List.Item>
        )}
      />
    );
  };

  // 渲染记录要求表格
  const renderRecordRequirements = (records: RecordRequirement[]) => {
    if (!records || records.length === 0) {
      return <Empty description="暂无记录要求" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    }

    const columns = [
      {
        title: '记录名称',
        dataIndex: 'name',
        key: 'name',
        render: (text: string, record: RecordRequirement) => (
          <Space>
            <FileTextOutlined />
            <Text strong>{text}</Text>
            {record.required && <Tag color="red">必须</Tag>}
          </Space>
        ),
      },
      {
        title: '说明',
        dataIndex: 'description',
        key: 'description',
        ellipsis: true,
      },
      {
        title: '保存期限',
        dataIndex: 'retentionPeriod',
        key: 'retentionPeriod',
        width: 120,
        render: (text: string) => text || '-',
      },
      {
        title: '模板',
        dataIndex: 'template',
        key: 'template',
        width: 100,
        render: (template: string) =>
          template ? (
            <Button type="link" size="small">
              下载
            </Button>
          ) : (
            '-'
          ),
      },
    ];

    return (
      <Table
        columns={columns}
        dataSource={records}
        rowKey="id"
        pagination={false}
        size="small"
      />
    );
  };

  // 渲染审核要点
  const renderAuditPoints = (audit_points: AuditPoint[]) => {
    if (!audit_points || audit_points.length === 0) {
      return <Empty description="暂无审核要点" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    }

    return (
      <Collapse
        accordion
        items={audit_points.map((point, index) => ({
          key: index.toString(),
          label: (
            <Space>
              <AuditOutlined style={{ color: '#1890ff' }} />
              <Text strong>{point.content}</Text>
              <Tag color={AUDIT_METHOD_CONFIG[point.method]?.color}>
                {AUDIT_METHOD_CONFIG[point.method]?.label || point.method}
              </Tag>
            </Space>
          ),
          children: (
            <div>
              <Descriptions column={1} size="small">
                <Descriptions.Item label="所需证据">
                  <List
                    dataSource={point.evidence}
                    renderItem={(item: string) => (
                      <List.Item style={{ padding: '4px 0', borderBottom: 'none' }}>
                        <Space>
                          <FileSearchOutlined style={{ color: '#1890ff' }} />
                          <Text>{item}</Text>
                        </Space>
                      </List.Item>
                    )}
                  />
                </Descriptions.Item>
                <Descriptions.Item label="常见问题">
                  <List
                    dataSource={point.common_issues}
                    renderItem={(item: string) => (
                      <List.Item style={{ padding: '4px 0', borderBottom: 'none' }}>
                        <Space>
                          <WarningOutlined style={{ color: '#faad14' }} />
                          <Text type="warning">{item}</Text>
                        </Space>
                      </List.Item>
                    )}
                  />
                </Descriptions.Item>
              </Descriptions>
            </div>
          ),
        }))}
      />
    );
  };

  // 渲染相关知识
  const renderRelatedKnowledge = () => {
    if (relatedKnowledge.length === 0) {
      return null;
    }

    return (
      <Card
        title={
          <Space>
            <BookOutlined />
            <span>相关知识</span>
          </Space>
        }
        style={{ marginTop: 16 }}
      >
        <List
          dataSource={relatedKnowledge}
          renderItem={(item) => (
            <List.Item
              style={{ cursor: 'pointer' }}
              onClick={() => navigate(`/knowledge/detail/${item.id}`)}
            >
              <List.Item.Meta
                title={item.title}
                description={item.summary}
              />
            </List.Item>
          )}
        />
      </Card>
    );
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!clause) {
    return (
      <Empty
        description="条款不存在"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      >
        <Button type="primary" onClick={handleBack}>
          返回知识库
        </Button>
      </Empty>
    );
  }

  return (
    <div style={{ padding: 0 }}>
      {/* 面包屑 */}
      <Breadcrumb
        items={[
          { title: '首页', href: '/' },
          { title: '知识库', href: '/knowledge' },
          { title: clause.standard },
          { title: `${clause.clause_number} ${clause.title}` },
        ]}
        style={{ marginBottom: 16 }}
      />

      {/* 返回按钮 */}
      <Button
        type="text"
        icon={<ArrowLeftOutlined />}
        onClick={handleBack}
        style={{ marginBottom: 16 }}
      >
        返回知识库
      </Button>

      {/* 条款基本信息 */}
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 标题区 */}
          <div>
            <Space align="start">
              <Tag color={STANDARD_COLORS[clause.standard || ''] || 'default'} style={{ marginTop: 4 }}>
                {clause.standard}
              </Tag>
              <div>
                <Title level={3} style={{ marginBottom: 8 }}>
                  {clause.clause_number} {clause.title}
                </Title>
                <Space>
                  {(clause.related_clauses?.length ?? 0) > 0 && (
                    <Text type="secondary">
                      相关条款: {clause.related_clauses?.join(', ')}
                    </Text>
                  )}
                </Space>
              </div>
            </Space>
          </div>

          <Divider style={{ margin: '12px 0' }} />

          {/* 条款内容 */}
          <div>
            <Title level={5}>
              <FileTextOutlined style={{ marginRight: 8 }} />
              条款内容
            </Title>
            <Paragraph style={{ paddingLeft: 24, whiteSpace: 'pre-wrap' }}>
              {clause.content}
            </Paragraph>
          </div>
        </Space>
      </Card>

      {/* 详细信息标签页 */}
      <Card style={{ marginTop: 16 }}>
        <Tabs
          defaultActiveKey="requirements"
          items={[
            {
              key: 'requirements',
              label: (
                <Space>
                  <CheckCircleOutlined />
                  <span>条款要求</span>
                </Space>
              ),
              children: renderRequirements(clause.requirements || []),
            },
            {
              key: 'records',
              label: (
                <Space>
                  <FileTextOutlined />
                  <span>记录要求</span>
                  {(clause.records?.length ?? 0) > 0 && (
                    <Tag color="blue">{clause.records?.length}</Tag>
                  )}
                </Space>
              ),
              children: renderRecordRequirements(clause.records || []),
            },
            {
              key: 'audit',
              label: (
                <Space>
                  <AuditOutlined />
                  <span>审核要点</span>
                  {(clause.audit_points?.length ?? 0) > 0 && (
                    <Tag color="orange">{clause.audit_points?.length}</Tag>
                  )}
                </Space>
              ),
              children: renderAuditPoints(clause.audit_points || []),
            },
          ]}
        />
      </Card>

      {/* 相关条款 */}
      {clause.related_clauses && clause.related_clauses.length > 0 && (
        <Card
          title={
            <Space>
              <LinkOutlined />
              <span>相关条款</span>
            </Space>
          }
          style={{ marginTop: 16 }}
        >
          <Space wrap>
            {clause.related_clauses.map((related: string) => (
              <Tag
                key={related}
                style={{ cursor: 'pointer' }}
                onClick={() => {
                  // 这里需要根据条款号查找对应的ID，暂时用条款号作为ID
                  message.info(`跳转到条款 ${related}`);
                }}
              >
                {related}
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      {/* 相关知识 */}
      {renderRelatedKnowledge()}
    </div>
  );
};

export default StandardDetail;
