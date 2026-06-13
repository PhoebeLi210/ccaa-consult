import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Tabs,
  Input,
  Button,
  message,
  Progress,
  List,
  Tag,
  Empty,
  Spin,
  Statistic,
  Row,
  Col,
  Alert,
} from 'antd';
import {
  FileTextOutlined,
  SafetyOutlined,
  EnvironmentOutlined,
  SendOutlined,
  ArrowLeftOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useResponsive } from '../../hooks/useResponsive';
import {
  analyzeEnvironmentalReport,
  analyzeSafetyAssessment,
  EnvironmentalReportResponse,
  SafetyAssessmentResponse,
} from '../../api';
import styles from './style.module.css';

const { TextArea } = Input;
const { TabPane } = Tabs;

/**
 * 环境/安全评估报告解析页面
 */
const AnalyzerPage: React.FC = () => {
  const navigate = useNavigate();
  const { isMobile } = useResponsive();

  // 环境评估状态
  const [envText, setEnvText] = useState('');
  const [envLoading, setEnvLoading] = useState(false);
  const [envResult, setEnvResult] = useState<EnvironmentalReportResponse | null>(null);

  // 安全评估状态
  const [safetyText, setSafetyText] = useState('');
  const [safetyLoading, setSafetyLoading] = useState(false);
  const [safetyResult, setSafetyResult] = useState<SafetyAssessmentResponse | null>(null);

  /**
   * 解析环境评估报告
   */
  const handleAnalyzeEnvironmental = async () => {
    if (!envText.trim()) {
      message.warning('请输入环境评估报告内容');
      return;
    }

    setEnvLoading(true);
    try {
      const result = await analyzeEnvironmentalReport(envText.trim());
      setEnvResult(result);
      message.success('环境评估报告解析完成');
    } catch (error) {
      message.error('解析失败，请重试');
      console.error('Environmental analysis error:', error);
    } finally {
      setEnvLoading(false);
    }
  };

  /**
   * 解析安全评估报告
   */
  const handleAnalyzeSafety = async () => {
    if (!safetyText.trim()) {
      message.warning('请输入职业健康安全评估报告内容');
      return;
    }

    setSafetyLoading(true);
    try {
      const result = await analyzeSafetyAssessment(safetyText.trim());
      setSafetyResult(result);
      message.success('安全评估报告解析完成');
    } catch (error) {
      message.error('解析失败，请重试');
      console.error('Safety analysis error:', error);
    } finally {
      setSafetyLoading(false);
    }
  };

  /**
   * 渲染环境评估结果
   */
  const renderEnvironmentalResult = () => {
    if (!envResult) return null;

    return (
      <div className={styles.resultContainer}>
        <Alert
          message="解析完成"
          description={`已为 ${envResult.company_name} 完成环境评估报告解析`}
          type="success"
          showIcon
          icon={<CheckCircleOutlined />}
          className={styles.resultAlert}
        />

        <Row gutter={[16, 16]} className={styles.statisticsRow}>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="环境因素总数"
                value={envResult.aspects_count}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="重要环境因素"
                value={envResult.significant_aspects_count}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="合规率"
                value={envResult.compliance_rate}
                suffix="%"
                valueStyle={{ color: envResult.compliance_rate >= 90 ? '#3f8600' : '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>

        <Card title="环境因素列表" className={styles.listCard}>
          <List
            dataSource={envResult.environmental_aspects}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <div className={styles.aspectTitle}>
                      <span>{item.aspect}</span>
                      <Tag color={item.significance === '重要' ? 'red' : 'default'}>
                        {item.significance}
                      </Tag>
                    </div>
                  }
                  description={
                    <div className={styles.aspectDescription}>
                      <p><strong>活动：</strong>{item.activity}</p>
                      <p><strong>环境影响：</strong>{item.impact}</p>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Card>

        {envResult.generated_documents && (
          <Card title="生成的ISO14001文档" className={styles.documentsCard}>
            <div className={styles.documentList}>
              {Object.entries(envResult.generated_documents).map(([key, doc]) => (
                <div key={key} className={styles.documentItem}>
                  <FileTextOutlined className={styles.documentIcon} />
                  <span className={styles.documentName}>{key}</span>
                  <Tag color="blue">已生成</Tag>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    );
  };

  /**
   * 渲染安全评估结果
   */
  const renderSafetyResult = () => {
    if (!safetyResult) return null;

    return (
      <div className={styles.resultContainer}>
        <Alert
          message="解析完成"
          description={`已为 ${safetyResult.company_name} 完成职业健康安全评估报告解析`}
          type="success"
          showIcon
          icon={<CheckCircleOutlined />}
          className={styles.resultAlert}
        />

        <Row gutter={[16, 16]} className={styles.statisticsRow}>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="危险源总数"
                value={safetyResult.hazards_count}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="重大危险源"
                value={safetyResult.significant_hazards_count}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="合规率"
                value={safetyResult.compliance_rate}
                suffix="%"
                valueStyle={{ color: safetyResult.compliance_rate >= 90 ? '#3f8600' : '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>

        <Card title="危险源列表" className={styles.listCard}>
          <List
            dataSource={safetyResult.hazards}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <div className={styles.hazardTitle}>
                      <span>{item.hazard_source}</span>
                      <Tag
                        color={
                          item.risk_level === '重大'
                            ? 'red'
                            : item.risk_level === '较大'
                            ? 'orange'
                            : 'default'
                        }
                      >
                        {item.risk_level}风险
                      </Tag>
                    </div>
                  }
                  description={
                    <div className={styles.hazardDescription}>
                      <p><strong>活动：</strong>{item.activity}</p>
                      <p><strong>风险描述：</strong>{item.risk_description}</p>
                      <p><strong>风险评分：</strong>{item.risk_score}</p>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Card>

        {safetyResult.generated_documents && (
          <Card title="生成的ISO45001文档" className={styles.documentsCard}>
            <div className={styles.documentList}>
              {Object.entries(safetyResult.generated_documents).map(([key, doc]) => (
                <div key={key} className={styles.documentItem}>
                  <FileTextOutlined className={styles.documentIcon} />
                  <span className={styles.documentName}>{key}</span>
                  <Tag color="blue">已生成</Tag>
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    );
  };

  return (
    <div className={styles.container}>
      {/* 页面头部 */}
      <div className={styles.header}>
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
          className={styles.backButton}
        >
          返回
        </Button>
        <h1 className={styles.title}>
          <SafetyOutlined style={{ marginRight: 8 }} />
          评估报告解析
        </h1>
      </div>

      {/* 标签页 */}
      <Tabs defaultActiveKey="environmental" type="card" className={styles.tabs}>
        <TabPane
          tab={
            <span>
              <EnvironmentOutlined />
              环境评估报告
            </span>
          }
          key="environmental"
        >
          <Card className={styles.inputCard}>
            <div className={styles.inputSection}>
              <h3>请输入环境评估报告内容</h3>
              <TextArea
                value={envText}
                onChange={(e) => setEnvText(e.target.value)}
                placeholder="请粘贴环境评估报告全文...&#10;&#10;报告通常包含以下内容：&#10;- 环境因素识别&#10;- 重要环境因素&#10;- 合规性评价&#10;- 目标指标&#10;- 管理方案"
                rows={10}
                disabled={envLoading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleAnalyzeEnvironmental}
                loading={envLoading}
                disabled={!envText.trim()}
                size="large"
                block={isMobile}
                className={styles.analyzeButton}
              >
                开始解析
              </Button>
            </div>
          </Card>

          {envLoading && (
            <div className={styles.loadingContainer}>
              <Spin size="large" tip="AI正在解析环境评估报告..." />
            </div>
          )}

          {renderEnvironmentalResult()}
        </TabPane>

        <TabPane
          tab={
            <span>
              <SafetyOutlined />
              安全评估报告
            </span>
          }
          key="safety"
        >
          <Card className={styles.inputCard}>
            <div className={styles.inputSection}>
              <h3>请输入职业健康安全评估报告内容</h3>
              <TextArea
                value={safetyText}
                onChange={(e) => setSafetyText(e.target.value)}
                placeholder="请粘贴职业健康安全评估报告全文...&#10;&#10;报告通常包含以下内容：&#10;- 危险源识别&#10;- 重大危险源&#10;- 事故/事件记录&#10;- 法规合规性&#10;- 目标指标&#10;- 应急程序"
                rows={10}
                disabled={safetyLoading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleAnalyzeSafety}
                loading={safetyLoading}
                disabled={!safetyText.trim()}
                size="large"
                block={isMobile}
                className={styles.analyzeButton}
              >
                开始解析
              </Button>
            </div>
          </Card>

          {safetyLoading && (
            <div className={styles.loadingContainer}>
              <Spin size="large" tip="AI正在解析安全评估报告..." />
            </div>
          )}

          {renderSafetyResult()}
        </TabPane>
      </Tabs>
    </div>
  );
};

export default AnalyzerPage;
