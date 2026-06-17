import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { NavBar, Button, Toast, Steps } from 'antd-mobile';
import { Card, Button as AntButton, message, Tag, Space, Typography } from 'antd';
import { FileTextOutlined, UploadOutlined, MessageOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useResponsive } from '@/hooks/useResponsive';
import { useProject } from '@/hooks/useProject';
import NaturalLanguageInput from '@/components/NaturalLanguageInput';
import IndustrySelector from '@/components/IndustrySelector';
import UploadSection from '@/components/UploadSection';
import { checkIndustryFeatures } from '@/api';
import type { ParseResult } from '@/api';
import type { IndustryConfig } from '@/api';

const { Text } = Typography;

/** 创建项目页面 - 4步流程 */
const ProjectCreatePage: React.FC = () => {
  const { isMobile } = useResponsive();
  const navigate = useNavigate();
  const { createNewProject, parseText } = useProject();

  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [parsing, setParsing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedIndustry, setSelectedIndustry] = useState<{ code: string; industry: IndustryConfig } | null>(null);
  const [industryFeatures, setIndustryFeatures] = useState<any>(null);
  const [checkingFeatures, setCheckingFeatures] = useState(false);
  const [createdProjectId, setCreatedProjectId] = useState<string | null>(null);

  /** AI解析回调 */
  const handleParse = useCallback(
    async (text: string): Promise<ParseResult> => {
      setParsing(true);
      try {
        const result = await parseText(text);
        setParseResult(result);
        return result;
      } catch {
        const fallback: ParseResult = {
          company_name: '',
          industry: '',
          employee_count: '',
          registered_capital: '',
          address: '',
          contact_person: '',
          contact_phone: '',
          business_scope: '',
          missing_fields: ['company_name', 'industry', 'employee_count', 'address', 'contact_person', 'contact_phone'],
        };
        setParseResult(fallback);
        return fallback;
      } finally {
        setParsing(false);
      }
    },
    [parseText],
  );

  /** 提交自然语言文本 */
  const handleSubmit = useCallback(
    async (text: string) => {
      setParsing(true);
      try {
        const result = await parseText(text);
        setParseResult(result);
        setCurrentStep(1);
        Toast.show({ content: '解析完成', icon: 'success' });
      } catch {
        message.error('AI解析失败，请重试');
      } finally {
        setParsing(false);
      }
    },
    [parseText],
  );

  /** 行业选择回调 */
  const handleIndustrySelect = useCallback(async (code: string, industry: IndustryConfig) => {
    setSelectedIndustry({ code, industry });
    if (parseResult) {
      setParseResult({ ...parseResult, industry: industry.industry_name });
    }
    setCheckingFeatures(true);
    try {
      const features = await checkIndustryFeatures(code);
      setIndustryFeatures(features);
    } catch {
      setIndustryFeatures(null);
    } finally {
      setCheckingFeatures(false);
    }
  }, [parseResult]);

  /** 创建项目 */
  const handleCreate = useCallback(async () => {
    if (!parseResult?.company_name) {
      message.warning('请填写公司名称');
      return;
    }
    setSubmitting(true);
    try {
      const project = await createNewProject({
        company_name: parseResult.company_name,
        industry: selectedIndustry?.industry?.industry_name || parseResult.industry || '',
        employee_count: parseResult.employee_count,
        address: parseResult.address,
        contact_person: parseResult.contact_person,
        contact_phone: parseResult.contact_phone,
        name: parseResult.company_name,
      });
      setCreatedProjectId(project.id);
      setCurrentStep(2);
      Toast.show({ content: '项目创建成功', icon: 'success' });
    } catch {
      Toast.show({ content: '创建失败，请重试', icon: 'fail' });
    } finally {
      setSubmitting(false);
    }
  }, [parseResult, createNewProject, selectedIndustry]);

  /** 完成创建 */
  const handleFinish = useCallback(() => {
    if (createdProjectId) {
      navigate(`/project/${createdProjectId}`);
    }
  }, [createdProjectId, navigate]);

  /** 跳过上传和对话 */
  const handleSkip = useCallback(() => {
    setCurrentStep(3);
  }, []);

  const steps = [
    { title: '描述企业', icon: <FileTextOutlined /> },
    { title: '确认信息', icon: <CheckCircleOutlined /> },
    { title: '上传资料', icon: <UploadOutlined /> },
    { title: '完成', icon: <CheckCircleOutlined /> },
  ];

  return (
    <div>
      {/* 移动端导航栏 */}
      {isMobile && (
        <NavBar onBack={() => navigate(-1)} style={{ backgroundColor: '#1677ff', color: '#fff' }}>
          创建项目
        </NavBar>
      )}

      <div style={{ padding: isMobile ? 12 : 24, maxWidth: 800, margin: '0 auto' }}>
        {/* 步骤条 */}
        <Steps current={currentStep} style={{ marginBottom: 24 }}>
          {steps.map((step, index) => (
            <Steps.Step key={index} title={step.title} icon={step.icon} />
          ))}
        </Steps>

        {/* 第一步：描述企业 */}
        {currentStep === 0 && (
          <Card title="请描述您客户的企业情况">
            <NaturalLanguageInput
              onSubmit={handleSubmit}
              onParse={handleParse}
              loading={parsing}
            />
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <AntButton type="link" onClick={() => {
                if (!parseResult) {
                  setParseResult({
                    company_name: '',
                    industry: '',
                    employee_count: '',
                    registered_capital: '',
                    address: '',
                    contact_person: '',
                    contact_phone: '',
                    business_scope: '',
                    missing_fields: ['company_name', 'industry', 'employee_count', 'address', 'contact_person', 'contact_phone'],
                  });
                }
                setCurrentStep(1);
              }}>
                跳过，直接手动填写
              </AntButton>
            </div>
          </Card>
        )}

        {/* 第二步：确认信息 */}
        {currentStep === 1 && parseResult && (
          <Card title="确认企业信息">
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">请确认以下信息是否正确，点击可修改</Text>
            </div>

            {/* 信息列表 */}
            <div style={{ display: 'grid', gap: 12 }}>
              {Object.entries({
                company_name: '公司名称',
                industry: '所属行业',
                employee_count: '员工人数',
                address: '公司地址',
                contact_person: '联系人',
                contact_phone: '联系电话',
              }).map(([key, label]) => {
                const value = (parseResult as any)[key];
                const isMissing = parseResult.missing_fields?.includes(key);
                return (
                  <div
                    key={key}
                    onClick={() => {
                      const newValue = window.prompt(`请输入${label}`, value || '');
                      if (newValue !== null) {
                        setParseResult({
                          ...parseResult,
                          [key]: newValue,
                          missing_fields: parseResult.missing_fields?.filter((f) => f !== key),
                        });
                      }
                    }}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      padding: '12px 16px',
                      background: isMissing ? '#fff2f0' : '#fafafa',
                      borderRadius: 8,
                      cursor: 'pointer',
                      border: isMissing ? '1px solid #ffccc7' : '1px solid #f0f0f0',
                    }}
                  >
                    <span style={{ color: isMissing ? '#ff4d4f' : '#666' }}>
                      {label}{isMissing && <span style={{ color: '#ff4d4f' }}>*</span>}
                    </span>
                    <span style={{ color: value ? '#333' : '#ccc' }}>{value || '点击补充'}</span>
                  </div>
                );
              })}
            </div>

            {/* 行业选择 */}
            <div style={{ marginTop: 16 }}>
              <Text strong>选择行业：</Text>
              <IndustrySelector onChange={handleIndustrySelect} />
            </div>

            {/* 行业特征 */}
            {industryFeatures && (
              <Card title="行业特征" size="small" style={{ marginTop: 16 }} loading={checkingFeatures}>
                <Space wrap>
                  {industryFeatures.has_design_development && <Tag color="blue">设计开发</Tag>}
                  {industryFeatures.has_equipment_operations && <Tag color="green">设备操作</Tag>}
                  {industryFeatures.emergency_plans?.length > 0 && <Tag color="red">需应急预案</Tag>}
                </Space>
              </Card>
            )}

            {/* 操作按钮 */}
            <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
              <AntButton block onClick={() => setCurrentStep(0)}>上一步</AntButton>
              <AntButton block type="primary" loading={submitting} onClick={handleCreate}>
                创建项目并继续
              </AntButton>
            </div>
          </Card>
        )}

        {/* 第三步：上传资料 */}
        {currentStep === 2 && createdProjectId && (
          <Card title="上传企业资料">
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">
                上传营业执照、组织架构图、设备清单等资料，帮助生成更准确的体系文件
              </Text>
            </div>
            <UploadSection projectId={createdProjectId} />
            <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
              <AntButton block onClick={() => setCurrentStep(1)}>上一步</AntButton>
              <AntButton block onClick={handleSkip}>跳过，直接完成</AntButton>
              <AntButton block type="primary" onClick={handleFinish}>
                完成创建
              </AntButton>
            </div>
          </Card>
        )}

        {/* 第四步：完成 */}
        {currentStep === 3 && (
          <Card title="项目创建完成">
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <CheckCircleOutlined style={{ fontSize: 64, color: '#52c41a' }} />
              <div style={{ marginTop: 16, fontSize: 18, fontWeight: 500 }}>项目创建成功！</div>
              <div style={{ marginTop: 8, color: '#666' }}>
                您可以在项目详情页查看和编辑企业信息，上传资料，或生成体系文件
              </div>
              <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 24 }}>
                <AntButton onClick={() => navigate('/')}>返回首页</AntButton>
                <AntButton type="primary" onClick={handleFinish}>
                  进入项目详情
                </AntButton>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ProjectCreatePage;
