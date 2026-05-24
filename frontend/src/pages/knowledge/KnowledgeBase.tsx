import React, { useState, useEffect } from 'react';
import {
  Layout,
  Menu,
  Card,
  Input,
  List,
  Tag,
  Space,
  Button,
  Empty,
  Spin,
  Typography,
  Tree,
  Select,
  Breadcrumb,
  message,
  Badge,
  Tooltip,
} from 'antd';
import {
  SearchOutlined,
  BookOutlined,
  ExperimentOutlined,
  AppstoreOutlined,
  UserOutlined,
  FileTextOutlined,
  RightOutlined,
  HistoryOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  getKnowledgeList,
  getKnowledgeCategoryTree,
  searchKnowledge,
  getSupportedStandardsList,
  getIndustryList,
  type KnowledgeItem,
  type KnowledgeCategoryTree,
  type KnowledgeCategory,
} from '../../api/knowledge';

const { Sider, Content } = Layout;
const { Search } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

/** 知识分类配置 */
const CATEGORY_CONFIG: Record<KnowledgeCategory, { label: string; icon: React.ReactNode; color: string }> = {
  standard: { label: '标准知识', icon: <BookOutlined />, color: 'blue' },
  experience: { label: '经验知识', icon: <ExperimentOutlined />, color: 'green' },
  application: { label: '应用知识', icon: <AppstoreOutlined />, color: 'orange' },
  user: { label: '用户知识', icon: <UserOutlined />, color: 'purple' },
};

/** 标准颜色配置 */
const STANDARD_COLORS: Record<string, string> = {
  ISO9001: 'blue',
  ISO14001: 'green',
  ISO45001: 'orange',
};

/**
 * 知识库主页组件
 */
