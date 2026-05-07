import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { NavBar, Button, Toast, Dialog, List, Tag } from 'antd-mobile';
import { Card, Button as AntButton, Table, Descriptions, Tag as AntTag, Space, message, Modal, Form, Input } from 'antd';
import { EditOutlined, FileTextOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { useProject } from '@/hooks/useProject';

/** 字段中文名映射 */
const fieldLabels: Record<string, string> = {
  companyName: '公司名称',
  industry: '所属行业',
  employeeCount: '员工人数',
  registeredCapital: '注册资本',
  address: '公司地址',
  contactPerson: '联系人',
  contactPhone: '联系电话',
  businessScope: '经营范围',
  status: '项目状态',
};

/** 项目状态映射 */
const statusMap: Record<string, { text: string; color: string }> = {
  draft: { text: '草稿', color: 'default' },
  in_progress: { text: '进行中', color: 'processing' },
  completed: { text: '已完成', color: 'success' },
};

/** 项目详情页面 */
const ProjectDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { isMobile } = useResponsive();
  const navigate = useNavigate();
  const {
    currentProject,
    loading,
    fetchProjectDetail,
    editProject,
    generateProjectDocuments,
  } = useProject();

  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (id) {
      fetchProjectDetail(id);
    }
  }, [id, fetchProjectDetail]);

  /** 开始编辑字段 */
  const handleEdit = useCallback((field: string, currentValue: string) => {
    setEditingField(field);
    setEditValue(currentValue);
  }, []);

  /** 保存编辑 */
  const handleSave = useCallback(async () => {
    if (!editingField || !id) return;
    try {
      await editProject(id, { [editingField]: editValue });
      setEditingField(null);
      Toast.show({ content: '保存成功', icon: 'success' });
    } catch {
      Toast.show({ content: '保存失败', icon: 'fail' });
    }
  }, [editingField, editValue, id, editProject]);

  /** 生成文档 */
  const handleGenerate = useCallback(async () => {
    if (!id) return;
    Dialog.confirm({
      content: '确定要生成项目文档吗？',
      onConfirm: async () => {
        setGenerating(true);
        try {
          await generateProjectDocuments(id);
          Toast.show({ content: '文档生成成功', icon: 'success' });
          navigate(`/project/${id}/documents`);
        } catch {
          Toast.show({ content: '文档生成失败', icon: 'fail' });
        } finally {
          setGenerating(false);
        }
      },
    });
  }, [id, generateProjectDocuments, navigate]);

  /** 获取缺失字段列表 */
  const getMissingFields = (): string[] => {
    if (!currentProject) return [];
    const missing: string[] = [];
    const checkFields = ['companyName', 'industry', 'employeeCount', 'registeredCapital', 'address', 'contactPerson', 'contactPhone'];
    checkFields.forEach((field) => {
      const value = (currentProject as Record<string, unknown>)[field];
      if (!value || value === '') {
        missing.push(field);
      }
    });
    return missing;
  };

  const missingFields = getMissingFields();

  /* ==================== 移动端渲染 ==================== */
  if (isMobile) {
    return (
      <div>
        <NavBar
          onBack={() => navigate(-1)}
          right={
            <Space>
              <Button
                size="small"
                color="primary"
                fill="outline"
                onClick={() => navigate(`/project/${id}/documents`)}
              >
                文档
              </Button>
            </Space>
          }
          style={{ backgroundColor: '#1677ff', color: '#fff' }}
        >
          项目详情
        </NavBar>

        <div style={{ padding: 12 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
              加载中...
            </div>
          ) : currentProject ? (
            <>
              {/* 缺失字段追问列表 */}
              {missingFields.length > 0 && (
                <div
                  style={{
                    padding: '10px 12px',
                    backgroundColor: '#fff7e6',
                    border: '1px solid #ffd591',
                    borderRadius: 6,
                    marginBottom: 12,
                    fontSize: 13,
                    color: '#d46b08',
                  }}
                >
                  <div style={{ fontWeight: 500, marginBottom: 6 }}>
                    以下信息缺失，建议补充：
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                    {missingFields.map((f) => (
                      <Tag
                        key={f}
                        color="warning"
                        onClick={() => handleEdit(f, '')}
                        style={{ cursor: 'pointer' }}
                      >
                        {fieldLabels[f]}
                      </Tag>
                    ))}
                  </div>
                </div>
              )}

              {/* 企业信息表格 */}
              <List header="企业信息">
                {Object.entries(fieldLabels).map(([key, label]) => {
                  if (key === 'status') return null;
                  const value = (currentProject as Record<string, unknown>)[key] as string;
                  const isMissing = missingFields.includes(key);

                  return (
                    <List.Item
                      key={key}
                      extra={
                        editingField === key ? (
                          <Space>
                            <input
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              style={{
                                border: '1px solid #d9d9d9',
                                borderRadius: 4,
                                padding: '2px 8px',
                                fontSize: 13,
                                width: 140,
                              }}
                              autoFocus
                            />
                            <Button
                              size="mini"
                              color="primary"
                              onClick={handleSave}
                            >
                              保存
                            </Button>
                          </Space>
                        ) : (
                          <span
                            onClick={() => handleEdit(key, value || '')}
                            style={{
                              color: isMissing ? '#ff4d4f' : '#333',
                              cursor: 'pointer',
                              fontSize: 13,
                            }}
                          >
                            {value || <span style={{ color: '#ccc' }}>点击补充</span>}
                          </span>
                        )
                      }
                    >
                      <span style={{ color: isMissing ? '#ff4d4f' : '#666', fontSize: 14 }}>
                        {label}
                        {isMissing && <span style={{ marginLeft: 2, color: '#ff4d4f' }}>*</span>}
                      </span>
                    </List.Item>
                  );
                })}
              </List>

              {/* 状态信息 */}
              <List header="项目状态" style={{ marginTop: 12 }}>
                <List.Item
                  extra={
                    <AntTag color={statusMap[currentProject.status]?.color || 'default'}>
                      {statusMap[currentProject.status]?.text || '未知'}
                    </AntTag>
                  }
                >
                  当前状态
                </List.Item>
                <List.Item extra={currentProject.createdAt}>创建时间</List.Item>
                <List.Item extra={currentProject.updatedAt}>更新时间</List.Item>
              </List>

              {/* 生成文档按钮 */}
              <Button
                block
                color="primary"
                size="large"
                icon={<FileTextOutlined />}
                loading={generating}
                onClick={handleGenerate}
                style={{ marginTop: 20 }}
              >
                生成文档
              </Button>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
              项目不存在
            </div>
          )}
        </div>
      </div>
    );
  }

  /* ==================== PC端渲染 ==================== */
  const infoFields = Object.entries(fieldLabels).filter(([key]) => key !== 'status');

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Space>
          <AntButton icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
            返回
          </AntButton>
          <h2 style={{ margin: 0 }}>{currentProject?.companyName || '项目详情'}</h2>
          {currentProject && (
            <AntTag color={statusMap[currentProject.status]?.color || 'default'}>
              {statusMap[currentProject.status]?.text || '未知'}
            </AntTag>
          )}
        </Space>
        <Space>
          <AntButton
            type="primary"
            icon={<FileTextOutlined />}
            loading={generating}
            onClick={handleGenerate}
          >
            生成文档
          </AntButton>
          <AntButton onClick={() => navigate(`/project/${id}/documents`)}>
            管理文档
          </AntButton>
        </Space>
      </div>

      {/* 缺失字段提示 */}
      {missingFields.length > 0 && (
        <div
          style={{
            padding: '10px 16px',
            backgroundColor: '#fff7e6',
            border: '1px solid #ffd591',
            borderRadius: 6,
            marginBottom: 16,
            color: '#d46b08',
          }}
        >
          以下信息缺失，建议补充：{missingFields.map((f) => fieldLabels[f]).join('、')}
        </div>
      )}

      <Card title="企业信息" loading={loading}>
        {currentProject && (
          <Descriptions bordered column={2}>
            {infoFields.map(([key, label]) => {
              const value = (currentProject as Record<string, unknown>)[key] as string;
              const isMissing = missingFields.includes(key);

              return (
                <Descriptions.Item
                  key={key}
                  label={
                    <span>
                      {label}
                      {isMissing && <span style={{ color: '#ff4d4f', marginLeft: 4 }}>*</span>}
                    </span>
                  }
                >
                  {editingField === key ? (
                    <Space>
                      <Input
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onPressEnter={handleSave}
                        size="small"
                        style={{ width: 200 }}
                        autoFocus
                      />
                      <AntButton type="link" size="small" onClick={handleSave}>
                        保存
                      </AntButton>
                      <AntButton type="link" size="small" onClick={() => setEditingField(null)}>
                        取消
                      </AntButton>
                    </Space>
                  ) : (
                    <Space>
                      <span style={{ color: isMissing ? '#ff4d4f' : undefined }}>
                        {value || <span style={{ color: '#ccc' }}>暂无</span>}
                      </span>
                      <AntButton
                        type="link"
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => handleEdit(key, value || '')}
                      />
                    </Space>
                  )}
                </Descriptions.Item>
              );
            })}
          </Descriptions>
        )}
      </Card>
    </div>
  );
};

export default ProjectDetailPage;
