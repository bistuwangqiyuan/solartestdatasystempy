import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from 'antd'
import { useAuthStore } from './stores/authStore'
import MainLayout from './layouts/MainLayout'
import AuthLayout from './layouts/AuthLayout'
import Dashboard from './pages/Dashboard'
import DataScreen from './pages/DataScreen'
import TestRecords from './pages/TestRecords'
import DeviceManagement from './pages/DeviceManagement'
import DataImport from './pages/DataImport'
import Statistics from './pages/Statistics'
import Login from './pages/Login'
import NotFound from './pages/NotFound'

const { Content } = Layout

function App() {
  const { isAuthenticated, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <Layout style={{ minHeight: '100vh', background: '#0F1419' }}>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/" replace /> : (
            <AuthLayout>
              <Login />
            </AuthLayout>
          )
        } />

        {/* 数据大屏（可选择是否需要认证） */}
        <Route path="/data-screen" element={<DataScreen />} />

        {/* 受保护的路由 */}
        <Route path="/" element={
          isAuthenticated ? <MainLayout /> : <Navigate to="/login" replace />
        }>
          <Route index element={<Dashboard />} />
          <Route path="records" element={<TestRecords />} />
          <Route path="devices" element={<DeviceManagement />} />
          <Route path="import" element={<DataImport />} />
          <Route path="statistics" element={<Statistics />} />
        </Route>

        {/* 404页面 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  )
}

export default App