import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Card,
  Input,
  Button,
  Progress,
  Tag,
  message,
  Spin,
  Empty,
  Tooltip,
} from 'antd';
import {
  SendOutlined,
  MessageOutlined,
  CheckCircleOutlined,
  InfoCircleOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useResponsive } from '../../hooks/useResponsive';
import {
  startConversation,
  continueConversation,
  completeConversation,
  ConversationResponse,
  FollowUpQuestion,
} from '../../api';
import styles from './style.module.css';

/**
 * 对话消息类型
 */
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  questions?: FollowUpQuestion[];
}

/**
 * 多轮对话页面
 * 支持自然语言输入、智能追问、信息收集
 */
const ConversationPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isMobile } = useResponsive();
  const projectId = searchParams.get('projectId');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 状态管理
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [parsedInfo, setParsedInfo] = useState<Record<string, any>>({});
  const [missingFields, setMissingFields] = useState<string[]>([]);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * 发送初始消息开始对话
   */
  const handleStartConversation = async () => {
    if (!inputValue.trim()) {
      message.warning('请输入企业信息描述');
      return;
    }

    setLoading(true);
    try {
      const response = await startConversation(inputValue.trim(), projectId || undefined);
      
      setSessionId(response.session_id);
      setProgress(response.progress_percent);
      setParsedInfo(response.parsed_info);
      setMissingFields(response.missing_fields);
      setIsComplete(response.status === 'complete');

      // 添加用户消息
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: inputValue.trim(),
        timestamp: new Date(),
      };

      // 添加助手回复
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        questions: response.follow_up_questions,
      };

      setMessages([userMessage, assistantMessage]);
      setInputValue('');
    } catch (error) {
      message.error('开始对话失败，请重试');
      console.error('Start conversation error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 继续对话，回答追问
   */
  const handleContinueConversation = async () => {
    if (!inputValue.trim() || !sessionId) return;

    setLoading(true);
    try {
      const response = await continueConversation(sessionId, inputValue.trim());
      
      setProgress(response.progress_percent);
      setParsedInfo(response.parsed_info);
      setMissingFields(response.missing_fields);
      setIsComplete(response.status === 'complete');

      // 添加用户消息
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: inputValue.trim(),
        timestamp: new Date(),
      };

      // 添加助手回复
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
        questions: response.follow_up_questions,
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setInputValue('');
    } catch (error) {
      message.error('发送消息失败，请重试');
      console.error('Continue conversation error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 完成对话，保存信息到项目
   */
  const handleComplete = async () => {
    if (!sessionId) return;

    setLoading(true);
    try {
      await completeConversation(sessionId, projectId || undefined);
      message.success('信息收集完成！');
      
      // 跳转到项目详情页
      if (projectId) {
        navigate(`/project/${projectId}`);
      } else {
        navigate('/');
      }
    } catch (error) {
      message.error('保存信息失败，请重试');
      console.error('Complete conversation error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 快速回答问题
   */
  const handleQuickAnswer = (answer: string) => {
    setInputValue(answer);
  };

  /**
   * 渲染消息气泡
   */
  const renderMessage = (msg: ChatMessage) => {
    const isUser = msg.role === 'user';
    
    return (
      <div
        key={msg.id}
        className={`${styles.messageItem} ${isUser ? styles.userMessage : styles.assistantMessage}`}
      >
        <div className={styles.messageAvatar}>
          {isUser ? (
            <div className={styles.userAvatar}>我</div>
          ) : (
            <div className={styles.assistantAvatar}>
              <MessageOutlined />
            </div>
          )}
        </div>
        <div className={styles.messageContent}>
          <div className={styles.messageBubble}>{msg.content}</div>
          
          {/* 渲染追问问题 */}
          {!isUser && msg.questions && msg.questions.length > 0 && (
            <div className={styles.questionsContainer}>
              {msg.questions.map((q, index) => (
                <Card
                  key={index}
                  size="small"
                  className={styles.questionCard}
                  title={
                    <span>
                      <InfoCircleOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                      {q.question}
                    </span>
                  }
                  extra={
                    q.reason && (
                      <Tooltip title={q.reason}>
                        <InfoCircleOutlined style={{ color: '#999' }} />
                      </Tooltip>
                    )
                  }
                >
                  {q.example && (
                    <div className={styles.questionExample}>
                      <Tag color="blue">示例</Tag>
                      <span>{q.example}</span>
                    </div>
                  )}
                  <Button
                    type="link"
                    size="small"
                    onClick={() => handleQuickAnswer(q.example || '')}
                  >
                    使用示例回答
                  </Button>
                </Card>
              ))}
            </div>
          )}
          
          <div className={styles.messageTime}>
            {msg.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  /**
   * 渲染信息收集进度
   */
  const renderProgress = () => {
    if (messages.length === 0) return null;

    return (
      <Card className={styles.progressCard} size="small">
        <div className={styles.progressHeader}>
          <span className={styles.progressTitle}>信息收集进度</span>
          <Tag color={isComplete ? 'success' : 'processing'}>
            {isComplete ? '已完成' : '收集中'}
          </Tag>
        </div>
        <Progress
          percent={progress}
          status={isComplete ? 'success' : 'active'}
          strokeColor={{ from: '#108ee9', to: '#87d068' }}
        />
        {missingFields.length > 0 && (
          <div className={styles.missingFields}>
            <span className={styles.missingLabel}>待补充：</span>
            {missingFields.map((field) => (
              <Tag key={field} color="warning" style={{ margin: '2px' }}>
                {field}
              </Tag>
            ))}
          </div>
        )}
      </Card>
    );
  };

  /**
   * 渲染初始输入界面
   */
  const renderInitialInput = () => (
    <Card className={styles.initialCard}>
      <Empty
        description="请输入企业信息开始对话"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      >
        <div className={styles.initialInput}>
          <Input.TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="请描述您的企业情况，例如：&#10;我公司是一家生产塑料制品的制造企业，员工50人，办公室面积300平米..."
            rows={6}
            disabled={loading}
          />
          <Button
            type="primary"
            size="large"
            icon={<SendOutlined />}
            onClick={handleStartConversation}
            loading={loading}
            disabled={!inputValue.trim()}
            block={isMobile}
            style={{ marginTop: 16 }}
          >
            开始对话
          </Button>
        </div>
      </Empty>
    </Card>
  );

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
          <MessageOutlined style={{ marginRight: 8 }} />
          智能信息收集
        </h1>
        {projectId && (
          <Tag color="blue" className={styles.projectTag}>
            项目ID: {projectId}
          </Tag>
        )}
      </div>

      {/* 进度展示 */}
      {renderProgress()}

      {/* 对话区域 */}
      {messages.length > 0 ? (
        <>
          <div className={styles.messagesContainer}>
            {messages.map(renderMessage)}
            <div ref={messagesEndRef} />
          </div>

          {/* 输入区域 */}
          <div className={styles.inputArea}>
            <Input.TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="请输入您的回答..."
              rows={3}
              disabled={loading || isComplete}
              onPressEnter={(e) => {
                if (!e.shiftKey) {
                  e.preventDefault();
                  handleContinueConversation();
                }
              }}
            />
            <div className={styles.inputActions}>
              {isComplete ? (
                <Button
                  type="primary"
                  icon={<CheckCircleOutlined />}
                  onClick={handleComplete}
                  loading={loading}
                  size="large"
                >
                  完成并保存
                </Button>
              ) : (
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleContinueConversation}
                  loading={loading}
                  disabled={!inputValue.trim()}
                  size="large"
                >
                  发送
                </Button>
              )}
            </div>
          </div>
        </>
      ) : (
        renderInitialInput()
      )}

      {/* 加载状态 */}
      {loading && (
        <div className={styles.loadingOverlay}>
          <Spin size="large" tip="AI思考中..." />
        </div>
      )}
    </div>
  );
};

export default ConversationPage;
