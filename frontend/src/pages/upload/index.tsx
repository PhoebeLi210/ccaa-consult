import React, { useState, useCallback, useRef } from 'react';
import { NavBar, Toast, List } from 'antd-mobile';
import {
  Upload,
  Button as AntButton,
  Card,
  message,
  Upload as AntUpload,
  Progress,
  Space,
  Empty as AntEmpty,
  Typography,
} from 'antd';
import { InboxOutlined, DeleteOutlined, CloudUploadOutlined, FileOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { uploadFile, getUploadedFiles, type UploadFileInfo } from '@/api';
import FileInfoCard from '@/components/FileInfoCard';

const { Dragger } = Upload;
const { Text } = Typography;

/** 允许上传的文件类型 */
const ACCEPT_TYPES = [
  '.xlsx',
  '.xls',
  '.docx',
  '.doc',
  '.pdf',
  '.png',
  '.jpg',
  '.jpeg',
  '.gif',
  '.bmp',
].join(',');

/** 允许上传的MIME类型 */
const ACCEPT_MIME = [
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword',
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/gif',
  'image/bmp',
].join(',');

/** 最大文件大小：50MB */
const MAX_FILE_SIZE = 50 * 1024 * 1024;

/** 文件上传页面（PC端核心页面） */
const UploadPage: React.FC = () => {
  const { isMobile } = useResponsive();
  const [fileList, setFileList] = useState<UploadFileInfo[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  /** 上传单个文件 */
  const handleUpload = useCallback(async (file: File) => {
    // 校验文件大小
    if (file.size > MAX_FILE_SIZE) {
      message.error(`文件 ${file.name} 超过50MB限制`);
      return;
    }

    // 创建文件记录
    const fileRecord: UploadFileInfo = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      name: file.name,
      size: file.size,
      type: file.type || file.name.split('.').pop() || '',
      url: '',
      status: 'uploading',
      progress: 0,
    };

    setFileList((prev) => [fileRecord, ...prev]);

    try {
      const result = await uploadFile(file, (progress) => {
        // 更新上传进度
        setFileList((prev) =>
          prev.map((f) =>
            f.id === fileRecord.id ? { ...f, progress } : f,
          ),
        );
      });

      // 上传成功，更新文件记录
      setFileList((prev) =>
        prev.map((f) =>
          f.id === fileRecord.id
            ? {
                ...f,
                status: 'success',
                url: result.url || '',
                progress: 100,
              }
            : f,
        ),
      );
      message.success(`${file.name} 上传成功`);
    } catch {
      // 上传失败
      setFileList((prev) =>
        prev.map((f) =>
          f.id === fileRecord.id ? { ...f, status: 'error' } : f,
        ),
      );
      message.error(`${file.name} 上传失败`);
    }
  }, []);

  /** 批量上传文件 */
  const handleBatchUpload = useCallback(
    async (files: FileList | File[]) => {
      setUploading(true);
      const fileArray = Array.from(files);
      for (const file of fileArray) {
        await handleUpload(file);
      }
      setUploading(false);
    },
    [handleUpload],
  );

  /** 删除文件记录 */
  const handleDelete = useCallback((fileId: string) => {
    setFileList((prev) => prev.filter((f) => f.id !== fileId));
  }, []);

  /** 预览文件 */
  const handlePreview = useCallback((file: UploadFileInfo) => {
    if (file.url) {
      window.open(file.url, '_blank');
    } else {
      message.info('文件尚未上传完成');
    }
  }, []);

  /** 拖拽上传处理 */
  const dropHandler = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleBatchUpload(files);
      }
    },
    [handleBatchUpload],
  );

  /** 拖拽经过处理 */
  const dragOverHandler = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  /** 文件输入变化处理 */
  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        handleBatchUpload(files);
      }
      // 重置input以允许重复选择同一文件
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    [handleBatchUpload],
  );

  /** 上传统计 */
  const successCount = fileList.filter((f) => f.status === 'success').length;
  const errorCount = fileList.filter((f) => f.status === 'error').length;
  const uploadingCount = fileList.filter((f) => f.status === 'uploading').length;

  /* ==================== 移动端渲染 ==================== */
  if (isMobile) {
    return (
      <div>
        <NavBar style={{ backgroundColor: '#1677ff', color: '#fff' }}>
          文件上传
        </NavBar>

        <div style={{ padding: 12 }}>
          {/* 上传区域 */}
          <div
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: '2px dashed #d9d9d9',
              borderRadius: 8,
              padding: '32px 16px',
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: '#fafafa',
              marginBottom: 16,
            }}
          >
            <CloudUploadOutlined style={{ fontSize: 36, color: '#1677ff', marginBottom: 8 }} />
            <div style={{ fontSize: 14, color: '#666' }}>点击选择文件上传</div>
            <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
              支持 Excel/Word/PDF/图片，单文件不超过50MB
            </div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={ACCEPT_TYPES}
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
          />

          {/* 上传统计 */}
          {fileList.length > 0 && (
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-around',
                padding: '8px 0',
                marginBottom: 12,
                backgroundColor: '#fff',
                borderRadius: 8,
                fontSize: 13,
              }}
            >
              <span>成功: {successCount}</span>
              <span>失败: {errorCount}</span>
              <span>上传中: {uploadingCount}</span>
            </div>
          )}

          {/* 文件列表 */}
          {fileList.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
              <FileOutlined style={{ fontSize: 32, marginBottom: 8 }} />
              <div>暂无文件</div>
            </div>
          ) : (
            fileList.map((file) => (
              <FileInfoCard
                key={file.id}
                file={file}
                onPreview={handlePreview}
                onDelete={handleDelete}
              />
            ))
          )}
        </div>
      </div>
    );
  }

  /* ==================== PC端渲染 ==================== */
  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>文件上传</h2>
        <Text type="secondary" style={{ fontSize: 13 }}>
          支持 Excel、Word、PDF、图片格式，单文件不超过50MB
        </Text>
      </div>

      {/* 拖拽上传区域 */}
      <Card style={{ marginBottom: 16 }}>
        <Dragger
          multiple
          accept={ACCEPT_MIME}
          showUploadList={false}
          customRequest={({ file }) => {
            handleUpload(file as File);
          }}
          style={{
            padding: '40px 20px',
          }}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: 48, color: '#1677ff' }} />
          </p>
          <p className="ant-upload-text" style={{ fontSize: 16 }}>
            点击或拖拽文件到此区域上传
          </p>
          <p className="ant-upload-hint" style={{ fontSize: 13 }}>
            支持批量上传 Excel(.xlsx/.xls)、Word(.docx/.doc)、PDF(.pdf)、图片(.png/.jpg/.gif) 格式文件
          </p>
        </Dragger>
      </Card>

      {/* 上传统计 */}
      {fileList.length > 0 && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 16,
          }}
        >
          <Space>
            <Text>共 {fileList.length} 个文件</Text>
            <Text type="success">成功 {successCount}</Text>
            {errorCount > 0 && <Text type="danger">失败 {errorCount}</Text>}
            {uploadingCount > 0 && <Text type="warning">上传中 {uploadingCount}</Text>}
          </Space>
          <Space>
            <AntButton
              onClick={() => fileInputRef.current?.click()}
              icon={<CloudUploadOutlined />}
            >
              继续上传
            </AntButton>
            {errorCount > 0 && (
              <AntButton danger onClick={() => setFileList((prev) => prev.filter((f) => f.status !== 'error'))}>
                清除失败项
              </AntButton>
            )}
          </Space>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={ACCEPT_TYPES}
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
      />

      {/* 已上传文件列表 */}
      <Card title="已上传文件">
        {fileList.length === 0 ? (
          <AntEmpty description="暂无文件" />
        ) : (
          fileList.map((file) => (
            <FileInfoCard
              key={file.id}
              file={file}
              onPreview={handlePreview}
              onDelete={handleDelete}
            />
          ))
        )}
      </Card>
    </div>
  );
};

export default UploadPage;
