import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Button } from 'antd';
import { AudioOutlined, AudioMutedOutlined } from '@ant-design/icons';

/** 语音录入组件属性 */
interface VoiceInputProps {
  /** 语音识别完成回调，返回识别文本 */
  onResult: (text: string) => void;
  /** 是否禁用 */
  disabled?: boolean;
  /** 识别语言，默认中文 */
  lang?: string;
}

/**
 * 语音录入组件
 * 基于Web Speech API的SpeechRecognition实现语音输入
 * 支持按住说话或点击开始/停止
 * 支持中文识别
 */
const VoiceInput: React.FC<VoiceInputProps> = ({
  onResult,
  disabled = false,
  lang = 'zh-CN',
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  /** 初始化语音识别 */
  useEffect(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setIsSupported(false);
      setError('当前浏览器不支持语音识别功能，请使用Chrome浏览器');
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = true; // 持续识别
    recognition.interimResults = true; // 返回临时结果
    recognition.lang = lang; // 设置识别语言

    /** 识别结果处理 */
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      // 显示临时识别结果
      if (interimTranscript) {
        setInterimText(interimTranscript);
      }

      // 最终结果回调
      if (finalTranscript) {
        setInterimText('');
        onResult(finalTranscript);
      }
    };

    /** 识别错误处理 */
    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error === 'no-speech') {
        // 没有检测到语音，不视为错误
        return;
      }
      setError(`语音识别错误: ${event.error}`);
      setIsRecording(false);
    };

    /** 识别结束处理 */
    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
    };
  }, [lang, onResult]);

  /** 开始/停止录音 */
  const toggleRecording = useCallback(() => {
    if (!recognitionRef.current) return;

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      setError(null);
      setInterimText('');
      try {
        recognitionRef.current.start();
        setIsRecording(true);
      } catch {
        setError('无法启动语音识别，请检查麦克风权限');
      }
    }
  }, [isRecording]);

  /** 按住说话 - 鼠标按下开始 */
  const handlePressStart = useCallback(() => {
    if (!isRecording && !disabled) {
      toggleRecording();
    }
  }, [isRecording, disabled, toggleRecording]);

  /** 按住说话 - 鼠标松开停止 */
  const handlePressEnd = useCallback(() => {
    if (isRecording) {
      toggleRecording();
    }
  }, [isRecording, toggleRecording]);

  if (!isSupported) {
    return (
      <div style={{ color: '#999', fontSize: 12, padding: '4px 0' }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Button
          type={isRecording ? 'primary' : 'default'}
          danger={isRecording}
          icon={isRecording ? <AudioMutedOutlined /> : <AudioOutlined />}
          onClick={toggleRecording}
          disabled={disabled}
          onMouseDown={handlePressStart}
          onMouseUp={handlePressEnd}
          onTouchStart={handlePressStart}
          onTouchEnd={handlePressEnd}
          style={{
            borderRadius: '50%',
            width: 44,
            height: 44,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {isRecording ? '停止' : '录音'}
        </Button>
        <span style={{ fontSize: 13, color: '#666' }}>
          {isRecording ? '正在录音，请说话...' : '点击开始语音录入'}
        </span>
      </div>

      {/* 实时识别文字显示 */}
      {interimText && (
        <div
          style={{
            padding: '8px 12px',
            backgroundColor: '#f6ffed',
            border: '1px solid #b7eb8f',
            borderRadius: 6,
            fontSize: 13,
            color: '#52c41a',
          }}
        >
          识别中: {interimText}
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div
          style={{
            padding: '8px 12px',
            backgroundColor: '#fff2f0',
            border: '1px solid #ffccc7',
            borderRadius: 6,
            fontSize: 13,
            color: '#ff4d4f',
          }}
        >
          {error}
        </div>
      )}
    </div>
  );
};

export default VoiceInput;
