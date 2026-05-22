import React, { useState, useEffect, useCallback } from 'react';
import { Card, Radio, Tag, Typography, Space, Spin, Alert, Tooltip } from 'antd';
import {
  FileTextOutlined,
  AuditOutlined,
  SyncOutlined,
  RetweetOutlined,
  InfoCircleOutlined,
  CheckCircleFilled,
} from '@ant-design/icons';

const { Text, Title, Paragraph } = Typography;

// ============ 类型定义 ============

/** 认证阶段类型 */
export type CertStageType = 'initial' | 'surveillance_1' | 'surveillance_2' | 'recertification';

/** 认证阶段信息 */
export interface CertStageOption {
  key: CertStageType;
  name: string;
  description: string;
  year: string;
  icon: React.ReactNode;
  color: string;
  /** 需要生成的文件范围 */
  documentScope: string[];
  /** 需要更新的文件范围 */
  updateScope: string[];
  /** 是否需要上传旧版文件 */
  requireOldFiles: boolean;
}

/** 文件范围信息 */
export interface DocumentScopeInfo {
  stage: CertStageType;
  /** 需要生成的文件列表 */
  generateFiles: Array<{
    category: string;
    files: string[];
  }>;
  /** 需要更新的文件列表 */
  updateFiles: Array<{
    category: string;
    files: string[];
  }>;
  /** 不需要处理的文件列表 */
  skipFiles: string[];
}

/** 组件Props */
interface CertStageSelectorProps {
  /** 当前选中的阶段 */
  value?: CertStageType;
  /** 选择变更回调 */
  onChange?: (stage: CertStageType, stageInfo: CertStageOption) => void;
  /** 确认回调 */
  onConfirm?: (stage: CertStageType, stageInfo: CertStageOption) => void;
  /** 是否显示确认按钮 */
  showConfirmButton?: boolean;
  /** 确认按钮文字 */
  confirmButtonText?: string;
  /** 是否禁用 */
  disabled?: boolean;
  /** 自定义样式 */
  className?: string;
  /** 企业信息（用于AI建议阶段） */
  companyInfo?: {
    companyName?: string;
    certStartDate?: string;
    lastAuditDate?: string;
    certCycle?: number;
  };
  /** 是否显示文件范围详情 */
  showScopeDetail?: boolean;
}

// ============ 阶段配置 ============

/** 获取阶段选项列表 */
const getStageOptions = (): CertStageOption[] => [
  {
    key: 'initial',
    name: '初次认证',
    description: '企业首次申请认证，需要建立完整的质量管理体系文件',
    year: '第1年',
    icon: <FileTextOutlined style={{ fontSize: 28 }} />,
    color: '#1677ff',
    documentScope: [
      '质量手册',
      '程序文件（全套）',
      '作业指导书',
      '质量记录表单',
      '管理评审报告',
      '内审报告',
      '不符合项报告',
      '纠正措施报告',
    ],
    updateScope: [],
    requireOldFiles: false,
  },
  {
    key: 'surveillance_1',
    name: '监督审核1',
    description: '初次认证后第2年的监督审核，检查体系运行的有效性',
    year: '第2年',
    icon: <AuditOutlined style={{ fontSize: 28 }} />,
    color: '#52c41a',
    documentScope: [
      '管理评审报告',
      '内审报告',
      '不符合项报告',
      '纠正措施报告',
    ],
    updateScope: [
      '质量手册（换版页）',
      '程序文件（修订记录）',
      '质量目标完成情况统计',
    ],
    requireOldFiles: true,
  },
  {
    key: 'surveillance_2',
    name: '监督审核2',
    description: '初次认证后第3年的监督审核，重点关注持续改进',
    year: '第3年',
    icon: <SyncOutlined style={{ fontSize: 28 }} />,
    color: '#faad14',
    documentScope: [
      '管理评审报告',
      '内审报告',
      '不符合项报告',
      '纠正措施报告',
      '持续改进报告',
    ],
    updateScope: [
      '质量手册（换版页）',
      '程序文件（修订记录）',
      '质量目标完成情况统计',
      '上年度不符合项关闭情况',
    ],
    requireOldFiles: true,
  },
  {
    key: 'recertification',
    name: '再认证',
    description: '认证周期到期前的再认证审核，全面评估体系运行情况',
    year: '第4年',
    icon: <RetweetOutlined style={{ fontSize: 28 }} />,
    color: '#722ed1',
    documentScope: [
      '质量手册（全面换版）',
      '程序文件（全面换版）',
      '管理评审报告',
      '内审报告',
      '不符合项报告',
      '纠正措施报告',
      '三年体系运行总结',
    ],
    updateScope: [
      '作业指导书（修订）',
      '质量记录表单（更新）',
      '组织架构调整文件',
    ],
    requireOldFiles: true,
  },
];

