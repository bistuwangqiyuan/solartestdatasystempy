import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message, Checkbox } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useAuthStore } from '@/stores/authStore'

interface LoginForm {
  email: string
  password: string
  remember: boolean
}

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (values: LoginForm) => {
    setLoading(true)
    try {
      await login(values.email, values.password)
      message.success('登录成功')
      navigate('/')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查邮箱和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card 
      className="data-card"
      style={{ 
        background: '#1A1F27',
        border: '1px solid #252B36',
      }}
    >
      <Form<LoginForm>
        name="login"
        initialValues={{ remember: true }}
        onFinish={handleSubmit}
        size="large"
        className="space-y-4"
      >
        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' },
          ]}
        >
          <Input 
            prefix={<UserOutlined className="text-text-secondary" />} 
            placeholder="邮箱地址"
            className="bg-background-tertiary border-background-tertiary"
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[{ required: true, message: '请输入密码' }]}
        >
          <Input.Password
            prefix={<LockOutlined className="text-text-secondary" />}
            placeholder="密码"
            className="bg-background-tertiary border-background-tertiary"
          />
        </Form.Item>

        <Form.Item>
          <Form.Item name="remember" valuePropName="checked" noStyle>
            <Checkbox className="text-text-secondary">记住我</Checkbox>
          </Form.Item>
          <a className="float-right text-primary hover:text-primary-light">
            忘记密码？
          </a>
        </Form.Item>

        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            block
            className="industrial-btn h-12"
          >
            登录系统
          </Button>
        </Form.Item>

        <div className="text-center text-text-secondary">
          还没有账号？
          <a className="text-primary hover:text-primary-light ml-1">
            立即注册
          </a>
        </div>
      </Form>
    </Card>
  )
}

export default Login