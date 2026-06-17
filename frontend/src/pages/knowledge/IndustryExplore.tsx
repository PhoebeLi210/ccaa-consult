import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input, List, Card, Tag, Badge, Typography, Space, Empty } from 'antd';
import { SearchOutlined, RightOutlined } from '@ant-design/icons';
import { getIndustryList } from '../../api/knowledge';
import type { KnowledgeIndustry, IndustryDataStatus } from '../../api/knowledge';

const { Title, Text } = Typography;

const statusMap: Record<
  IndustryDataStatus,
  { label: string; color: string; badge: 'success' | 'warning' | 'processing' | 'default' }
> = {
  complete: { label: '数据完整', color: 'green', badge: 'success' },
  partial: { label: '部分数据', color: 'orange', badge: 'warning' },
  template: { label: '模板数据', color: 'blue', badge: 'processing' },
  empty: { label: '待填充', color: 'default', badge: 'default' },
};

export default function IndustryExplore() {
  const navigate = useNavigate();
  const [industries, setIndustries] = useState<KnowledgeIndustry[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<KnowledgeIndustry | null>(null);

  useEffect(() => {
    setLoading(true);
    getIndustryList()
      .then((data: any) => setIndustries(data || []))
      .catch(() => setIndustries([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = industries.filter(
    (i) =>
      i.name.includes(search) ||
      (i.name_en && i.name_en.toLowerCase().includes(search.toLowerCase())) ||
      i.code.includes(search) ||
      i.keywords?.some((k: string) => k.includes(search)),
  );

  return (
    <div>
      <Title level={4} style={{ marginBottom: 24 }}>
        行业知识库浏览
      </Title>

      <div style={{ display: 'flex', gap: 16, height: 'calc(100vh - 180px)' }}>
        {/* 左侧列表 */}
        <Card
          style={{ width: 420, flexShrink: 0, display: 'flex', flexDirection: 'column' }}
          styles={{ body: { padding: 0, flex: 1, overflow: 'hidden' } }}
        >
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
            <Input
              prefix={<SearchOutlined />}
              placeholder="搜索行业名称、代码或关键词..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              allowClear
            />
          </div>
          <div style={{ flex: 1, overflow: 'auto' }}>
            <List
              loading={loading}
              dataSource={filtered}
              renderItem={(item) => {
                const st = statusMap[item.data_status as IndustryDataStatus] || statusMap.empty;
                return (
                  <List.Item
                    onClick={() => setSelected(item)}
                    style={{
                      cursor: 'pointer',
                      padding: '10px 16px',
                      background:
                        selected?.code === item.code ? '#e6f4ff' : undefined,
                      transition: 'background 0.2s',
                    }}
                  >
                    <div style={{ width: '100%' }}>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: 4,
                        }}
                      >
                        <Text strong>{item.name}</Text>
                        <Badge status={st.badge} text={st.label} />
                      </div>
                      <Space size={4}>
                        <Tag>{item.code}</Tag>
                        {item.name_en && (
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {item.name_en}
                          </Text>
                        )}
                      </Space>
                    </div>
                  </List.Item>
                );
              }}
              locale={{
                emptyText: <Empty description="未找到匹配的行业" />,
              }}
            />
          </div>
        </Card>

        {/* 右侧详情 */}
        <Card style={{ flex: 1 }}>
          {selected ? (
            <div>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: 24,
                }}
              >
                <div>
                  <Title level={4} style={{ marginBottom: 8 }}>
                    {selected.name}
                  </Title>
                  <Space>
                    <Tag color="blue">{selected.code}</Tag>
                    {selected.name_en && (
                      <Text type="secondary">{selected.name_en}</Text>
                    )}
                    <Tag color={statusMap[selected.data_status as IndustryDataStatus]?.color}>
                      {statusMap[selected.data_status as IndustryDataStatus]?.label}
                    </Tag>
                  </Space>
                </div>
                {selected.sub_categories_count != null && (
                  <Tag color="blue" icon={<RightOutlined />}>
                    共 {selected.sub_categories_count} 个子类
                  </Tag>
                )}
              </div>

              {selected.description && (
                <div style={{ marginBottom: 16 }}>
                  <Text type="secondary">{selected.description}</Text>
                </div>
              )}

              {selected.keywords && selected.keywords.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <Text strong>关键词：</Text>
                  <div style={{ marginTop: 8 }}>
                    {selected.keywords.map((kw: string) => (
                      <Tag key={kw}>{kw}</Tag>
                    ))}
                  </div>
                </div>
              )}

              {selected.key_processes && selected.key_processes.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <Text strong>关键过程：</Text>
                  <div style={{ marginTop: 8 }}>
                    {selected.key_processes.map((p: string) => (
                      <Tag key={p} color="cyan">
                        {p}
                      </Tag>
                    ))}
                  </div>
                </div>
              )}

              {selected.priority_clauses && selected.priority_clauses.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <Text strong>优先条款：</Text>
                  <div style={{ marginTop: 8 }}>
                    {selected.priority_clauses.map((c: string) => (
                      <Tag key={c} color="volcano">
                        {c}
                      </Tag>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ marginTop: 24 }}>
                <Space>
                  <Tag>审核要点：{selected.audit_points_count ?? '-'}</Tag>
                  <Tag>典型不符合项：{selected.typical_ncs_count ?? '-'}</Tag>
                  <Tag>检查清单：{selected.checklist_count ?? '-'}</Tag>
                  <Tag>法规要求：{selected.regulations_count ?? '-'}</Tag>
                </Space>
              </div>

              <div style={{ marginTop: 24 }}>
                <a
                  onClick={() => navigate(`/knowledge/industry/${selected.code}`)}
                  style={{ fontSize: 14 }}
                >
                  查看完整行业详情 <RightOutlined />
                </a>
              </div>
            </div>
          ) : (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
              }}
            >
              <Empty description="请从左侧选择一个行业" />
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
