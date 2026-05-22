import React, { useState, useCallback, useRef } from 'react';
import {
  Card,
  Upload,
  Button,
  Typography,
  Space,
  Alert,
  Progress,
  Spin,
  Divider,
  Form,
  Input,
  Tag,
  List,
  message,
  Descriptions,
  Row,
  Col,
  Empty,
} from 'antd';
import {
  UploadOutlined,
  InboxOutlined,
  FileExcelOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileTextOutlined,
  ExtractOutlined,
  CheckCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  LoadingOutlined,
} from '@ant-design/icons';

const { Text, Title, Paragraph } = Typography;
const { Dragger } = Upload;

// ============ 类型定义 ============

/** 上传文件项 */
interface UploadFileItem {
  uid: string;
  name: string;
  size: number;
  type: string;
  status: 'uploading' | 'success' | 'error';
  progress: number;
  file?: File;
}

/** 提取结果 - 质量方针 */
interface QualityPolicy {
  text: string;
  source: string;
}

/** 提取结果 - 质量目标 */
interface QualityObjective {
  id: string;
  content: string;
  department: string;
  target: string;
  period: string;
}

/** 提取结果 - 文件编号规则 */
interface FileNamingRule {
  prefix: string;
  category: string;
  format: string;
  example: string;
}

/** 提取结果 - 部门信息 */
interface DepartmentInfo {
  name: string;
  code: string;
  description?: string;
  functions?: string[];
}

/** 提取结果 - 企业信息 */
interface CompanyExtractInfo {
  companyName: string;
  address: string;
  legalPerson: string;
  registeredCapital: string;
  businessScope: string;
  establishedDate: string;
  unifiedSocialCreditCode: string;
}

/** 完整提取结果 */
export interface ExtractionResult {
  qualityPolicy: QualityPolicy;
  qualityObjectives: QualityObjective[];
  fileNamingRules: FileNamingRule[];
  departments: DepartmentInfo[];
  companyInfo: CompanyExtractInfo;
  rawFiles: Array<{
    fileName: string;
    fileType: string;
    extractedFields: string[];
  }>;
}

/** 组件Props */
interface OldFilesUploadProps {
  /** 项目ID */
  projectId: string;
  /** 提取完成回调 */
  onExtractComplete?: (result: ExtractionResult) => void;
  /** 确认回调 */
  onConfirm?: (result: ExtractionResult) => void;
  /** 是否禁用 */
  disabled?: boolean;
  /** 自定义样式 */
  className?: string;
}

// ============ 辅助函数 ============

/** 允许的文件类型 */
const ALLOWED_TYPES = [
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
  'application/pdf', // .pdf
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
  'text/plain', // .txt
];

/** 允许的文件扩展名 */
const ALLOWED_EXTENSIONS = ['.docx', '.pdf', '.xlsx', '.txt'];

/** 最大文件大小（50MB） */
const MAX_FILE_SIZE = 50 * 1024 * 1024;

/** 根据文件类型获取图标 */
const getFileIcon = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'docx':
    case 'doc':
      return <FileWordOutlined style={{ fontSize: 24, color: '#2b579a' }} />;
    case 'pdf':
      return <FilePdfOutlined style={{ fontSize: 24, color: '#d4380d' }} />;
    case 'xlsx':
    case 'xls':
      return <FileExcelOutlined style={{ fontSize: 24, color: '#217346' }} />;
    case 'txt':
      return <FileTextOutlined style={{ fontSize: 24, color: '#8c8c8c' }} />;
    default:
      return <FileTextOutlined style={{ fontSize: 24 }} />;
  }
};

/** 格式化文件大小 */
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

// ============ 组件 ============

/**
 * 旧版文件上传和提取组件
 *
 * 功能：
 * - 文件上传区域（支持拖拽上传，docx/pdf/xlsx/txt）
 * - 上传进度展示
 * - 提取按钮（触发后端提取API）
 * - 提取结果展示：质量方针、质量目标、文件编号规则、部门列表、企业信息
 * - 用户可修改提取结果
 * - 确认按钮
 */
