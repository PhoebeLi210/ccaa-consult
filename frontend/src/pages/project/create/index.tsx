import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { NavBar, Button, Toast, Dialog, Form, Input } from 'antd-mobile';
import { Card, Button as AntButton, Steps, message, Modal, Form as AntForm, Input as AntInput, Tabs, Tag } from 'antd';
import { useResponsive } from '@/hooks/useResponsive';
import { useProject } from '@/hooks/useProject';
import NaturalLanguageInput from '@/components/NaturalLanguageInput';
import IndustrySelector from '@/components/IndustrySelector';
import { checkIndustryFeatures } from '@/api';
import type { ParseResult } from '@/api';
import type { IndustryConfig } from '@/api';

/** 创建项目页面 */
const ProjectCreatePage: React.FC = () => {
  const { isMobile } = useResponsive();
  const navigate = useNavigate();
  const { createNewProject, parseText } = useProject();

  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [parsing, setParsing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [inputMode, setInputMode] = useState<'ai' | 'manual'>('ai');
  const [selectedIndustry, setSelectedIndustry] = useState<{ code: string; industry: IndustryConfig } | null>(null);
  const [industryFeatures, setIndustryFeatures] = useState<any>(null);
  const [checkingFeatures, setCheckingFeatures] = useState(false);

  /** AI解析回调（实时解析） */
  const handleParse = useCallback(
    async (text: string) => {
      setParsing(true);
      try {
        const result = await parseText(text);
        setParseResult(result);
      } catch {
        // 解析失败时使用模拟数据
        setParseResult({
          company_name: '',
          industry: '',
          employee_count: '',
          registered_capital: '',
          address: '',
          contact_person: '',
          contact_phone: '',
          business_scope: '',
          missing_fields: [
            'company_name',
            'industry',
            'employee_count',
            'registered_capital',
            'address',
            'contact_person',
            'contact_phone',
          ],
        });
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

  /** 补充缺失字段 */
  const handleFieldFill = useCallback((fieldName: string) => {
    Dialog.prompt({
      title: '补充信息',
      placeholder: '请输入内容',
      onConfirm: (value) => {
        if (value && parseResult) {
          setParseResult({
            ...parseResult,
            [fieldName]: value,
            missing_fields: (parseResult.missing_fields || []).filter(
              (f) => f !== fieldName,
            ),
          });
        }
      },
    });
  }, [parseResult]);

  /** 行业选择回调 */
  const handleIndustrySelect = useCallback(async (code: string, industry: IndustryConfig) => {
    setSelectedIndustry({ code, industry });
    if (parseResult) {
      setParseResult({
        ...parseResult,
        industry: industry.industry_name,
      });
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

  /** 手动创建项目 */
  const handleManualCreate = useCallback(async (values: Record<string, string>) => {
    setSubmitting(true);
    try {
      const project = await createNewProject({
        company_name: values.company_name,
        industry: values.industry || selectedIndustry?.industry?.industry_name || '',
        employee_count: values.employee_count,
        registered_capital: values.registered_capital,
        address: values.address,
        contact_person: values.contact_person,
        contact_phone: values.contact_phone,
        name: values.company_name || '新项目',
      });
      Toast.show({ content: '项目创建成功', icon: 'success' });
      navigate(`/project/${project.id}`);
    } catch {
      Toast.show({ content: '创建失败，请重试', icon: 'fail' });
    } finally {
      setSubmitting(false);
    }
  }, [createNewProject, navigate, selectedIndustry]);

  /** AI模式创建项目 */
  const handleCreate = useCallback(async () => {
    if (!parseResult) return;
    setSubmitting(true);
    try {
      const project = await createNewProject({
        company_name: parseResult.company_name,
        industry: parseResult.industry || selectedIndustry?.industry?.industry_name || '',
        employee_count: parseResult.employee_count,
        registered_capital: parseResult.registered_capital,
        address: parseResult.address,
        contact_person: parseResult.contact_person,
        contact_phone: parseResult.contact_phone,
        name: parseResult.company_name || '新项目',
      });
      Toast.show({ content: '项目创建成功', icon: 'success' });
      navigate(`/project/${project.id}`);
    } catch {
      Toast.show({ content: '创建失败，请重试', icon: 'fail' });
    } finally {
      setSubmitting(false);
    }
  }, [parseResult, createNewProject, navigate, selectedIndustry]);

  /** 字段中文名映射 */
  const fieldLabels: Record<string, string> = {
    company_name: '公司名称',
    industry: '所属行业',
    employee_count: '员工人数',
    registered_capital: '注册资本',
    address: '公司地址',
    contact_person: '联系人',
    contact_phone: '联系电话',
    business_scope: '经营范围',
  };

  /* ==================== 移动端渲染 ==================== */
  if (isMobile) {
    return (
      <div>
        <NavBar onBack={() => navigate(-1)} style={{ backgroundColor: '#1677ff', color: '#fff' }}>
          创建项目
        </NavBar>

        <div style={{ padding: 12 }}>
          {/* 步骤指示 */}
          <Steps current={currentStep} style={{ marginBottom: 16 }}>
            <Steps.Step title="描述企业" />
            <Steps.Step title="确认信息" />
            <Steps.Step title="完成" />
          </Steps>

          {/* 第一步：自然语言输入 */}
          {currentStep === 0 && (
            <div>
              <h3 style={{ marginBottom: 12, fontSize: 16 }}>请描述您客户的企业情况</h3>
              <NaturalLanguageInput
                onSubmit={handleSubmit}
                onParse={handleParse}
                loading={parsing}
                parseResult={parseResult}
              />
            </div>
          )}

          {/* 第二步：确认信息 */}
          {currentStep === 1 && parseResult && (
            <div>
              <h3 style={{ marginBottom: 12, fontSize: 16 }}>确认企业信息</h3>

              {/* 缺失项提示 */}
              {parseResult.missing_fields && parseResult.missing_fields.length > 0 && (
                <div
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#fff7e6',
                    border: '1px solid #ffd591',
                    borderRadius: 6,
                    marginBottom: 12,
                    fontSize: 13,
                    color: '#d46b08',
                  }}
                >
                  以下信息缺失，请点击补充：{parseResult.missing_fields.map((f) => fieldLabels[f]).join('、')}
                </div>
              )}

              {/* 信息确认表 */}
              {Object.entries(fieldLabels).map(([key, label]) => {
                const value = (parseResult as Record<string, unknown>)[key] as string;
                const isMissing = parseResult.missing_fields?.includes(key);

                return (
                  <div
                    key={key}
                    onClick={() => isMissing && handleFieldFill(key)}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '10px 0',
                      borderBottom: '1px solid #f0f0f0',
                      cursor: isMissing ? 'pointer' : 'default',
                      backgroundColor: isMissing ? '#fff2f0' : 'transparent',
                      paddingInline: 8,
                      borderRadius: 4,
                      marginBottom: 2,
                    }}
                  >
                    <span style={{ color: isMissing ? '#ff4d4f' : '#666', fontSize: 14 }}>
                      {label}
                      {isMissing && <span style={{ marginLeft: 4 }}>*</span>}
                    </span>
                    <span
                      style={{
                        color: value ? '#333' : '#ccc',
                        fontSize: 14,
                        fontWeight: value ? 500 : 400,
                      }}
                    >
                      {value || '点击补充'}
                    </span>
                  </div>
                );
              })}

              {/* 行业特征展示 */}
              {industryFeatures && (
                <Card title="行业特征" style={{ marginTop: 16 }} loading={checkingFeatures}>
                  <div style={{ marginBottom: 12 }}>
                    <div style={{ fontWeight: 500, marginBottom: 8 }}>行业特征标签</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {industryFeatures.has_design_development && <Tag color="blue">设计开发</Tag>}
                      {industryFeatures.has_equipment_operations && <Tag color="green">设备操作</Tag>}
                      {industryFeatures.has_multi_projects && <Tag color="orange">多项目</Tag>}
                      {industryFeatures.has_outsourcing && <Tag color="purple">外包</Tag>}
                      {!industryFeatures.has_design_development && !industryFeatures.has_equipment_operations && !industryFeatures.has_multi_projects && !industryFeatures.has_outsourcing && (
                        <span style={{ color: '#999' }}>无特殊特征</span>
                      )}
                    </div>
                  </div>
                  {industryFeatures.emergency_plans && industryFeatures.emergency_plans.length > 0 && (
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontWeight: 500, marginBottom: 8 }}>应急预案</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {industryFeatures.emergency_plans.map((plan: string) => (
                          <Tag key={plan} color="red">{plan}</Tag>
                        ))}
                      </div>
                    </div>
                  )}
                  {industryFeatures.required_licenses && industryFeatures.required_licenses.length > 0 && (
                    <div>
                      <div style={{ fontWeight: 500, marginBottom: 8 }}>所需资质许可</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        {industryFeatures.required_licenses.map((license: string) => (
                          <Tag key={license} color="cyan">{license}</Tag>
                        ))}
                      </div>
                    </div>
                  )}
                </Card>
              )}

              {/* 操作按钮 */}
              <div style={{ display: 'flex', gap: 12, marginTop: 20 }}>
                <Button block onClick={() => setCurrentStep(0)}>
                  上一步
                </Button>
                <Button
                  block
                  color="primary"
                  loading={submitting}
                  onClick={handleCreate}
                >
                  创建项目
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  /* ==================== PC端渲染 ==================== */
  return (
    <div>
      <Steps
        current={currentStep}
        style={{ marginBottom: 24 }}
        items={[
          { title: '描述企业' },
          { title: '确认信息' },
          { title: '完成' },
        ]}
      />

      {/* 第一步：选择输入方式 */}
      {currentStep === 0 && (
        <Card>
          <Tabs
            activeKey={inputMode}
            onChange={(key) => setInputMode(key as 'ai' | 'manual')}
            items={[
              {
                key: 'ai',
                label: 'AI智能解析',
                children: (
                  <div>
                    <p style={{ color: '#666', marginBottom: 16 }}>
                      用自然语言描述企业情况，AI自动提取关键信息
                    </p>
                    <NaturalLanguageInput
                      onSubmit={handleSubmit}
                      onParse={handleParse}
                      loading={parsing}
                      parseResult={parseResult}
                    />
                    <div style={{ marginTop: 16, textAlign: 'right' }}>
                      <AntButton
                        type="primary"
                        size="large"
                        disabled={!parseResult}
                        onClick={() => setCurrentStep(1)}
                      >
                        下一步
                      </AntButton>
                    </div>
                  </div>
                ),
              },
              {
                key: 'manual',
                label: '手动填写',
                children: (
                  <div>
                    <p style={{ color: '#666', marginBottom: 16 }}>
                      手动填写企业信息，适合已知详细信息的情况
                    </p>
                    <IndustrySelector
                      value={selectedIndustry?.code}
                      onChange={handleIndustrySelect}
                      style={{ marginBottom: 24 }}
                    />
                    <AntForm layout="vertical">
                      {Object.entries(fieldLabels).map(([key, label]) => (
                        <AntForm.Item key={key} label={label}>
                          <AntInput
                            placeholder={`请输入${label}`}
                            onChange={(e) => {
                              if (parseResult) {
                                setParseResult({
                                  ...parseResult,
                                  [key]: e.target.value,
                                });
                              } else {
                                setParseResult({
                                  company_name: '',
                                  industry: '',
                                  employee_count: '',
                                  registered_capital: '',
                                  address: '',
                                  contact_person: '',
                                  contact_phone: '',
                                  business_scope: '',
                                  missing_fields: [],
                                  [key]: e.target.value,
                                } as ParseResult);
                              }
                            }}
                          />
                        </AntForm.Item>
                      ))}
                    </AntForm>
                    <div style={{ textAlign: 'right' }}>
                      <AntButton
                        type="primary"
                        size="large"
                        onClick={() => setCurrentStep(1)}
                      >
                        下一步
                      </AntButton>
                    </div>
                  </div>
                ),
              },
            ]}
          />
        </Card>
      )}

      {/* 第二步：确认信息 */}
      {currentStep === 1 && parseResult && (
        <Card title="确认企业信息">
          {parseResult.missing_fields && parseResult.missing_fields.length > 0 && (
            <div
              style={{
                padding: '10px 16px',
                backgroundColor: '#fff7e6',
                border: '1px solid #ffd591',
                borderRadius: 6,
                marginBottom: 16,
                color: '#d46b08',
              }}
            >
              以下信息缺失，请点击补充：{parseResult.missing_fields.map((f) => fieldLabels[f]).join('、')}
            </div>
          )}

          {/* 行业选择器（第二步也可修改行业） */}
          <IndustrySelector
            value={selectedIndustry?.code}
            onChange={handleIndustrySelect}
            style={{ marginBottom: 24 }}
          />

          {/* 行业特征展示 */}
          {industryFeatures && (
            <Card title="行业特征" style={{ marginBottom: 24 }} loading={checkingFeatures}>
              <div style={{ marginBottom: 16 }}>
                <div style={{ fontWeight: 500, marginBottom: 8 }}>行业特征标签</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {industryFeatures.has_design_development && <Tag color="blue">设计开发</Tag>}
                  {industryFeatures.has_equipment_operations && <Tag color="green">设备操作</Tag>}
                  {industryFeatures.has_multi_projects && <Tag color="orange">多项目</Tag>}
                  {industryFeatures.has_outsourcing && <Tag color="purple">外包</Tag>}
                  {!industryFeatures.has_design_development && !industryFeatures.has_equipment_operations && !industryFeatures.has_multi_projects && !industryFeatures.has_outsourcing && (
                    <span style={{ color: '#999' }}>无特殊特征</span>
                  )}
                </div>
              </div>
              {industryFeatures.emergency_plans && industryFeatures.emergency_plans.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontWeight: 500, marginBottom: 8 }}>应急预案</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {industryFeatures.emergency_plans.map((plan: string) => (
                      <Tag key={plan} color="red">{plan}</Tag>
                    ))}
                  </div>
                </div>
              )}
              {industryFeatures.required_licenses && industryFeatures.required_licenses.length > 0 && (
                <div>
                  <div style={{ fontWeight: 500, marginBottom: 8 }}>所需资质许可</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {industryFeatures.required_licenses.map((license: string) => (
                      <Tag key={license} color="cyan">{license}</Tag>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          )}

          <AntForm layout="vertical">
            {Object.entries(fieldLabels).map(([key, label]) => {
              const value = (parseResult as Record<string, unknown>)[key] as string;
              const isMissing = parseResult.missing_fields?.includes(key);

              return (
                <AntForm.Item
                  key={key}
                  label={
                    <span>
                      {label}
                      {isMissing && (
                        <span style={{ color: '#ff4d4f', marginLeft: 4 }}>*</span>
                      )}
                    </span>
                  }
                  required={isMissing}
                  validateStatus={isMissing ? 'warning' : undefined}
                  help={isMissing ? '该字段缺失，请补充' : undefined}
                >
                  <AntInput
                    value={value}
                    placeholder={isMissing ? '请输入' + label : ''}
                    onChange={(e) => {
                      setParseResult({
                        ...parseResult,
                        [key]: e.target.value,
                        missing_fields: (parseResult.missing_fields || []).filter(
                          (f) => f !== key,
                        ),
                      });
                    }}
                    status={isMissing ? 'warning' : undefined}
                  />
                </AntForm.Item>
              );
            })}
          </AntForm>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 16 }}>
            <AntButton size="large" onClick={() => setCurrentStep(0)}>
              上一步
            </AntButton>
            <AntButton
              type="primary"
              size="large"
              loading={submitting}
              onClick={handleCreate}
            >
              创建项目
            </AntButton>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ProjectCreatePage;
