import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Checkbox,
  message,
  Modal,
  Form,
  Switch,
  Select,
  Progress,
  Empty,
  Spin,
  Typography,
  Divider,
  Alert,
  Tooltip,
  Tabs,
  Timeline,
  Badge,
  Input,
} from 'antd';
import {
  DownloadOutlined,
  FileZipOutlined,
  FileWordOutlined,
  FilePdfOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  ArrowLeftOutlined,
  ReloadOutlined,
  HistoryOutlined,
  FileTextOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import {
  getProjectDocuments,
  getProjectDetail,
  exportSingleDocument,
  exportProjectDocuments,
  getExportTaskStatus,
  downloadExportedFile,
} from '@/api';
import type { DocumentInfo, ProjectInfo, ExportStatus, ExportOptions } from '@/api';
import ExportButton from '@/components/ExportButton';
import ConfirmBadge from '@/components/ConfirmBadge';

const { Text, Title } = Typography;

/** 导出历史记录 */
interface ExportHistory {
  id: string;
  taskId: string;
  projectName: string;
  documentCount: number;
  format: 'docx' | 'pdf' | 'zip';
  status: 'completed' | 'failed';
  createdAt: string;
  downloadUrl?: string;
}

/** 导出选项配置面板 */
const ExportOptionsPanel: React.FC<{
  options: ExportOptions;
  onChange: (options: ExportOptions) => void;
  unconfirmedCount: number;
}> = ({ options, onChange, unconfirmedCount }) => {
  return (
    <Card title="导出选项" size="small">
      <Form layout="vertical" size="small">
        <Form.Item label="导出格式">
          <Select
            value={options.documentFormat || 'docx'}
            onChange={(value) => onChange({ ...options, documentFormat: value })}
            style={{ width: '100%' }}
            options={[
              { label: 'Word文档 (.docx)', value: 'docx' },
              { label: 'PDF文档 (.pdf)', value: 'pdf' },
            ]}
          />
        </Form.Item>
        <Form.Item label="添加水印">
          <Space>
            <Switch
              checked={options.includeWatermark}
              onChange={(checked) => onChange({ ...options, includeWatermark: checked })}
            />
            <Text type="secondary">在文档中添加"仅供审核使用"水印</Text>
          </Space>
        </Form.Item>
        <Form.Item label="包含公司Logo">
          <Space>
            <Switch
              checked={options.includeLogo}
              onChange={(checked) => onChange({ ...options, includeLogo: checked })}
            />
            <Text type="secondary">在文档页眉添加公司Logo</Text>
          </Space>
        </Form.Item>
        {unconfirmedCount > 0 && (
          <Form.Item label="强制导出">
            <Space>
              <Switch
                checked={options.forceExport}
                onChange={(checked) => onChange({ ...options, forceExport: checked })}
              />
              <Text type="warning">
                包含 {unconfirmedCount} 个未确认文档
              </Text>
            </Space>
          </Form.Item>
        )}
      </Form>
    </Card>
  );
};

/** 导出历史面板 */
const ExportHistoryPanel: React.FC<{
  history: ExportHistory[];
  loading: boolean;
  onRefresh: () => void;
}> = ({ history, loading, onRefresh }) => {
  const getStatusTag = (status: string) => {
    switch (status) {
      case 'completed':
        return <Tag color="success" icon={<CheckCircleOutlined />}>成功</Tag>;
      case 'failed':
        return <Tag color="error" icon={<CloseCircleOutlined />}>失败</Tag>;
      default:
        return <Tag>未知</Tag>;
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'docx':
        return <FileWordOutlined style={{ color: '#1677ff' }} />;
      case 'pdf':
        return <FilePdfOutlined style={{ color: '#ff4d4f' }} />;
      case 'zip':
        return <FileZipOutlined style={{ color: '#52c41a' }} />;
      default:
        return <FileTextOutlined />;
    }
  };

  return (
    <Card
      title={
        <Space>
          <HistoryOutlined />
          导出历史
        </Space>
      }
      size="small"
      extra={
        <Button size="small" icon={<ReloadOutlined />} onClick={onRefresh} loading={loading}>
          刷新
        </Button>
      }
    >
      {history.length === 0 ? (
        <Empty description="暂无导出记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        <Timeline
          items={history.map((item) => ({
            color: item.status === 'completed' ? 'green' : 'red',
            children: (
              <div>
                <div style={{ marginBottom: 4 }}>
                  <Space>
                    {getFormatIcon(item.format)}
                    <Text strong>{item.projectName}</Text>
                    {getStatusTag(item.status)}
                  </Space>
                </div>
                <div style={{ fontSize: 12, color: '#666' }}>
                  <Space split={<Divider type="vertical" />}>
                    <span>{item.documentCount} 个文档</span>
                    <span>{item.createdAt}</span>
                    {item.status === 'completed' && item.downloadUrl && (
                      <a href={item.downloadUrl} target="_blank" rel="noopener noreferrer">
                        重新下载
                      </a>
                    )}
                  </Space>
                </div>
              </div>
            ),
          }))}
        />
      )}
    </Card>
  );
};

/** 文档导出页面 */
const DocumentExportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { isMobile } = useResponsive();
  const navigate = useNavigate();

  // 状态
  const [loading, setLoading] = useState(false);
  const [project, setProject] = useState<ProjectInfo | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [searchText, setSearchText] = useState('');
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    documentFormat: 'docx',
    includeWatermark: false,
    includeLogo: false,
    forceExport: false,
  });
  const [exporting, setExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<ExportStatus | null>(null);
  const [progressVisible, setProgressVisible] = useState(false);
  const [exportHistory, setExportHistory] = useState<ExportHistory[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // 加载数据
  useEffect(() => {
    if (id) {
      loadData(id);
      loadExportHistory();
    }
  }, [id]);

  const loadData = async (projectId: string) => {
    setLoading(true);
    try {
      const [projectData, documentsData] = await Promise.all([
        getProjectDetail(projectId),
        getProjectDocuments(projectId),
      ]);
      setProject(projectData);
      setDocuments(documentsData);
    } catch (error) {
      message.error('加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadExportHistory = async () => {
    // 模拟加载历史记录，实际应从API获取
    setHistoryLoading(true);
    try {
      // TODO: 调用实际的API
      // const history = await getExportHistory(id);
      setExportHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  // 筛选文档
  const filteredDocuments = documents.filter(
    (doc) =>
      doc.name.toLowerCase().includes(searchText.toLowerCase()) ||
      doc.type.toLowerCase().includes(searchText.toLowerCase()),
  );

  // 未确认文档数量
  const unconfirmedCount = documents.filter((d) => d.status !== 'confirmed').length;

  // 选择处理
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedIds(filteredDocuments.map((d) => d.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectToggle = (docId: string, checked: boolean) => {
    if (checked) {
      setSelectedIds([...selectedIds, docId]);
    } else {
      setSelectedIds(selectedIds.filter((id) => id !== docId));
    }
  };

  // 导出单个文档
  const handleExportSingle = async (doc: DocumentInfo, format: 'docx' | 'pdf') => {
    try {
      await exportSingleDocument(doc.id, format);
      message.success(`正在导出: ${doc.name}`);
    } catch (error) {
      message.error('导出失败');
    }
  };

  // 批量导出
  const handleBatchExport = async () => {
    if (selectedIds.length === 0) {
      message.warning('请先选择要导出的文档');
      return;
    }

    // 检查未确认文档
    const selectedDocs = documents.filter((d) => selectedIds.includes(d.id));
    const unconfirmedSelected = selectedDocs.filter((d) => d.status !== 'confirmed');
    
    if (unconfirmedSelected.length > 0 && !exportOptions.forceExport) {
      Modal.confirm({
        title: '存在未确认文档',
        content: (
          <div>
            <p>选中的文档中有 {unconfirmedSelected.length} 个尚未确认，是否继续导出？</p>
            <p style={{ color: '#999', fontSize: 12 }}>
              未确认的文档可能包含未审核的内容。
            </p>
          </div>
        ),
        okText: '继续导出',
        cancelText: '取消',
        onOk: () => startBatchExport(),
      });
      return;
    }

    await startBatchExport();
  };

  const startBatchExport = async () => {
    setExporting(true);
    setProgressVisible(true);
    setExportStatus(null);

    try {
      const status = await exportProjectDocuments(id!, {
        ...exportOptions,
        // 如果有选中特定文档，需要后端支持
      });
      setExportStatus(status);

      if (status.taskId) {
        pollExportStatus(status.taskId);
      }
    } catch (error) {
      message.error('导出失败');
      setProgressVisible(false);
    } finally {
      setExporting(false);
    }
  };

  // 轮询导出状态
  const pollExportStatus = async (taskId: string) => {
    try {
      const status = await getExportTaskStatus(taskId);
      setExportStatus(status);

      if (status.status === 'processing') {
        setTimeout(() => pollExportStatus(taskId), 1000);
      } else if (status.status === 'completed') {
        message.success('导出完成');
        // 添加到历史记录
        setExportHistory((prev) => [
          {
            id: Date.now().toString(),
            taskId: status.taskId,
            projectName: project?.name || '',
            documentCount: status.totalDocuments,
            format: 'zip',
            status: 'completed',
            createdAt: new Date().toLocaleString(),
            downloadUrl: `/api/v1/generator/export/download/${status.taskId}`,
          },
          ...prev,
        ]);
      } else if (status.status === 'failed') {
        message.error('导出失败: ' + (status.error || '未知错误'));
      }
    } catch (error) {
      message.error('获取导出状态失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: (
        <Checkbox
          checked={selectedIds.length === filteredDocuments.length && filteredDocuments.length > 0}
          indeterminate={selectedIds.length > 0 && selectedIds.length < filteredDocuments.length}
          onChange={(e) => handleSelectAll(e.target.checked)}
        />
      ),
      key: 'select',
      width: 50,
      render: (_: unknown, record: DocumentInfo) => (
        <Checkbox
          checked={selectedIds.includes(record.id)}
          onChange={(e) => handleSelectToggle(record.id, e.target.checked)}
        />
      ),
    },
    {
      title: '文档名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: DocumentInfo) => (
        <Space>
          <FileTextOutlined />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (text: string) => <Tag>{text}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => <ConfirmBadge status={status as DocumentInfo['status']} />,
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: unknown, record: DocumentInfo) => (
        <Space>
          <Tooltip title="导出为Word">
            <Button
              type="text"
              size="small"
              icon={<FileWordOutlined style={{ color: '#1677ff' }} />}
              onClick={() => handleExportSingle(record, 'docx')}
            />
          </Tooltip>
          <Tooltip title="导出为PDF">
            <Button
              type="text"
              size="small"
              icon={<FilePdfOutlined style={{ color: '#ff4d4f' }} />}
              onClick={() => handleExportSingle(record, 'pdf')}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  // 导出进度弹窗
  const renderProgressModal = () => (
    <Modal
      open={progressVisible}
      title="导出进度"
      onCancel={exportStatus?.status === 'completed' || exportStatus?.status === 'failed' ? () => setProgressVisible(false) : undefined}
      footer={
        exportStatus?.status === 'completed' ? (
          <Space>
            <Button onClick={() => setProgressVisible(false)}>关闭</Button>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => {
                if (exportStatus?.taskId) {
                  downloadExportedFile(exportStatus.taskId);
                }
              }}
            >
              下载文件
            </Button>
          </Space>
        ) : exportStatus?.status === 'failed' ? (
          <Button onClick={() => setProgressVisible(false)}>关闭</Button>
        ) : null
      }
      maskClosable={false}
      closable={exportStatus?.status === 'completed' || exportStatus?.status === 'failed'}
    >
      <div style={{ textAlign: 'center', padding: '20px 0' }}>
        {exportStatus?.status === 'processing' ? (
          <Spin size="large" />
        ) : exportStatus?.status === 'completed' ? (
          <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
        ) : exportStatus?.status === 'failed' ? (
          <CloseCircleOutlined style={{ fontSize: 48, color: '#ff4d4f' }} />
        ) : (
          <Spin size="large" />
        )}
        <div style={{ fontSize: 16, marginTop: 16 }}>
          {exportStatus?.status === 'processing' && '正在导出...'}
          {exportStatus?.status === 'completed' && '导出完成'}
          {exportStatus?.status === 'failed' && '导出失败'}
          {!exportStatus && '准备中...'}
        </div>
        {exportStatus && (
          <>
            <Progress
              percent={exportStatus.progress}
              status={exportStatus.status === 'failed' ? 'exception' : undefined}
              style={{ marginTop: 16 }}
            />
            {exportStatus.status === 'processing' && (
              <Text type="secondary">
                已处理 {exportStatus.processedDocuments} / {exportStatus.totalDocuments} 个文档
              </Text>
            )}
          </>
        )}
      </div>
    </Modal>
  );

  // 移动端渲染
  if (isMobile) {
    return (
      <div>
        <div style={{ padding: 12, backgroundColor: '#fff', marginBottom: 12 }}>
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
              返回
            </Button>
            <Title level={5} style={{ margin: 0 }}>
              文档导出
            </Title>
            <ExportButton
              projectId={id!}
              documents={documents}
              disabled={selectedIds.length === 0}
              showDropdown={false}
              buttonText="导出选中"
            />
          </Space>
        </div>

        <div style={{ padding: '0 12px' }}>
          {/* 统计信息 */}
          <Card size="small" style={{ marginBottom: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-around' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, fontWeight: 'bold', color: '#1677ff' }}>
                  {documents.length}
                </div>
                <div style={{ fontSize: 12, color: '#999' }}>总文档</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, fontWeight: 'bold', color: '#52c41a' }}>
                  {documents.filter((d) => d.status === 'confirmed').length}
                </div>
                <div style={{ fontSize: 12, color: '#999' }}>已确认</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, fontWeight: 'bold', color: '#faad14' }}>
                  {selectedIds.length}
                </div>
                <div style={{ fontSize: 12, color: '#999' }}>已选中</div>
              </div>
            </div>
          </Card>

          {/* 文档列表 */}
          <Card size="small" title="文档列表">
            {loading ? (
              <div style={{ textAlign: 'center', padding: 20 }}>
                <Spin />
              </div>
            ) : documents.length === 0 ? (
              <Empty description="暂无文档" />
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  style={{
                    padding: '12px 0',
                    borderBottom: '1px solid #f0f0f0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Space>
                    <Checkbox
                      checked={selectedIds.includes(doc.id)}
                      onChange={(e) => handleSelectToggle(doc.id, e.target.checked)}
                    />
                    <div>
                      <div>{doc.name}</div>
                      <Space size={4} style={{ marginTop: 4 }}>
                        <Tag>{doc.type}</Tag>
                        <ConfirmBadge status={doc.status} />
                      </Space>
                    </div>
                  </Space>
                  <Space>
                    <Button
                      type="text"
                      size="small"
                      icon={<FileWordOutlined />}
                      onClick={() => handleExportSingle(doc, 'docx')}
                    />
                    <Button
                      type="text"
                      size="small"
                      icon={<FilePdfOutlined />}
                      onClick={() => handleExportSingle(doc, 'pdf')}
                    />
                  </Space>
                </div>
              ))
            )}
          </Card>
        </div>

        {renderProgressModal()}
      </div>
    );
  }

  // PC端渲染
  return (
    <div>
      {/* 页面头部 */}
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
              返回
            </Button>
            <Title level={4} style={{ margin: 0 }}>
              文档导出
            </Title>
            {project && <Tag color="blue">{project.name}</Tag>}
          </Space>
          <Space>
            <ExportButton
              projectId={id!}
              documents={documents}
              onExportComplete={() => loadData(id!)}
            />
          </Space>
        </Space>
      </div>

      {/* 主内容区 */}
      <div style={{ display: 'flex', gap: 16 }}>
        {/* 左侧：文档列表 */}
        <Card style={{ flex: 1 }} title="项目文档">
          {/* 工具栏 */}
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
            <Space>
              <Input
                placeholder="搜索文档"
                prefix={<SearchOutlined />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ width: 200 }}
                allowClear
              />
              <Text type="secondary">
                已选中 {selectedIds.length} / {filteredDocuments.length} 个文档
              </Text>
            </Space>
            <Space>
              <Button onClick={() => handleSelectAll(true)}>全选</Button>
              <Button onClick={() => setSelectedIds([])}>清空</Button>
              <Button
                type="primary"
                icon={<FileZipOutlined />}
                disabled={selectedIds.length === 0}
                loading={exporting}
                onClick={handleBatchExport}
              >
                导出选中 ({selectedIds.length})
              </Button>
            </Space>
          </div>

          {/* 提示信息 */}
          {unconfirmedCount > 0 && (
            <Alert
              type="warning"
              showIcon
              message={`有 ${unconfirmedCount} 个文档尚未确认`}
              description="建议先确认文档内容后再导出，或使用"强制导出"选项。"
              style={{ marginBottom: 16 }}
            />
          )}

          {/* 文档表格 */}
          <Table
            columns={columns}
            dataSource={filteredDocuments}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个文档`,
            }}
            locale={{ emptyText: <Empty description="暂无文档" /> }}
            rowSelection={{
              selectedRowKeys: selectedIds,
              onChange: (keys) => setSelectedIds(keys as string[]),
            }}
          />
        </Card>

        {/* 右侧：导出选项和历史 */}
        <div style={{ width: 320, flexShrink: 0 }}>
          <Tabs
            defaultActiveKey="options"
            items={[
              {
                key: 'options',
                label: '导出选项',
                children: (
                  <ExportOptionsPanel
                    options={exportOptions}
                    onChange={setExportOptions}
                    unconfirmedCount={unconfirmedCount}
                  />
                ),
              },
              {
                key: 'history',
                label: (
                  <Badge count={exportHistory.length} size="small" offset={[10, 0]}>
                    导出历史
                  </Badge>
                ),
                children: (
                  <ExportHistoryPanel
                    history={exportHistory}
                    loading={historyLoading}
                    onRefresh={loadExportHistory}
                  />
                ),
              },
            ]}
          />
        </div>
      </div>

      {renderProgressModal()}
    </div>
  );
};

export default DocumentExportPage;
