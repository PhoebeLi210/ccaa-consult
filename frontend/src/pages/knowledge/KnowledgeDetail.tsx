import React, { useState, useEffect } from 'react';
import {
  Card,
  Tag,
  Space,
  Button,
  Typography,
  Divider,
  Empty,
  Spin,
  Breadcrumb,
  message,
  Descriptions,
} from 'antd';
import {
  ArrowLeftOutlined,
  BookOutlined,
  ExperimentOutlined,
  AppstoreOutlined,
  UserOutlined,
  HistoryOutlined,
  StarOutlined,
  ShareAltOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import {
  getKnowledgeDetail,
  getRelatedKnowledge,
  incrementViewCount,
  type KnowledgeItem,
  type KnowledgeCategory,
} from '../../api/knowledge';

const { Title, Text, Paragraph } = Typography;

/** 知识分类配置 */
const CATEGORY_CONFIG: Record<KnowledgeCategory, { label: string; icon: React.ReactNode; color: string }> = {
  standard: { label: '标准知识', icon: <BookOutlined />, color: 'blue' },
  experience: { label: '经验知识', icon: <ExperimentOutlined />, color: 'green' },
  application: { label: '应用知识', icon: <AppstoreOutlined />, color: 'orange' },
  user: { label: '用户知识', icon: <UserOutlined />, color: 'purple' },
};

/**
 * 知识详情页组件
 */
const KnowledgeDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  // 状态
  const [loading, setLoading] = useState(true);
  const [knowledge, setKnowledge] = useState<KnowledgeItem | null>(null);
  const [relatedKnowledge, setRelatedKnowledge] = useState<KnowledgeItem[]>([]);

  // 加载知识详情
  useEffect(() => {
    const loadDetail = async () => {
      if (!id) return;

      setLoading(true);
      try {
        const [knowledgeData, relatedData] = await Promise.all([
          getKnowledgeDetail(id),
          getRelatedKnowledge(id, 5).catch(() => []),
        ]);

        setKnowledge(knowledgeData);
        setRelatedKnowledge(relatedData);

        // 增加查看次数
        incrementViewCount(id).catch(() => {});
      } catch (error) {
        message.error('加载知识详情失败');
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

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!knowledge) {
    return (
      <Empty
        description="知识不存在"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      >
        <Button type="primary" onClick={handleBack}>
          返回知识库
        </Button>
      </Empty>
    );
  }

  const categoryConfig = CATEGORY_CONFIG[knowledge.category];

  return (
    <div style={{ padding: 0 }}>
      {/* 面包屑 */}
      <Breadcrumb
        items={[
          { title: '首页', href: '/' },
          { title: '知识库', href: '/knowledge' },
          { title: categoryConfig.label },
          { title: knowledge.title },
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

      {/* 知识基本信息 */}
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 标题区 */}
          <div>
            <Space align="start" wrap>
              <Tag color={categoryConfig.color} icon={categoryConfig.icon}>
                {categoryConfig.label}
              </Tag>
              {knowledge.standard && (
                <Tag color="blue">{knowledge.standard}</Tag>
              )}
              {knowledge.industryName && (
                <Tag color="cyan">{knowledge.industryName}</Tag>
              )}
            </Space>
            <Title level={3} style={{ marginTop: 12, marginBottom: 8 }}>
              {knowledge.title}
            </Title>
            <Space split={<Divider type="vertical" />}>
              <Space size={4}>
                <HistoryOutlined style={{ color: '#999' }} />
                <Text type="secondary">浏览 {knowledge.viewCount} 次</Text>
              </Space>
              <Text type="secondary">
                更新于 {new Date(knowledge.updatedAt).toLocaleDateString()}
              </Text>
            </Space>
          </div>

          <Divider style={{ margin: '12px 0' }} />

          {/* 摘要 */}
          <div>
            <Title level={5}>摘要</Title>
            <Paragraph style={{ paddingLeft: 24, color: '#666' }}>
              {knowledge.summary}
            </Paragraph>
          </div>

          {/* 标签 */}
          {knowledge.tags && knowledge.tags.length > 0 && (
            <div>
              <Title level={5}>标签</Title>
              <Space wrap style={{ paddingLeft: 24 }}>
                {knowledge.tags.map((tag) => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Space>
            </div>
          )}

          {/* 详细内容 */}
          {knowledge.content && (
            <div>
              <Title level={5}>详细内容</Title>
              <Paragraph style={{ paddingLeft: 24, whiteSpace: 'pre-wrap' }}>
                {knowledge.content}
              </Paragraph>
            </div>
          )}
        </Space>
      </Card>

      {/* 相关知识 */}
      {relatedKnowledge.length > 0 && (
        <Card
          title={
            <Space>
              <BookOutlined />
              <span>相关知识</span>
            </Space>
          }
          style={{ marginTop: 16 }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {relatedKnowledge.map((item) => (
              <Card
                key={item.id}
                size="small"
                hoverable
                onClick={() => navigate(`/knowledge/detail/${item.id}`)}
              >
                <Space direction="vertical" size={4}>
                  <Text strong>{item.title}</Text>
                  <Text type="secondary" ellipsis style={{ maxWidth: 600 }}>
                    {item.summary}
                  </Text>
                </Space>
              </Card>
            ))}
          </Space>
        </Card>
      )}
    </div>
  );
};

export default KnowledgeDetail;
