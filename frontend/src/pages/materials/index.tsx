import React, { useEffect, useState, useCallback } from 'react';
import {
  Card,
  Select,
  Button,
  Tag,
  Collapse,
  Empty,
  Space,
  Typography,
  Badge,
  Spin,
  message,
  List,
} from 'antd';
import {
  DownloadOutlined,
  FileTextOutlined,
  InboxOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import {
  getIndustries,
  getMaterialList,
  downloadTemplate,
} from '@/api';
import type {
  Industry,
  MaterialItem,
  MaterialListResponse,
} from '@/api';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

/** 分类图标映射 */
const categoryIcons: Record<string, React.ReactNode> = {
  基础材料: <FileTextOutlined />,
  业务材料: <AppstoreOutlined />,
  场地材料: <AppstoreOutlined />,
  人员资质: <FileTextOutlined />,
  体系运行: <FileTextOutlined />,
};

/** 分类默认图标 */
const defaultCategoryIcon = <FileTextOutlined />;

/**
 * 模板下载中心页面
 * 支持按行业筛选材料清单，下载对应模板文件
 * 响应式布局：PC端使用antd组件，移动端适配小屏
 */
const MaterialsPage: React.FC = () => {
  const { isMobile } = useResponsive();

  // 状态管理
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [selectedIndustry, setSelectedIndustry] = useState<string | undefined>(undefined);
  const [materialData, setMaterialData] = useState<MaterialListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [industriesLoading, setIndustriesLoading] = useState(false);

  /** 加载行业列表 */
  useEffect(() => {
    const fetchIndustries = async () => {
      setIndustriesLoading(true);
      try {
        const data = await getIndustries();
        setIndustries(data as unknown as Industry[]);
      } catch {
        message.error('获取行业列表失败，请稍后重试');
      } finally {
        setIndustriesLoading(false);
      }
    };
    fetchIndustries();
  }, []);

  /** 加载材料清单 */
  const fetchMaterials = useCallback(async (industryCode: string) => {
    setLoading(true);
    try {
      const data = await getMaterialList(industryCode);
      setMaterialData(data as unknown as MaterialListResponse);
    } catch {
      message.error('获取材料清单失败，请稍后重试');
      setMaterialData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  /** 行业选择变更 */
  const handleIndustryChange = (value: string) => {
    setSelectedIndustry(value);
    if (value) {
      fetchMaterials(value);
    } else {
      setMaterialData(null);
    }
  };

  /** 下载单个模板 */
  const handleDownload = (materialName: string) => {
    downloadTemplate(materialName);
    message.success(`正在下载：${materialName}`);
  };

  /** 批量下载所有有模板的材料 */
  const handleBatchDownload = () => {
    if (!materialData) return;

    const allMaterials = [
      ...Object.values(materialData.materials.common).flat(),
      ...Object.values(materialData.materials.industry_specific).flat(),
    ];

    const downloadableMaterials = allMaterials.filter((m) => m.template_available);

    if (downloadableMaterials.length === 0) {
      message.warning('当前行业没有可下载的模板');
      return;
    }

    downloadableMaterials.forEach((m, index) => {
      setTimeout(() => {
        downloadTemplate(m.name);
      }, index * 500); // 间隔500ms避免浏览器拦截
    });

    message.success(`正在下载 ${downloadableMaterials.length} 个模板文件`);
  };

  /** 计算可下载模板总数 */
  const getDownloadableCount = (): number => {
    if (!materialData) return 0;
    const allMaterials = [
      ...Object.values(materialData.materials.common).flat(),
      ...Object.values(materialData.materials.industry_specific).flat(),
    ];
    return allMaterials.filter((m) => m.template_available).length;
  };

  /** 渲染单个材料项 */
  const renderMaterialItem = (item: MaterialItem) => (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: isMobile ? '10px 0' : '12px 16px',
        borderBottom: '1px solid #f0f0f0',
        gap: 8,
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          {item.required && (
            <span style={{ color: '#ff4d4f', fontSize: 14 }}>*</span>
          )}
          <Text strong style={{ fontSize: isMobile ? 14 : 15 }}>
            {item.name}
          </Text>
          <Tag color={item.required ? 'error' : 'blue'} style={{ marginLeft: 4 }}>
            {item.required ? '必需' : '可选'}
          </Tag>
        </div>
        {item.description && (
          <Paragraph
            type="secondary"
            style={{
              margin: '4px 0 0',
              fontSize: isMobile ? 12 : 13,
              lineHeight: 1.5,
            }}
            ellipsis={{ rows: 2 }}
          >
            {item.description}
          </Paragraph>
        )}
      </div>
      <div style={{ flexShrink: 0, marginLeft: 8 }}>
        {item.template_available ? (
          <Button
            type="primary"
            size={isMobile ? 'small' : 'middle'}
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(item.name)}
          >
            {isMobile ? '下载' : '下载模板'}
          </Button>
        ) : (
          <Text type="secondary" style={{ fontSize: isMobile ? 12 : 13 }}>
            需自行提供原件
          </Text>
        )}
      </div>
    </div>
  );

  /** 渲染材料分类面板 */
  const renderCategoryPanel = (categoryName: string, items: MaterialItem[]) => {
    if (!items || items.length === 0) return null;

    const icon = categoryIcons[categoryName] || defaultCategoryIcon;
    const requiredCount = items.filter((i) => i.required).length;
    const templateCount = items.filter((i) => i.template_available).length;

    return (
      <Panel
        key={categoryName}
        header={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ color: '#1677ff' }}>{icon}</span>
            <Text strong>{categoryName}</Text>
            <Badge
              count={items.length}
              style={{ backgroundColor: '#1677ff' }}
              overflowCount={99}
            />
            {requiredCount > 0 && (
              <Tag color="error" style={{ marginLeft: 4 }}>
                {requiredCount}项必需
              </Tag>
            )}
            {templateCount > 0 && (
              <Tag color="green" style={{ marginLeft: 4 }}>
                {templateCount}个模板
              </Tag>
            )}
          </div>
        }
      >
        {items.map((item) => (
          <div key={item.name}>{renderMaterialItem(item)}</div>
        ))}
      </Panel>
    );
  };

  /** 渲染空状态 */
  const renderEmpty = () => (
    <Empty
      image={<InboxOutlined style={{ fontSize: 64, color: '#bfbfbf' }} />}
      description={
        <Space direction="vertical" size={4}>
          <Text type="secondary" style={{ fontSize: 16 }}>
            {selectedIndustry ? '该行业暂无材料清单' : '请先选择行业'}
          </Text>
          <Text type="secondary" style={{ fontSize: 13 }}>
            {selectedIndustry
              ? '请联系管理员添加相关材料信息'
              : '选择您的行业后，将展示对应的认证材料清单'}
          </Text>
        </Space>
      }
    />
  );

  /* ==================== 页面渲染 ==================== */
  return (
    <div style={{ maxWidth: isMobile ? '100%' : 960, margin: '0 auto' }}>
      {/* 页面标题区域 */}
      <div
        style={{
          textAlign: 'center',
          marginBottom: isMobile ? 16 : 24,
        }}
      >
        <Title level={isMobile ? 4 : 3} style={{ marginBottom: 4 }}>
          模板下载中心
        </Title>
        <Paragraph type="secondary" style={{ marginBottom: 0, fontSize: isMobile ? 13 : 15 }}>
          选择您的行业，下载所需材料的空白模板
        </Paragraph>
      </div>

      {/* 行业选择区域 */}
      <Card
        size={isMobile ? 'small' : 'default'}
        style={{ marginBottom: isMobile ? 12 : 16 }}
        bodyStyle={{ padding: isMobile ? '12px 16px' : '16px 24px' }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: isMobile ? 12 : 16,
            flexWrap: 'wrap',
          }}
        >
          <Text strong style={{ whiteSpace: 'nowrap', fontSize: isMobile ? 14 : 15 }}>
            选择行业：
          </Text>
          <Select
            showSearch
            allowClear
            placeholder="请选择您的行业"
            style={{ width: isMobile ? '100%' : 320, flex: isMobile ? 1 : undefined }}
            value={selectedIndustry}
            onChange={handleIndustryChange}
            loading={industriesLoading}
            options={industries.map((item) => ({
              value: item.code,
              label: item.name,
              title: item.description || item.name,
            }))}
            filterOption={(input, option) =>
              (option?.label as string)?.toLowerCase().includes(input.toLowerCase()) ?? false
            }
          />
          {materialData && (
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleBatchDownload}
              size={isMobile ? 'middle' : 'large'}
              style={isMobile ? { width: '100%', marginTop: 8 } : {}}
            >
              批量下载全部模板
              {getDownloadableCount() > 0 && (
                <Badge
                  count={getDownloadableCount()}
                  size="small"
                  style={{ marginLeft: 8 }}
                />
              )}
            </Button>
          )}
        </div>
      </Card>

      {/* 材料清单区域 */}
      <Spin spinning={loading} tip="加载材料清单中...">
        {!materialData ? (
          renderEmpty()
        ) : (
          <>
            {/* 通用材料 */}
            {Object.keys(materialData.materials.common).length > 0 && (
              <Card
                title={
                  <Space>
                    <FileTextOutlined />
                    <Text strong>通用材料</Text>
                    <Text type="secondary" style={{ fontSize: 13 }}>
                      （所有行业通用）
                    </Text>
                  </Space>
                }
                size={isMobile ? 'small' : 'default'}
                style={{ marginBottom: isMobile ? 12 : 16 }}
                bodyStyle={{ padding: 0 }}
              >
                <Collapse
                  defaultActiveKey={Object.keys(materialData.materials.common)}
                  ghost
                  expandIconPosition="start"
                >
                  {Object.entries(materialData.materials.common).map(
                    ([category, items]) => renderCategoryPanel(category, items),
                  )}
                </Collapse>
              </Card>
            )}

            {/* 行业专属材料 */}
            {Object.keys(materialData.materials.industry_specific).length > 0 && (
              <Card
                title={
                  <Space>
                    <AppstoreOutlined />
                    <Text strong>
                      {materialData.industry_name} - 专属材料
                    </Text>
                    <Text type="secondary" style={{ fontSize: 13 }}>
                      （行业特定要求）
                    </Text>
                  </Space>
                }
                size={isMobile ? 'small' : 'default'}
                style={{ marginBottom: isMobile ? 12 : 16 }}
                bodyStyle={{ padding: 0 }}
              >
                <Collapse
                  defaultActiveKey={Object.keys(materialData.materials.industry_specific)}
                  ghost
                  expandIconPosition="start"
                >
                  {Object.entries(materialData.materials.industry_specific).map(
                    ([category, items]) => renderCategoryPanel(category, items),
                  )}
                </Collapse>
              </Card>
            )}

            {/* 如果两个区域都为空 */}
            {Object.keys(materialData.materials.common).length === 0 &&
              Object.keys(materialData.materials.industry_specific).length === 0 && (
                renderEmpty()
              )}
          </>
        )}
      </Spin>

      {/* 底部提示 */}
      {materialData && (
        <div
          style={{
            textAlign: 'center',
            padding: isMobile ? '12px 0' : '16px 0',
          }}
        >
          <Paragraph type="secondary" style={{ fontSize: isMobile ? 12 : 13, marginBottom: 0 }}>
            提示：标有红色星号（*）的材料为必需项，请确保准备齐全。如有疑问请联系咨询师。
          </Paragraph>
        </div>
      )}
    </div>
  );
};

export default MaterialsPage;
