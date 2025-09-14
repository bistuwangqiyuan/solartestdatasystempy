import React, { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Avatar, Dropdown, Space, Badge } from 'antd'
import {
  DashboardOutlined,
  DatabaseOutlined,
  UploadOutlined,
  BarChartOutlined,
  SettingOutlined,
  LogoutOutlined,
  UserOutlined,
  BellOutlined,
  FullscreenOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  AppstoreOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '@/stores/authStore'

const { Header, Sider, Content } = Layout

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/records',
      icon: <DatabaseOutlined />,
      label: '测试记录',
    },
    {
      key: '/devices',
      icon: <AppstoreOutlined />,
      label: '设备管理',
    },
    {
      key: '/import',
      icon: <UploadOutlined />,
      label: '数据导入',
    },
    {
      key: '/statistics',
      icon: <BarChartOutlined />,
      label: '统计分析',
    },
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout()
      navigate('/login')
    }
  }

  const openDataScreen = () => {
    window.open('/data-screen', '_blank')
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        style={{
          background: '#1A1F27',
          borderRight: '1px solid #252B36',
        }}
      >
        <div className="flex items-center justify-center h-16 border-b border-background-tertiary">
          <h1 className={`text-primary font-bold transition-all ${collapsed ? 'text-lg' : 'text-xl'}`}>
            {collapsed ? 'PV' : '光伏数据管理'}
          </h1>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ background: 'transparent', borderRight: 0 }}
        />
      </Sider>
      
      <Layout>
        <Header 
          style={{ 
            padding: '0 24px', 
            background: '#1A1F27',
            borderBottom: '1px solid #252B36',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Space size="large">
            {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
              className: 'text-xl text-text-primary hover:text-primary cursor-pointer transition-colors',
              onClick: () => setCollapsed(!collapsed),
            })}
          </Space>
          
          <Space size="large">
            <FullscreenOutlined 
              className="text-xl text-text-secondary hover:text-primary cursor-pointer transition-colors"
              onClick={openDataScreen}
              title="数据大屏"
            />
            
            <Badge count={5} size="small">
              <BellOutlined className="text-xl text-text-secondary hover:text-primary cursor-pointer transition-colors" />
            </Badge>
            
            <Dropdown
              menu={{ 
                items: userMenuItems,
                onClick: handleMenuClick,
              }}
              placement="bottomRight"
            >
              <Space className="cursor-pointer">
                <Avatar 
                  size="default" 
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#0E7FFF' }}
                />
                <span className="text-text-primary">{user?.full_name || user?.email}</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        
        <Content
          style={{
            margin: '24px',
            minHeight: 280,
          }}
        >
          <div className="fade-in">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default MainLayout