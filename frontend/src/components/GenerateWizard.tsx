import React, { useState, useEffect, useCallback } from 'react';
import {
  Modal,
  Steps,
  Card,
  Checkbox,
  Button,
  Space,
  Table,
  Progress,
  Tag,
  Alert,
  Empty,
  Spin,
  message,
  Typography,
  Divider,
  Collapse,
  Tooltip,
} from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import {
  getSupportedLevels,
  getAvailableTemplates,
  generateByLevel,
  generateAllDocuments,
  generateBatchDocuments,
  getGenerateTaskStatus,
} from '@/api';
import type { DocumentInfo, GenerateStatus, GenerateOptions } from '@/api';

const { Text, Title } = Typography;
const { Panel } = Collapse;

/** 文档层级信息 */
interface LevelInfo {
  level: number;
  name: string;
  description: string;
  document_count: number;
}

/** 模板信息 */
interface TemplateInfo {
  template_id: string;
  name: string;
  level: number;
  category: string;
  standard?: string;
  description?: string;
}

/** 生成向导组件属性 */
interface GenerateWizardProps {
  /** 是否显示 */
  visible: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 项目ID */
  projectId: string;
  /** 生成完成回调 */
  onGenerateComplete?: (documents: DocumentInfo[]) => void;
}

/** 步骤1：选择文档层级 */
const StepSelectLevel: React.FC<{
  levels: LevelInfo[];
  selectedLevels: number[];
  onChange: (levels: number[]) => void;
  loading: boolean;
}> = ({ levels, selectedLevels, onChange, loading }) => {
  const handleSelectAll = () => {
    onChange(levels.map((l) => l.level));
  };

  const handleClearAll = () => {
    onChange([]);
  };

  const handleToggle = (level: number, checked: boolean) => {
    if (checked) {
      onChange([...selectedLevels, level].sort());
    } else {
      onChange(selectedLevels.filter((l) => l !== level));
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <Spin />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text>请选择要生成的文档层级：</Text>
        <Space>
          <Button size="small" onClick={handleSelectAll}>
            全选
          </Button>
          <Button size="small" onClick={handleClearAll}>
            清空
          </Button>
        </Space>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
        {levels.map((levelInfo) => (
          <Card
            key={levelInfo.level}
            size="small"
            hoverable
            style={{
              borderColor: selectedLevels.includes(levelInfo.level) ? '#1677ff' : undefined,
              backgroundColor: selectedLevels.includes(levelInfo.level) ? '#f0f7ff' : undefined,
            }}
            onClick={() => handleToggle(levelInfo.level, !selectedLevels.includes(levelInfo.level))}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <Checkbox
                checked={selectedLevels.includes(levelInfo.level)}
                onChange={(e) => handleToggle(levelInfo.level, e.target.checked)}
              />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500, marginBottom: 4 }}>
                  {levelInfo.level}级 - {levelInfo.name}
                </div>
                <div style={{ fontSize: 12, color: '#666', marginBottom: 4 }}>
                  {levelInfo.description}
                </div>
                <Tag color="blue">{levelInfo.document_count} 个文档</Tag>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {selectedLevels.length > 0 && (
        <Alert
          type="info"
          showIcon
          style={{ marginTop: 16 }}
          message={`已选择 ${selectedLevels.length} 个层级，预计生成 ${levels
            .filter((l) => selectedLevels.includes(l.level))
            .reduce((sum, l) => sum + l.document_count, 0)} 个文档`}
        />
      )}
    </div>
  );
};

/** 步骤2：选择标准 */
const StepSelectStandard: React.FC<{
  selectedStandards: string[];
  onChange: (standards: string[]) => void;
}> = ({ selectedStandards, onChange }) => {
  const standards = [
    {
      code: 'ISO9001',
      name: 'ISO 9001 质量管理体系',
      description: '适用于需要证实其具有稳定提供满足顾客要求及适用法律法规要求的产品和服务的能力的组织',
      color: 'blue',
    },
    {
      code: 'ISO14001',
      name: 'ISO 14001 环境管理体系',
      description: '适用于需要管理其环境责任的组织，包括环境因素识别、合规义务、环境目标等',
      color: 'green',
    },
    {
      code: 'ISO45001',
      name: 'ISO 45001 职业健康安全管理体系',
      description: '适用于需要管理职业健康安全风险的组织，包括危险源识别、风险控制、健康监护等',
      color: 'orange',
    },
  ];

  const handleToggle = (code: string, checked: boolean) => {
    if (checked) {
      onChange([...selectedStandards, code]);
    } else {
      onChange(selectedStandards.filter((s) => s !== code));
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Text>请选择适用的管理体系标准（可多选）：</Text>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(1, 1fr)', gap: 12 }}>
        {standards.map((standard) => (
          <Card
            key={standard.code}
            size="small"
            hoverable
            style={{
              borderColor: selectedStandards.includes(standard.code) ? '#1677ff' : undefined,
              backgroundColor: selectedStandards.includes(standard.code) ? '#f0f7ff' : undefined,
            }}
            onClick={() => handleToggle(standard.code, !selectedStandards.includes(standard.code))}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <Checkbox
                checked={selectedStandards.includes(standard.code)}
                onChange={(e) => handleToggle(standard.code, e.target.checked)}
              />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500, marginBottom: 4 }}>
                  <Tag color={standard.color}>{standard.code}</Tag>
                  {standard.name}
                </div>
                <div style={{ fontSize: 12, color: '#666' }}>{standard.description}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Alert
        type="info"
        showIcon
        style={{ marginTop: 16 }}
        message="提示：选择多个标准将生成整合型的管理体系文件"
      />
    </div>
  );
};

/** 步骤3：预览文档列表 */
const StepPreview: React.FC<{
  templates: TemplateInfo[];
  selectedTemplates: string[];
  onToggleTemplate: (template_id: string, checked: boolean) => void;
  loading: boolean;
}> = ({ templates, selectedTemplates, onToggleTemplate, loading }) => {
  const [expandedCategories, setExpandedCategories] = useState<string[]>([]);

  // 按层级和类别分组
  const groupedTemplates = templates.reduce(
    (acc, template) => {
      const key = `${template.level}-${template.category}`;
      if (!acc[key]) {
        acc[key] = {
          level: template.level,
          category: template.category,
          templates: [],
        };
      }
      acc[key].templates.push(template);
      return acc;
    },
    {} as Record<string, { level: number; category: string; templates: TemplateInfo[] }>,
  );

  const levelNames: Record<number, string> = {
    1: '一级文件',
    2: '二级文件',
    3: '三级文件',
    4: '四级文件',
  };

  const handleSelectAll = () => {
    templates.forEach((t) => {
      if (!selectedTemplates.includes(t.template_id)) {
        onToggleTemplate(t.template_id, true);
      }
    });
  };

  const handleClearAll = () => {
    selectedTemplates.forEach((id) => onToggleTemplate(id, false));
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <Spin tip="正在加载模板列表..." />
      </div>
    );
  }

  if (templates.length === 0) {
    return <Empty description="没有可用的模板" />;
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Text strong>将要生成的文档列表：</Text>
          <Tag color="blue">{selectedTemplates.length} / {templates.length} 个文档</Tag>
        </Space>
        <Space>
          <Button size="small" onClick={handleSelectAll}>
            全选
          </Button>
          <Button size="small" onClick={handleClearAll}>
            清空
          </Button>
        </Space>
      </div>

      <div style={{ maxHeight: 400, overflow: 'auto' }}>
        <Collapse
          activeKey={expandedCategories}
          onChange={(keys) => setExpandedCategories(keys as string[])}
        >
          {Object.entries(groupedTemplates).map(([key, group]) => (
            <Panel
              key={key}
              header={
                <Space>
                  <Tag color="blue">{levelNames[group.level]}</Tag>
                  <Text>{group.category}</Text>
                  <Text type="secondary">({group.templates.length} 个文档)</Text>
                </Space>
              }
            >
              <Table
                size="small"
                dataSource={group.templates}
                rowKey="template_id"
                pagination={false}
                columns={[
                  {
                    title: '选择',
                    width: 60,
                    render: (_, record) => (
                      <Checkbox
                        checked={selectedTemplates.includes(record.template_id)}
                        onChange={(e) => onToggleTemplate(record.template_id, e.target.checked)}
                      />
                    ),
                  },
                  {
                    title: '文档名称',
                    dataIndex: 'name',
                    render: (text, record) => (
                      <Space>
                        <FileTextOutlined />
                        <span>{text}</span>
                        {record.standard && <Tag color="green">{record.standard}</Tag>}
                      </Space>
                    ),
                  },
                  {
                    title: '说明',
                    dataIndex: 'description',
                    width: 200,
                    render: (text) => (
                      <Tooltip title={text}>
                        <Text type="secondary" ellipsis style={{ maxWidth: 180 }}>
                          {text || '-'}
                        </Text>
                      </Tooltip>
                    ),
                  },
                ]}
              />
            </Panel>
          ))}
        </Collapse>
      </div>
    </div>
  );
};

/** 步骤4：生成进度 */
const StepProgress: React.FC<{
  status: GenerateStatus | null;
  isGenerating: boolean;
}> = ({ status, isGenerating }) => {
  const getStatusIcon = () => {
    if (!status) return <LoadingOutlined spin style={{ fontSize: 48, color: '#1677ff' }} />;
    
    switch (status.status) {
      case 'pending':
        return <LoadingOutlined spin style={{ fontSize: 48, color: '#1677ff' }} />;
      case 'processing':
        return <LoadingOutlined spin style={{ fontSize: 48, color: '#1677ff' }} />;
      case 'completed':
        return <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ fontSize: 48, color: '#ff4d4f' }} />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    if (!status) return '准备中...';
    
    switch (status.status) {
      case 'pending':
        return '等待生成...';
      case 'processing':
        return '正在生成文档...';
      case 'completed':
        return '生成完成';
      case 'failed':
        return '生成失败';
      default:
        return '准备中...';
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '20px 0' }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>{getStatusIcon()}</div>
      <div style={{ fontSize: 18, marginBottom: 8 }}>{getStatusText()}</div>

      {status && (
        <>
          <Progress
            percent={status.progress}
            status={status.status === 'failed' ? 'exception' : undefined}
            style={{ marginBottom: 16, maxWidth: 400, margin: '0 auto' }}
          />

          {status.status === 'processing' && (
            <Text type="secondary">
              已生成 {status.generated_documents.length} / {status.total_documents} 个文档
            </Text>
          )}

          {status.status === 'completed' && (
            <div style={{ marginTop: 16 }}>
              <Text type="success">成功生成 {status.generated_documents.length} 个文档</Text>
            </div>
          )}

          {status.status === 'failed' && status.errors.length > 0 && (
            <div style={{ marginTop: 16, textAlign: 'left', maxWidth: 400, margin: '16px auto' }}>
              <Alert
                type="error"
                message="部分文档生成失败"
                description={
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {status.errors.slice(0, 5).map((err, idx) => (
                      <li key={idx}>
                        {err.document_name}: {err.error}
                      </li>
                    ))}
                    {status.errors.length > 5 && (
                      <li>...还有 {status.errors.length - 5} 个错误</li>
                    )}
                  </ul>
                }
              />
            </div>
          )}
        </>
      )}
    </div>
  );
};

/**
 * 文档生成向导组件
 * 支持按层级、按标准批量生成文档
 */
const GenerateWizard: React.FC<GenerateWizardProps> = ({
  visible,
  onClose,
  projectId,
  onGenerateComplete,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [levels, setLevels] = useState<LevelInfo[]>([]);
  const [templates, setTemplates] = useState<TemplateInfo[]>([]);
  const [selectedLevels, setSelectedLevels] = useState<number[]>([1, 2, 3, 4]);
  const [selectedStandards, setSelectedStandards] = useState<string[]>(['ISO9001']);
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>([]);
  const [generateStatus, setGenerateStatus] = useState<GenerateStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  // 加载层级信息
  useEffect(() => {
    if (visible) {
      loadLevels();
    }
  }, [visible]);

  // 当层级或标准变化时，加载模板
  useEffect(() => {
    if (visible && currentStep === 2) {
      loadTemplates();
    }
  }, [visible, currentStep, selectedLevels, selectedStandards]);

  const loadLevels = async () => {
    setLoading(true);
    try {
      const data = await getSupportedLevels();
      setLevels(
        data.map((item) => ({
          level: item.level,
          name: item.name,
          description: item.description,
          document_count: item.document_count,
        })),
      );
    } catch (error) {
      message.error('加载层级信息失败');
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    setLoading(true);
    try {
      // 加载所有选中层级的模板
      const allTemplates: TemplateInfo[] = [];
      for (const level of selectedLevels) {
        const data = await getAvailableTemplates(level);
        // 过滤选中标准的模板
        const filtered = data.filter(
          (t) => !t.standard || selectedStandards.includes(t.standard),
        );
        allTemplates.push(...filtered);
      }
      setTemplates(allTemplates);
      // 默认全选
      setSelectedTemplates(allTemplates.map((t) => t.template_id));
    } catch (error) {
      message.error('加载模板列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTemplate = (template_id: string, checked: boolean) => {
    if (checked) {
      setSelectedTemplates([...selectedTemplates, template_id]);
    } else {
      setSelectedTemplates(selectedTemplates.filter((id) => id !== template_id));
    }
  };

  const handleNext = () => {
    if (currentStep === 0 && selectedLevels.length === 0) {
      message.warning('请至少选择一个文档层级');
      return;
    }
    if (currentStep === 1 && selectedStandards.length === 0) {
      message.warning('请至少选择一个管理体系标准');
      return;
    }
    if (currentStep === 2 && selectedTemplates.length === 0) {
      message.warning('请至少选择一个文档模板');
      return;
    }
    setCurrentStep(currentStep + 1);
  };

  const handlePrev = () => {
    setCurrentStep(currentStep - 1);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerateStatus(null);

    try {
      let status: GenerateStatus;

      if (selectedTemplates.length > 0) {
        // 使用选中的模板批量生成
        status = await generateBatchDocuments(projectId, selectedTemplates);
      } else {
        // 按层级生成
        status = await generateByLevel(projectId, selectedLevels, selectedStandards);
      }

      setGenerateStatus(status);

      // 开始轮询状态
      if (status.task_id) {
        pollGenerateStatus(status.task_id);
      }
    } catch (error) {
      message.error('启动生成任务失败');
      setIsGenerating(false);
    }
  };

  const pollGenerateStatus = async (taskId: string) => {
    try {
      const status = await getGenerateTaskStatus(taskId);
      setGenerateStatus(status);

      if (status.status === 'processing') {
        setTimeout(() => pollGenerateStatus(taskId), 1000);
      } else if (status.status === 'completed') {
        setIsGenerating(false);
        onGenerateComplete?.(status.generated_documents);
      } else if (status.status === 'failed') {
        setIsGenerating(false);
      }
    } catch (error) {
      message.error('获取生成状态失败');
      setIsGenerating(false);
    }
  };

  const handleClose = () => {
    if (isGenerating) {
      Modal.confirm({
        title: '确认关闭',
        content: '文档正在生成中，关闭后可稍后在文档列表中查看生成结果。确定要关闭吗？',
        onOk: () => {
          resetState();
          onClose();
        },
      });
    } else {
      resetState();
      onClose();
    }
  };

  const resetState = () => {
    setCurrentStep(0);
    setSelectedLevels([1, 2, 3, 4]);
    setSelectedStandards(['ISO9001']);
    setSelectedTemplates([]);
    setGenerateStatus(null);
    setIsGenerating(false);
  };

  const steps = [
    { title: '选择层级', description: '选择要生成的文档层级' },
    { title: '选择标准', description: '选择管理体系标准' },
    { title: '预览文档', description: '确认要生成的文档' },
    { title: '生成文档', description: '生成进度' },
  ];

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <StepSelectLevel
            levels={levels}
            selectedLevels={selectedLevels}
            onChange={setSelectedLevels}
            loading={loading}
          />
        );
      case 1:
        return (
          <StepSelectStandard
            selectedStandards={selectedStandards}
            onChange={setSelectedStandards}
          />
        );
      case 2:
        return (
          <StepPreview
            templates={templates}
            selectedTemplates={selectedTemplates}
            onToggleTemplate={handleToggleTemplate}
            loading={loading}
          />
        );
      case 3:
        return <StepProgress status={generateStatus} isGenerating={isGenerating} />;
      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return selectedLevels.length > 0;
      case 1:
        return selectedStandards.length > 0;
      case 2:
        return selectedTemplates.length > 0;
      default:
        return true;
    }
  };

  return (
    <Modal
      open={visible}
      title="文档生成向导"
      onCancel={handleClose}
      width={720}
      footer={
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <div>
            {currentStep === 3 && generateStatus?.status === 'completed' && (
              <Button type="primary" icon={<CheckCircleOutlined />} onClick={handleClose}>
                完成
              </Button>
            )}
          </div>
          <Space>
            {currentStep > 0 && currentStep < 3 && (
              <Button onClick={handlePrev}>上一步</Button>
            )}
            {currentStep < 2 && (
              <Button type="primary" onClick={handleNext} disabled={!canProceed()}>
                下一步
              </Button>
            )}
            {currentStep === 2 && (
              <Button type="primary" onClick={handleNext} disabled={!canProceed()}>
                确认生成
              </Button>
            )}
            {currentStep === 3 && generateStatus?.status !== 'completed' && (
              <Button type="primary" loading={isGenerating} onClick={handleGenerate}>
                {isGenerating ? '生成中...' : '开始生成'}
              </Button>
            )}
          </Space>
        </div>
      }
      maskClosable={false}
    >
      <Steps current={currentStep} items={steps} style={{ marginBottom: 24 }} />

      <Divider />

      <div style={{ minHeight: 300 }}>{renderStepContent()}</div>
    </Modal>
  );
};

export default GenerateWizard;
