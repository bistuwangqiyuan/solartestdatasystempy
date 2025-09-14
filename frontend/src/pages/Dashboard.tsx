import React from 'react'
import { Row, Col, Card, Statistic, Progress, Space, Table, Tag } from 'antd'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ThunderboltOutlined,
  ExperimentOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { useQuery } from '@tanstack/react-query'
import api from '@/utils/api'

const Dashboard: React.FC = () => {
  // 获取统计数据
  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/summary')
      return response.data
    },
    refetchInterval: 30000, // 每30秒刷新一次
  })

  // 获取实时数据
  const { data: realtime } = useQuery({
    queryKey: ['realtime-stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/realtime')
      return response.data
    },
    refetchInterval: 5000, // 每5秒刷新一次
  })

  // 趋势图配置
  const trendOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1F27',
      borderColor: '#252B36',
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: stats?.daily_trend?.map((item: any) => item.date) || [],
      axisLine: { lineStyle: { color: '#252B36' } },
      axisLabel: { color: '#9CA3AF' },
    },
    yAxis: [
      {
        type: 'value',
        name: '测试数量',
        axisLine: { lineStyle: { color: '#252B36' } },
        axisLabel: { color: '#9CA3AF' },
        splitLine: { lineStyle: { color: '#252B36', type: 'dashed' } },
      },
      {
        type: 'value',
        name: '合格率(%)',
        axisLine: { lineStyle: { color: '#252B36' } },
        axisLabel: { color: '#9CA3AF' },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '测试数量',
        type: 'line',
        data: stats?.daily_trend?.map((item: any) => item.count) || [],
        smooth: true,
        itemStyle: { color: '#0E7FFF' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(14, 127, 255, 0.3)' },
              { offset: 1, color: 'rgba(14, 127, 255, 0.05)' },
            ],
          },
        },
      },
      {
        name: '合格率',
        type: 'line',
        yAxisIndex: 1,
        data: stats?.daily_trend?.map((item: any) => item.pass_rate) || [],
        smooth: true,
        itemStyle: { color: '#10B981' },
      },
    ],
  }

  // 设备分布饼图配置
  const deviceOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1A1F27',
      borderColor: '#252B36',
    },
    legend: {
      orient: 'vertical',
      left: 'right',
      textStyle: { color: '#9CA3AF' },
    },
    series: [
      {
        name: '设备分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold',
            color: '#FFFFFF',
          },
        },
        labelLine: {
          show: false,
        },
        data: Object.entries(stats?.device_distribution || {}).map(([name, value]) => ({
          name,
          value,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 1,
              colorStops: [
                { offset: 0, color: '#0E7FFF' },
                { offset: 1, color: '#3D9AFF' },
              ],
            },
          },
        })),
      },
    ],
  }

  // 最近测试记录列
  const columns = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      ellipsis: true,
    },
    {
      title: '设备型号',
      dataIndex: 'device_model',
      key: 'device_model',
    },
    {
      title: '合格率',
      dataIndex: 'pass_rate',
      key: 'pass_rate',
      render: (value: number) => {
        const isPass = value >= 95
        return (
          <Tag 
            icon={isPass ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            color={isPass ? 'success' : 'error'}
          >
            {value?.toFixed(2)}%
          </Tag>
        )
      },
    },
    {
      title: '测试时间',
      dataIndex: 'test_date',
      key: 'test_date',
      render: (value: string) => new Date(value).toLocaleString('zh-CN'),
    },
  ]

  return (
    <div className="space-y-6">
      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">今日测试</span>}
              value={realtime?.today_count || 0}
              suffix="次"
              valueStyle={{ color: '#0E7FFF' }}
              prefix={<ThunderboltOutlined />}
            />
            <div className="mt-4">
              <span className="text-text-tertiary text-sm">
                较昨日 
                <span className="text-success ml-1">
                  <ArrowUpOutlined /> 12.5%
                </span>
              </span>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">本月测试</span>}
              value={stats?.month_count || 0}
              suffix="次"
              valueStyle={{ color: '#3D9AFF' }}
              prefix={<ExperimentOutlined />}
            />
            <Progress 
              percent={75} 
              strokeColor="#3D9AFF"
              trailColor="#252B36"
              showInfo={false}
              className="mt-4"
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">今日合格率</span>}
              value={realtime?.today_pass_rate || 0}
              suffix="%"
              precision={2}
              valueStyle={{ color: '#10B981' }}
              prefix={<CheckCircleOutlined />}
            />
            <div className="mt-4">
              <span className="text-text-tertiary text-sm">
                目标: 95.00%
              </span>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">活跃设备</span>}
              value={realtime?.active_devices || 0}
              suffix="台"
              valueStyle={{ color: '#F59E0B' }}
            />
            <div className="mt-4">
              <span className="text-text-tertiary text-sm">
                总设备数: {stats?.device_distribution ? Object.keys(stats.device_distribution).length : 0}
              </span>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card 
            title={<span className="text-text-primary">测试趋势</span>}
            className="data-card"
          >
            <ReactECharts 
              option={trendOption} 
              style={{ height: 400 }}
              theme="dark"
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Card 
            title={<span className="text-text-primary">设备分布</span>}
            className="data-card"
          >
            <ReactECharts 
              option={deviceOption} 
              style={{ height: 400 }}
              theme="dark"
            />
          </Card>
        </Col>
      </Row>

      {/* 最近测试记录 */}
      <Card 
        title={<span className="text-text-primary">最近测试记录</span>}
        className="data-card"
      >
        <Table
          columns={columns}
          dataSource={realtime?.recent_tests || []}
          rowKey="id"
          pagination={false}
          style={{ background: 'transparent' }}
        />
      </Card>
    </div>
  )
}

export default Dashboard