const OldFilesUpload: React.FC<OldFilesUploadProps> = ({
  projectId,
  onExtractComplete,
  onConfirm,
  disabled = false,
  className = '',
}) => {
  // ============ 状态 ============
  const [fileList, setFileList] = useState<UploadFileItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [extracted, setExtracted] = useState(false);
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);

  // ============ 文件上传处理 ============

  /** 验证文件 */
  const beforeUpload = useCallback((file: File) => {
    const ext = '.' + (file.name.split('.').pop() || '').toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      message.error(`不支持的文件格式：${ext}，请上传 ${ALLOWED_EXTENSIONS.join('、')} 格式的文件`);
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      message.error(`文件大小超过限制（最大 ${MAX_FILE_SIZE / (1024 * 1024)}MB）`);
      return false;
    }
    return true;
  }, []);

  /** 模拟上传文件 */
  const handleUpload = useCallback(
    (files: File[]) => {
      if (disabled) return;

      const newFiles: UploadFileItem[] = files.map((file) => ({
        uid: `upload-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading' as const,
        progress: 0,
        file,
      }));

      setFileList((prev) => [...prev, ...newFiles]);
      setUploading(true);

      // 模拟上传进度
      newFiles.forEach((newFile) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += Math.random() * 30 + 10;
          if (progress >= 100) {
            progress = 100;
            clearInterval(interval);

            setFileList((prev) =>
              prev.map((f) =>
                f.uid === newFile.uid
                  ? { ...f, status: 'success' as const, progress: 100 }
                  : f,
              ),
            );

            // 检查是否所有文件都上传完成
            setFileList((currentList) => {
              const allDone = currentList.every(
                (f) => f.status === 'success' || f.status === 'error',
              );
              if (allDone) {
                setUploading(false);
              }
              return currentList;
            });
          } else {
            setFileList((prev) =>
              prev.map((f) =>
                f.uid === newFile.uid ? { ...f, progress: Math.min(progress, 99) } : f,
              ),
            );
          }
        }, 200);
      });
    },
    [disabled],
  );

  /** 删除文件 */
  const handleRemoveFile = useCallback((uid: string) => {
    setFileList((prev) => prev.filter((f) => f.uid !== uid));
  }, []);

  // ============ 提取处理 ============

  /** 触发提取 */
  const handleExtract = useCallback(async () => {
    const successFiles = fileList.filter((f) => f.status === 'success');
    if (successFiles.length === 0) {
      message.warning('请先上传文件');
      return;
    }

    setExtracting(true);
    try {
      // 调用后端提取API
      // const result = await extractOldFiles(projectId);
      // 模拟提取结果
      const mockResult: ExtractionResult = {
        qualityPolicy: {
          text: '以客户为中心，持续改进，追求卓越品质，全员参与质量管理',
          source: '质量手册 第2章',
        },
        qualityObjectives: [
          {
            id: '1',
            content: '产品一次合格率 >= 98%',
            department: '生产部',
            target: '98%',
            period: '年度',
          },
          {
            id: '2',
            content: '客户满意度 >= 95%',
            department: '销售部',
            target: '95%',
            period: '年度',
          },
          {
            id: '3',
            content: '供应商合格率 >= 90%',
            department: '采购部',
            target: '90%',
            period: '年度',
          },
        ],
        fileNamingRules: [
          {
            prefix: 'QM',
            category: '质量手册',
            format: 'QM-XXXX',
            example: 'QM-2024-001',
          },
          {
            prefix: 'QP',
            category: '程序文件',
            format: 'QP-XX-XXXX',
            example: 'QP-01-2024-001',
          },
          {
            prefix: 'WI',
            category: '作业指导书',
            format: 'WI-XX-XX-XXXX',
            example: 'WI-01-01-2024-001',
          },
          {
            prefix: 'QR',
            category: '质量记录',
            format: 'QR-XX-XXXX',
            example: 'QR-01-2024-001',
          },
        ],
        departments: [
          {
            name: '总经理办公室',
            code: 'GM',
            description: '负责公司整体管理和战略决策',
            functions: ['管理评审', '资源配置', '内部沟通'],
          },
          {
            name: '质量部',
            code: 'QA',
            description: '负责质量管理体系运行和维护',
            functions: ['内部审核', '不合格品控制', '纠正措施', '数据分析'],
          },
          {
            name: '生产部',
            code: 'PD',
            description: '负责产品生产制造过程管理',
            functions: ['生产计划', '过程控制', '设备管理'],
          },
          {
            name: '销售部',
            code: 'SD',
            description: '负责市场销售和客户关系管理',
            functions: ['客户沟通', '合同评审', '客户满意度调查'],
          },
          {
            name: '采购部',
            code: 'PU',
            description: '负责物资采购和供应商管理',
            functions: ['供应商评价', '采购控制', '进货检验'],
          },
        ],
        companyInfo: {
          companyName: '示例科技有限公司',
          address: '北京市朝阳区XX路XX号',
          legalPerson: '张三',
          registeredCapital: '500万元',
          businessScope: '技术开发、技术咨询、技术服务',
          establishedDate: '2010-05-15',
          unifiedSocialCreditCode: '91110105MA01XXXXX',
        },
        rawFiles: successFiles.map((f) => ({
          fileName: f.name,
          fileType: f.name.split('.').pop() || '',
          extractedFields: ['企业信息', '质量方针'],
        })),
      };

      setExtractionResult(mockResult);
      setExtracted(true);
      message.success('文件信息提取完成');
      onExtractComplete?.(mockResult);
    } catch {
      message.error('提取失败，请重试');
    } finally {
      setExtracting(false);
    }
  }, [fileList, projectId, onExtractComplete]);

  // ============ 编辑处理 ============

  /** 更新提取结果字段 */
  const updateResultField = useCallback(
    (path: string, value: any) => {
      if (!extractionResult) return;

      const keys = path.split('.');
      const newResult = JSON.parse(JSON.stringify(extractionResult));
      let current: any = newResult;

      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = value;

      setExtractionResult(newResult);
    },
    [extractionResult],
  );

  /** 确认提取结果 */
  const handleConfirm = useCallback(async () => {
    if (!extractionResult) return;
    setConfirming(true);
    try {
      // const result = await classifyFiles(projectId);
      message.success('旧版文件信息已确认');
      onConfirm?.(extractionResult);
    } catch {
      message.error('确认失败，请重试');
    } finally {
      setConfirming(false);
    }
  }, [extractionResult, projectId, onConfirm]);

  // ============ 渲染 ============

  const successFileCount = fileList.filter((f) => f.status === 'success').length;

  return (
    <Card
      className={className}
      title="上传旧版体系文件"
      extra={
        extracted ? (
          <Tag color="success" icon={<CheckCircleOutlined />}>
            已提取
          </Tag>
        ) : (
          <Text type="secondary">
            已上传 {successFileCount} 个文件
          </Text>
        )
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 提示信息 */}
        <Alert
          message="请上传旧版质量管理体系文件，系统将自动提取其中的关键信息"
          description="支持格式：.docx、.pdf、.xlsx、.txt，单个文件最大50MB。建议上传质量手册、程序文件、营业执照等文件。"
          type="info"
          showIcon
          style={{ marginBottom: 0 }}
        />

        {/* 文件上传区域 */}
        <Dragger
          multiple
          accept={ALLOWED_EXTENSIONS.join(',')}
          beforeUpload={(file) => {
            if (beforeUpload(file)) {
              handleUpload([file]);
            }
            return false; // 阻止自动上传
          }}
          disabled={disabled || uploading}
          showUploadList={false}
          style={{
            padding: '24px 16px',
            backgroundColor: extracted ? '#f6ffed' : '#fafafa',
            borderColor: extracted ? '#b7eb8f' : '#d9d9d9',
          }}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: 48, color: extracted ? '#52c41a' : '#1890ff' }} />
          </p>
          <p className="ant-upload-text" style={{ fontSize: 15, fontWeight: 500 }}>
            点击或拖拽文件到此区域上传
          </p>
          <p className="ant-upload-hint" style={{ fontSize: 13 }}>
            支持 .docx、.pdf、.xlsx、.txt 格式
          </p>
        </Dragger>

        {/* 已上传文件列表 */}
        {fileList.length > 0 && (
          <div>
            <Text strong style={{ display: 'block', marginBottom: 8 }}>
              已上传文件（{fileList.length}）
            </Text>
            <List
              size="small"
              bordered
              dataSource={fileList}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    item.status === 'uploading' ? (
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {item.progress}%
                      </Text>
                    ) : item.status === 'success' ? (
                      <Tag color="success" style={{ fontSize: 11 }}>已上传</Tag>
                    ) : (
                      <Tag color="error" style={{ fontSize: 11 }}>失败</Tag>
                    ),
                    !disabled && (
                      <Button
                        type="text"
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemoveFile(item.uid)}
                      />
                    ),
                  ].filter(Boolean)}
                >
                  <List.Item.Meta
                    avatar={getFileIcon(item.name)}
                    title={
                      <Space>
                        <Text style={{ fontSize: 13 }}>{item.name}</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          ({formatFileSize(item.size)})
                        </Text>
                      </Space>
                    }
                  />
                  {item.status === 'uploading' && (
                    <Progress
                      percent={item.progress}
                      size="small"
                      style={{ marginBottom: 0, width: 120 }}
                      showInfo={false}
                    />
                  )}
                </List.Item>
              )}
            />
          </div>
        )}

        {/* 提取按钮 */}
        {!extracted && (
          <div style={{ textAlign: 'center' }}>
            <Button
              type="primary"
              size="large"
              icon={<ExtractOutlined />}
              loading={extracting}
              disabled={successFileCount === 0 || uploading || disabled}
              onClick={handleExtract}
            >
              {extracting ? '正在提取信息...' : '提取文件信息'}
            </Button>
          </div>
        )}

        {/* 提取中状态 */}
        {extracting && (
          <div style={{ textAlign: 'center', padding: '24px 0' }}>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 32 }} />} />
            <div style={{ marginTop: 12 }}>
              <Text type="secondary">正在分析文件内容，提取关键信息...</Text>
            </div>
          </div>
        )}

        {/* 提取结果展示 */}
        {extracted && extractionResult && (
          <>
            <Divider orientation="left">提取结果</Divider>

            {/* 企业信息 */}
            <div>
              <Title level={5}>
                <Space>
                  企业信息
                  <Tag color="blue" style={{ fontSize: 11 }}>从营业执照提取</Tag>
                </Space>
              </Title>
              <Descriptions
                bordered
                size="small"
                column={{ xs: 1, sm: 2 }}
                contentStyle={{ backgroundColor: '#fafafa' }}
              >
                <Descriptions.Item label="公司名称">
                  {editingField === 'companyInfo.companyName' ? (
                    <Input
                      size="small"
                      defaultValue={extractionResult.companyInfo.companyName}
                      onBlur={(e) => {
                        updateResultField('companyInfo.companyName', e.target.value);
                        setEditingField(null);
                      }}
                      onPressEnter={(e) => {
                        updateResultField('companyInfo.companyName', (e.target as HTMLInputElement).value);
                        setEditingField(null);
                      }}
                      autoFocus
                    />
                  ) : (
                    <Text
                      style={{ cursor: 'pointer' }}
                      onClick={() => setEditingField('companyInfo.companyName')}
                    >
                      {extractionResult.companyInfo.companyName}
                      <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                    </Text>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="统一社会信用代码">
                  {editingField === 'companyInfo.unifiedSocialCreditCode' ? (
                    <Input
                      size="small"
                      defaultValue={extractionResult.companyInfo.unifiedSocialCreditCode}
                      onBlur={(e) => {
                        updateResultField('companyInfo.unifiedSocialCreditCode', e.target.value);
                        setEditingField(null);
                      }}
                      onPressEnter={(e) => {
                        updateResultField('companyInfo.unifiedSocialCreditCode', (e.target as HTMLInputElement).value);
                        setEditingField(null);
                      }}
                      autoFocus
                    />
                  ) : (
                    <Text
                      style={{ cursor: 'pointer' }}
                      onClick={() => setEditingField('companyInfo.unifiedSocialCreditCode')}
                    >
                      {extractionResult.companyInfo.unifiedSocialCreditCode}
                      <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                    </Text>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="法定代表人">
                  {editingField === 'companyInfo.legalPerson' ? (
                    <Input
                      size="small"
                      defaultValue={extractionResult.companyInfo.legalPerson}
                      onBlur={(e) => {
                        updateResultField('companyInfo.legalPerson', e.target.value);
                        setEditingField(null);
                      }}
                      onPressEnter={(e) => {
                        updateResultField('companyInfo.legalPerson', (e.target as HTMLInputElement).value);
                        setEditingField(null);
                      }}
                      autoFocus
                    />
                  ) : (
                    <Text
                      style={{ cursor: 'pointer' }}
                      onClick={() => setEditingField('companyInfo.legalPerson')}
                    >
                      {extractionResult.companyInfo.legalPerson}
                      <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                    </Text>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="注册资本">
                  {editingField === 'companyInfo.registeredCapital' ? (
                    <Input
                      size="small"
                      defaultValue={extractionResult.companyInfo.registeredCapital}
                      onBlur={(e) => {
                        updateResultField('companyInfo.registeredCapital', e.target.value);
                        setEditingField(null);
                      }}
                      onPressEnter={(e) => {
                        updateResultField('companyInfo.registeredCapital', (e.target as HTMLInputElement).value);
                        setEditingField(null);
                      }}
                      autoFocus
                    />
                  ) : (
                    <Text
                      style={{ cursor: 'pointer' }}
                      onClick={() => setEditingField('companyInfo.registeredCapital')}
                    >
                      {extractionResult.companyInfo.registeredCapital}
                      <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                    </Text>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="地址" span={2}>
                  {editingField === 'companyInfo.address' ? (
                    <Input
                      size="small"
                      defaultValue={extractionResult.companyInfo.address}
                      onBlur={(e) => {
                        updateResultField('companyInfo.address', e.target.value);
                        setEditingField(null);
                      }}
                      onPressEnter={(e) => {
                        updateResultField('companyInfo.address', (e.target as HTMLInputElement).value);
                        setEditingField(null);
                      }}
                      autoFocus
                    />
                  ) : (
                    <Text
                      style={{ cursor: 'pointer' }}
                      onClick={() => setEditingField('companyInfo.address')}
                    >
                      {extractionResult.companyInfo.address}
                      <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                    </Text>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="经营范围" span={2}>
                  {editingField === 'companyInfo.businessScope' ? (
                    <Input.TextArea
                      size="small"
                      rows={2}
                      defaultValue={extractionResult.companyInfo.businessScope}
                      onBlur={(e) => {
                        updateResultField('companyInfo.businessScope', e.target.value);
                        setEditingField(null);
                      }}
                      autoFocus
                    />
                  ) : (
                    <Text
                      style={{ cursor: 'pointer' }}
                      onClick={() => setEditingField('companyInfo.businessScope')}
                    >
                      {extractionResult.companyInfo.businessScope}
                      <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                    </Text>
                  )}
                </Descriptions.Item>
              </Descriptions>
            </div>

            {/* 质量方针 */}
            <div>
              <Title level={5}>
                <Space>
                  质量方针
                  <Tag color="green" style={{ fontSize: 11 }}>从质量手册提取</Tag>
                </Space>
              </Title>
              <div
                style={{
                  padding: 12,
                  backgroundColor: '#f6ffed',
                  border: '1px solid #b7eb8f',
                  borderRadius: 6,
                }}
              >
                {editingField === 'qualityPolicy.text' ? (
                  <Input.TextArea
                    rows={2}
                    defaultValue={extractionResult.qualityPolicy.text}
                    onBlur={(e) => {
                      updateResultField('qualityPolicy.text', e.target.value);
                      setEditingField(null);
                    }}
                    autoFocus
                  />
                ) : (
                  <Text
                    style={{ cursor: 'pointer', fontSize: 15, lineHeight: 1.8 }}
                    onClick={() => setEditingField('qualityPolicy.text')}
                  >
                    {extractionResult.qualityPolicy.text}
                    <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                  </Text>
                )}
                <div style={{ marginTop: 4 }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    来源：{extractionResult.qualityPolicy.source}
                  </Text>
                </div>
              </div>
            </div>

            {/* 质量目标 */}
            <div>
              <Title level={5}>
                <Space>
                  质量目标
                  <Tag color="green" style={{ fontSize: 11 }}>从质量手册提取</Tag>
                </Space>
              </Title>
              <List
                size="small"
                bordered
                dataSource={extractionResult.qualityObjectives}
                renderItem={(item, index) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Tag color="blue">{index + 1}</Tag>
                      }
                      title={
                        editingField === `qualityObjectives.${index}.content` ? (
                          <Input
                            size="small"
                            defaultValue={item.content}
                            onBlur={(e) => {
                              const newObj = [...extractionResult.qualityObjectives];
                              newObj[index] = { ...newObj[index], content: e.target.value };
                              updateResultField('qualityObjectives', newObj);
                              setEditingField(null);
                            }}
                            onPressEnter={(e) => {
                              const newObj = [...extractionResult.qualityObjectives];
                              newObj[index] = { ...newObj[index], content: (e.target as HTMLInputElement).value };
                              updateResultField('qualityObjectives', newObj);
                              setEditingField(null);
                            }}
                            autoFocus
                            style={{ maxWidth: 400 }}
                          />
                        ) : (
                          <Text
                            style={{ cursor: 'pointer' }}
                            onClick={() => setEditingField(`qualityObjectives.${index}.content`)}
                          >
                            {item.content}
                            <EditOutlined style={{ marginLeft: 4, fontSize: 11, color: '#999' }} />
                          </Text>
                        )
                      }
                      description={
                        <Space size="large">
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            部门：{item.department}
                          </Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            目标值：{item.target}
                          </Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            周期：{item.period}
                          </Text>
                        </Space>
                      }
                    />
                  </List.Item>
                )}
              />
            </div>

            {/* 文件编号规则 */}
            <div>
              <Title level={5}>
                <Space>
                  文件编号规则
                  <Tag color="green" style={{ fontSize: 11 }}>从质量手册提取</Tag>
                </Space>
              </Title>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 8 }}>
                {extractionResult.fileNamingRules.map((rule, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '8px 12px',
                      backgroundColor: '#fafafa',
                      border: '1px solid #f0f0f0',
                      borderRadius: 6,
                    }}
                  >
                    <Space>
                      <Tag color="blue">{rule.prefix}</Tag>
                      <Text strong style={{ fontSize: 13 }}>{rule.category}</Text>
                    </Space>
                    <div style={{ marginTop: 4 }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        格式：{rule.format}
                      </Text>
                    </div>
                    <div>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        示例：{rule.example}
                      </Text>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 部门列表 */}
            <div>
              <Title level={5}>
                <Space>
                  部门列表
                  <Tag color="green" style={{ fontSize: 11 }}>从质量手册提取</Tag>
                </Space>
              </Title>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 8 }}>
                {extractionResult.departments.map((dept, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '10px 12px',
                      backgroundColor: '#fafafa',
                      border: '1px solid #f0f0f0',
                      borderRadius: 6,
                    }}
                  >
                    <Space>
                      <Tag color="purple">{dept.code}</Tag>
                      <Text strong style={{ fontSize: 13 }}>{dept.name}</Text>
                    </Space>
                    {dept.description && (
                      <div style={{ marginTop: 4 }}>
                        <Text type="secondary" style={{ fontSize: 12 }}>{dept.description}</Text>
                      </div>
                    )}
                    {dept.functions && dept.functions.length > 0 && (
                      <div style={{ marginTop: 4 }}>
                        <Space wrap size={[4, 4]}>
                          {dept.functions.map((func, fi) => (
                            <Tag key={fi} style={{ fontSize: 11, margin: 0 }}>{func}</Tag>
                          ))}
                        </Space>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* 确认按钮 */}
            <div style={{ textAlign: 'right', paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
              <Space>
                <Button
                  onClick={handleExtract}
                  disabled={successFileCount === 0 || uploading || extracting}
                  loading={extracting}
                >
                  重新提取
                </Button>
                <Button
                  type="primary"
                  size="large"
                  icon={<CheckCircleOutlined />}
                  loading={confirming}
                  disabled={disabled}
                  onClick={handleConfirm}
                >
                  确认提取结果
                </Button>
              </Space>
            </div>
          </>
        )}
      </Space>
    </Card>
  );
};

export default OldFilesUpload;
export type { OldFilesUploadProps, ExtractionResult };