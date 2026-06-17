import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, message, Typography, Tabs } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuth } from '../../contexts/AuthContext';
import { register } from '../../api/auth';

const { Title, Text } = Typography;

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');

  const handleLogin = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success('登录成功');
      navigate('/');
    } catch (err: any) {
      message.error(err.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: { username: string; password: string; email: string }) => {
    setLoading(true);
    try {
      await register(values);
      message.success('注册成功，请登录');
      setActiveTab('login');
    } catch (err: any) {
      message.error(err.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={3} style={{ margin: 0 }}>智质通 · 咨询版</Title>
          <Text type="secondary">CCAA咨询管理系统</Text>
        </div>
        <Tabs activeKey={activeTab} onChange={setActiveTab} centered items={[
          {
            key: 'login',
            label: '登录',
            children: (
              <Form onFinish={handleLogin} size="large">
                <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
                  <Input prefix={<UserOutlined />} placeholder="用户名" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block>登录</Button>
                </Form.Item>
              </Form>
            )
          },
          {
            key: 'register',
            label: '注册',
            children: (
              <Form onFinish={handleRegister} size="large">
                <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
                  <Input prefix={<UserOutlined />} placeholder="用户名" />
                </Form.Item>
                <Form.Item name="email" rules={[{ type: 'email', message: '请输入有效的邮箱' }]}>
                  <Input prefix={<MailOutlined />} placeholder="邮箱（可选）" />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }, { min: 6, message: '密码至少6位' }]}>
                  <Input.Password prefix={<LockOutlined />} placeholder="密码" />
                </Form.Item>
                <Form.Item>
                  <Button type="primary" htmlType="submit" loading={loading} block>注册</Button>
                </Form.Item>
              </Form>
            )
          }
        ]} />
      </Card>
    </div>
  );
};

export default LoginPage;
