import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Tabs,
  Table,
  Tag,
  Card,
  Typography,
  Space,
  Spin,
  Alert,
  Descriptions,
  List,
} from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { getIndustryContext } from '../../api/knowledge';
import type {
  IndustryContext,
  AuditPoint,
  TypicalNC,
  ChecklistItem,
  Regulation,
  CompanyCase,
} from '../../api/knowledge';

const { Text, Paragraph } = Typography;

const riskLevelMap: Record<string, { label: string; color: string }> = {
  high: { label: '高', color: 'red' },
  medium: { label: '中', color: 'orange' },
  low: { label: '低', color: 'green' },
};

export default function IndustryDetail() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const [context, setContext] = useState<IndustryContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!code) return;
    setLoading(true);
    setError(null);
    getIndustryContext(code)
      .then(setContext)
      .catch((err) => setError(err.message || '加载失败'))
      .finally(() => setLoading(false));
  }, [code]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 100 }}>
        <Spin size="large" tip="加载行业数据中..." />
      </div>
    );
  }

  if (error || !context) {
    return (
      <Alert
        type="error"
        message="加载失败"
        description={error || '未找到行业数据'}
        showIcon
        action={
          <a onClick={() => navigate('/knowledge/industries')}>返回行业列表</a>
        }
      />
    );
  }

  const { industry, audit_points, typical_ncs, checklist, regulations, company_cases } =
    context;

  const tabItems = [
    {
      key: 'audit_points',
      label: `审核要点 (${audit_points?.length ?? 0})`,
      children: <AuditPointsTab data={audit_points ?? []} />,
    },
    {
      key: 'typical_ncs',
      label: `典型不符合项 (${typical_ncs?.length ?? 0})`,
      children: <TypicalNCsTab data={typical_ncs ?? []} />,
    },
    {
      key: 'checklist',
      label: `检查清单 (${checklist?.length ?? 0})`,
      children: <ChecklistTab data={checklist ?? []} />,
    },
    {
      key: 'regulations',
      label: `法规要求 (${regulations?.length ?? 0})`,
      children: <RegulationsTab data={regulations ?? []} />,
    },
    ...(company_cases && company_cases.length > 0
      ? [
          {
            key: 'cases',
            label: `公司案例 (${company_cases.length})`,
            children: <CasesTab data={company_cases} />,
          },
        ]
      : []),
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <a onClick={() => navigate('/knowledge/industries')}>
          <ArrowLeftOutlined /> 返回行业列表
        </a>
      </Space>

      <Card style={{ marginBottom: 16 }}>
        <Descriptions title={industry.name} bordered column={2}>
          <Descriptions.Item label="行业代码">
            <Tag color="blue">{industry.code}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="英文名称">
            {industry.name_en}
          </Descriptions.Item>
          <Descriptions.Item label="数据状态">
            <Tag
              color={
                industry.data_status === 'complete'
                  ? 'green'
                  : industry.data_status === 'partial'
                    ? 'orange'
                    : industry.data_status === 'template'
                      ? 'blue'
                      : 'default'
              }
            >
              {industry.data_status === 'complete'
                ? '数据完整'
                : industry.data_status === 'partial'
                  ? '部分数据'
                  : industry.data_status === 'template'
                    ? '模板数据'
                    : '待填充'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="子类数量">
            {industry.sub_categories_count}
          </Descriptions.Item>
          {industry.keywords && industry.keywords.length > 0 && (
            <Descriptions.Item label="关键词" span={2}>
              {industry.keywords.map((kw) => (
                <Tag key={kw}>{kw}</Tag>
              ))}
            </Descriptions.Item>
          )}
          {industry.key_processes && industry.key_processes.length > 0 && (
            <Descriptions.Item label="关键过程" span={2}>
              {industry.key_processes.map((p) => (
                <Tag key={p} color="cyan">
                  {p}
                </Tag>
              ))}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      <Card>
        <Tabs items={tabItems} defaultActiveKey="audit_points" />
      </Card>
    </div>
  );
}

/** 审核要点 Tab */
function AuditPointsTab({ data }: { data: AuditPoint[] }) {
  if (data.length === 0) return <EmptyText />;
  return (
    <List
      dataSource={data}
      renderItem={(item) => {
        const risk = riskLevelMap[item.risk_level] || {
          label: item.risk_level,
          color: 'default',
        };
        return (
          <List.Item>
            <List.Item.Meta
              title={
                <Space>
                  <Tag>{item.clause}</Tag>
                  <Text strong>{item.title}</Text>
                  <Tag color={risk.color}>风险等级: {risk.label}</Tag>
                </Space>
              }
              description={
                <div>
                  <Paragraph style={{ marginBottom: 4 }}>
                    {item.description}
                  </Paragraph>
                  <Text type="secondary">
                    审核关注点：{item.audit_focus}
                  </Text>
                </div>
              }
            />
          </List.Item>
        );
      }}
    />
  );
}

/** 典型不符合项 Tab */
function TypicalNCsTab({ data }: { data: TypicalNC[] }) {
  if (data.length === 0) return <EmptyText />;
  const freqMap: Record<string, { label: string; color: string }> = {
    high: { label: '高频', color: 'red' },
    medium: { label: '中频', color: 'orange' },
    low: { label: '低频', color: 'green' },
  };
  return (
    <List
      dataSource={data}
      renderItem={(item) => {
        const freq = freqMap[item.frequency] || {
          label: item.frequency,
          color: 'default',
        };
        return (
          <List.Item>
            <List.Item.Meta
              title={
                <Space>
                  <Tag>{item.clause}</Tag>
                  <Tag color="purple">{item.nc_type}</Tag>
                  <Text strong>{item.description}</Text>
                  <Tag color={freq.color}>频率: {freq.label}</Tag>
                </Space>
              }
              description={
                <div>
                  <Paragraph style={{ marginBottom: 4 }}>
                    <Text type="secondary">根本原因：</Text>
                    {item.root_cause}
                  </Paragraph>
                  <Paragraph style={{ marginBottom: 0 }}>
                    <Text type="secondary">纠正措施：</Text>
                    {item.corrective_action}
                  </Paragraph>
                </div>
              }
            />
          </List.Item>
        );
      }}
    />
  );
}

/** 检查清单 Tab */
function ChecklistTab({ data }: { data: ChecklistItem[] }) {
  if (data.length === 0) return <EmptyText />;
  const columns = [
    { title: '条款', dataIndex: 'clause', key: 'clause', width: 100 },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 120,
    },
    { title: '检查项目', dataIndex: 'check_item', key: 'check_item' },
    { title: '证据', dataIndex: 'evidence', key: 'evidence', width: 180 },
    { title: '方法', dataIndex: 'method', key: 'method', width: 100 },
    {
      title: '风险等级',
      dataIndex: 'risk_level',
      key: 'risk_level',
      width: 100,
      render: (v: string) => {
        const r = riskLevelMap[v] || { label: v, color: 'default' };
        return <Tag color={r.color}>{r.label}</Tag>;
      },
    },
  ];
  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="clause"
      pagination={false}
      size="small"
    />
  );
}

