import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { NavBar, Button, Toast, Dialog, List, SwipeAction, Tag } from 'antd-mobile';
import { Card, Button as AntButton, Table, Space, Tag as AntTag, Checkbox, message, Empty as AntEmpty, Spin } from 'antd';
import { CheckOutlined, FileTextOutlined, ArrowLeftOutlined, DownloadOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { useProject } from '@/hooks/useProject';
import DocumentTree from '@/components/DocumentTree';
import ConfirmBadge from '@/components/ConfirmBadge';
import type { DocumentInfo } from '@/api';

/** 文档管理页面 */
const ProjectDocumentsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { isMobile } = useResponsive();
  const navigate = useNavigate();
  const {
    documents,
    loading,
    fetchDocuments,
    confirmSingleDocument,
    confirmMultipleDocuments,
  } = useProject();

  const [selectedDoc, setSelectedDoc] = useState<DocumentInfo | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    if (id) {
      fetchDocuments(id);
    }
  }, [id, fetchDocuments]);

  /** 选中单个文档 */
  const handleSelectDoc = useCallback((doc: DocumentInfo) => {
    setSelectedDoc(doc);
  }, []);

  /** 确认单个文档 */
  const handleConfirm = useCallback(
    async (docId: string) => {
      try {
        await confirmSingleDocument(docId);
        Toast.show({ content: '确认成功', icon: 'success' });
      } catch {
        Toast.show({ content: '确认失败', icon: 'fail' });
      }
    },
    [confirmSingleDocument],
  );

  /** 批量确认 */
  const handleBatchConfirm = useCallback(async () => {
    if (selectedIds.length === 0) {
      Toast.show({ content: '请先选择文档', icon: 'fail' });
      return;
    }
    Dialog.confirm({
      content: `确定确认选中的 ${selectedIds.length} 个文档？`,
      onConfirm: async () => {
        try {
          await confirmMultipleDocuments(selectedIds);
          Toast.show({ content: '批量确认成功', icon: 'success' });
          setSelectedIds([]);
        } catch {
          Toast.show({ content: '批量确认失败', icon: 'fail' });
        }
      },
    });
  }, [selectedIds, confirmMultipleDocuments]);

  /** 多选切换 */
  const handleSelectToggle = useCallback((docId: string, checked: boolean) => {
    setSelectedIds((prev) =>
      checked ? [...prev, docId] : prev.filter((id) => id !== docId),
    );
  }, []);

  /** 全选/取消全选 */
  const handleSelectAll = useCallback(
    (checked: boolean) => {
      if (checked) {
        setSelectedIds(documents.map((d) => d.id));
      } else {
        setSelectedIds([]);
      }
    },
    [documents],
  );

  /** 待确认文档数量 */
  const pendingCount = documents.filter((d) => d.status === 'pending').length;

  /* ==================== 移动端渲染 ==================== */
  if (isMobile) {
    return (
      <div>
        <NavBar
          onBack={() => navigate(-1)}
          right={
            <Button
              size="small"
              color="primary"
              disabled={selectedIds.length === 0}
              onClick={handleBatchConfirm}
            >
              批量确认{selectedIds.length > 0 ? `(${selectedIds.length})` : ''}
            </Button>
          }
          style={{ backgroundColor: '#1677ff', color: '#fff' }}
        >
          文档管理
        </NavBar>

        <div style={{ padding: 12 }}>
          {/* 统计信息 */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-around',
              padding: '12px 0',
              marginBottom: 12,
              backgroundColor: '#fff',
              borderRadius: 8,
            }}
          >
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
                {pendingCount}
              </div>
              <div style={{ fontSize: 12, color: '#999' }}>待确认</div>
            </div>
          </div>

          {/* 文档列表 */}
          {loading ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <Spin />
            </div>
          ) : documents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
              <FileTextOutlined style={{ fontSize: 32, marginBottom: 8 }} />
              <div>暂无文档</div>
              <Button
                size="small"
                color="primary"
                fill="outline"
                onClick={() => navigate(-1)}
                style={{ marginTop: 12 }}
              >
                返回生成文档
              </Button>
            </div>
          ) : (
            <List>
              {documents.map((doc) => (
                <SwipeAction
                  key={doc.id}
                  rightActions={[
                    {
                      key: 'confirm',
                      text: '确认',
                      color: 'primary',
                      onClick: () => handleConfirm(doc.id),
                    },
                  ]}
                >
                  <List.Item
                    onClick={() => setSelectedDoc(doc)}
                    prefix={
                      <Checkbox
                        checked={selectedIds.includes(doc.id)}
                        onChange={(val) => handleSelectToggle(doc.id, val)}
                      />
                    }
                    description={
                      <span style={{ fontSize: 12, color: '#999' }}>
                        {doc.createdAt}
                      </span>
                    }
                    extra={<ConfirmBadge status={doc.status} />}
                  >
                    <span style={{ fontSize: 14 }}>{doc.name}</span>
                  </List.Item>
                </SwipeAction>
              ))}
            </List>
          )}

          {/* 文档预览弹窗 */}
          {selectedDoc && (
            <Dialog
              visible
              title={selectedDoc.name}
              content={
                <div>
                  <div style={{ marginBottom: 12 }}>
                    <ConfirmBadge status={selectedDoc.status} />
                  </div>
                  <div style={{ fontSize: 13, color: '#666', lineHeight: 1.8 }}>
                    <p>文档类型：{selectedDoc.type}</p>
                    <p>创建时间：{selectedDoc.createdAt}</p>
                    <p>更新时间：{selectedDoc.updatedAt}</p>
                  </div>
                  {selectedDoc.url && (
                    <div style={{ marginTop: 12 }}>
                      <a
                        href={selectedDoc.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: '#1677ff' }}
                      >
                        在线预览
                      </a>
                    </div>
                  )}
                </div>
              }
              actions={[
                {
                  key: 'close',
                  text: '关闭',
                },
                ...(selectedDoc.status === 'pending'
                  ? [
                      {
                        key: 'confirm',
                        text: '确认',
                        bold: true,
                        onClick: () => {
                          handleConfirm(selectedDoc.id);
                          setSelectedDoc(null);
                        },
                      },
                    ]
                  : []),
              ]}
              onClose={() => setSelectedDoc(null)}
            />
          )}
        </div>
      </div>
    );
  }

  /* ==================== PC端渲染 ==================== */
  const columns = [
    {
      title: (
        <Checkbox
          checked={selectedIds.length === documents.length && documents.length > 0}
          indeterminate={selectedIds.length > 0 && selectedIds.length < documents.length}
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
        <a onClick={() => setSelectedDoc(record)}>{text}</a>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => <ConfirmBadge status={status as DocumentInfo['status']} />,
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: unknown, record: DocumentInfo) => (
        <Space>
          {record.url && (
            <AntButton type="link" size="small" icon={<DownloadOutlined />}>
              预览
            </AntButton>
          )}
          {record.status === 'pending' && (
            <AntButton
              type="link"
              size="small"
              icon={<CheckOutlined />}
              onClick={() => handleConfirm(record.id)}
            >
              确认
            </AntButton>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Space>
          <AntButton icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
            返回
          </AntButton>
          <h2 style={{ margin: 0 }}>文档管理</h2>
          <AntTag color="blue">共 {documents.length} 个</AntTag>
          {pendingCount > 0 && <AntTag color="warning">{pendingCount} 个待确认</AntTag>}
        </Space>
        <AntButton
          type="primary"
          icon={<CheckOutlined />}
          disabled={selectedIds.length === 0}
          onClick={handleBatchConfirm}
        >
          批量确认{selectedIds.length > 0 ? `(${selectedIds.length})` : ''}
        </AntButton>
      </div>

      <div style={{ display: 'flex', gap: 16, height: 'calc(100vh - 200px)' }}>
        {/* 左侧文档树 */}
        <Card
          title="文档目录"
          size="small"
          style={{ width: 280, flexShrink: 0, overflow: 'auto' }}
          bodyStyle={{ padding: '8px 12px' }}
        >
          <DocumentTree
            documents={documents}
            onSelect={handleSelectDoc}
            selectedId={selectedDoc?.id}
          />
        </Card>

        {/* 右侧文档列表/预览 */}
        <Card title="文档列表" style={{ flex: 1, overflow: 'auto' }}>
          <Table
            columns={columns}
            dataSource={documents}
            rowKey="id"
            loading={loading}
            locale={{ emptyText: <AntEmpty description="暂无文档" /> }}
            pagination={false}
            size="small"
            scroll={{ y: 'calc(100vh - 340px)' }}
          />
        </Card>
      </div>

      {/* 文档预览弹窗 */}
      {selectedDoc && (
        <Modal
          open
          title={selectedDoc.name}
          onCancel={() => setSelectedDoc(null)}
          footer={[
            <AntButton key="close" onClick={() => setSelectedDoc(null)}>
              关闭
            </AntButton>,
            selectedDoc.status === 'pending' && (
              <AntButton
                key="confirm"
                type="primary"
                icon={<CheckOutlined />}
                onClick={() => {
                  handleConfirm(selectedDoc.id);
                  setSelectedDoc(null);
                }}
              >
                确认文档
              </AntButton>
            ),
          ]}
        >
          <div style={{ lineHeight: 2 }}>
            <p>
              <strong>文档类型：</strong>
              {selectedDoc.type}
            </p>
            <p>
              <strong>确认状态：</strong>
              <ConfirmBadge status={selectedDoc.status} />
            </p>
            <p>
              <strong>创建时间：</strong>
              {selectedDoc.createdAt}
            </p>
            <p>
              <strong>更新时间：</strong>
              {selectedDoc.updatedAt}
            </p>
            {selectedDoc.url && (
              <p>
                <a
                  href={selectedDoc.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  在线预览文档
                </a>
              </p>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};

export default ProjectDocumentsPage;
