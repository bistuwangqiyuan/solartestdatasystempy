import React, { useState } from 'react'
import { Card, Row, Col, Select, DatePicker, Space, Statistic, Button } from 'antd'
import {
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  DownloadOutlined,
  FileExcelOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import { useQuery } from '@tanstack/react-query'
import dayjs from 'dayjs'
import api from '@/utils/api'

const { RangePicker } = DatePicker
const { Option } = Select

const Statistics: React.FC = () => {
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(30, 'days'),
    dayjs(),
  ])
  const [selectedDevice, setSelectedDevice] = useState<string>()
  const [metric, setMetric] = useState('voltage')

  // 获取质量指标
  const { data: qualityMetrics } = useQuery({
    queryKey: ['quality-metrics', dateRange],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/quality-metrics', {
        params: {
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
      })
      return response.data
    },
  })

  // 获取趋势数据
  const { data: trends } = useQuery({
    queryKey: ['trends', dateRange, selectedDevice],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/trends', {
        params: {
          days: dateRange[1].diff(dateRange[0], 'days'),
          device_model: selectedDevice,
        },
      })
      return response.data
    },
  })

  // 获取分布数据
  const { data: distribution } = useQuery({
    queryKey: ['distribution', metric, dateRange, selectedDevice],
    queryFn: async () => {
      const response = await api.get('/api/v1/statistics/distribution', {
        params: {
          metric,
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
          device_model: selectedDevice,
        },
      })
      return response.data
    },
  })

  // 获取设备对比数据
  const { data: devices } = useQuery({
    queryKey: ['devices-simple'],
    queryFn: async () => {
      const response = await api.get('/api/v1/devices')
      return response.data
    },
  })

  // 趋势图配置
  const trendChartOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1F27',
      borderColor: '#252B36',
    },
    legend: {
      data: ['测试数量', '合格率'],
      textStyle: { color: '#9CA3AF' },
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
      data: trends?.map((item: any) => item.period) || [],
      axisLine: { lineStyle: { color: '#252B36' } },
      axisLabel: { 
        color: '#9CA3AF',
        formatter: (value: string) => dayjs(value).format('MM-DD'),
      },
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
        type: 'bar',
        data: trends?.map((item: any) => item.count) || [],
        itemStyle: { color: '#3D9AFF' },
      },
      {
        name: '合格率',
        type: 'line',
        yAxisIndex: 1,
        data: trends?.map((item: any) => item.average_pass_rate) || [],
        smooth: true,
        itemStyle: { color: '#10B981' },
      },
    ],
  }

  // 分布图配置
  const distributionChartOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1A1F27',
      borderColor: '#252B36',
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}<br/>数量: ${data.value} (${data.data.percentage.toFixed(1)}%)`
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: distribution?.map((item: any) => item.range) || [],
      axisLine: { lineStyle: { color: '#252B36' } },
      axisLabel: { 
        color: '#9CA3AF',
        rotate: 45,
      },
    },
    yAxis: {
      type: 'value',
      name: '数量',
      axisLine: { lineStyle: { color: '#252B36' } },
      axisLabel: { color: '#9CA3AF' },
      splitLine: { lineStyle: { color: '#252B36', type: 'dashed' } },
    },
    series: [
      {
        type: 'bar',
        data: distribution?.map((item: any) => ({
          value: item.count,
          percentage: item.percentage,
        })) || [],
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#0E7FFF' },
              { offset: 1, color: '#3D9AFF' },
            ],
          },
        },
      },
    ],
  }

  // 导出统计报告
  const handleExport = async (format: 'excel' | 'csv') => {
    try {
      const response = await api.get('/api/v1/statistics/export', {
        params: {
          format,
          start_date: dateRange[0].format('YYYY-MM-DD'),
          end_date: dateRange[1].format('YYYY-MM-DD'),
        },
        responseType: 'blob',
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `statistics_${dayjs().format('YYYYMMDD')}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Export failed:', error)
    }
  }

  return (
    <div className="space-y-4">
      {/* 筛选条件 */}
      <Card className="data-card">
        <Space size="large" wrap>
          <RangePicker
            value={dateRange}
            onChange={(dates) => dates && setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
          />
          
          <Select
            placeholder="选择设备"
            style={{ width: 200 }}
            allowClear
            value={selectedDevice}
            onChange={setSelectedDevice}
          >
            {devices?.map((device: any) => (
              <Option key={device.id} value={device.device_model}>
                {device.device_model}
              </Option>
            ))}
          </Select>
          
          <Select
            value={metric}
            onChange={setMetric}
            style={{ width: 150 }}
          >
            <Option value="voltage">电压分布</Option>
            <Option value="current">电流分布</Option>
            <Option value="power">功率分布</Option>
            <Option value="resistance">电阻分布</Option>
          </Select>
          
          <Button icon={<FileExcelOutlined />} onClick={() => handleExport('excel')}>
            导出Excel
          </Button>
        </Space>
      </Card>

      {/* 质量指标卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">总测试数</span>}
              value={qualityMetrics?.total_tests || 0}
              suffix="次"
              valueStyle={{ color: '#0E7FFF' }}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">平均合格率</span>}
              value={qualityMetrics?.pass_rate || 0}
              suffix="%"
              precision={2}
              valueStyle={{ color: '#10B981' }}
              prefix={<PieChartOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">CPK指标</span>}
              value={qualityMetrics?.cpk || 0}
              precision={2}
              valueStyle={{ color: '#F59E0B' }}
              prefix={<LineChartOutlined />}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card className="data-card">
            <Statistic
              title={<span className="text-text-secondary">PPM值</span>}
              value={qualityMetrics?.ppm || 0}
              valueStyle={{ color: '#8B5CF6' }}
              suffix="ppm"
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={24}>
          <Card 
            title={<span className="text-text-primary">测试趋势分析</span>}
            className="data-card"
          >
            <ReactECharts 
              option={trendChartOption} 
              style={{ height: 400 }}
              theme="dark"
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={24}>
          <Card 
            title={<span className="text-text-primary">{metric === 'voltage' ? '电压' : metric === 'current' ? '电流' : metric === 'power' ? '功率' : '电阻'}分布</span>}
            className="data-card"
          >
            <ReactECharts 
              option={distributionChartOption} 
              style={{ height: 300 }}
              theme="dark"
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Statistics