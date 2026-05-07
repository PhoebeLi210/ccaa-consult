import React, { useState } from 'react';
import { Tree, Space, Typography, Tag } from 'antd';
import {
  FileOutlined,
  FolderOutlined,
  FolderOpenOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';
import type { DocumentInfo } from '@/api';
import ConfirmBadge from './ConfirmBadge';

const { Text } = Typography;

/** 文档树组件属性 */
interface DocumentTreeProps {
  /** 文档列表 */
  documents: DocumentInfo[];
  /** 选中文档回调 */
  onSelect?: (document: DocumentInfo) => void;
  /** 当前选中的文档ID */
  selectedId?: string;
}

/** 将文档列表转换为树形结构 */
const buildTreeData = (documents: DocumentInfo[]): DataNode[] => {
  // 按文档类型分组
  const groups: Record<string, DocumentInfo[]> = {};
  const groupNames: Record<string, string> = {
    contract: '合同文件',
    report: '报告文件',
    certificate: '资质证书',
    financial: '财务文件',
    other: '其他文件',
  };

  documents.forEach((doc) => {
    const group = doc.type || 'other';
    if (!groups[group]) {
      groups[group] = [];
    }
    groups[group].push(doc);
  });

  // 构建树节点
  return Object.entries(groups).map(([group, docs]) => ({
    key: `group-${group}`,
    title: (
      <Space>
        <Text strong>{groupNames[group] || group}</Text>
        <Tag>{docs.length}</Tag>
      </Space>
    ),
    icon: ({ expanded }: { expanded: boolean }) =>
      expanded ? <FolderOpenOutlined /> : <FolderOutlined />,
    children: docs.map((doc) => ({
      key: doc.id,
      title: (
        <Space>
          <Text style={{ fontSize: 13 }}>{doc.name}</Text>
          <ConfirmBadge status={doc.status} />
        </Space>
      ),
      icon: <FileOutlined style={{ color: '#8c8c8c' }} />,
      isLeaf: true,
    })),
  }));
};

/**
 * 文档树组件
 * 以树形结构展示项目文档
 * 按文档类型分组，显示确认状态
 */
const DocumentTree: React.FC<DocumentTreeProps> = ({
  documents,
  onSelect,
  selectedId,
}) => {
  const [expandedKeys, setExpandedKeys] = useState<string[]>([]);

  /** 树节点选择处理 */
  const handleSelect = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length === 0) return;
    const key = selectedKeys[0] as string;

    // 如果点击的是分组节点，展开/收起
    if (key.startsWith('group-')) {
      setExpandedKeys((prev) =>
        prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key],
      );
      return;
    }

    // 找到对应的文档
    const doc = documents.find((d) => d.id === key);
    if (doc) {
      onSelect?.(doc);
    }
  };

  /** 展开/收起处理 */
  const handleExpand = (keys: React.Key[]) => {
    setExpandedKeys(keys as string[]);
  };

  const treeData = buildTreeData(documents);

  return (
    <div style={{ height: '100%', overflow: 'auto' }}>
      {documents.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: 24,
            color: '#999',
          }}
        >
          <FileOutlined style={{ fontSize: 32, marginBottom: 8 }} />
          <div>暂无文档</div>
        </div>
      ) : (
        <Tree
          showIcon
          treeData={treeData}
          selectedKeys={selectedId ? [selectedId] : []}
          expandedKeys={expandedKeys}
          onSelect={handleSelect}
          onExpand={handleExpand}
          blockNode
          defaultExpandAll
        />
      )}
    </div>
  );
};

export default DocumentTree;
