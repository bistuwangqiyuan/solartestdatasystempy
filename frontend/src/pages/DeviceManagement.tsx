import React, { useState } from 'react'
import { Card, Table, Button, Space, Tag, Modal, Form, Input, InputNumber, message } from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  AppstoreOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import api from '@/utils/api'

interface Device {
  id: string
  device_model: string
  device_name: string
  manufacturer: string
  rated_voltage: number
  rated_current: number
  rated_power: number
  test_count: number
  average_pass_rate: number
  last_test_date: string
  is_active: boolean
  created_at: string
}

const DeviceManagement: React.FC = () => {
  const [modalVisible, setModalVisible] = useState(false)
  const [editingDevice, setEditingDevice] = useState<Device | null>(null)
  const [form] = Form.useForm()
  
  const queryClient = useQueryClient()

  // 获取设备列表
  const { data: devices, isLoading } = useQuery({
    queryKey: ['devices'],
    queryFn: async () => {
      const response = await api.get('/api/v1/devices/with-stats')
      return response.data
    },
  })

  // 创建/更新设备
  const saveMutation = useMutation({
    mutationFn: async (values: any) => {
      if (editingDevice) {
        return api.put(`/api/v1/devices/${editingDevice.id}`, values)
      } else {
        return api.post('/api/v1/devices', values)
      }
    },
    onSuccess: () => {
      message.success(editingDevice ? '更新成功' : '创建成功')
      setModalVisible(false)
      form.resetFields()
      setEditingDevice(null)
      queryClient.invalidateQueries({ queryKey: ['devices'] })
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '操作失败')
    },
  })

  // 删除设备
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/devices/${id}`)
    },
    onSuccess: () => {
      message.success('删除成功')
      queryClient.invalidateQueries({ queryKey: ['devices'] })
    },
    onError: () => {
      message.error('删除失败')
    },
  })

  // 表格列定义
  const columns: ColumnsType<Device> = [
    {
      title: '设备型号',
      dataIndex: 'device_model',
      key: 'device_model',
      render: (text, record) => (
        <Space>
          <AppstoreOutlined className="text-primary" />
          <span className="font-medium">{text}</span>
          {!record.is_active && <Tag color="default">已停用</Tag>}
        </Space>
      ),
    },
    {
      title: '设备名称',
      dataIndex: 'device_name',
      key: 'device_name',
      ellipsis: true,
    },
    {
      title: '制造商',
      dataIndex: 'manufacturer',
      key: 'manufacturer',
    },
    {
      title: '额定参数',
      key: 'rated_params',
      render: (_, record) => (
        <Space size="small" wrap>
          <Tag color="blue">{record.rated_voltage}V</Tag>
          <Tag color="green">{record.rated_current}A</Tag>
          <Tag color="orange">{record.rated_power}W</Tag>
        </Space>
      ),
    },
    {
      title: '测试统计',
      key: 'stats',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <span>测试次数: <strong>{record.test_count}</strong></span>
          <span>
            平均合格率: 
            <Tag color={record.average_pass_rate >= 95 ? 'success' : 'warning'} className="ml-2">
              {record.average_pass_rate?.toFixed(2)}%
            </Tag>
          </span>
        </Space>
      ),
    },
    {
      title: '最后测试',
      dataIndex: 'last_test_date',
      key: 'last_test_date',
      render: (value: string) => value ? dayjs(value).format('YYYY-MM-DD') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => {
              setEditingDevice(record)
              form.setFieldsValue(record)
              setModalVisible(true)
            }}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => {
              Modal.confirm({
                title: '确认删除',
                content: `确定要删除设备 ${record.device_model} 吗？`,
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

  // 处理表单提交
  const handleSubmit = (values: any) => {
    saveMutation.mutate(values)
  }

  return (
    <div className="space-y-4">
      {/* 顶部操作栏 */}
      <Card className="data-card">
        <div className="flex justify-between items-center">
          <Space>
            <ThunderboltOutlined className="text-2xl text-primary" />
            <span className="text-xl font-medium">设备管理</span>
          </Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingDevice(null)
              form.resetFields()
              setModalVisible(true)
            }}
          >
            添加设备
          </Button>
        </div>
      </Card>

      {/* 设备列表 */}
      <Card className="data-card">
        <Table
          columns={columns}
          dataSource={devices || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 台设备`,
          }}
        />
      </Card>

      {/* 添加/编辑设备弹窗 */}
      <Modal
        title={editingDevice ? '编辑设备' : '添加设备'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
          setEditingDevice(null)
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="device_model"
            label="设备型号"
            rules={[{ required: true, message: '请输入设备型号' }]}
          >
            <Input placeholder="例如: PV-Shutoff-1" disabled={!!editingDevice} />
          </Form.Item>

          <Form.Item
            name="device_name"
            label="设备名称"
            rules={[{ required: true, message: '请输入设备名称' }]}
          >
            <Input placeholder="设备的描述性名称" />
          </Form.Item>

          <Form.Item
            name="manufacturer"
            label="制造商"
            rules={[{ required: true, message: '请输入制造商' }]}
          >
            <Input placeholder="制造商名称" />
          </Form.Item>

          <Space size="large" style={{ width: '100%' }}>
            <Form.Item
              name="rated_voltage"
              label="额定电压 (V)"
              rules={[{ required: true, message: '请输入额定电压' }]}
            >
              <InputNumber min={0} max={1000} precision={2} style={{ width: 150 }} />
            </Form.Item>

            <Form.Item
              name="rated_current"
              label="额定电流 (A)"
              rules={[{ required: true, message: '请输入额定电流' }]}
            >
              <InputNumber min={0} max={100} precision={2} style={{ width: 150 }} />
            </Form.Item>

            <Form.Item
              name="rated_power"
              label="额定功率 (W)"
              rules={[{ required: true, message: '请输入额定功率' }]}
            >
              <InputNumber min={0} max={10000} precision={2} style={{ width: 150 }} />
            </Form.Item>
          </Space>

          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea rows={3} placeholder="设备的详细描述（可选）" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={saveMutation.isPending}>
                {editingDevice ? '更新' : '创建'}
              </Button>
              <Button onClick={() => {
                setModalVisible(false)
                form.resetFields()
                setEditingDevice(null)
              }}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default DeviceManagement