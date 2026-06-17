import React, { useState, useEffect, useMemo } from 'react';
import { Input, Card, Tag, Badge, Space, message, Spin } from 'antd';
import {
  SearchOutlined,
  SafetyCertificateOutlined,
  ToolOutlined,
  DesktopOutlined,
  BuildOutlined,
  HomeOutlined,
  TeamOutlined,
  CheckCircleFilled,
} from '@ant-design/icons';
import { getIndustryConfigs, IndustryConfig } from '@/api';
import { useResponsive } from '@/hooks/useResponsive';

// ============ 类型定义 ============

/** 组件Props */
interface IndustrySelectorProps {
  /** 选中的行业代码 */
  value?: string;
  /** 选择变更回调 */
  onChange?: (code: string, industry: IndustryConfig) => void;
  /** 确认回调 */
  onConfirm?: (code: string, industry: IndustryConfig) => void;
  /** 是否显示确认按钮 */
  showConfirmButton?: boolean;
  /** 是否禁用 */
  disabled?: boolean;
  /** 自定义样式类名 */
  className?: string;
  /** 自定义样式 */
  style?: React.CSSProperties;
}

// ============ 行业图标映射 ============

/** 根据行业代码获取对应图标 */
const getIndustryIcon = (code: string): React.ReactNode => {
  const iconMap: Record<string, React.ReactNode> = {
    system_integration: <DesktopOutlined style={{ fontSize: 28 }} />,
    software_development: <DesktopOutlined style={{ fontSize: 28 }} />,
    construction: <BuildOutlined style={{ fontSize: 28 }} />,
    steel_structure: <BuildOutlined style={{ fontSize: 28 }} />,
    archive_digitalization: <DesktopOutlined style={{ fontSize: 28 }} />,
    intelligent_manufacturing: <ToolOutlined style={{ fontSize: 28 }} />,
    food_production: <SafetyCertificateOutlined style={{ fontSize: 28 }} />,
    electromechanical: <BuildOutlined style={{ fontSize: 28 }} />,
    intelligent_tech: <DesktopOutlined style={{ fontSize: 28 }} />,
    property_management: <HomeOutlined style={{ fontSize: 28 }} />,
    labor_dispatch: <TeamOutlined style={{ fontSize: 28 }} />,
  };
  return iconMap[code] || <ToolOutlined style={{ fontSize: 28 }} />;
};

/** 根据行业代码获取图标颜色 */
const getIndustryColor = (code: string): string => {
  const colorMap: Record<string, string> = {
    system_integration: '#1677ff',
    software_development: '#13c2c2',
    construction: '#fa8c16',
    steel_structure: '#a8071a',
    archive_digitalization: '#722ed1',
    intelligent_manufacturing: '#2f54eb',
    food_production: '#52c41a',
    electromechanical: '#eb2f96',
    intelligent_tech: '#1890ff',
    property_management: '#faad14',
    labor_dispatch: '#597ef7',
  };
  return colorMap[code] || '#1677ff';
};

// ============ 组件 ============

/**
 * 行业选择器组件
 *
 * 功能：
 * - 加载行业列表并以卡片网格形式展示
 * - 支持按行业名称/代码搜索过滤
 * - 每个行业卡片显示图标、名称、描述及特征标签
 * - 选中态：蓝色边框 + 浅蓝背景 + 阴影
 * - 响应式布局（PC端3列，移动端1列）
 */
