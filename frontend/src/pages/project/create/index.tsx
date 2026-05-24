import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { NavBar, Button, Toast, Dialog, Form, Input } from 'antd-mobile';
import { Card, Button as AntButton, Steps, message, Modal, Form as AntForm, Input as AntInput } from 'antd';
import { useResponsive } from '@/hooks/useResponsive';
import { useProject } from '@/hooks/useProject';
import NaturalLanguageInput from '@/components/NaturalLanguageInput';
import type { ParseResult } from '@/api';

/** 创建项目页面 */
const ProjectCreatePage: React.FC = () => {
  const { isMobile } = useResponsive();
  const navigate = useNavigate();
  const { createNewProject, parseText } = useProject();

  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [parsing, setParsing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

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
          companyName: '',
          industry: '',
          employeeCount: '',
          registeredCapital: '',
          address: '',
          contactPerson: '',
          contactPhone: '',
          businessScope: '',
          missingFields: [
            'companyName',
            'industry',
            'employeeCount',
            'registeredCapital',
            'address',
            'contactPerson',
            'contactPhone',
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
            missingFields: (parseResult.missingFields || []).filter(
              (f) => f !== fieldName,
            ),
          });
        }
      },
    });
  }, [parseResult]);

  /** 创建项目 */
  const handleCreate = useCallback(async () => {
    if (!parseResult) return;
    setSubmitting(true);
    try {
      const project = await createNewProject({
        companyName: parseResult.companyName,
        industry: parseResult.industry,
        employeeCount: parseResult.employeeCount,
        registeredCapital: parseResult.registeredCapital,
        address: parseResult.address,
        contactPerson: parseResult.contactPerson,
        contactPhone: parseResult.contactPhone,
        name: parseResult.companyName || '新项目',
      });
      Toast.show({ content: '项目创建成功', icon: 'success' });
      navigate(`/project/${project.id}`);
    } catch {
      Toast.show({ content: '创建失败，请重试', icon: 'fail' });
    } finally {
      setSubmitting(false);
    }
  }, [parseResult, createNewProject, navigate]);

  /** 字段中文名映射 */
  const fieldLabels: Record<string, string> = {
    companyName: '公司名称',
    industry: '所属行业',
    employeeCount: '员工人数',
    registeredCapital: '注册资本',
    address: '公司地址',
    contactPerson: '联系人',
    contactPhone: '联系电话',
    businessScope: '经营范围',
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
              {parseResult.missingFields && parseResult.missingFields.length > 0 && (
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
                  以下信息缺失，请点击补充：{parseResult.missingFields.map((f) => fieldLabels[f]).join('、')}
                </div>
              )}

              {/* 信息确认表 */}
              {Object.entries(fieldLabels).map(([key, label]) => {
                const value = (parseResult as Record<string, unknown>)[key] as string;
                const isMissing = parseResult.missingFields?.includes(key);

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

      {/* 第一步：自然语言输入 */}
      {currentStep === 0 && (
        <Card title="请描述您客户的企业情况">
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
        </Card>
      )}

      {/* 第二步：确认信息 */}
      {currentStep === 1 && parseResult && (
        <Card title="确认企业信息">
          {parseResult.missingFields && parseResult.missingFields.length > 0 && (
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
              以下信息缺失，请点击补充：{parseResult.missingFields.map((f) => fieldLabels[f]).join('、')}
            </div>
          )}

          <AntForm layout="vertical">
            {Object.entries(fieldLabels).map(([key, label]) => {
              const value = (parseResult as Record<string, unknown>)[key] as string;
              const isMissing = parseResult.missingFields?.includes(key);

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
                        missingFields: (parseResult.missingFields || []).filter(
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
