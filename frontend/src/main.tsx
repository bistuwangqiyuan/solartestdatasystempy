import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

import App from './App'
import './index.css'

// 设置 dayjs 语言
dayjs.locale('zh-cn')

// 创建 QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5分钟
    },
  },
})

// Antd 主题配置
const theme = {
  token: {
    colorPrimary: '#0E7FFF',
    colorSuccess: '#10B981',
    colorWarning: '#F59E0B',
    colorError: '#EF4444',
    colorInfo: '#3B82F6',
    borderRadius: 4,
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
  },
  algorithm: undefined, // 可以设置为 theme.darkAlgorithm
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={zhCN} theme={theme}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  </React.StrictMode>,
)