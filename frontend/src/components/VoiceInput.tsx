import React, { useState, useCallback, useRef } from 'react';
import { Button, message } from 'antd';
import { AudioOutlined, AudioMutedOutlined, LoadingOutlined } from '@ant-design/icons';

interface VoiceInputProps {
  onResult: (text: string) => void;
  disabled?: boolean;
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onResult, disabled = false }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      chunksRef.current = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (err: any) {
      message.error('无法访问麦克风，请检查浏览器权限');
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  const processAudio = async (audioBlob: Blob) => {
    setProcessing(true);
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64 = (reader.result as string).split(',')[1];
        try {
          const response = await fetch('/api/v1/speech/recognize', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
            },
            body: JSON.stringify({
              audio_base64: base64,
              language: 'zh',
            }),
          });

          if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '识别失败');
          }

          const result = await response.json();
          if (result.text) {
            onResult(result.text);
            message.success('语音识别完成');
          } else {
            message.warning('未识别到有效内容');
          }
        } catch (err: any) {
          message.error(err.message || '语音识别失败');
        } finally {
          setProcessing(false);
        }
      };
      reader.readAsDataURL(audioBlob);
    } catch {
      setProcessing(false);
      message.error('音频处理失败');
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const loading = processing;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <Button
        type={isRecording ? 'primary' : 'default'}
        danger={isRecording}
        loading={loading}
        icon={
          loading ? <LoadingOutlined /> :
          isRecording ? <AudioMutedOutlined /> :
          <AudioOutlined />
        }
        onClick={toggleRecording}
        disabled={disabled || processing}
        style={{
          borderRadius: '50%',
          width: 40,
          height: 40,
          minWidth: 40,
          padding: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      />
      <span style={{ fontSize: 13, color: '#666' }}>
        {isRecording ? '录音中，点击停止...' :
         processing ? '识别中...' :
         '点击开始语音录入'}
      </span>
    </div>
  );
};

export default VoiceInput;