const IndustrySelector: React.FC<IndustrySelectorProps> = ({
  value,
  onChange,
  onConfirm,
  showConfirmButton = false,
  disabled = false,
  className = '',
  style,
}) => {
  // ============ 状态 ============
  const [industries, setIndustries] = useState<IndustryConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedCode, setSelectedCode] = useState<string | undefined>(value);
  const { isMobile } = useResponsive();

  // ============ 初始化 ============

  useEffect(() => {
    setSelectedCode(value);
  }, [value]);

  /** 加载行业列表 */
  useEffect(() => {
    let cancelled = false;
    const loadIndustries = async () => {
      setLoading(true);
      try {
        const data = await getIndustryConfigs({ active_only: true });
        if (!cancelled) {
          setIndustries(data as unknown as IndustryConfig[]);
        }
      } catch (err) {
        if (!cancelled) {
          message.error('加载行业列表失败');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };
    loadIndustries();
    return () => {
      cancelled = true;
    };
  }, []);

  // ============ 过滤逻辑 ============

  /** 根据搜索文本过滤行业列表 */
  const filteredIndustries = useMemo(() => {
    if (!searchText.trim()) return industries;
    const keyword = searchText.trim().toLowerCase();
    return industries.filter(
      (item) =>
        item.industry_name.toLowerCase().includes(keyword) ||
        item.industry_code.toLowerCase().includes(keyword),
    );
  }, [industries, searchText]);

  // ============ 事件处理 ============

  /** 处理行业卡片点击 */
  const handleSelect = (industry: IndustryConfig) => {
    if (disabled) return;
    setSelectedCode(industry.industry_code);
    onChange?.(industry.industry_code, industry);
  };

  /** 处理确认按钮点击 */
  const handleConfirm = () => {
    if (!selectedCode) return;
    const selectedIndustry = industries.find((i) => i.industry_code === selectedCode);
    if (selectedIndustry) {
      onConfirm?.(selectedCode, selectedIndustry);
    }
  };

  /** 渲染行业特征标签 */
  const renderFeatureTags = (industry: IndustryConfig) => {
    const tags: Array<{ label: string; color: string }> = [];

    if (industry.has_design_development) {
      tags.push({ label: '设计开发', color: 'blue' });
    }
    if (industry.has_equipment_operations) {
      tags.push({ label: '设备操作', color: 'orange' });
    }
    if (industry.has_multi_projects) {
      tags.push({ label: '多项目', color: 'purple' });
    }
    if (industry.has_outsourcing) {
      tags.push({ label: '外包', color: 'cyan' });
    }
    if (industry.internal_audit_by_dept) {
      tags.push({ label: '按部门内审', color: 'geekblue' });
    }

    return tags;
  };

  // ============ 渲染 ============

  return (
    <Card
      className={className}
      title="选择行业类型"
      style={style}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {/* 搜索框 */}
        <Input
          prefix={<SearchOutlined />}
          placeholder="搜索行业名称或代码..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ maxWidth: 400 }}
        />

        {/* 加载状态 */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <Spin size="large" tip="加载行业列表..." />
          </div>
        ) : filteredIndustries.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            {searchText ? '未找到匹配的行业' : '暂无可用行业'}
          </div>
        ) : (
          <>
            {/* 行业卡片网格 */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: isMobile
                  ? '1fr'
                  : 'repeat(3, 1fr)',
                gap: 16,
              }}
            >
              {filteredIndustries.map((industry) => {
                const isSelected = selectedCode === industry.industry_code;
                const color = getIndustryColor(industry.industry_code);
                const featureTags = renderFeatureTags(industry);

                return (
                  <div
                    key={industry.industry_code}
                    onClick={() => handleSelect(industry)}
                    style={{
                      position: 'relative',
                      border: `2px solid ${isSelected ? '#1677ff' : '#f0f0f0'}`,
                      borderRadius: 8,
                      padding: 16,
                      cursor: disabled ? 'not-allowed' : 'pointer',
                      backgroundColor: isSelected ? '#e6f4ff' : '#fff',
                      transition: 'all 0.3s ease',
                      opacity: disabled ? 0.6 : 1,
                      boxShadow: isSelected
                        ? '0 2px 8px rgba(22, 119, 255, 0.25)'
                        : '0 1px 4px rgba(0, 0, 0, 0.06)',
                    }}
                  >
                    {/* 选中标记 */}
                    {isSelected && (
                      <div
                        style={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          color: '#1677ff',
                        }}
                      >
                        <CheckCircleFilled style={{ fontSize: 20 }} />
                      </div>
                    )}

                    {/* 特殊文件数量徽标 */}
                    {industry.special_file_count > 0 && (
                      <div
                        style={{
                          position: 'absolute',
                          top: 8,
                          right: isSelected ? 36 : 8,
                        }}
                      >
                        <Badge
                          count={industry.special_file_count}
                          size="small"
                          style={{ backgroundColor: color }}
                        />
                      </div>
                    )}

                    {/* 图标和名称 */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 10,
                        marginBottom: 8,
                      }}
                    >
                      <div style={{ color }}>{getIndustryIcon(industry.industry_code)}</div>
                      <span
                        style={{
                          fontSize: 16,
                          fontWeight: 600,
                          color: isSelected ? '#1677ff' : undefined,
                        }}
                      >
                        {industry.industry_name}
                      </span>
                    </div>

                    {/* 描述 */}
                    <div
                      style={{
                        fontSize: 13,
                        color: '#8c8c8c',
                        lineHeight: 1.6,
                        marginBottom: 12,
                        // 最多显示两行
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {industry.description}
                    </div>

                    {/* 特征标签 */}
                    {featureTags.length > 0 && (
                      <div style={{ borderTop: '1px solid #f5f5f5', paddingTop: 10 }}>
                        <Space wrap size={[4, 4]}>
                          {featureTags.map((tag) => (
                            <Tag
                              key={tag.label}
                              color={tag.color}
                              style={{ fontSize: 11, margin: 0 }}
                            >
                              {tag.label}
                            </Tag>
                          ))}
                        </Space>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* 确认按钮 */}
            {showConfirmButton && (
              <div
                style={{
                  textAlign: 'right',
                  paddingTop: 16,
                  borderTop: '1px solid #f0f0f0',
                }}
              >
                <button
                  type="button"
                  onClick={handleConfirm}
                  disabled={!selectedCode || disabled}
                  style={{
                    padding: '8px 32px',
                    fontSize: 14,
                    fontWeight: 500,
                    color: '#fff',
                    backgroundColor: selectedCode ? '#1677ff' : '#d9d9d9',
                    border: 'none',
                    borderRadius: 6,
                    cursor: selectedCode && !disabled ? 'pointer' : 'not-allowed',
                  }}
                >
                  确认选择
                </button>
              </div>
            )}
          </>
        )}
      </Space>
    </Card>
  );
};

export default IndustrySelector;
export type { IndustrySelectorProps };
