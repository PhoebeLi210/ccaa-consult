import React, { useState, useCallback, useEffect } from 'react';
import { Card, Upload, Button, List, Tag, Space, message, Progress, Typography, Empty } from 'antd';
import { InboxOutlined, DeleteOutlined, FileOutlined, CloudUploadOutlined } from '@ant-design/icons';
import { uploadFile, getUploadedFiles, type UploadFileInfo } from '@/api';

const { Dragger } = Upload;
const { Text } = Typography;

const ACCEPT_TYPES = ['.xlsx', '.xls', '.docx', '.doc', '.pdf', '.png', '.jpg', '.jpeg'].join(',');
const MAX_FILE_SIZE = 50 * 1024 * 1024;

interface UploadSectionProps {
  projectId: string;
}

const UploadSection: React.FC<UploadSectionProps> = ({ projectId }) => {
  const [fileList, setFileList] = useState<UploadFileInfo[]>([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (projectId) {
      loadFiles();
    }
  }, [projectId]);

  const loadFiles = async () => {
    try {
      const files = await getUploadedFiles(projectId);
      setFileList(files);
    } catch {
      // ignore
    }
  };

  const handleUpload = useCallback(async (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      message.error(`文件 ${file.name} 超过50MB限制`);
      return false;
    }

    setUploading(true);
    try {
      await uploadFile(projectId, file);
      message.success(`${file.name} 上传成功`);
      loadFiles();
    } catch (err: any) {
      message.error(err.message || '上传失败');
    } finally {
      setUploading(false);
    }
    return false;
  }, [projectId]);

  return (
    <Card
      title={
        <Space>
          <CloudUploadOutlined />
          <span>企业资料上传</span>
        </Space>
      }
      size="small"
      style={{ marginTop: 16 }}
    >
      <Dragger
        name="file"
        multiple
        accept={ACCEPT_TYPES}
        beforeUpload={handleUpload}
        showUploadList={false}
        disabled={uploading}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">
          支持 Excel、Word、PDF、图片等格式，单个文件最大 50MB
        </p>
      </Dragger>

      {fileList.length > 0 ? (
        <List
          size="small"
          style={{ marginTop: 16 }}
          dataSource={fileList}
          renderItem={(file) => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  danger
                  size="small"
                  icon={<DeleteOutlined />}
                  onClick={async () => {
                    try {
                      // await deleteFile(file.id);
                      setFileList((prev) => prev.filter((f) => f.id !== file.id));
                      message.success('已删除');
                    } catch {
                      message.error('删除失败');
                    }
                  }}
                >
                  删除
                </Button>,
              ]}
            >
              <List.Item.Meta
                avatar={<FileOutlined style={{ fontSize: 16, color: '#1890ff' }} />}
                title={<Text style={{ fontSize: 13 }}>{file.name}</Text>}
                description={
                  <Space size={4}>
                    <Tag color="blue">{(file.size / 1024).toFixed(1)} KB</Tag>
                    <Tag color={file.status === 'success' ? 'green' : 'orange'}>
                      {file.status === 'success' ? '已上传' : '上传中'}
                    </Tag>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无上传文件"
          style={{ marginTop: 16 }}
        />
      )}

      <div style={{ marginTop: 12, padding: '8px 12px', background: '#f6f8fa', borderRadius: 6 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          建议上传：营业执照、组织架构图、设备清单、工艺流程图、现有体系文件等
        </Text>
      </div>
    </Card>
  );
};

export default UploadSection;
