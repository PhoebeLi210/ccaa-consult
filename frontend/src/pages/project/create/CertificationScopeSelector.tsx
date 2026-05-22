import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, Checkbox, AutoComplete, Tag, Button, Space, Typography, Alert, Spin, TreeSelect } from 'antd';
import { SearchOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

// ============ 类型定义 ============

/** 认证标准 */
interface CertificationStandard {
  code: string;
  name: string;
  name_en: string;
  description: string;
  version: string;
}

/** 专业代码 */
interface ProfessionalCode {
  code: string;
  name: string;
  name_en?: string;
  description?: string;
  parent_code?: string;
  level: number;
  children?: ProfessionalCode[];
  applicable_standards: string[];
}

/** 验证结果 */
interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  details: {
    valid_standards: string[];
    valid_codes: Array<{ code: string; name: string; applicable_standards: string[] }>;
    invalid_standards: string[];
    invalid_codes: string[];
    incompatible_codes: Array<{ code: string; standard: string }>;
  };
}

/** 组件Props */
interface CertificationScopeSelectorProps {
  /** 初始选中的认证标准 */
  initialStandards?: string[];
  /** 初始选中的专业代码 */
  initialProfessionalCodes?: string[];
  /** 选择变更回调 */
  onChange?: (standards: string[], professionalCodes: string[]) => void;
  /** 确认回调 */
  onConfirm?: (standards: string[], professionalCodes: string[]) => void;
  /** 是否显示确认按钮 */
  showConfirmButton?: boolean;
  /** 确认按钮文字 */
  confirmButtonText?: string;
  /** 是否允许多选专业代码 */
  multipleProfessionalCodes?: boolean;
  /** 自定义样式 */
  className?: string;
  /** 是否禁用 */
  disabled?: boolean;
}

// ============ API 服务 ============

const API_BASE_URL = '/api/v1';

/** 获取认证标准列表 */
const fetchStandards = async (): Promise<CertificationStandard[]> => {
  const response = await fetch(`${API_BASE_URL}/certification-scope/standards`);
  if (!response.ok) throw new Error('获取认证标准失败');
  return response.json();
};

/** 获取专业代码分类树 */
const fetchProfessionalCodes = async (): Promise<ProfessionalCode[]> => {
  const response = await fetch(`${API_BASE_URL}/certification-scope/professional-codes`);
  if (!response.ok) throw new Error('获取专业代码失败');
  return response.json();
};

/** 搜索专业代码 */
const searchProfessionalCodes = async (keyword: string): Promise<{ total: number; codes: ProfessionalCode[] }> => {
  const response = await fetch(`${API_BASE_URL}/certification-scope/professional-codes/search?q=${encodeURIComponent(keyword)}`);
  if (!response.ok) throw new Error('搜索专业代码失败');
  return response.json();
};

