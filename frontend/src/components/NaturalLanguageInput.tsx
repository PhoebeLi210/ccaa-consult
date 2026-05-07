import React, { useState, useCallback, useRef } from 'react';
import { Input, Card, Tag, Space, Collapse } from 'antd';
import { SendOutlined, LoadingOutlined } from '@ant-design/icons';
import VoiceInput from './VoiceInput';
import type { ParseResult } from '@/api';

/** 自然语言输入组件属性 */
interface NaturalLanguageInputProps {
  /** 提交文本回调 */
  onSubmit: (text: string) => void;
  /** AI解析回调（实时解析） */
  onParse: (text: string) => Promise<ParseResult>;
  /** 是否正在解析中 */
  loading?: boolean;
  /** 占位提示文字 */
  placeholder?: string;
  /** 当前解析结果 */
  parseResult?: ParseResult | null;
}

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

/**
 * 自然语言输入框组件
 * 大文本框 + 语音录入 + 实时AI解析预览
 * 解析结果以卡片形式展示，缺失字段高亮
 */
const NaturalLanguageInput: React.FC<NaturalLanguageInputProps> = ({
  onSubmit,
  onParse,
  loading = false,
  placeholder = '请描述您客户的企业情况，例如：北京XX科技有限公司，互联网行业，约200人，注册资本500万...',
  parseResult: externalParseResult,
}) => {
  const [text, setText] = useState('');
  const [internalParseResult, setInternalParseResult] = useState<ParseResult | null>(null);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /** 当前使用的解析结果（优先外部传入） */
  const parseResult = externalParseResult ?? internalParseResult;

  /** 文本变化时实时解析（防抖500ms） */
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const value = e.target.value;
      setText(value);

      // 清除之前的防抖定时器
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      // 文本为空时清除解析结果
      if (!value.trim()) {
        setInternalParseResult(null);
        return;
      }

      // 防抖500ms后触发解析
      debounceTimerRef.current = setTimeout(async () => {
        try {
          const result = await onParse(value.trim());
          setInternalParseResult(result);
        } catch {
          // 解析失败不阻塞输入
        }
      }, 500);
    },
    [onParse],
  );

  /** 提交文本 */
  const handleSubmit = useCallback(() => {
    if (text.trim()) {
      onSubmit(text.trim());
    }
  }, [text, onSubmit]);

  /** 语音识别结果追加到文本 */
  const handleVoiceResult = useCallback((voiceText: string) => {
    setText((prev) => (prev ? `${prev}${voiceText}` : voiceText));
  }, []);

  /** 判断字段是否缺失 */
  const isFieldMissing = (fieldName: string): boolean => {
    if (!parseResult) return false;
    return parseResult.missingFields?.includes(fieldName) ?? false;
  };

  /** 获取字段值 */
  const getFieldValue = (fieldName: string): string => {
    if (!parseResult) return '';
    return (parseResult as Record<string, unknown>)[fieldName] as string || '';
  };

  /** 渲染解析结果卡片 */
  const renderParseResult = () => {
    if (!parseResult) return null;

    const fields = Object.keys(fieldLabels);

    return (
      <Collapse
        defaultActiveKey={['1']}
        size="small"
        style={{ marginTop: 12 }}
        items={[
          {
            key: '1',
            label: (
              <Space>
                <span>AI 解析结果</span>
                {loading && <LoadingOutlined />}
                {parseResult.missingFields && parseResult.missingFields.length > 0 && (
                  <Tag color="warning">
                    {parseResult.missingFields.length} 项待补充
                  </Tag>
                )}
              </Space>
            ),
            children: (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
                  gap: 8,
                }}
              >
                {fields.map((field) => {
                  const value = getFieldValue(field);
                  const missing = isFieldMissing(field);

                  return (
                    <div
                      key={field}
                      style={{
                        padding: '8px 12px',
                        backgroundColor: missing ? '#fff2f0' : '#fafafa',
                        border: `1px solid ${missing ? '#ffccc7' : '#f0f0f0'}`,
                        borderRadius: 6,
                        cursor: missing ? 'pointer' : 'default',
                      }}
                    >
                      <div
                        style={{
                          fontSize: 12,
                          color: missing ? '#ff4d4f' : '#999',
                          marginBottom: 4,
                        }}
                      >
                        {fieldLabels[field]}
                        {missing && (
                          <Tag
                            color="error"
                            style={{ marginLeft: 4, fontSize: 11 }}
                          >
                            缺失
                          </Tag>
                        )}
                      </div>
                      <div
                        style={{
                          fontSize: 14,
                          color: value ? '#333' : '#ccc',
                          fontWeight: value ? 500 : 400,
                        }}
                      >
                        {value || '暂无信息'}
                      </div>
                    </div>
                  );
                })}
              </div>
            ),
          },
        ]}
      />
    );
  };

  return (
    <div>
      {/* 大文本输入框 */}
      <Input.TextArea
        value={text}
        onChange={handleChange}
        placeholder={placeholder}
        autoSize={{ minRows: 4, maxRows: 8 }}
        style={{ fontSize: 15, lineHeight: 1.8 }}
        disabled={loading}
      />

      {/* 操作栏：语音录入 + 提交按钮 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginTop: 12,
          flexWrap: 'wrap',
          gap: 8,
        }}
      >
        <VoiceInput onResult={handleVoiceResult} disabled={loading} />
        <div style={{ display: 'flex', gap: 8 }}>
          {text && (
            <a
              onClick={() => setText('')}
              style={{ fontSize: 13, color: '#999', cursor: 'pointer' }}
            >
              清空
            </a>
          )}
          <Card
            size="small"
            style={{
              cursor: 'pointer',
              userSelect: 'none',
              backgroundColor: text.trim() ? '#1677ff' : '#f5f5f5',
              color: text.trim() ? '#fff' : '#999',
              border: 'none',
              padding: '4px 16px',
            }}
            onClick={handleSubmit}
          >
            <Space size={4}>
              {loading ? <LoadingOutlined /> : <SendOutlined />}
              <span style={{ fontSize: 14 }}>提交</span>
            </Space>
          </Card>
        </div>
      </div>

      {/* 实时解析结果预览 */}
      {renderParseResult()}
    </div>
  );
};

export default NaturalLanguageInput;
