import React, { useState } from 'react'
import { Card, Table, Button, Space, Tag, Input, DatePicker, Select, Modal, Descriptions, message } from 'antd'
import {
  SearchOutlined,
  DownloadOutlined,
  EyeOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FilterOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import api from '@/utils/api'

const { RangePicker } = DatePicker
const { Option } = Select

interface TestRecord {
  id: string
  file_name: string
  test_date: string
  voltage: number
  current: number
  resistance: number
  power: number
  device_model: string
  batch_number: string
  operator: string
  status: string
  pass_rate: number
  sample_count: number
  created_at: string
}

const TestRecords: React.FC = () => {
  const [selectedRecord, setSelectedRecord] = useState<TestRecord | null>(null)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [filters, setFilters] = useState<any>({})
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 })
  
  const queryClient = useQueryClient()

  // 获取测试记录
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['test-records', filters, pagination],
    queryFn: async () => {
      const params = {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...filters,
      }
      const response = await api.get('/api/v1/records', { params })
      return response.data
    },
  })

  // 删除记录
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/records/${id}`)
    },
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['test-records'] })
    },
    onError: () => {
      message.error('删除失败')
    },
  })

  // 表格列定义
  const columns: ColumnsType<TestRecord> = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      ellipsis: true,
      width: 200,
    },
    {
      title: '设备型号',
      dataIndex: 'device_model',
      key: 'device_model',
      width: 120,
    },
    {
      title: '测试参数',
      key: 'parameters',
      width: 200,
      render: (_, record) => (
        <Space size="small" wrap>
          <Tag color="blue">{record.voltage}V</Tag>
          <Tag color="green">{record.current}A</Tag>
          {record.power && <Tag color="orange">{record.power}W</Tag>}
        </Space>
      ),
    },
    {
      title: '合格率',
      dataIndex: 'pass_rate',
      key: 'pass_rate',
      width: 100,
      render: (value: number) => {
        const color = value >= 95 ? 'success' : value >= 90 ? 'warning' : 'error'
        return <Tag color={color}>{value?.toFixed(2)}%</Tag>
      },
    },
    {
      title: '样本数',
      dataIndex: 'sample_count',
      key: 'sample_count',
      width: 80,
    },
    {
      title: '测试时间',
      dataIndex: 'test_date',
      key: 'test_date',
      width: 180,
      render: (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedRecord(record)
              setDetailModalVisible(true)
            }}
          >
            详情
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => {
              Modal.confirm({
                title: '确认删除',
                content: `确定要删除测试记录 ${record.file_name} 吗？`,
                onOk: () => deleteMutation.mutate(record.id),
              })
            }}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  // 处理搜索
  const handleSearch = (values: any) => {
    const newFilters: any = {}
    if (values.keyword) newFilters.keyword = values.keyword
    if (values.device_model) newFilters.device_model = values.device_model
    if (values.dateRange) {
      newFilters.start_date = values.dateRange[0].format('YYYY-MM-DD')
      newFilters.end_date = values.dateRange[1].format('YYYY-MM-DD')
    }
    if (values.voltage_range) {
      newFilters.min_voltage = values.voltage_range[0]
      newFilters.max_voltage = values.voltage_range[1]
    }
    setFilters(newFilters)
    setPagination({ ...pagination, current: 1 })
  }

  return (
    <div className="space-y-4">
      {/* 搜索栏 */}
      <Card className="data-card">
        <Space size="large" wrap>
          <Input
            placeholder="搜索文件名或备注"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            onChange={(e) => handleSearch({ keyword: e.target.value })}
          />
          
          <Select
            placeholder="选择设备型号"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => handleSearch({ device_model: value })}
          >
            <Option value="PV-Shutoff-1">PV-Shutoff-1</Option>
            <Option value="PV-Shutoff-2">PV-Shutoff-2</Option>
            <Option value="PV-Shutoff-3">PV-Shutoff-3</Option>
          </Select>
          
          <RangePicker
            onChange={(dates) => handleSearch({ dateRange: dates })}
          />
          
          <Button icon={<FilterOutlined />}>
            高级筛选
          </Button>
          
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
          >
            刷新
          </Button>
          
          <Button icon={<DownloadOutlined />}>
            导出数据
          </Button>
        </Space>
      </Card>

      {/* 数据表格 */}
      <Card className="data-card">
        <Table
          columns={columns}
          dataSource={data || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            ...pagination,
            total: data?.length || 0,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setPagination({ current: page, pageSize: pageSize || 20 })
            },
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="测试记录详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedRecord && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="文件名" span={2}>
              {selectedRecord.file_name}
            </Descriptions.Item>
            <Descriptions.Item label="设备型号">
              {selectedRecord.device_model}
            </Descriptions.Item>
            <Descriptions.Item label="批次号">
              {selectedRecord.batch_number || '-'}
            </Descriptions.Item>
            <Descriptions.Item label="电压">
              {selectedRecord.voltage} V
            </Descriptions.Item>
            <Descriptions.Item label="电流">
              {selectedRecord.current} A
            </Descriptions.Item>
            <Descriptions.Item label="电阻">
              {selectedRecord.resistance} Ω
            </Descriptions.Item>
            <Descriptions.Item label="功率">
              {selectedRecord.power} W
            </Descriptions.Item>
            <Descriptions.Item label="合格率">
              <Tag color={selectedRecord.pass_rate >= 95 ? 'success' : 'error'}>
                {selectedRecord.pass_rate?.toFixed(2)}%
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="样本数">
              {selectedRecord.sample_count}
            </Descriptions.Item>
            <Descriptions.Item label="测试时间">
              {dayjs(selectedRecord.test_date).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {dayjs(selectedRecord.created_at).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="操作员">
              {selectedRecord.operator || '-'}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}

export default TestRecords