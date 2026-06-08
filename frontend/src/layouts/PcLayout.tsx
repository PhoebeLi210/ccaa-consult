import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import {
  HomeOutlined,
  FolderOpenOutlined,
  CloudUploadOutlined,
  FileTextOutlined,
  FileMarkdownOutlined,
  TeamOutlined,
  BookOutlined,
  MessageOutlined,
  SafetyCertificateOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const { Sider, Content, Header } = Layout;

/** PC端布局组件属性 */
interface PcLayoutProps {
  children: React.ReactNode;
}

/** 侧边栏菜单项 */
const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: '首页',
  },
  {
    key: '/project/create',
    icon: <FileTextOutlined />,
    label: '创建项目',
  },
  {
    key: '/conversation',
    icon: <MessageOutlined />,
    label: '多轮对话',
  },
  {
    key: '/materials',
    icon: <FolderOpenOutlined />,
    label: '材料管理',
  },
  {
    key: '/upload',
    icon: <CloudUploadOutlined />,
    label: '文件上传',
  },
  {
    key: '/analyzer',
    icon: <SafetyCertificateOutlined />,
    label: '评估报告',
  },
  {
    key: '/knowledge',
    icon: <BookOutlined />,
    label: '知识库',
  },
  {
    key: '/templates',
    icon: <FileMarkdownOutlined />,
    label: '我的模板',
  },
  {
    key: '/team',
    icon: <TeamOutlined />,
    label: '团队协作',
  },
];

/**
 * PC端布局组件
 * 包含侧边栏导航 + 顶部标题栏 + 内容区域
 */
const PcLayout: React.FC<PcLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  /** 菜单点击跳转 */
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  /** 根据当前路径确定选中的菜单项 */
  const getSelectedKey = () => {
    if (location.pathname.startsWith('/project/') && location.pathname !== '/project/create') {
      return '/project/create';
    }
    if (location.pathname.startsWith('/knowledge/')) {
      return '/knowledge';
    }
    return location.pathname;
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: collapsed ? 16 : 20,
            fontWeight: 'bold',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
          }}
        >
          {collapsed ? 'CCAA' : 'CCAA 咨询管理'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>

      {/* 右侧主内容区 */}
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'margin-left 0.2s' }}>
        {/* 顶部栏 */}
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <span style={{ fontSize: 16, fontWeight: 500 }}>
            {menuItems.find((item) => item.key === getSelectedKey())?.label || '首页'}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ color: '#666', fontSize: 14 }}>管理员</span>
          </div>
        </Header>

        {/* 内容区域 */}
        <Content
          style={{
            margin: 16,
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            minHeight: 280,
            overflow: 'auto',
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default PcLayout;
