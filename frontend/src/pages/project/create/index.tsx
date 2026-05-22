import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { NavBar, Button, Toast, Dialog, Form, Input } from 'antd-mobile';
import { Card, Button as AntButton, Steps, message, Modal, Form as AntForm, Input as AntInput, Alert, Tag } from 'antd';
import { useResponsive } from '@/hooks/useResponsive';
import { useProject } from '@/hooks/useProject';
import NaturalLanguageInput from '@/components/NaturalLanguageInput';
import CertStageSelector from './CertStageSelector';
import OldFilesUpload from './OldFilesUpload';
import type { ParseResult } from '@/api';
import type { CertStageType, CertStageOption } from './CertStageSelector';
import type { ExtractionResult } from './OldFilesUpload';

/** 创建项目页面 */
const ProjectCreatePage: React.FC = () => {
  const { isMobile } = useResponsive();
  const navigate = useNavigate();
  const { createNewProject, parseText } = useProject();

  const [parseResult, setParseResult] = useState<ParseResult | null>(null);
  const [parsing, setParsing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  // 认证阶段相关状态
  const [selectedStage, setSelectedStage] = useState<CertStageType | null>(null);
  const [stageInfo, setStageInfo] = useState<CertStageOption | null>(null);

  // 旧版文件相关状态
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);
  const [oldFilesConfirmed, setOldFilesConfirmed] = useState(false);

  // 临时项目ID（用于旧版文件上传）
  const [tempProjectId] = useState<string>(() => `temp-${Date.now()}`);

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

  /** 认证阶段选择回调 */
  const handleStageChange = useCallback((stage: CertStageType, info: CertStageOption) => {
    setSelectedStage(stage);
    setStageInfo(info);
    // 如果切换阶段，重置旧版文件状态
    if (stage !== selectedStage) {
      setExtractionResult(null);
      setOldFilesConfirmed(false);
    }
  }, [selectedStage]);

  /** 旧版文件提取完成回调 */
  const handleExtractComplete = useCallback((result: ExtractionResult) => {
    setExtractionResult(result);
  }, []);

  /** 旧版文件确认回调 */
  const handleOldFilesConfirm = useCallback((result: ExtractionResult) => {
    setExtractionResult(result);
    setOldFilesConfirmed(true);
    Toast.show({ content: '旧版文件信息已确认', icon: 'success' });
  }, []);

  /** 判断是否需要上传旧版文件 */
  const needOldFiles = selectedStage !== null && selectedStage !== 'initial';

  /** 获取总步骤数 */
  const getTotalSteps = () => {
    if (!selectedStage) return 4; // 选择阶段 + 描述企业 + 确认信息 + 完成
    if (needOldFiles) return 5; // 选择阶段 + 描述企业 + 上传旧版文件 + 确认信息 + 完成
    return 4;
  };

  /** 获取步骤配置 */
  const getStepItems = () => {
    const items = [
      { title: '选择阶段' },
      { title: '描述企业' },
    ];
    if (needOldFiles) {
      items.push({ title: '上传旧版文件' });
    }
    items.push({ title: '确认信息' });
    items.push({ title: '完成' });
    return items;
  };

  /** 获取当前步骤在UI中的显示索引 */
  const getDisplayStep = () => {
    if (currentStep === 0) return 0; // 选择阶段
    if (currentStep === 1) return 1; // 描述企业
    if (currentStep === 2 && needOldFiles) return 2; // 上传旧版文件
    if (needOldFiles) {
      if (currentStep === 2) return 3; // 确认信息
      if (currentStep === 3) return 4; // 完成
    }
    if (currentStep === 2) return 2; // 确认信息
    if (currentStep === 3) return 3; // 完成
    return currentStep;
  };

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

  /** 渲染文件范围提示 */
  const renderScopeHint = () => {
    if (!stageInfo) return null;
    return (
      <Alert
        message={
          <Space>
            <span>当前阶段文件范围：</span>
            <Tag color="blue">{stageInfo.name}</Tag>
          </Space>
        }
        description={
          <div>
            <div style={{ marginBottom: 4 }}>
              <strong>需要生成：</strong>
              {stageInfo.documentScope.join('、') || '无'}
            </div>
            {stageInfo.updateScope.length > 0 && (
              <div>
                <strong>需要更新：</strong>
                {stageInfo.updateScope.join('、')}
              </div>
            )}
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
    );
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
          <Steps current={getDisplayStep()} style={{ marginBottom: 16 }}>
            {getStepItems().map((item, index) => (
              <Steps.Step key={index} title={item.title} />
            ))}
          </Steps>

          {/* 第一步：选择认证阶段 */}
          {currentStep === 0 && (
            <div>
              <h3 style={{ marginBottom: 12, fontSize: 16 }}>请选择认证阶段</h3>
              <CertStageSelector
                value={selectedStage || undefined}
                onChange={handleStageChange}
                showScopeDetail={true}
              />
              <div style={{ marginTop: 16, textAlign: 'right' }}>
                <Button
                  block
                  color="primary"
                  disabled={!selectedStage}
                  onClick={() => setCurrentStep(1)}
                >
                  下一步
                </Button>
              </div>
            </div>
          )}

          {/* 第二步：描述企业 */}
          {currentStep === 1 && (
            <div>
              <h3 style={{ marginBottom: 12, fontSize: 16 }}>请描述您客户的企业情况</h3>
              {renderScopeHint()}
              <NaturalLanguageInput
                onSubmit={handleSubmit}
                onParse={handleParse}
                loading={parsing}
                parseResult={parseResult}
              />
              <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                <Button block onClick={() => setCurrentStep(0)}>
                  上一步
                </Button>
                <Button
                  block
                  color="primary"
                  disabled={!parseResult}
                  onClick={() => {
                    if (needOldFiles) {
                      setCurrentStep(2);
                    } else {
                      setCurrentStep(3);
                    }
                  }}
                >
                  下一步
                </Button>
              </div>
            </div>
          )}

          {/* 第三步：上传旧版文件（仅监督审核和再认证） */}
          {currentStep === 2 && needOldFiles && (
            <div>
              <h3 style={{ marginBottom: 12, fontSize: 16 }}>上传旧版体系文件</h3>
              <OldFilesUpload
                projectId={tempProjectId}
                onExtractComplete={handleExtractComplete}
                onConfirm={handleOldFilesConfirm}
              />
              <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                <Button block onClick={() => setCurrentStep(1)}>
                  上一步
                </Button>
                <Button
                  block
                  color="primary"
                  disabled={!oldFilesConfirmed}
                  onClick={() => setCurrentStep(3)}
                >
                  下一步
                </Button>
              </div>
            </div>
          )}

          {/* 确认信息步骤 */}
          {((currentStep === 2 && !needOldFiles) || (currentStep === 3 && needOldFiles)) && parseResult && (
            <div>
              <h3 style={{ marginBottom: 12, fontSize: 16 }}>确认企业信息</h3>
              {renderScopeHint()}

              {/* 认证阶段信息 */}
              {stageInfo && (
                <div
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#e6f7ff',
                    border: '1px solid #91d5ff',
                    borderRadius: 6,
                    marginBottom: 12,
                    fontSize: 13,
                    color: '#096dd9',
                  }}
                >
                  认证阶段：{stageInfo.name}（{stageInfo.year}）
                </div>
              )}

              {/* 旧版文件提取结果摘要 */}
              {extractionResult && (
                <div
                  style={{
                    padding: '8px 12px',
                    backgroundColor: '#f6ffed',
                    border: '1px solid #b7eb8f',
                    borderRadius: 6,
                    marginBottom: 12,
                    fontSize: 13,
                    color: '#389e0d',
                  }}
                >
                  已提取旧版文件信息：{extractionResult.departments.length} 个部门、
                  {extractionResult.qualityObjectives.length} 个质量目标
                </div>
              )}

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
                <Button block onClick={() => setCurrentStep(needOldFiles ? 2 : 1)}>
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
        current={getDisplayStep()}
        style={{ marginBottom: 24 }}
        items={getStepItems()}
      />

      {/* 第一步：选择认证阶段 */}
      {currentStep === 0 && (
        <Card title="请选择认证阶段">
          <CertStageSelector
            value={selectedStage || undefined}
            onChange={handleStageChange}
            showScopeDetail={true}
          />
          <div style={{ marginTop: 16, textAlign: 'right' }}>
            <AntButton
              type="primary"
              size="large"
              disabled={!selectedStage}
              onClick={() => setCurrentStep(1)}
            >
              下一步
            </AntButton>
          </div>
        </Card>
      )}

      {/* 第二步：描述企业 */}
      {currentStep === 1 && (
        <Card title="请描述您客户的企业情况">
          {renderScopeHint()}
          <NaturalLanguageInput
            onSubmit={handleSubmit}
            onParse={handleParse}
            loading={parsing}
            parseResult={parseResult}
          />
          <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between' }}>
            <AntButton size="large" onClick={() => setCurrentStep(0)}>
              上一步
            </AntButton>
            <AntButton
              type="primary"
              size="large"
              disabled={!parseResult}
              onClick={() => {
                if (needOldFiles) {
                  setCurrentStep(2);
                } else {
                  setCurrentStep(3);
                }
              }}
            >
              下一步
            </AntButton>
          </div>
        </Card>
      )}

      {/* 第三步：上传旧版文件（仅监督审核和再认证） */}
      {currentStep === 2 && needOldFiles && (
        <div>
          <OldFilesUpload
            projectId={tempProjectId}
            onExtractComplete={handleExtractComplete}
            onConfirm={handleOldFilesConfirm}
          />
          <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between' }}>
            <AntButton size="large" onClick={() => setCurrentStep(1)}>
              上一步
            </AntButton>
            <AntButton
              type="primary"
              size="large"
              disabled={!oldFilesConfirmed}
              onClick={() => setCurrentStep(3)}
            >
              下一步
            </AntButton>
          </div>
        </div>
      )}

      {/* 确认信息步骤 */}
      {((currentStep === 2 && !needOldFiles) || (currentStep === 3 && needOldFiles)) && parseResult && (
        <Card title="确认企业信息">
          {renderScopeHint()}

          {/* 认证阶段信息 */}
          {stageInfo && (
            <Alert
              message={
                <Space>
                  <span>认证阶段：</span>
                  <Tag color="blue">{stageInfo.name}</Tag>
                  <Tag>{stageInfo.year}</Tag>
                </Space>
              }
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          {/* 旧版文件提取结果摘要 */}
          {extractionResult && (
            <Alert
              message="旧版文件信息已提取"
              description={
                <Space split="，">
                  <span>{extractionResult.departments.length} 个部门</span>
                  <span>{extractionResult.qualityObjectives.length} 个质量目标</span>
                  <span>{extractionResult.fileNamingRules.length} 个编号规则</span>
                </Space>
              }
              type="success"
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

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
            <AntButton size="large" onClick={() => setCurrentStep(needOldFiles ? 2 : 1)}>
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