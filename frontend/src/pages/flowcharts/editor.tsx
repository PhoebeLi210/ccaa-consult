import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Card,
  Button,
  Space,
  message,
  Modal,
  Form,
  Input,
  Tooltip,
  Popconfirm,
} from 'antd';
import {
  SaveOutlined,
  ArrowLeftOutlined,
  SettingOutlined,
  FileTextOutlined,
  DeleteOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import {
  getFlowchartDetail,
  updateFlowchart,
  FlowchartNode,
  FlowchartEdge,
  FlowchartData,
  NodeType,
} from '../../api';
import styles from './style.module.css';

/**
 * 节点类型配置
 */
const NODE_TYPES: Record<NodeType, { label: string; color: string; icon: string }> = {
  start: { label: '开始', color: '#52c41a', icon: '▶' },
  end: { label: '结束', color: '#f5222d', icon: '■' },
  process: { label: '处理', color: '#1890ff', icon: '□' },
  decision: { label: '判断', color: '#faad14', icon: '◇' },
  document: { label: '文档', color: '#722ed1', icon: '📄' },
};

/**
 * 流程图编辑器页面
 * 支持添加节点、删除节点、连接节点、保存流程图
 */
const FlowchartEditorPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const flowchartId = searchParams.get('id');
  const canvasRef = useRef<HTMLDivElement>(null);
  const [form] = Form.useForm();

  // 状态
  const [nodes, setNodes] = useState<FlowchartNode[]>([]);
  const [edges, setEdges] = useState<FlowchartEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<FlowchartNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<FlowchartEdge | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [flowchartName, setFlowchartName] = useState('');
  const [nodeModalVisible, setNodeModalVisible] = useState(false);
  const [editingNode, setEditingNode] = useState<FlowchartNode | null>(null);

  // 初始化：加载流程图数据
  useEffect(() => {
    if (flowchartId) {
      loadFlowchart(flowchartId);
    } else {
      // 新建流程图，添加默认开始节点
      const startNode: FlowchartNode = {
        id: `node_${Date.now()}`,
        type: 'start',
        label: '开始',
        x: 400,
        y: 50,
      };
      setNodes([startNode]);
    }
  }, [flowchartId]);

  // 加载流程图数据
  const loadFlowchart = async (id: string) => {
    setLoading(true);
    try {
      const data = await getFlowchartDetail(id);
      setFlowchartName(data.name);
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
    } catch (error) {
      message.error('加载流程图失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存流程图
  const handleSave = async () => {
    if (!flowchartId) {
      message.error('请先创建流程图');
      return;
    }
    setSaving(true);
    try {
      const data: FlowchartData = {
        nodes,
        edges,
      };
      await updateFlowchart(flowchartId, { data });
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  // 添加节点
  const handleAddNode = (type: NodeType) => {
    const newNode: FlowchartNode = {
      id: `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      label: NODE_TYPES[type].label,
      x: 300 + Math.random() * 200,
      y: 150 + Math.random() * 200,
    };
    setNodes([...nodes, newNode]);
    message.success(`已添加${NODE_TYPES[type].label}节点`);
  };

  // 删除节点
  const handleDeleteNode = (nodeId: string) => {
    setNodes(nodes.filter((n) => n.id !== nodeId));
    setEdges(edges.filter((e) => e.source !== nodeId && e.target !== nodeId));
    setSelectedNode(null);
    message.success('节点已删除');
  };

  // 删除边
  const handleDeleteEdge = (edgeId: string) => {
    setEdges(edges.filter((e) => e.id !== edgeId));
    setSelectedEdge(null);
    message.success('连线已删除');
  };

  // 清空画布
  const handleClear = () => {
    Modal.confirm({
      title: '确定要清空画布吗？',
      content: '所有节点和连线将被删除，此操作不可恢复',
      onOk: () => {
        setNodes([]);
        setEdges([]);
        setSelectedNode(null);
        setSelectedEdge(null);
        message.success('画布已清空');
      },
    });
  };

  // 开始连接
  const handleStartConnect = (nodeId: string) => {
    setIsConnecting(true);
    setConnectingFrom(nodeId);
    message.info('请点击目标节点完成连接');
  };

  // 完成连接
  const handleCompleteConnect = (targetId: string) => {
    if (connectingFrom && connectingFrom !== targetId) {
      // 检查是否已存在连接
      const exists = edges.some(
        (e) => e.source === connectingFrom && e.target === targetId
      );
      if (exists) {
        message.warning('连接已存在');
      } else {
        const newEdge: FlowchartEdge = {
          id: `edge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          source: connectingFrom,
          target: targetId,
          label: '',
        };
        setEdges([...edges, newEdge]);
        message.success('连接成功');
      }
    }
    setIsConnecting(false);
    setConnectingFrom(null);
  };

  // 节点点击
  const handleNodeClick = (node: FlowchartNode) => {
    if (isConnecting && connectingFrom) {
      handleCompleteConnect(node.id);
    } else {
      setSelectedNode(node);
      setSelectedEdge(null);
    }
  };

  // 边点击
  const handleEdgeClick = (edge: FlowchartEdge, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedEdge(edge);
    setSelectedNode(null);
  };

  // 编辑节点
  const handleEditNode = () => {
    if (selectedNode) {
      setEditingNode(selectedNode);
      form.setFieldsValue({
        label: selectedNode.label,
        description: selectedNode.description || '',
      });
      setNodeModalVisible(true);
    }
  };

  // 保存节点编辑
  const handleSaveNode = (values: { label: string; description: string }) => {
    if (editingNode) {
      setNodes(
        nodes.map((n) =>
          n.id === editingNode.id
            ? { ...n, label: values.label, description: values.description }
            : n
        )
      );
      setSelectedNode({ ...editingNode, ...values });
      setNodeModalVisible(false);
      message.success('节点已更新');
    }
  };

  // 拖拽节点
  const handleMouseDown = (node: FlowchartNode, e: React.MouseEvent) => {
    e.stopPropagation();
    const startX = e.clientX;
    const startY = e.clientY;
    const startNodeX = node.x;
    const startNodeY = node.y;

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const dx = moveEvent.clientX - startX;
      const dy = moveEvent.clientY - startY;
      setNodes((prev) =>
        prev.map((n) =>
          n.id === node.id
            ? { ...n, x: startNodeX + dx, y: startNodeY + dy }
            : n
        )
      );
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // 计算边的路径
  const getEdgePath = (edge: FlowchartEdge) => {
    const source = nodes.find((n) => n.id === edge.source);
    const target = nodes.find((n) => n.id === edge.target);
    if (!source || !target) return '';

    const sx = source.x + 60;
    const sy = source.y + 30;
    const tx = target.x + 60;
    const ty = target.y + 30;

    // 使用贝塞尔曲线
    const midY = (sy + ty) / 2;
    return `M ${sx} ${sy} C ${sx} ${midY}, ${tx} ${midY}, ${tx} ${ty}`;
  };

  // 渲染节点
  const renderNode = (node: FlowchartNode) => {
    const isSelected = selectedNode?.id === node.id;
    const isConnectingFrom = connectingFrom === node.id;
    const config = NODE_TYPES[node.type];

    return (
      <div
        key={node.id}
        className={`${styles.node} ${isSelected ? styles.selected : ''} ${
          isConnectingFrom ? styles.connecting : ''
        }`}
        style={{
          left: node.x,
          top: node.y,
          borderColor: config.color,
          backgroundColor: isSelected ? `${config.color}20` : '#fff',
        }}
        onClick={() => handleNodeClick(node)}
        onMouseDown={(e) => handleMouseDown(node, e)}
      >
        <div
          className={styles.nodeIcon}
          style={{ backgroundColor: config.color }}
        >
          {config.icon}
        </div>
        <div className={styles.nodeLabel}>{node.label}</div>
        {isSelected && (
          <div className={styles.nodeActions}>
            <Tooltip title="连接">
              <Button
                size="small"
                type="primary"
                icon={<SettingOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleStartConnect(node.id);
                }}
              />
            </Tooltip>
            <Tooltip title="编辑">
              <Button
                size="small"
                icon={<FileTextOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleEditNode();
                }}
              />
            </Tooltip>
            {node.type !== 'start' && (
              <Tooltip title="删除">
                <Button
                  size="small"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteNode(node.id);
                  }}
                />
              </Tooltip>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={styles.editorContainer}>
      {/* 顶部工具栏 */}
      <div className={styles.toolbar}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/flowcharts')}>
            返回
          </Button>
          <span className={styles.title}>
            {flowchartName || '未命名流程图'}
          </span>
        </Space>
        <Space>
          <Button
            icon={<ClearOutlined />}
            onClick={handleClear}
          >
            清空
          </Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            loading={saving}
            onClick={handleSave}
          >
            保存
          </Button>
        </Space>
      </div>

      <div className={styles.mainContent}>
        {/* 左侧节点面板 */}
        <div className={styles.nodePanel}>
          <div className={styles.panelTitle}>节点类型</div>
          <div className={styles.nodeList}>
            {(Object.keys(NODE_TYPES) as NodeType[]).map((type) => (
              <div
                key={type}
                className={styles.nodeItem}
                onClick={() => handleAddNode(type)}
              >
                <span
                  className={styles.nodeItemIcon}
                  style={{ backgroundColor: NODE_TYPES[type].color }}
                >
                  {NODE_TYPES[type].icon}
                </span>
                <span className={styles.nodeItemLabel}>
                  {NODE_TYPES[type].label}
                </span>
              </div>
            ))}
          </div>

          <div className={styles.panelTitle} style={{ marginTop: 24 }}>
            操作说明
          </div>
          <div className={styles.helpText}>
            <p>1. 点击左侧节点类型添加节点</p>
            <p>2. 拖拽节点调整位置</p>
            <p>3. 点击节点，选择"连接"创建连线</p>
            <p>4. 点击节点，选择"编辑"修改内容</p>
            <p>5. 点击连线可选中并删除</p>
          </div>
        </div>

        {/* 画布区域 */}
        <div
          ref={canvasRef}
          className={styles.canvas}
          onClick={() => {
            setSelectedNode(null);
            setSelectedEdge(null);
            setIsConnecting(false);
            setConnectingFrom(null);
          }}
        >
          {/* SVG 连线层 */}
          <svg className={styles.svgLayer}>
            {edges.map((edge) => (
              <g key={edge.id}>
                <path
                  d={getEdgePath(edge)}
                  className={`${styles.edge} ${
                    selectedEdge?.id === edge.id ? styles.selectedEdge : ''
                  }`}
                  onClick={(e) => handleEdgeClick(edge, e)}
                />
                {edge.label && (
                  <text
                    className={styles.edgeLabel}
                    x={(edge.source.length + edge.target.length) * 10}
                    y={(edge.source.length - edge.target.length) * 5}
                  >
                    {edge.label}
                  </text>
                )}
              </g>
            ))}
          </svg>

          {/* 节点层 */}
          {nodes.map(renderNode)}

          {/* 选中边时的操作提示 */}
          {selectedEdge && (
            <div
              className={styles.edgeActions}
              style={{
                position: 'absolute',
                left: 20,
                bottom: 20,
              }}
            >
              <Popconfirm
                title="删除连线"
                description="确定要删除这条连线吗？"
                onConfirm={() => handleDeleteEdge(selectedEdge.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button danger icon={<DeleteOutlined />}>
                  删除连线
                </Button>
              </Popconfirm>
            </div>
          )}
        </div>
      </div>

      {/* 节点编辑弹窗 */}
      <Modal
        title="编辑节点"
        open={nodeModalVisible}
        onOk={() => form.submit()}
        onCancel={() => setNodeModalVisible(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" onFinish={handleSaveNode}>
          <Form.Item
            name="label"
            label="节点名称"
            rules={[{ required: true, message: '请输入节点名称' }]}
          >
            <Input placeholder="请输入节点名称" />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea
              rows={3}
              placeholder="请输入节点描述（可选）"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default FlowchartEditorPage;
