import React, { useState, useEffect, useCallback } from 'react';
import {
  Button,
  Dropdown,
  Modal,
  Progress,
  Space,
  Switch,
  Form,
  Select,
  message,
  Tooltip,
  Popconfirm,
} from 'antd';
import {
  DownloadOutlined,
  FileZipOutlined,
  FileWordOutlined,
  FilePdfOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import {
  exportSingleDocument,
  exportProjectDocuments,
  getExportTaskStatus,
  downloadExportedFile,
} from '@/api';
import type { DocumentInfo, ExportStatus, ExportOptions } from '@/api';

/** 导出按钮组件属性 */
interface ExportButtonProps {
  /** 项目ID */
  projectId: string;
  /** 单个文档ID（可选，用于导出单个文档） */
  documentId?: string;
  /** 文档信息（用于显示文档名称等） */
  document?: DocumentInfo;
  /** 文档列表（用于批量导出时检查状态） */
  documents?: DocumentInfo[];
  /** 导出完成回调 */
  onExportComplete?: () => void;
  /** 按钮类型 */
  type?: 'primary' | 'default' | 'text' | 'link' | 'dashed';
  /** 按钮大小 */
  size?: 'large' | 'middle' | 'small';
  /** 是否禁用 */
  disabled?: boolean;
  /** 是否显示为下拉菜单形式 */
  showDropdown?: boolean;
  /** 自定义按钮文字 */
  buttonText?: string;
}

/** 导出选项配置组件 */
const ExportOptionsForm: React.FC<{
  options: ExportOptions;
  onChange: (options: ExportOptions) => void;
}> = ({ options, onChange }) => {
  return (
    <Form layout="vertical" size="small">
      <Form.Item label="导出格式">
        <Select
          value={options.documentFormat || 'docx'}
          onChange={(value) => onChange({ ...options, documentFormat: value })}
          options={[
            { label: 'Word文档 (.docx)', value: 'docx' },
            { label: 'PDF文档 (.pdf)', value: 'pdf' },
          ]}
        />
      </Form.Item>
      <Form.Item label="添加水印">
        <Switch
          checked={options.includeWatermark}
          onChange={(checked) => onChange({ ...options, includeWatermark: checked })}
        />
      </Form.Item>
      <Form.Item label="包含Logo">
        <Switch
          checked={options.includeLogo}
          onChange={(checked) => onChange({ ...options, includeLogo: checked })}
        />
      </Form.Item>
    </Form>
  );
};

/** 导出进度弹窗 */
const ExportProgressModal: React.FC<{
  visible: boolean;
  status: ExportStatus | null;
  onClose: () => void;
  onComplete: () => void;
}> = ({ visible, status, onClose, onComplete }) => {
  useEffect(() => {
    if (status?.status === 'completed') {
      onComplete();
    }
  }, [status, onComplete]);

  const getStatusIcon = () => {
    switch (status?.status) {
      case 'pending':
        return <LoadingOutlined spin style={{ color: '#1677ff' }} />;
      case 'processing':
        return <LoadingOutlined spin style={{ color: '#1677ff' }} />;
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (status?.status) {
      case 'pending':
        return '等待中...';
      case 'processing':
        return '正在导出...';
      case 'completed':
        return '导出完成';
      case 'failed':
        return '导出失败';
      default:
        return '准备中...';
    }
  };

  return (
    <Modal
      open={visible}
      title="导出进度"
      onCancel={status?.status === 'completed' || status?.status === 'failed' ? onClose : undefined}
      footer={
        status?.status === 'completed' ? (
          <Space>
            <Button onClick={onClose}>关闭</Button>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={() => {
                if (status?.taskId) {
                  downloadExportedFile(status.taskId);
                }
              }}
            >
              下载文件
            </Button>
          </Space>
        ) : status?.status === 'failed' ? (
          <Button onClick={onClose}>关闭</Button>
        ) : null
      }
      maskClosable={false}
      closable={status?.status === 'completed' || status?.status === 'failed'}
    >
      <div style={{ textAlign: 'center', padding: '20px 0' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>{getStatusIcon()}</div>
        <div style={{ fontSize: 16, marginBottom: 8 }}>{getStatusText()}</div>
        {status && status.status !== 'pending' && (
          <>
            <Progress
              percent={status.progress}
              status={status.status === 'failed' ? 'exception' : undefined}
              style={{ marginBottom: 8 }}
            />
            {status.status === 'processing' && (
              <div style={{ color: '#666', fontSize: 13 }}>
                已处理 {status.processedDocuments} / {status.totalDocuments} 个文档
              </div>
            )}
          </>
        )}
        {status?.error && (
          <div style={{ color: '#ff4d4f', marginTop: 8 }}>{status.error}</div>
        )}
      </div>
    </Modal>
  );
};

/**
 * 文档导出按钮组件
 * 支持导出单个文档和批量导出为ZIP
 */
const ExportButton: React.FC<ExportButtonProps> = ({
  projectId,
  documentId,
  document,
  documents = [],
  onExportComplete,
  type = 'default',
  size = 'middle',
  disabled = false,
  showDropdown = true,
  buttonText,
}) => {
  const [optionsVisible, setOptionsVisible] = useState(false);
  const [progressVisible, setProgressVisible] = useState(false);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    documentFormat: 'docx',
    includeWatermark: false,
    includeLogo: false,
    forceExport: false,
  });
  const [exportStatus, setExportStatus] = useState<ExportStatus | null>(null);
  const [exporting, setExporting] = useState(false);

  /** 轮询导出状态 */
  const pollExportStatus = useCallback(async (taskId: string) => {
    try {
      const status = await getExportTaskStatus(taskId);
      setExportStatus(status);

      if (status.status === 'processing') {
        setTimeout(() => pollExportStatus(taskId), 1000);
      }
    } catch (error) {
      message.error('获取导出状态失败');
      setProgressVisible(false);
    }
  }, []);

  /** 导出单个文档 */
  const handleExportSingle = useCallback(
    async (format: 'docx' | 'pdf' = 'docx') => {
      if (!documentId) {
        message.warning('请选择要导出的文档');
        return;
      }

      try {
        setExporting(true);
        await exportSingleDocument(documentId, format);
        message.success('文档导出已开始');
        onExportComplete?.();
      } catch (error) {
        message.error('导出失败');
      } finally {
        setExporting(false);
      }
    },
    [documentId, onExportComplete],
  );

  /** 导出全部文档为ZIP */
  const handleExportAll = useCallback(async () => {
    // 检查是否有未确认的文档
    const unconfirmedDocs = documents.filter((d) => d.status !== 'confirmed');
    if (unconfirmedDocs.length > 0 && !exportOptions.forceExport) {
      Modal.confirm({
        title: '存在未确认文档',
        content: (
          <div>
            <p>当前有 {unconfirmedDocs.length} 个文档尚未确认，是否继续导出？</p>
            <p style={{ color: '#999', fontSize: 12 }}>
              未确认的文档可能包含未审核的内容。
            </p>
          </div>
        ),
        okText: '继续导出',
        cancelText: '取消',
        onOk: () => startExport(),
      });
      return;
    }

    await startExport();
  }, [documents, exportOptions.forceExport]);

  /** 开始导出 */
  const startExport = useCallback(async () => {
    try {
      setExporting(true);
      setProgressVisible(true);
      setExportStatus(null);

      const status = await exportProjectDocuments(projectId, exportOptions);
      setExportStatus(status);

      // 开始轮询状态
      if (status.taskId) {
        pollExportStatus(status.taskId);
      }
    } catch (error) {
      message.error('导出失败');
      setProgressVisible(false);
    } finally {
      setExporting(false);
    }
  }, [projectId, exportOptions, pollExportStatus]);

  /** 下拉菜单项 */
  const menuItems: MenuProps['items'] = documentId
    ? [
        {
          key: 'docx',
          icon: <FileWordOutlined />,
          label: '导出为 Word',
          onClick: () => handleExportSingle('docx'),
        },
        {
          key: 'pdf',
          icon: <FilePdfOutlined />,
          label: '导出为 PDF',
          onClick: () => handleExportSingle('pdf'),
        },
        { type: 'divider' },
        {
          key: 'settings',
          icon: <SettingOutlined />,
          label: '导出设置',
          onClick: () => setOptionsVisible(true),
        },
      ]
    : [
        {
          key: 'all',
          icon: <FileZipOutlined />,
          label: '导出全部文档为 ZIP',
          onClick: handleExportAll,
        },
        { type: 'divider' },
        {
          key: 'settings',
          icon: <SettingOutlined />,
          label: '导出设置',
          onClick: () => setOptionsVisible(true),
        },
      ];

  /** 处理导出完成 */
  const handleExportComplete = useCallback(() => {
    message.success('导出完成');
    onExportComplete?.();
  }, [onExportComplete]);

  // 单按钮模式（不显示下拉）
  if (!showDropdown) {
    return (
      <>
        <Tooltip title={documentId ? '导出当前文档' : '导出全部文档'}>
          <Button
            type={type}
            size={size}
            icon={<DownloadOutlined />}
            loading={exporting}
            disabled={disabled}
            onClick={documentId ? () => handleExportSingle() : handleExportAll}
          >
            {buttonText || '导出'}
          </Button>
        </Tooltip>

        <Modal
          open={optionsVisible}
          title="导出设置"
          onCancel={() => setOptionsVisible(false)}
          onOk={() => setOptionsVisible(false)}
          okText="确定"
        >
          <ExportOptionsForm options={exportOptions} onChange={setExportOptions} />
        </Modal>

        <ExportProgressModal
          visible={progressVisible}
          status={exportStatus}
          onClose={() => setProgressVisible(false)}
          onComplete={handleExportComplete}
        />
      </>
    );
  }

  return (
    <>
      <Dropdown menu={{ items: menuItems }} disabled={disabled || exporting}>
        <Button type={type} size={size} icon={<DownloadOutlined />} loading={exporting} disabled={disabled}>
          {buttonText || '导出'} 
        </Button>
      </Dropdown>

      <Modal
        open={optionsVisible}
        title="导出设置"
        onCancel={() => setOptionsVisible(false)}
        onOk={() => setOptionsVisible(false)}
        okText="确定"
      >
        <ExportOptionsForm options={exportOptions} onChange={setExportOptions} />
      </Modal>

      <ExportProgressModal
        visible={progressVisible}
        status={exportStatus}
        onClose={() => setProgressVisible(false)}
        onComplete={handleExportComplete}
      />
    </>
  );
};

export default ExportButton;
