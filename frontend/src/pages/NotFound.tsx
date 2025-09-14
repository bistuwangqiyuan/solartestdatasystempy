import React from 'react'
import { Button, Result } from 'antd'
import { useNavigate } from 'react-router-dom'

const NotFound: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <Result
        status="404"
        title="404"
        subTitle="抱歉，您访问的页面不存在。"
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            返回首页
          </Button>
        }
        style={{ color: '#FFFFFF' }}
      />
    </div>
  )
}

export default NotFound