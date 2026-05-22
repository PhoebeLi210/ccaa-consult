import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Card,
  Upload,
  Button,
  message,
  Select,
  Progress,
  List,
  Tag,
  Empty,
  Spin,
  Tooltip,
  Popconfirm,
} from 'antd';
import {
  UploadOutlined,
  FileOutlined,
  TeamOutlined,
  ToolOutlined,
  NodeIndexOutlined,
  EnvironmentOutlined,
  SafetyCertificateOutlined,
  FileProtectOutlined,
  DeleteOutlined,
  ReloadOutlined,
  EyeOutlined,
  ArrowLeftOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import { useResponsive } from '../../hooks/useResponsive';
import {
  getMaterialTypes,
  uploadMaterial,
  getProjectMaterials,
  deleteMaterial,
  reprocessMaterial,
  MaterialTypeConfig,
  MaterialInfo,
} from '../../api';
import styles from './upload.module.css';

const { Dragger } = Upload;
const { Option } = Select;

/**
 * 材料类型图标映射
 */
const materialTypeIcons: Record<string, React.ReactNode> = {
  org_chart: <TeamOutlined />,
  equipment_list: <ToolOutlined />,
  process_flow: <NodeIndexOutlined />,
  site_layout: <EnvironmentOutlined />,
  license_cert: <SafetyCertificateOutlined />,
  previous_cert: <FileProtectOutlined />,
  other: <FileOutlined />,
};

/**
 * 材料类型颜色映射
 */
const materialTypeColors: Record<string, string> = {
  org_chart: 'blue',
  equipment_list: 'green',
  process_flow: 'purple',
  site_layout: 'orange',
  license_cert: 'red',
  previous_cert: 'cyan',
  other: 'default',
};

/**
 * 补充材料上传页面
 */
const MaterialsUploadPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isMobile } = useResponsive();
  const projectId = searchParams.get('projectId');

  // 状态管理
  const [materialTypes, setMaterialTypes] = useState<MaterialTypeConfig[]>([]);
  const [selectedType, setSelectedType] = useState<string>('');
  const [materials, setMaterials] = useState<MaterialInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [fetchingMaterials, setFetchingMaterials] = useState(false);

  // 加载材料类型
  useEffect(() => {
    fetchMaterialTypes();
  }, []);

  // 加载项目材料列表
  useEffect(() => {
    if (projectId) {
      fetchProjectMaterials();
    }
  }, [projectId]);

  /**
   * 获取材料类型列表
   */
  const fetchMaterialTypes = async () => {
    try {
      const types = await getMaterialTypes();
      setMaterialTypes(types);
      if (types.length > 0) {
        setSelectedType(types[0].type);
      }
    } catch (error) {
      message.error('获取材料类型失败');
      console.error('Fetch material types error:', error);
    }
  };

  /**
   * 获取项目材料列表
   */
  const fetchProjectMaterials = async () => {
    if (!projectId) return;
    
    setFetchingMaterials(true);
    try {
      const response = await getProjectMaterials(projectId);
      setMaterials(response.materials);
    } catch (error) {
      message.error('获取材料列表失败');
      console.error('Fetch materials error:', error);
    } finally {
      setFetchingMaterials(false);
    }
  };

  /**
   * 处理文件上传
   */
  const handleUpload = async (file: File) => {
    if (!projectId) {
      message.warning('请先选择项目');
      return false;
    }

    if (!selectedType) {
      message.warning('请选择材料类型');
      return false;
    }

    const fileId = `${Date.now()}-${file.name}`;
    setUploadProgress((prev) => ({ ...prev, [fileId]: 0 }));

    try {
      const response = await uploadMaterial(
        projectId,
        selectedType,
        file,
        (progress) => {
          setUploadProgress((prev) => ({ ...prev, [fileId]: progress }));
        }
      );

      message.success(`${file.name} 上传成功`);
      
      // 刷新材料列表
      await fetchProjectMaterials();
      
      // 清除进度
      setUploadProgress((prev) => {
        const newProgress = { ...prev };
        delete newProgress[fileId];
        return newProgress;
      });

      return false; // 阻止默认上传行为
    } catch (error) {
      message.error(`${file.name} 上传失败`);
      console.error('Upload error:', error);
      
      setUploadProgress((prev) => {
        const newProgress = { ...prev };
        delete newProgress[fileId];
        return newProgress;
      });
      
      return false;
    }
  };

  /**
   * 删除材料
   */
  const handleDelete = async (materialId: string) => {
    try {
      await deleteMaterial(materialId);
      message.success('删除成功');
      await fetchProjectMaterials();
    } catch (error) {
      message.error('删除失败');
      console.error('Delete error:', error);
    }
  };

  /**
   * 重新处理材料
   */
  const handleReprocess = async (materialId: string) => {
    setLoading(true);
    try {
      await reprocessMaterial(materialId);
      message.success('重新处理完成');
      await fetchProjectMaterials();
    } catch (error) {
      message.error('重新处理失败');
      console.error('Reprocess error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 格式化文件大小
   */
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  /**
   * 获取材料类型名称
   */
  const getMaterialTypeName = (type: string) => {
    const config = materialTypes.find((t) => t.type === type);
    return config?.name || type;
  };

  /**
   * 渲染上传区域
   */
  const renderUploadArea = () => {
    const selectedConfig = materialTypes.find((t) => t.type === selectedType);

    return (
      <Card className={styles.uploadCard} title="上传补充材料">
        <div className={styles.typeSelector}>
          <span className={styles.label}>材料类型：</span>
          <Select
            value={selectedType}
            onChange={setSelectedType}
            style={{ width: isMobile ? '100%' : 300 }}
            placeholder="选择材料类型"
          >
            {materialTypes.map((type) => (
              <Option key={type.type} value={type.type}>
                <span style={{ marginRight: 8 }}>
                  {materialTypeIcons[type.type]}
                </span>
                {type.name}
              </Option>
            ))}
          </Select>
        </div>

        {selectedConfig && (
          <div className={styles.typeInfo}>
            <p className={styles.typeDescription}>{selectedConfig.description}</p>
            <div className={styles.typeMeta}>
              <Tag color="blue">
                最大 {selectedConfig.max_size_mb}MB
              </Tag>
              <span className={styles.extensions}>
                支持格式：{selectedConfig.allowed_extensions.join(', ')}
              </span>
            </div>
          </div>
        )}

        <Dragger
          accept={selectedConfig?.allowed_extensions.join(',')}
          beforeUpload={handleUpload}
          showUploadList={false}
          disabled={!projectId || !selectedType}
          className={styles.dragger}
        >
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持单次上传一个文件，文件大小不超过{selectedConfig?.max_size_mb || 10}MB
          </p>
        </Dragger>

        {/* 上传进度 */}
        {Object.entries(uploadProgress).map(([fileId, progress]) => (
          <div key={fileId} className={styles.progressItem}>
            <span className={styles.progressFileName}>
              {fileId.split('-').slice(1).join('-')}
            </span>
            <Progress percent={progress} size="small" />
          </div>
        ))}
      </Card>
    );
  };

  /**
   * 渲染材料列表
   */
  const renderMaterialsList = () => {
    if (fetchingMaterials) {
      return (
        <Card className={styles.listCard}>
          <div className={styles.loadingContainer}>
            <Spin size="large" tip="加载中..." />
          </div>
        </Card>
      );
    }

    return (
      <Card
        className={styles.listCard}
        title={
          <span>
            已上传材料
            <Tag color="blue" style={{ marginLeft: 8 }}>
              {materials.length}
            </Tag>
          </span>
        }
      >
        {materials.length === 0 ? (
          <Empty
            description={
              projectId ? '暂无上传的材料' : '请先选择项目'
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <List
            dataSource={materials}
            renderItem={(item) => (
              <List.Item
                className={styles.materialItem}
                actions={[
                  <Tooltip title="查看详情" key="view">
                    <Button
                      icon={<EyeOutlined />}
                      size="small"
                      onClick={() => {
                        // TODO: 实现查看详情
                        message.info('查看功能开发中');
                      }}
                    />
                  </Tooltip>,
                  <Tooltip title="重新处理" key="reprocess">
                    <Button
                      icon={<ReloadOutlined />}
                      size="small"
                      onClick={() => handleReprocess(item.materialId)}
                      loading={loading}
                    />
                  </Tooltip>,
                  <Popconfirm
                    key="delete"
                    title="确认删除"
                    description="删除后无法恢复，是否继续？"
                    onConfirm={() => handleDelete(item.materialId)}
                    okText="删除"
                    cancelText="取消"
                    okButtonProps={{ danger: true }}
                  >
                    <Button
                      icon={<DeleteOutlined />}
                      size="small"
                      danger
                    />
                  </Popconfirm>,
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <div
                      className={styles.materialIcon}
                      style={{
                        color: `var(--ant-${materialTypeColors[item.materialType]}-color)`,
                      }}
                    >
                      {materialTypeIcons[item.materialType] || <FileOutlined />}
                    </div>
                  }
                  title={
                    <div className={styles.materialTitle}>
                      <span className={styles.fileName}>{item.fileName}</span>
                      <Tag
                        color={materialTypeColors[item.materialType]}
                        size="small"
                      >
                        {getMaterialTypeName(item.materialType)}
                      </Tag>
                    </div>
                  }
                  description={
                    <div className={styles.materialMeta}>
                      <span>{formatFileSize(item.fileSize)}</span>
                      <span className={styles.separator}>|</span>
                      <span>
                        {new Date(item.uploadedAt).toLocaleDateString()}
                      </span>
                      <span className={styles.separator}>|</span>
                      <Tag
                        color={
                          item.status === 'completed'
                            ? 'success'
                            : item.status === 'processing'
                            ? 'processing'
                            : 'default'
                        }
                        size="small"
                      >
                        {item.status === 'completed'
                          ? '已完成'
                          : item.status === 'processing'
                          ? '处理中'
                          : '待处理'}
                      </Tag>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    );
  };

  return (
    <div className={styles.container}>
      {/* 页面头部 */}
      <div className={styles.header}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
          className={styles.backButton}
        >
          返回
        </Button>
        <h1 className={styles.title}>补充材料上传</h1>
        {projectId && (
          <Tag color="blue" className={styles.projectTag}>
            项目ID: {projectId}
          </Tag>
        )}
      </div>

      {/* 主要内容 */}
      <div className={styles.content}>
        {renderUploadArea()}
        {renderMaterialsList()}
      </div>
    </div>
  );
};

export default MaterialsUploadPage;
