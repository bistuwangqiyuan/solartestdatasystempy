import React from 'react'
import { Layout } from 'antd'

const { Content } = Layout

interface AuthLayoutProps {
  children: React.ReactNode
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <Layout style={{ minHeight: '100vh', background: '#0F1419' }}>
      <Content className="flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-primary mb-2">
              光伏关断器检测数据管理系统
            </h1>
            <p className="text-text-secondary">
              PV Shutoff Test Data Management System
            </p>
          </div>
          {children}
        </div>
      </Content>
      
      {/* 背景装饰 */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div 
          className="absolute -top-40 -right-40 w-80 h-80 bg-primary rounded-full opacity-10 blur-3xl"
          style={{ animation: 'pulse 4s ease-in-out infinite' }}
        />
        <div 
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent rounded-full opacity-10 blur-3xl"
          style={{ animation: 'pulse 4s ease-in-out infinite 2s' }}
        />
      </div>
    </Layout>
  )
}

export default AuthLayout