const KnowledgeBase: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // 状态
  const [loading, setLoading] = useState(false);
  const [knowledgeList, setKnowledgeList] = useState<KnowledgeItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [selectedCategory, setSelectedCategory] = useState<KnowledgeCategory | 'all'>(
    (searchParams.get('category') as KnowledgeCategory) || 'all'
  );
  const [selectedStandard, setSelectedStandard] = useState<string>(
    searchParams.get('standard') || ''
  );
  const [selectedIndustry, setSelectedIndustry] = useState<string>(
    searchParams.get('industry') || ''
  );

  // 下拉选项数据
  const [standards, setStandards] = useState<Array<{ code: string; name: string }>>([]);
  const [industries, setIndustries] = useState<Array<{ code: string; name: string }>>([]);
  const [categoryTree, setCategoryTree] = useState<KnowledgeCategoryTree[]>([]);

  // 加载下拉选项
  useEffect(() => {
    const loadOptions = async () => {
      try {
        const [standardsData, industriesData, treeData] = await Promise.all([
          getSupportedStandardsList(),
          getIndustryList(),
          getKnowledgeCategoryTree(),
        ]);
        setStandards(standardsData);
        setIndustries(industriesData);
        setCategoryTree(treeData);
      } catch (error) {
        console.error('加载选项失败:', error);
      }
    };
    loadOptions();
  }, []);

  // 加载知识列表
  const loadKnowledgeList = async () => {
    setLoading(true);
    try {
      const params: any = {
        page,
        pageSize,
      };
      if (selectedCategory !== 'all') {
        params.category = selectedCategory;
      }
      if (selectedStandard) {
        params.standard = selectedStandard;
      }
      if (selectedIndustry) {
        params.industry = selectedIndustry;
      }

      let result;
      if (searchQuery) {
        result = await searchKnowledge({
          query: searchQuery,
          ...params,
        });
      } else {
        result = await getKnowledgeList(params);
      }

      setKnowledgeList(result.items);
      setTotal(result.total);
    } catch (error) {
      message.error('加载知识列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledgeList();
  }, [page, pageSize, selectedCategory, selectedStandard, selectedIndustry]);

  // 搜索
  const handleSearch = (value: string) => {
    setSearchQuery(value);
    setPage(1);
    // 更新URL参数
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set('q', value);
    } else {
      params.delete('q');
    }
    setSearchParams(params);
    loadKnowledgeList();
  };

  // 分类点击
  const handleCategoryClick = (category: KnowledgeCategory | 'all') => {
    setSelectedCategory(category);
    setPage(1);
    const params = new URLSearchParams(searchParams);
    if (category === 'all') {
      params.delete('category');
    } else {
      params.set('category', category);
    }
    setSearchParams(params);
  };

  // 标准选择
  const handleStandardChange = (value: string) => {
    setSelectedStandard(value);
    setPage(1);
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set('standard', value);
    } else {
      params.delete('standard');
    }
    setSearchParams(params);
  };

  // 行业选择
  const handleIndustryChange = (value: string) => {
    setSelectedIndustry(value);
    setPage(1);
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set('industry', value);
    } else {
      params.delete('industry');
    }
    setSearchParams(params);
  };

  // 查看详情
  const handleViewDetail = (item: KnowledgeItem) => {
    if (item.category === 'standard') {
      navigate(`/knowledge/standard/${item.id}`);
    } else {
      navigate(`/knowledge/detail/${item.id}`);
    }
  };

  // 渲染分类菜单
  const renderCategoryMenu = () => {
    const menuItems = [
      {
        key: 'all',
        icon: <AppstoreOutlined />,
        label: '全部知识',
      },
      ...Object.entries(CATEGORY_CONFIG).map(([key, config]) => ({
        key,
        icon: config.icon,
        label: config.label,
      })),
    ];

    return (
      <Menu
        mode="inline"
        selectedKeys={[selectedCategory]}
        items={menuItems}
        onClick={({ key }) => handleCategoryClick(key as KnowledgeCategory | 'all')}
        style={{ borderRight: 0 }}
      />
    );
  };

  // 渲染知识项
  const renderKnowledgeItem = (item: KnowledgeItem) => {
    const categoryConfig = CATEGORY_CONFIG[item.category];
    return (
      <List.Item
        key={item.id}
        actions={[
          <Space key="actions">
            <Tooltip title="浏览次数">
              <Space size={4}>
                <HistoryOutlined style={{ color: '#999' }} />
                <Text type="secondary">{item.viewCount}</Text>
              </Space>
            </Tooltip>
            <Button
              type="link"
              icon={<RightOutlined />}
              onClick={() => handleViewDetail(item)}
            >
              查看
            </Button>
          </Space>,
        ]}
      >
        <List.Item.Meta
          title={
            <Space>
              <Text strong style={{ cursor: 'pointer' }} onClick={() => handleViewDetail(item)}>
                {item.title}
              </Text>
              {item.standard && (
                <Tag color={STANDARD_COLORS[item.standard] || 'default'}>
                  {item.standard}
                </Tag>
              )}
            </Space>
          }
          description={
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Paragraph
                ellipsis={{ rows: 2 }}
                style={{ marginBottom: 0, color: '#666' }}
              >
                {item.summary}
              </Paragraph>
              <Space size={4} wrap>
                <Tag icon={categoryConfig.icon} color={categoryConfig.color}>
                  {categoryConfig.label}
                </Tag>
                {item.industryName && (
                  <Tag color="cyan">{item.industryName}</Tag>
                )}
                {item.tags?.slice(0, 3).map((tag) => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Space>
            </Space>
          }
        />
      </List.Item>
    );
  };

  return (
    <div style={{ padding: 0 }}>
      {/* 面包屑 */}
      <Breadcrumb
        items={[
          { title: '首页', href: '/' },
          { title: '知识库' },
          ...(selectedCategory !== 'all'
            ? [{ title: CATEGORY_CONFIG[selectedCategory]?.label || selectedCategory }]
            : []),
        ]}
        style={{ marginBottom: 16 }}
      />

      <Layout style={{ background: '#fff', minHeight: 'calc(100vh - 200px)' }}>
        {/* 左侧分类导航 */}
        <Sider
          width={240}
          style={{
            background: '#fafafa',
            borderRight: '1px solid #f0f0f0',
          }}
        >
          <div style={{ padding: '16px 12px' }}>
            <Title level={5} style={{ marginBottom: 12 }}>
              <BookOutlined style={{ marginRight: 8 }} />
              知识分类
            </Title>
            {renderCategoryMenu()}
          </div>

          {/* 标准筛选 */}
          <div style={{ padding: '12px 16px', borderTop: '1px solid #f0f0f0' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              按标准筛选
            </Text>
            <Select
              placeholder="选择标准"
              allowClear
              style={{ width: '100%', marginTop: 8 }}
              value={selectedStandard || undefined}
              onChange={handleStandardChange}
            >
              {standards.map((s) => (
                <Option key={s.code} value={s.code}>
                  {s.name}
                </Option>
              ))}
            </Select>
          </div>

          {/* 行业筛选 */}
          <div style={{ padding: '12px 16px', borderTop: '1px solid #f0f0f0' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              按行业筛选
            </Text>
            <Select
              placeholder="选择行业"
              allowClear
              showSearch
              optionFilterProp="children"
              style={{ width: '100%', marginTop: 8 }}
              value={selectedIndustry || undefined}
              onChange={handleIndustryChange}
            >
              {industries.map((i) => (
                <Option key={i.code} value={i.code}>
                  {i.name}
                </Option>
              ))}
            </Select>
          </div>
        </Sider>

        {/* 右侧内容区 */}
        <Content style={{ padding: 16 }}>
          {/* 搜索栏 */}
          <Card style={{ marginBottom: 16 }}>
            <Space style={{ width: '100%' }} direction="vertical">
              <Search
                placeholder="搜索知识库内容..."
                allowClear
                enterButton="搜索"
                size="large"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onSearch={handleSearch}
              />
              <Space wrap>
                <Text type="secondary">热门搜索:</Text>
                {['质量目标', '风险管理', '内审', '管理评审', '不合格品'].map((keyword) => (
                  <Tag
                    key={keyword}
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleSearch(keyword)}
                  >
                    {keyword}
                  </Tag>
                ))}
              </Space>
            </Space>
          </Card>

          {/* 知识列表 */}
          <Card
            title={
              <Space>
                <FileTextOutlined />
                <span>
                  {selectedCategory === 'all'
                    ? '全部知识'
                    : CATEGORY_CONFIG[selectedCategory]?.label}
                </span>
                <Badge count={total} style={{ backgroundColor: '#1890ff' }} />
              </Space>
            }
          >
            <Spin spinning={loading}>
              {knowledgeList.length > 0 ? (
                <List
                  itemLayout="vertical"
                  dataSource={knowledgeList}
                  renderItem={renderKnowledgeItem}
                  pagination={{
                    current: page,
                    pageSize,
                    total,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total) => `共 ${total} 条`,
                    onChange: (p, ps) => {
                      setPage(p);
                      setPageSize(ps);
                    },
                  }}
                />
              ) : (
                <Empty
                  description={
                    searchQuery ? '未找到相关知识' : '暂无知识内容'
                  }
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
              )}
            </Spin>
          </Card>
        </Content>
      </Layout>
    </div>
  );
};

export default KnowledgeBase;
