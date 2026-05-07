import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { List, Card, Tag, Button, Empty, SearchBar, Toast, SwipeAction } from 'antd-mobile';
import { Table, Card as AntCard, Button as AntButton, Input, Space, Tag as AntTag, Empty as AntEmpty, Popconfirm, message } from 'antd';
import { PlusOutlined, SearchOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { useProject } from '@/hooks/useProject';
import type { ProjectInfo } from '@/api';

/** 项目状态映射 */
const statusMap: Record<string, { text: string; color: string }> = {
  draft: { text: '草稿', color: 'default' },
  in_progress: { text: '进行中', color: 'processing' },
  completed: { text: '已完成', color: 'success' },
};

/**
 * 首页 - 项目列表
 * PC端使用antd表格，移动端使用antd-mobile列表
 * 支持搜索、查看详情、删除
 */
const HomePage: React.FC = () => {
  const { isMobile } = useResponsive();
  const navigate = useNavigate();
  const { projects, loading, fetchProjects, removeProject } = useProject();
  const [keyword, setKeyword] = useState('');

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  /** 搜索项目 */
  const handleSearch = (value: string) => {
    setKeyword(value);
    fetchProjects(value);
  };

  /** 删除项目 */
  const handleDelete = async (id: string) => {
    try {
      await removeProject(id);
      if (isMobile) {
        Toast.show({ content: '删除成功', icon: 'success' });
      } else {
        message.success('删除成功');
      }
    } catch {
      if (isMobile) {
        Toast.show({ content: '删除失败', icon: 'fail' });
      } else {
        message.error('删除失败');
      }
    }
  };

  /** 查看项目详情 */
  const handleView = (id: string) => {
    navigate(`/project/${id}`);
  };

  /** 过滤项目列表 */
  const filteredProjects = keyword
    ? projects.filter(
        (p) =>
          p.name.includes(keyword) ||
          p.companyName.includes(keyword) ||
          p.industry.includes(keyword),
      )
    : projects;

  /* ==================== 移动端渲染 ==================== */
  if (isMobile) {
    return (
      <div style={{ padding: 12 }}>
        {/* 搜索栏 */}
        <SearchBar
          placeholder="搜索项目名称、公司名"
          onSearch={handleSearch}
          onChange={setKeyword}
          style={{ marginBottom: 12 }}
        />

        {/* 创建按钮 */}
        <Button
          block
          color="primary"
          size="large"
          onClick={() => navigate('/project/create')}
          style={{ marginBottom: 16 }}
        >
          <PlusOutlined /> 创建新项目
        </Button>

        {/* 项目列表 */}
        {filteredProjects.length === 0 ? (
          <Empty
            style={{ padding: '40px 0' }}
            description="暂无项目"
          />
        ) : (
          <List>
            {filteredProjects.map((project) => {
              const status = statusMap[project.status] || statusMap.draft;
              return (
                <SwipeAction
                  key={project.id}
                  rightActions={[
                    {
                      key: 'delete',
                      text: '删除',
                      danger: true,
                      onClick: () => handleDelete(project.id),
                    },
                  ]}
                >
                  <List.Item
                    onClick={() => handleView(project.id)}
                    description={
                      <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                        <span>{project.industry}</span>
                        <span style={{ marginLeft: 8 }}>{project.employeeCount}人</span>
                      </div>
                    }
                    extra={<Tag color={status.color}>{status.text}</Tag>}
                  >
                    <div style={{ fontWeight: 500 }}>{project.companyName || project.name}</div>
                    <div style={{ fontSize: 12, color: '#bbb', marginTop: 2 }}>
                      {project.createdAt}
                    </div>
                  </List.Item>
                </SwipeAction>
              );
            })}
          </List>
        )}
      </div>
    );
  }

  /* ==================== PC端渲染 ==================== */
  const columns = [
    {
      title: '项目名称',
      dataIndex: 'companyName',
      key: 'companyName',
      render: (text: string, record: ProjectInfo) => (
        <a onClick={() => handleView(record.id)}>{text || record.name}</a>
      ),
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 120,
    },
    {
      title: '员工数',
      dataIndex: 'employeeCount',
      key: 'employeeCount',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const s = statusMap[status] || statusMap.draft;
        return <AntTag color={s.color}>{s.text}</AntTag>;
      },
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
      width: 160,
      render: (_: unknown, record: ProjectInfo) => (
        <Space>
          <AntButton
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record.id)}
          >
            查看
          </AntButton>
          <Popconfirm
            title="确定删除该项目？"
            onConfirm={() => handleDelete(record.id)}
          >
            <AntButton type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </AntButton>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      {/* 顶部操作栏 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <Input
          placeholder="搜索项目名称、公司名"
          prefix={<SearchOutlined />}
          value={keyword}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ width: 300 }}
          allowClear
        />
        <AntButton
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/project/create')}
        >
          创建新项目
        </AntButton>
      </div>

      {/* 项目表格 */}
      <AntCard>
        <Table
          columns={columns}
          dataSource={filteredProjects}
          rowKey="id"
          loading={loading}
          locale={{ emptyText: <AntEmpty description="暂无项目" /> }}
          pagination={{
            pageSize: 10,
            showTotal: (total) => `共 ${total} 个项目`,
            showSizeChanger: true,
          }}
        />
      </AntCard>
    </div>
  );
};

export default HomePage;
