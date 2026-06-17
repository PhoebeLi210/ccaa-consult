import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useResponsive } from './hooks/useResponsive';
import PcLayout from './layouts/PcLayout';
import MobileLayout from './layouts/MobileLayout';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/login';
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
import FlowchartListPage from './pages/flowcharts';

/** 包裹Layout的路由组件 */
const LayoutRoutes: React.FC = () => {
  const { isMobile } = useResponsive();
  const Layout = isMobile ? MobileLayout : PcLayout;

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/project/create" element={<ProjectCreatePage />} />
        <Route path="/project/:id" element={<ProjectDetailPage />} />
        <Route path="/project/:id/documents" element={<ProjectDocumentsPage />} />
        <Route path="/project/:id/export" element={<DocumentExportPage />} />
        <Route path="/project/:id/file-list" element={<FileListPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/materials" element={<MaterialsPage />} />
        <Route path="/materials/upload" element={<MaterialsUploadPage />} />
        <Route path="/conversation" element={<ConversationPage />} />
        <Route path="/analyzer" element={<AnalyzerPage />} />
        <Route path="/templates" element={<TemplatesPage />} />
        <Route path="/team" element={<TeamPage />} />
        <Route path="/knowledge" element={<KnowledgeBase />} />
        <Route path="/knowledge/standard/:id" element={<StandardDetail />} />
        <Route path="/knowledge/detail/:id" element={<KnowledgeDetail />} />
        <Route path="/flowcharts" element={<FlowchartListPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
};

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/*" element={
        <ProtectedRoute>
          <LayoutRoutes />
        </ProtectedRoute>
      } />
    </Routes>
  );
};

export default App;
