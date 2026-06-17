import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, Tag, Space, Button, Typography, Spin, Empty, message, List } from 'antd';
import { ArrowLeftOutlined, BookOutlined, FileTextOutlined, DownloadOutlined } from '@ant-design/icons';
import { getKnowledgeDetail, type KnowledgeItem } from '../../api/knowledge';
import { request } from '../../api/request';

const { Title, Text } = Typography;

const KnowledgeDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [knowledge, setKnowledge] = useState<any>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);

    const isUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);

    if (isUUID) {
      request.get(`/v1/knowledge/articles/${id}`)
        .then((article: any) => {
          setKnowledge({
            title: article.title || '未命名',
            summary: article.summary || '',
            category: article.category || 'standard',
            tags: article.tags || [],
            source_file: article.source_file || '',
            content_length: article.content?.length || 0,
          });
        })
        .catch(() => message.error('文章加载失败'))
        .finally(() => setLoading(false));
    } else {
      getKnowledgeDetail(id)
        .then((data) => setKnowledge(data))
        .catch(() => message.error('加载失败'))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>;
  if (!knowledge) return <Empty description="内容不存在"><Button onClick={() => navigate('/knowledge')}>返回</Button></Empty>;

  const isImportedArticle = !!knowledge.source_file || knowledge.content?.length > 0;

  return (
    <div style={{ padding: 0 }}>
      <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate('/knowledge')} style={{ marginBottom: 16 }}>
        返回知识库
      </Button>

      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Tag color="blue" icon={knowledge.category === 'standard' ? <BookOutlined /> : <FileTextOutlined />}>
              {isImportedArticle ? '标准文档' : '行业知识'}
            </Tag>
            <Title level={3} style={{ marginTop: 12 }}>{knowledge.title}</Title>
          </div>

          {knowledge.summary && (
            <div>
              <Title level={5}>摘要</Title>
              <Text style={{ paddingLeft: 24 }}>{knowledge.summary}</Text>
            </div>
          )}

          {knowledge.tags?.length > 0 && (
            <div>
              <Title level={5}>标签</Title>
              <Space wrap style={{ paddingLeft: 24 }}>
                {knowledge.tags.map((t: string) => <Tag key={t}>{t}</Tag>)}
              </Space>
            </div>
          )}

          {knowledge.applicable_standards?.length > 0 && (
            <div>
              <Title level={5}>适用标准</Title>
              <Space wrap style={{ paddingLeft: 24 }}>
                {knowledge.applicable_standards.map((s: string) => <Tag key={s} color="blue">{s}</Tag>)}
              </Space>
            </div>
          )}

          {knowledge.key_requirements?.length > 0 && (
            <div>
              <Title level={5}>关键要求</Title>
              <ul style={{ paddingLeft: 48 }}>
                {knowledge.key_requirements.map((r: string) => <li key={r}>{r}</li>)}
              </ul>
            </div>
          )}

          {knowledge.common_documents?.length > 0 && (
            <div>
              <Title level={5}>常用文件</Title>
              <ul style={{ paddingLeft: 48 }}>
                {knowledge.common_documents.map((d: string) => <li key={d}>{d}</li>)}
              </ul>
            </div>
          )}

          {isImportedArticle && knowledge.content && (
            <div>
              <Title level={5}>文档内容</Title>
              <div style={{
                paddingLeft: 24,
                maxHeight: 600,
                overflow: 'auto',
                whiteSpace: 'pre-wrap',
                lineHeight: 1.8,
                background: '#fafafa',
                padding: 16,
                borderRadius: 8,
                border: '1px solid #f0f0f0',
              }}>
                {knowledge.content}
              </div>
            </div>
          )}

          {isImportedArticle && !knowledge.content && (
            <div>
              <Title level={5}>文档信息</Title>
              <Space direction="vertical" style={{ paddingLeft: 24 }}>
                <Text type="secondary">这是一个完整的标准文档</Text>
              </Space>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default KnowledgeDetail;