/** 验证认证范围组合 */
const validateScope = async (standards: string[], professionalCodes: string[]): Promise<ValidationResult> => {
  const response = await fetch(`${API_BASE_URL}/certification-scope/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ standards, professional_codes: professionalCodes }),
  });
  if (!response.ok) throw new Error('验证失败');
  return response.json();
};

// ============ 组件 ============

/**
 * 认证范围选择组件
 * 
 * 功能：
 * - 三列选择：认证标准（ISO9001/14001/45001）
 * - 专业代码搜索框（带自动完成）
 * - 已选项标签展示
 * - 确认按钮
 */
const CertificationScopeSelector: React.FC<CertificationScopeSelectorProps> = ({
  initialStandards = [],
  initialProfessionalCodes = [],
  onChange,
  onConfirm,
  showConfirmButton = true,
  confirmButtonText = '确认选择',
  multipleProfessionalCodes = true,
  className = '',
  disabled = false,
}) => {
  // ============ 状态 ============
  
  // 认证标准列表
  const [standards, setStandards] = useState<CertificationStandard[]>([]);
  // 专业代码树
  const [professionalCodesTree, setProfessionalCodesTree] = useState<ProfessionalCode[]>([]);
  // 选中的认证标准
  const [selectedStandards, setSelectedStandards] = useState<string[]>(initialStandards);
  // 选中的专业代码
  const [selectedProfessionalCodes, setSelectedProfessionalCodes] = useState<string[]>(initialProfessionalCodes);
  // 搜索关键词
  const [searchKeyword, setSearchKeyword] = useState('');
  // 搜索选项
  const [searchOptions, setSearchOptions] = useState<{ value: string; label: React.ReactNode; code: ProfessionalCode }[]>([]);
  // 验证结果
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  // 加载状态
  const [loading, setLoading] = useState({
    standards: false,
    codes: false,
    search: false,
    validate: false,
  });
  // 错误信息
  const [error, setError] = useState<string | null>(null);

  // ============ 初始化加载 ============
  
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(prev => ({ ...prev, standards: true, codes: true }));
    setError(null);
    
    try {
      const [standardsData, codesData] = await Promise.all([
        fetchStandards(),
        fetchProfessionalCodes(),
      ]);
      setStandards(standardsData);
      setProfessionalCodesTree(codesData);
    } catch (err) {
      setError('加载数据失败，请刷新页面重试');
      console.error('加载认证范围数据失败:', err);
    } finally {
      setLoading(prev => ({ ...prev, standards: false, codes: false }));
    }
  };

  // ============ 事件处理 ============

  /** 处理认证标准选择变更 */
  const handleStandardChange = useCallback((standardCode: string, checked: boolean) => {
    setSelectedStandards(prev => {
      const newStandards = checked
        ? [...prev, standardCode]
        : prev.filter(s => s !== standardCode);
      
      // 触发变更回调
      onChange?.(newStandards, selectedProfessionalCodes);
      
      // 自动验证
      if (newStandards.length > 0 && selectedProfessionalCodes.length > 0) {
        performValidation(newStandards, selectedProfessionalCodes);
      }
      
      return newStandards;
    });
  }, [selectedProfessionalCodes, onChange]);

  /** 处理专业代码选择 */
  const handleProfessionalCodeSelect = useCallback((value: string, option: any) => {
    const code = option?.code as ProfessionalCode;
    if (!code) return;

    setSelectedProfessionalCodes(prev => {
      let newCodes: string[];
      
      if (multipleProfessionalCodes) {
        // 多选模式
        if (prev.includes(code.code)) {
          newCodes = prev; // 已存在，不重复添加
        } else {
          newCodes = [...prev, code.code];
        }
      } else {
        // 单选模式
        newCodes = [code.code];
      }
      
      // 触发变更回调
      onChange?.(selectedStandards, newCodes);
      
      // 自动验证
      if (selectedStandards.length > 0 && newCodes.length > 0) {
        performValidation(selectedStandards, newCodes);
      }
      
      return newCodes;
    });

    // 清空搜索框
    setSearchKeyword('');
    setSearchOptions([]);
  }, [selectedStandards, multipleProfessionalCodes, onChange]);

  /** 移除已选专业代码 */
  const handleRemoveProfessionalCode = useCallback((code: string) => {
    setSelectedProfessionalCodes(prev => {
      const newCodes = prev.filter(c => c !== code);
      onChange?.(selectedStandards, newCodes);
      
      if (selectedStandards.length > 0 && newCodes.length > 0) {
        performValidation(selectedStandards, newCodes);
      } else {
        setValidationResult(null);
      }
      
      return newCodes;
    });
  }, [selectedStandards, onChange]);

  /** 搜索专业代码 */
  const handleSearch = useCallback(async (keyword: string) => {
    setSearchKeyword(keyword);
    
    if (!keyword || keyword.length < 1) {
      setSearchOptions([]);
      return;
    }

    setLoading(prev => ({ ...prev, search: true }));
    
    try {
      const result = await searchProfessionalCodes(keyword);
      const options = result.codes.map(code => ({
        value: code.code,
        label: (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>
              <Text strong>{code.code}</Text>
              <Text style={{ marginLeft: 8 }}>{code.name}</Text>
            </span>
            {code.level > 1 && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                {code.parent_code}
              </Text>
            )}
          </div>
        ),
        code,
      }));
      setSearchOptions(options);
    } catch (err) {
      console.error('搜索专业代码失败:', err);
    } finally {
      setLoading(prev => ({ ...prev, search: false }));
    }
  }, []);

  /** 执行验证 */
  const performValidation = useCallback(async (standards: string[], codes: string[]) => {
    if (standards.length === 0 || codes.length === 0) {
      setValidationResult(null);
      return;
    }

    setLoading(prev => ({ ...prev, validate: true }));
    
    try {
      const result = await validateScope(standards, codes);
      setValidationResult(result);
    } catch (err) {
      console.error('验证失败:', err);
    } finally {
      setLoading(prev => ({ ...prev, validate: false }));
    }
  }, []);

  /** 确认选择 */
  const handleConfirm = useCallback(() => {
    if (selectedStandards.length === 0) {
      setError('请至少选择一个认证标准');
      return;
    }
    if (selectedProfessionalCodes.length === 0) {
      setError('请至少选择一个专业代码');
      return;
    }
    
    setError(null);
    onConfirm?.(selectedStandards, selectedProfessionalCodes);
  }, [selectedStandards, selectedProfessionalCodes, onConfirm]);

  // ============ 辅助函数 ============

  /** 获取专业代码详情 */
  const getProfessionalCodeDetail = useCallback((code: string): ProfessionalCode | undefined => {
    const findCode = (codes: ProfessionalCode[]): ProfessionalCode | undefined => {
      for (const c of codes) {
        if (c.code === code) return c;
        if (c.children) {
          const found = findCode(c.children);
          if (found) return found;
        }
      }
      return undefined;
    };
    return findCode(professionalCodesTree);
  }, [professionalCodesTree]);

  /** 将专业代码树转换为 TreeSelect 选项 */
  const treeData = useMemo(() => {
    const convertToTreeData = (codes: ProfessionalCode[]): any[] => {
      return codes.map(code => ({
        title: `${code.code} ${code.name}`,
        value: code.code,
        key: code.code,
        children: code.children ? convertToTreeData(code.children) : undefined,
      }));
    };
    return convertToTreeData(professionalCodesTree);
  }, [professionalCodesTree]);

  // ============ 渲染 ============

  return (
    <Card className={className} title="认证范围选择" loading={loading.standards || loading.codes}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        
        {/* 错误提示 */}
        {error && (
          <Alert
            message={error}
            type="error"
            closable
            onClose={() => setError(null)}
          />
        )}

        {/* 第一部分：认证标准选择 */}
        <div>
          <Title level={5}>1. 选择认证标准</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            请选择需要申请的认证标准（可多选）
          </Text>
          <Space wrap>
            {standards.map(standard => (
              <Checkbox
                key={standard.code}
                checked={selectedStandards.includes(standard.code)}
                onChange={e => handleStandardChange(standard.code, e.target.checked)}
                disabled={disabled}
              >
                <Space direction="vertical" size={0} style={{ marginLeft: 4 }}>
                  <Text strong>{standard.code}</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>{standard.name}</Text>
                </Space>
              </Checkbox>
            ))}
          </Space>
        </div>

        {/* 第二部分：专业代码选择 */}
        <div>
          <Title level={5}>2. 选择专业代码</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
            请搜索并选择专业代码{multipleProfessionalCodes ? '（可多选）' : '（单选）'}
          </Text>
          
          {/* 搜索框 */}
          <AutoComplete
            style={{ width: '100%', marginBottom: 16 }}
            placeholder="输入专业代码或名称进行搜索，如：03.01 或 食品"
            value={searchKeyword}
            options={searchOptions}
            onSearch={handleSearch}
            onSelect={handleProfessionalCodeSelect}
            disabled={disabled}
            notFoundContent={loading.search ? <Spin size="small" /> : '无匹配结果'}
          >
            <div style={{ position: 'relative' }}>
              <SearchOutlined style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#999' }} />
              <input
                style={{
                  width: '100%',
                  padding: '8px 12px 8px 36px',
                  border: '1px solid #d9d9d9',
                  borderRadius: 6,
                  fontSize: 14,
                }}
                placeholder="输入专业代码或名称进行搜索"
              />
            </div>
          </AutoComplete>

          {/* 树形选择器（可选，作为搜索的补充） */}
          {professionalCodesTree.length > 0 && (
            <TreeSelect
              style={{ width: '100%', marginBottom: 16 }}
              treeData={treeData}
              placeholder="或从分类树中选择"
              treeDefaultExpandAll={false}
              treeDefaultExpandedKeys={['01', '02', '03']}
              onSelect={(value) => {
                const code = getProfessionalCodeDetail(value as string);
                if (code) {
                  handleProfessionalCodeSelect(value as string, { code });
                }
              }}
              disabled={disabled}
              allowClear
              showSearch
              treeNodeFilterProp="title"
            />
          )}

          {/* 已选专业代码标签 */}
          <div>
            <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
              已选择的专业代码：
            </Text>
            {selectedProfessionalCodes.length === 0 ? (
              <Text type="secondary" style={{ fontStyle: 'italic' }}>
                尚未选择任何专业代码
              </Text>
            ) : (
              <Space wrap>
                {selectedProfessionalCodes.map(code => {
                  const detail = getProfessionalCodeDetail(code);
                  return (
                    <Tag
                      key={code}
                      closable={!disabled}
                      onClose={() => handleRemoveProfessionalCode(code)}
                      color="blue"
                      style={{ padding: '4px 8px' }}
                    >
                      <Space>
                        <Text strong style={{ color: 'inherit' }}>{code}</Text>
                        <Text style={{ color: 'inherit' }}>{detail?.name || ''}</Text>
                      </Space>
                    </Tag>
                  );
                })}
              </Space>
            )}
          </div>
        </div>

        {/* 第三部分：验证结果 */}
        {validationResult && (
          <div>
            <Title level={5}>3. 验证结果</Title>
            {loading.validate ? (
              <Spin size="small" tip="正在验证..." />
            ) : (
              <>
                {validationResult.valid ? (
                  <Alert
                    message="认证范围组合有效"
                    description="当前选择的认证标准和专业代码组合符合要求"
                    type="success"
                    showIcon
                    icon={<CheckCircleOutlined />}
                  />
                ) : (
                  <Alert
                    message="认证范围组合存在问题"
                    type="error"
                    showIcon
                    icon={<CloseCircleOutlined />}
                    description={
                      <ul style={{ margin: 0, paddingLeft: 20 }}>
                        {validationResult.errors.map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                      </ul>
                    }
                  />
                )}
                
                {validationResult.warnings.length > 0 && (
                  <Alert
                    message="温馨提示"
                    type="warning"
                    showIcon
                    style={{ marginTop: 8 }}
                    description={
                      <ul style={{ margin: 0, paddingLeft: 20 }}>
                        {validationResult.warnings.map((warning, index) => (
                          <li key={index}>{warning}</li>
                        ))}
                      </ul>
                    }
                  />
                )}
              </>
            )}
          </div>
        )}

        {/* 第四部分：确认按钮 */}
        {showConfirmButton && (
          <div style={{ textAlign: 'right', paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
            <Button
              type="primary"
              size="large"
              onClick={handleConfirm}
              disabled={disabled || selectedStandards.length === 0 || selectedProfessionalCodes.length === 0}
              loading={loading.validate}
            >
              {confirmButtonText}
            </Button>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default CertificationScopeSelector;
