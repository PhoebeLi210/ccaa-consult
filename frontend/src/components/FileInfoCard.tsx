import React from 'react';
import { Card, Tag, Space, Typography } from 'antd';
import {
  FileOutlined,
  FileExcelOutlined,
  FileWordOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import type { UploadFileInfo } from '@/api';

const { Text, Paragraph } = Typography;

/** 文件信息卡片属性 */
interface FileInfoCardProps {
  /** 文件信息 */
  file: UploadFileInfo;
  /** 预览回调 */
  onPreview?: (file: UploadFileInfo) => void;
  /** 删除回调 */
  onDelete?: (fileId: string) => void;
}

/** 根据文件类型返回对应图标 */
const getFileIcon = (fileType: string) => {
  if (fileType.includes('excel') || fileType.includes('spreadsheet') || fileType.endsWith('.xlsx') || fileType.endsWith('.xls')) {
    return <FileExcelOutlined style={{ fontSize: 28, color: '#52c41a' }} />;
  }
  if (fileType.includes('word') || fileType.includes('document') || fileType.endsWith('.docx') || fileType.endsWith('.doc')) {
    return <FileWordOutlined style={{ fontSize: 28, color: '#1677ff' }} />;
  }
  if (fileType.includes('pdf') || fileType.endsWith('.pdf')) {
    return <FilePdfOutlined style={{ fontSize: 28, color: '#ff4d4f' }} />;
  }
  if (fileType.startsWith('image/')) {
    return <FileImageOutlined style={{ fontSize: 28, color: '#faad14' }} />;
  }
  return <FileOutlined style={{ fontSize: 28, color: '#8c8c8c' }} />;
};

/** 格式化文件大小 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/** 获取上传状态标签 */
const getStatusTag = (status: UploadFileInfo['status']) => {
  switch (status) {
    case 'uploading':
      return <Tag color="processing">上传中</Tag>;
    case 'success':
      return <Tag color="success">已完成</Tag>;
    case 'error':
      return <Tag color="error">失败</Tag>;
    default:
      return null;
  }
};

/**
 * 文件信息卡片组件
 * 展示文件图标、名称、大小、上传状态
 * 支持预览和删除操作
 */
const FileInfoCard: React.FC<FileInfoCardProps> = ({
  file,
  onPreview,
  onDelete,
}) => {
  return (
    <Card
      size="small"
      hoverable
      style={{ marginBottom: 8 }}
      actions={
        file.status === 'success'
          ? [
              <EyeOutlined key="preview" onClick={() => onPreview?.(file)} />,
              <DeleteOutlined key="delete" onClick={() => onDelete?.(file.id)} />,
            ]
          : undefined
      }
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        {/* 文件图标 */}
        <div style={{ flexShrink: 0 }}>{getFileIcon(file.type)}</div>

        {/* 文件信息 */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <Paragraph
            ellipsis={{ rows: 1 }}
            style={{ marginBottom: 4, fontSize: 14, fontWeight: 500 }}
          >
            {file.name}
          </Paragraph>
          <Space size={8}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {formatFileSize(file.size)}
            </Text>
            {getStatusTag(file.status)}
          </Space>

          {/* 上传进度条 */}
          {file.status === 'uploading' && (
            <div
              style={{
                marginTop: 6,
                height: 4,
                backgroundColor: '#f0f0f0',
                borderRadius: 2,
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${file.progress}%`,
                  backgroundColor: '#1677ff',
                  borderRadius: 2,
                  transition: 'width 0.3s',
                }}
              />
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default FileInfoCard;
