import React, { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic } from 'antd'
import ReactECharts from 'echarts-for-react'
import { useQuery } from '@tanstack/react-query'
import api from '@/utils/api'
import dayjs from 'dayjs'

const DataScreen: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(dayjs())

  // 更新时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(dayjs())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // 获取实时数据
  const { data: realtime } = useQuery({
    queryKey: ['realtime-screen'],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/realtime')
      return response.data
    },
    refetchInterval: 5000,
  })

  // 获取趋势数据
  const { data: trends } = useQuery({
    queryKey: ['trends-screen'],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/trends?period=hour&days=1')
      return response.data
    },
    refetchInterval: 60000,
  })

  // 获取质量指标
  const { data: quality } = useQuery({
    queryKey: ['quality-metrics'],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/quality-metrics')
      return response.data
    },
    refetchInterval: 300000,
  })

  // 实时趋势图
  const realtimeTrendOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26, 31, 39, 0.9)',
      borderColor: '#252B36',
    },
    grid: {
      left: '2%',
      right: '2%',
      bottom: '2%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trends?.map((item: any) => dayjs(item.period).format('HH:mm')) || [],
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#6B7280', fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#6B7280', fontSize: 12 },
      splitLine: { lineStyle: { color: '#252B36', type: 'dashed' } },
    },
    series: [
      {
        data: trends?.map((item: any) => item.count) || [],
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: {
          width: 3,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#3D9AFF' },
              { offset: 1, color: '#0E7FFF' },
            ],
          },
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(14, 127, 255, 0.4)' },
              { offset: 1, color: 'rgba(14, 127, 255, 0.05)' },
            ],
          },
        },
      },
    ],
  }

  // 合格率仪表盘
  const gaugeOption = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        splitNumber: 10,
        radius: '90%',
        center: ['50%', '70%'],
        axisLine: {
          lineStyle: {
            width: 20,
            color: [
              [0.7, '#EF4444'],
              [0.9, '#F59E0B'],
              [1, '#10B981'],
            ],
          },
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '60%',
          width: 15,
          offsetCenter: [0, '-40%'],
          itemStyle: {
            color: '#0E7FFF',
          },
        },
        axisTick: {
          length: 12,
          lineStyle: {
            color: 'auto',
            width: 2,
          },
        },
        splitLine: {
          length: 20,
          lineStyle: {
            color: 'auto',
            width: 5,
          },
        },
        axisLabel: {
          color: '#9CA3AF',
          fontSize: 14,
          distance: -50,
        },
        title: {
          offsetCenter: [0, '20%'],
          fontSize: 16,
          color: '#9CA3AF',
        },
        detail: {
          fontSize: 30,
          offsetCenter: [0, '-10%'],
          valueAnimation: true,
          color: '#FFFFFF',
          formatter: '{value}%',
        },
        data: [
          {
            value: realtime?.today_pass_rate || 0,
            name: '今日合格率',
          },
        ],
      },
    ],
  }

  // 设备状态环形图
  const deviceStatusOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(26, 31, 39, 0.9)',
      borderColor: '#252B36',
    },
    series: [
      {
        type: 'pie',
        radius: ['50%', '80%'],
        avoidLabelOverlap: false,
        label: {
          show: true,
          position: 'center',
          formatter: '{c}',
          fontSize: 36,
          fontWeight: 'bold',
          color: '#FFFFFF',
        },
        emphasis: {
          scale: false,
        },
        labelLine: {
          show: false,
        },
        data: [
          {
            value: realtime?.active_devices || 0,
            name: '活跃设备',
            itemStyle: { color: '#0E7FFF' },
          },
          {
            value: 10 - (realtime?.active_devices || 0),
            name: '离线设备',
            itemStyle: { color: '#252B36' },
            label: { show: false },
          },
        ],
      },
    ],
  }

  return (
    <div className="min-h-screen bg-background p-6">
      {/* 顶部标题栏 */}
      <div className="mb-6 text-center">
        <h1 className="text-4xl font-bold text-primary mb-2">
          光伏关断器检测数据管理系统
        </h1>
        <div className="text-xl text-text-secondary">
          {currentTime.format('YYYY年MM月DD日 HH:mm:ss')}
        </div>
      </div>

      {/* 主要指标 */}
      <Row gutter={[24, 24]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <div className="bg-background-secondary rounded-lg p-6 border border-primary/30 hover:border-primary transition-all">
            <div className="text-text-secondary mb-2">今日测试数</div>
            <div className="text-4xl font-bold text-primary">
              {realtime?.today_count || 0}
            </div>
            <div className="text-sm text-text-tertiary mt-2">
              最近1小时: {realtime?.hour_count || 0}
            </div>
          </div>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <div className="bg-background-secondary rounded-lg p-6 border border-success/30 hover:border-success transition-all">
            <div className="text-text-secondary mb-2">月累计测试</div>
            <div className="text-4xl font-bold text-success">
              {quality?.total_tests || 0}
            </div>
            <div className="text-sm text-text-tertiary mt-2">
              平均合格率: {quality?.pass_rate || 0}%
            </div>
          </div>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <div className="bg-background-secondary rounded-lg p-6 border border-warning/30 hover:border-warning transition-all">
            <div className="text-text-secondary mb-2">质量指标CPK</div>
            <div className="text-4xl font-bold text-warning">
              {quality?.cpk || 0}
            </div>
            <div className="text-sm text-text-tertiary mt-2">
              PPM: {quality?.ppm || 0}
            </div>
          </div>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <div className="bg-background-secondary rounded-lg p-6 border border-accent/30 hover:border-accent transition-all">
            <div className="text-text-secondary mb-2">首次合格率</div>
            <div className="text-4xl font-bold text-accent">
              {quality?.first_pass_yield || 0}%
            </div>
            <div className="text-sm text-text-tertiary mt-2">
              目标: ≥95%
            </div>
          </div>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={16}>
          <Card 
            className="bg-background-secondary border-background-tertiary"
            title={<span className="text-xl text-text-primary">24小时测试趋势</span>}
            bordered={false}
          >
            <ReactECharts 
              option={realtimeTrendOption} 
              style={{ height: 400 }}
              theme="dark"
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={8}>
          <Row gutter={[0, 24]}>
            <Col span={24}>
              <Card 
                className="bg-background-secondary border-background-tertiary"
                title={<span className="text-xl text-text-primary">合格率监控</span>}
                bordered={false}
              >
                <ReactECharts 
                  option={gaugeOption} 
                  style={{ height: 200 }}
                  theme="dark"
                />
              </Card>
            </Col>
            
            <Col span={24}>
              <Card 
                className="bg-background-secondary border-background-tertiary"
                title={<span className="text-xl text-text-primary">设备状态</span>}
                bordered={false}
              >
                <ReactECharts 
                  option={deviceStatusOption} 
                  style={{ height: 180 }}
                  theme="dark"
                />
                <div className="text-center mt-4">
                  <span className="text-text-secondary">设备在线率: </span>
                  <span className="text-2xl font-bold text-primary">
                    {((realtime?.active_devices || 0) / 10 * 100).toFixed(0)}%
                  </span>
                </div>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>

      {/* 底部滚动信息 */}
      <div className="mt-6 bg-background-secondary rounded-lg p-4 border border-background-tertiary">
        <div className="flex items-center space-x-8 text-text-secondary animate-pulse">
          <span>系统运行正常</span>
          <span className="text-success">● 数据库连接正常</span>
          <span className="text-primary">● 实时数据更新中</span>
          <span>最后更新: {currentTime.format('HH:mm:ss')}</span>
        </div>
      </div>
    </div>
  )
}

export default DataScreen