import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { TabBar } from 'antd-mobile';
import {
  AppOutline,
  FileOutline,
  ContentOutline,
  CloudUploadOutline,
} from 'antd-mobile-icons';

/** 移动端布局组件属性 */
interface MobileLayoutProps {
  children: React.ReactNode;
}

/** 底部Tab栏配置 */
const tabs = [
  { key: '/', title: '首页', icon: <AppOutline /> },
  { key: '/project/create', title: '创建', icon: <ContentOutline /> },
  { key: '/upload', title: '上传', icon: <CloudUploadOutline /> },
  { key: '/project/documents', title: '文档', icon: <FileOutline /> },
];

/**
 * 移动端布局组件
 * 包含顶部标题栏 + 内容区域 + 底部Tab栏
 */
const MobileLayout: React.FC<MobileLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  /** 根据当前路径确定激活的Tab */
  const getActiveKey = () => {
    // 精确匹配或前缀匹配
    if (location.pathname === '/') return '/';
    if (location.pathname.startsWith('/project/create')) return '/project/create';
    if (location.pathname.startsWith('/upload')) return '/upload';
    if (location.pathname.startsWith('/project') && location.pathname.includes('document')) {
      return '/project/documents';
    }
    // 项目详情页也归到首页
    if (location.pathname.startsWith('/project/')) return '/';
    return '/';
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        backgroundColor: '#f5f5f5',
      }}
    >
      {/* 顶部标题栏 */}
      <div
        style={{
          height: 48,
          backgroundColor: '#1677ff',
          color: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 17,
          fontWeight: 600,
          flexShrink: 0,
        }}
      >
        CCAA 咨询管理
      </div>

      {/* 内容区域 */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          paddingBottom: 0,
        }}
      >
        {children}
      </div>

      {/* 底部Tab栏 */}
      <TabBar
        activeKey={getActiveKey()}
        onChange={(key) => navigate(key)}
        style={{
          borderTop: '1px solid #eee',
          backgroundColor: '#fff',
        }}
      >
        {tabs.map((tab) => (
          <TabBar.Item key={tab.key} icon={tab.icon} title={tab.title} />
        ))}
      </TabBar>
    </div>
  );
};

export default MobileLayout;