// ============ 组件 ============

/**
 * 认证阶段选择组件
 *
 * 功能：
 * - 4个阶段卡片：初次认证、监督审核1、监督审核2、再认证
 * - 每个卡片显示：阶段名称、说明、需要生成/更新的文件范围
 * - 选中状态高亮
 * - 支持两处调用：创建项目时、输入企业信息后
 */
const CertStageSelector: React.FC<CertStageSelectorProps> = ({
  value,
  onChange,
  onConfirm,
  showConfirmButton = false,
  confirmButtonText = '确认选择',
  disabled = false,
  className = '',
  companyInfo,
  showScopeDetail = true,
}) => {
  // ============ 状态 ============
  const [selectedStage, setSelectedStage] = useState<CertStageType | undefined>(value);
  const [stageOptions] = useState<CertStageOption[]>(getStageOptions);
  const [loading, setLoading] = useState(false);
  const [suggestedStage, setSuggestedStage] = useState<CertStageType | null>(null);
  const [expandedStage, setExpandedStage] = useState<CertStageType | null>(null);

  // ============ 初始化 ============

  useEffect(() => {
    setSelectedStage(value);
  }, [value]);

  // ============ 事件处理 ============

  /** 处理阶段选择 */
  const handleStageChange = useCallback(
    (stageKey: CertStageType) => {
      if (disabled) return;
      setSelectedStage(stageKey);
      const stageInfo = stageOptions.find((s) => s.key === stageKey);
      if (stageInfo) {
        onChange?.(stageKey, stageInfo);
      }
    },
    [disabled, stageOptions, onChange],
  );

  /** 确认选择 */
  const handleConfirm = useCallback(() => {
    if (!selectedStage) return;
    const stageInfo = stageOptions.find((s) => s.key === selectedStage);
    if (stageInfo) {
      onConfirm?.(selectedStage, stageInfo);
    }
  }, [selectedStage, stageOptions, onConfirm]);

  /** 切换展开/收起文件范围 */
  const toggleExpand = useCallback((stageKey: CertStageType, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedStage((prev) => (prev === stageKey ? null : stageKey));
  }, []);

  // ============ 渲染 ============

  /** 渲染文件范围标签 */
  const renderScopeTags = (files: string[], color: string) => {
    if (files.length === 0) {
      return <Text type="secondary" style={{ fontSize: 12 }}>无</Text>;
    }
    const displayFiles = expandedStage ? files : files.slice(0, 4);
    const hasMore = files.length > 4;

    return (
      <Space wrap size={[4, 4]}>
        {displayFiles.map((file, index) => (
          <Tag key={index} color={color} style={{ fontSize: 11, margin: 0 }}>
            {file}
          </Tag>
        ))}
        {hasMore && !expandedStage && (
          <Tooltip title={files.slice(4).join('、')}>
            <Tag style={{ fontSize: 11, margin: 0, cursor: 'pointer' }}>
              +{files.length - 4} 项
            </Tag>
          </Tooltip>
        )}
      </Space>
    );
  };

  return (
    <Card
      className={className}
      title="选择认证阶段"
      extra={
        suggestedStage && (
          <Tag color="orange" style={{ fontSize: 12 }}>
            <InfoCircleOutlined /> AI建议：{stageOptions.find((s) => s.key === suggestedStage)?.name}
          </Tag>
        )
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        {/* 阶段卡片网格 */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: 16,
          }}
        >
          {stageOptions.map((stage) => {
            const isSelected = selectedStage === stage.key;
            const isSuggested = suggestedStage === stage.key;

            return (
              <div
                key={stage.key}
                onClick={() => handleStageChange(stage.key)}
                style={{
                  position: 'relative',
                  border: `2px solid ${isSelected ? stage.color : '#f0f0f0'}`,
                  borderRadius: 8,
                  padding: 16,
                  cursor: disabled ? 'not-allowed' : 'pointer',
                  backgroundColor: isSelected ? `${stage.color}08` : '#fff',
                  transition: 'all 0.3s ease',
                  opacity: disabled ? 0.6 : 1,
                  boxShadow: isSelected ? `0 2px 8px ${stage.color}30` : '0 1px 4px rgba(0,0,0,0.06)',
                }}
              >
                {/* 选中标记 */}
                {isSelected && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      color: stage.color,
                    }}
                  >
                    <CheckCircleFilled style={{ fontSize: 20 }} />
                  </div>
                )}

                {/* AI建议标记 */}
                {isSuggested && !isSelected && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                    }}
                  >
                    <Tag color="orange" style={{ fontSize: 11 }}>推荐</Tag>
                  </div>
                )}

                {/* 年份标签 */}
                <Tag
                  color={stage.color}
                  style={{
                    marginBottom: 8,
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                >
                  {stage.year}
                </Tag>

                {/* 图标和名称 */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                  <div style={{ color: stage.color }}>{stage.icon}</div>
                  <Title level={5} style={{ margin: 0, color: isSelected ? stage.color : undefined }}>
                    {stage.name}
                  </Title>
                </div>

                {/* 说明 */}
                <Paragraph
                  type="secondary"
                  style={{ fontSize: 13, marginBottom: 12, lineHeight: 1.6 }}
                >
                  {stage.description}
                </Paragraph>

                {/* 文件范围 */}
                {showScopeDetail && (
                  <div style={{ borderTop: '1px solid #f5f5f5', paddingTop: 10 }}>
                    {/* 需要生成的文件 */}
                    <div style={{ marginBottom: 8 }}>
                      <Text
                        strong
                        style={{ fontSize: 12, color: stage.color, display: 'block', marginBottom: 4 }}
                      >
                        需要生成：
                      </Text>
                      {renderScopeTags(stage.documentScope, stage.color)}
                    </div>

                    {/* 需要更新的文件 */}
                    {stage.updateScope.length > 0 && (
                      <div>
                        <Text
                          strong
                          style={{ fontSize: 12, color: '#8c8c8c', display: 'block', marginBottom: 4 }}
                        >
                          需要更新：
                        </Text>
                        {renderScopeTags(stage.updateScope, 'default')}
                      </div>
                    )}

                    {/* 是否需要上传旧版文件 */}
                    {stage.requireOldFiles && (
                      <div style={{ marginTop: 8 }}>
                        <Tag color="warning" style={{ fontSize: 11 }}>
                          需要上传旧版体系文件
                        </Tag>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* 确认按钮 */}
        {showConfirmButton && (
          <div style={{ textAlign: 'right', paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
            <button
              type="button"
              onClick={handleConfirm}
              disabled={!selectedStage || disabled}
              style={{
                padding: '8px 32px',
                fontSize: 14,
                fontWeight: 500,
                color: '#fff',
                backgroundColor: selectedStage ? '#1677ff' : '#d9d9d9',
                border: 'none',
                borderRadius: 6,
                cursor: selectedStage && !disabled ? 'pointer' : 'not-allowed',
              }}
            >
              {confirmButtonText}
            </button>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default CertStageSelector;
export type { CertStageSelectorProps, CertStageOption, DocumentScopeInfo };