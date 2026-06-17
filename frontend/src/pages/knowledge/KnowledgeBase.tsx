import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Layout,
  Card,
  Input,
  List,
  Tag,
  Space,
  Button,
  Empty,
  Spin,
  Typography,
  Select,
  Badge,
  Tabs,
} from 'antd';
import {
  SearchOutlined,
  BookOutlined,
  RightOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import {
  getKnowledgeList,
  getSupportedStandardsList,
  getIndustryList,
  type KnowledgeItem,
} from '../../api/knowledge';
import { request } from '../../api/request';

const { Search } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

const STANDARD_COLORS: Record<string, string> = {
  'ISO9001:2015': 'blue',
  'ISO14001:2015': 'green',
  'ISO45001:2018': 'orange',
  'ISO27001:2022': 'purple',
  'ISO22000:2018': 'red',
  'ISO13485:2016': 'cyan',
  'CMMI': 'geekblue',
};

interface KnowledgeArticle {
  id: number;
  article_id: string;
  title: string;
  category: string;
  content: string;
  summary: string;
  tags: string[];
}

const KnowledgeBase: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('industry');
  const [knowledgeList, setKnowledgeList] = useState<KnowledgeItem[]>([]);
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [total, setTotal] = useState(0);
  const [articlesTotal, setArticlesTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState<string>('');
  const [industries, setIndustries] = useState<Array<{ code: string; name: string }>>([]);

  useEffect(() => {
    const loadOptions = async () => {
      try {
        const industriesData = await getIndustryList();
        setIndustries(industriesData);
      } catch (error) {
        console.error('加载选项失败:', error);
      }
    };
    loadOptions();
  }, []);

  useEffect(() => {
    if (activeTab === 'industry') {
      loadKnowledgeList();
    } else {
      loadArticles();
    }
  }, [activeTab, page, pageSize, selectedIndustry]);

  const loadKnowledgeList = async () => {
    setLoading(true);
    try {
      const params: any = { page, page_size: pageSize };
      if (selectedIndustry) params.industry = selectedIndustry;
      const result = await getKnowledgeList(params);
      setKnowledgeList(result.items || []);
      setTotal(result.total || 0);
    } catch (error) {
      console.error('加载知识列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadArticles = async () => {
    setLoading(true);
    try {
      const result: any = await request.get('/v1/knowledge/articles', {
        params: { page, page_size: pageSize }
      });
      setArticles(result.items || []);
      setArticlesTotal(result.total || 0);
    } catch (error) {
      console.error('加载文章列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setPage(1);
  };

  const renderIndustryItem = (item: KnowledgeItem) => (
    <List.Item
      key={item.id}
      style={{ cursor: 'pointer', padding: '16px 0' }}
      onClick={() => navigate(`/knowledge/detail/${item.id}`)}
    >
      <List.Item.Meta
        title={<Text strong style={{ fontSize: 16 }}>{item.title}</Text>}
        description={
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 0, color: '#666' }}>
              {item.summary}
            </Paragraph>
            <Space size={4} wrap>
              {item.applicable_standards?.slice(0, 3).map((std: string) => (
                <Tag key={std} color={STANDARD_COLORS[std] || 'default'}>{std}</Tag>
              ))}
              {item.tags?.slice(0, 3).map((tag: string) => (
                <Tag key={tag}>{tag}</Tag>
              ))}
            </Space>
          </Space>
        }
      />
      <RightOutlined style={{ color: '#999' }} />
    </List.Item>
  );

  const renderArticleItem = (item: KnowledgeArticle) => (
    <List.Item
      key={item.article_id}
      style={{ cursor: 'pointer', padding: '16px 0' }}
      onClick={() => navigate(`/knowledge/detail/${item.article_id}`)}
    >
      <List.Item.Meta
        avatar={<FileTextOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
        title={<Text strong style={{ fontSize: 16 }}>{item.title}</Text>}
        description={
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 0, color: '#666' }}>
              {item.summary}
            </Paragraph>
            <Space size={4} wrap>
              <Tag color="blue">{item.category}</Tag>
              {item.tags?.map((tag: string) => (
                <Tag key={tag}>{tag}</Tag>
              ))}
            </Space>
          </Space>
        }
      />
      <RightOutlined style={{ color: '#999' }} />
    </List.Item>
  );

  const filterList = (list: any[]) => {
    if (!searchQuery) return list;
    const q = searchQuery.toLowerCase();
    return list.filter((item: any) =>
      item.title?.toLowerCase().includes(q) ||
      item.summary?.toLowerCase().includes(q)
    );
  };

  return (
    <div style={{ padding: 0 }}>
      {/* 搜索栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Search
            placeholder="搜索知识库..."
            allowClear
            onSearch={handleSearch}
            style={{ width: '100%' }}
          />
          {activeTab === 'industry' && (
            <Select
              placeholder="选择行业"
              allowClear
              showSearch
              optionFilterProp="children"
              style={{ width: 200 }}
              value={selectedIndustry || undefined}
              onChange={(v) => { setSelectedIndustry(v || ''); setPage(1); }}
            >
              {industries.map((ind) => (
                <Option key={ind.code} value={ind.code}>{ind.name}</Option>
              ))}
            </Select>
          )}
        </Space>
      </Card>

      {/* 标签页切换 */}
      <Tabs activeKey={activeTab} onChange={setActiveTab} style={{ marginBottom: 16 }}>
        <TabPane tab={<span><BookOutlined /> 行业知识</span>} key="industry" />
        <TabPane tab={<span><FileTextOutlined /> 标准文档 <Badge count={articlesTotal} size="small" /></span>} key="articles" />
      </Tabs>

      {/* 内容区域 */}
      <Card>
        <Spin spinning={loading}>
          {activeTab === 'industry' ? (
            filterList(knowledgeList).length > 0 ? (
              <List
                itemLayout="vertical"
                dataSource={filterList(knowledgeList)}
                renderItem={renderIndustryItem}
                pagination={{
                  current: page,
                  pageSize,
                  total,
                  showSizeChanger: true,
                  showTotal: (t) => `共 ${t} 个行业`,
                  onChange: (p, ps) => { setPage(p); setPageSize(ps); },
                }}
              />
            ) : (
              <Empty description="暂无行业知识" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )
          ) : (
            filterList(articles).length > 0 ? (
              <List
                itemLayout="vertical"
                dataSource={filterList(articles)}
                renderItem={renderArticleItem}
                pagination={{
                  current: page,
                  pageSize,
                  total: articlesTotal,
                  showSizeChanger: true,
                  showTotal: (t) => `共 ${t} 篇文档`,
                  onChange: (p, ps) => { setPage(p); setPageSize(ps); },
                }}
              />
            ) : (
              <Empty description="暂无标准文档" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default KnowledgeBase;
