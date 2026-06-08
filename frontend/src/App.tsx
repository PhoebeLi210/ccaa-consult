import { Routes, Route, Navigate } from 'react-router-dom';
import { useResponsive } from './hooks/useResponsive';
import PcLayout from './layouts/PcLayout';
import MobileLayout from './layouts/MobileLayout';
import HomePage from './pages/home';
import ProjectCreatePage from './pages/project/create';
import ProjectDetailPage from './pages/project/detail';
import ProjectDocumentsPage from './pages/project/documents';
import DocumentExportPage from './pages/project/DocumentExport';
import FileListPage from './pages/project/FileListPage';
import UploadPage from './pages/upload';
import MaterialsPage from './pages/materials';
import MaterialsUploadPage from './pages/materials/upload';
import ConversationPage from './pages/conversation';
import AnalyzerPage from './pages/analyzer';
import TemplatesPage from './pages/templates';
import TeamPage from './pages/team';
import { KnowledgeBase, StandardDetail, KnowledgeDetail } from './pages/knowledge';

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
        
        {/* 文档导出 (V2.2) */}
        <Route path="/project/:id/export" element={<DocumentExportPage />} />
        
        {/* 文件清单 (V2.2) */}
        <Route path="/project/:id/file-list" element={<FileListPage />} />
        
        {/* 文件上传 */}
        <Route path="/upload" element={<UploadPage />} />
        
        {/* 模板下载 */}
        <Route path="/materials" element={<MaterialsPage />} />
        
        {/* 补充材料上传 (V1.1) */}
        <Route path="/materials/upload" element={<MaterialsUploadPage />} />
        
        {/* 多轮对话 (V1.1) */}
        <Route path="/conversation" element={<ConversationPage />} />
        
        {/* 评估报告解析 (V1.2) */}
        <Route path="/analyzer" element={<AnalyzerPage />} />

        {/* 模板管理 (V1.3) */}
        <Route path="/templates" element={<TemplatesPage />} />

        {/* 团队协作 (V1.3) */}
        <Route path="/team" element={<TeamPage />} />

        {/* 知识库 (V1.4) */}
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/knowledge/standard/:id" element={<StandardDetail />} />
        <Route path="/knowledge/detail/:id" element={<KnowledgeDetail />} />

        {/* 未匹配路由重定向到首页 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
};

export default App;
