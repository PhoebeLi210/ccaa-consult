import { Routes, Route, Navigate } from 'react-router-dom';
import { useResponsive } from './hooks/useResponsive';
import PcLayout from './layouts/PcLayout';
import MobileLayout from './layouts/MobileLayout';
import HomePage from './pages/home';
import ProjectCreatePage from './pages/project/create';
import ProjectDetailPage from './pages/project/detail';
import ProjectDocumentsPage from './pages/project/documents';
import UploadPage from './pages/upload';

/**
 * 根组件
 * 根据屏幕宽度自动切换PC端/移动端布局
 */
const App: React.FC = () => {
  const { isMobile } = useResponsive();
  const Layout = isMobile ? MobileLayout : PcLayout;

  return (
    <Layout>
      <Routes>
        {/* 首页 - 项目列表 */}
        <Route path="/" element={<HomePage />} />
        {/* 创建项目 */}
        <Route path="/project/create" element={<ProjectCreatePage />} />
        {/* 项目详情 */}
        <Route path="/project/:id" element={<ProjectDetailPage />} />
        {/* 文档管理 */}
        <Route path="/project/:id/documents" element={<ProjectDocumentsPage />} />
        {/* 文件上传 */}
        <Route path="/upload" element={<UploadPage />} />
        {/* 未匹配路由重定向到首页 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
};

export default App;