/** 法规要求 Tab */
function RegulationsTab({ data }: { data: Regulation[] }) {
  if (data.length === 0) return <EmptyText />;
  return (
    <List
      dataSource={data}
      renderItem={(item) => (
        <List.Item>
          <List.Item.Meta
            title={
              <Space>
                <Tag color="blue">{item.code}</Tag>
                <Text strong>{item.name}</Text>
              </Space>
            }
            description={
              <div>
                <Paragraph style={{ marginBottom: 4 }}>
                  <Text type="secondary">适用范围：</Text>
                  {item.scope}
                </Paragraph>
                <Paragraph style={{ marginBottom: 4 }}>
                  <Text type="secondary">生效日期：</Text>
                  {item.effective_date}
                </Paragraph>
                {item.key_requirements && item.key_requirements.length > 0 && (
                  <div>
                    <Text type="secondary">关键要求：</Text>
                    <ul style={{ marginTop: 4, paddingLeft: 20 }}>
                      {item.key_requirements.map((req, idx) => (
                        <li key={idx}>{req}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
}

/** 公司案例 Tab */
function CasesTab({ data }: { data: CompanyCase[] }) {
  if (data.length === 0) return <EmptyText />;
  return (
    <List
      dataSource={data}
      renderItem={(item) => (
        <List.Item>
          <List.Item.Meta
            title={
              <Space>
                <Text strong>{item.company_name}</Text>
                <Tag>{item.audit_type}</Tag>
                <Tag color="volcano">{item.severity}</Tag>
              </Space>
            }
            description={
              <div>
                <Paragraph style={{ marginBottom: 4 }}>{item.findings}</Paragraph>
                <Text type="secondary">审核日期：{item.date}</Text>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
}

function EmptyText() {
  return (
    <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
      暂无数据
    </div>
  );
}
