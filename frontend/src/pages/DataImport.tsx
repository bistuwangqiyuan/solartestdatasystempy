import React, { useState } from 'react'
import { Card, Upload, Button, Table, Progress, Tag, Space, message, Alert } from 'antd'
import {
  InboxOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  CloudUploadOutlined,
  FileExcelOutlined,
} from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import type { UploadProps } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import api from '@/utils/api'

const { Dragger } = Upload

interface ImportRecord {
  id: string
  file_name: string
  file_size: number
  import_status: 'pending' | 'processing' | 'completed' | 'failed' | 'partial'
  total_records: number
  success_records: number
  failed_records: number
  error_message?: string
  created_at: string
  completed_at?: string
}

const DataImport: React.FC = () => {
  const [uploading, setUploading] = useState(false)
  const queryClient = useQueryClient()

  // 获取导入记录
  const { data: importRecords, isLoading } = useQuery({
    queryKey: ['import-records'],
    queryFn: async () => {
      const response = await api.get('/api/v1/imports')
      return response.data
    },
    refetchInterval: 5000, // 每5秒刷新一次以更新进度
  })

  // 文件上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    customRequest: async ({ file, onSuccess, onError }) => {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', file as any)

      try {
        const response = await api.post('/api/v1/imports/excel', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        message.success(`${(file as any).name} 文件上传成功，开始处理...`)
        onSuccess?.(response.data)
        queryClient.invalidateQueries({ queryKey: ['import-records'] })
      } catch (error) {
        message.error('文件上传失败')
        onError?.(error as Error)
      } finally {
        setUploading(false)
      }
    },
    onChange(info) {
      const { status } = info.file
      if (status === 'done') {
        message.success(`${info.file.name} 文件上传成功`)
      } else if (status === 'error') {
        message.error(`${info.file.name} 文件上传失败`)
      }
    },
  }

  // 重试导入
  const retryMutation = useMutation({
    mutationFn: async (importId: string) => {
      const response = await api.post(`/api/v1/imports/${importId}/retry`)
      return response.data
    },
    onSuccess: () => {
      message.success('重试导入任务已启动')
      queryClient.invalidateQueries({ queryKey: ['import-records'] })
    },
    onError: () => {
      message.error('重试失败')
    },
  })

  // 表格列定义
  const columns: ColumnsType<ImportRecord> = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      ellipsis: true,
      render: (text) => (
        <Space>
          <FileExcelOutlined className="text-green-500" />
          {text}
        </Space>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => {
        const mb = size / 1024 / 1024
        return mb > 1 ? `${mb.toFixed(2)} MB` : `${(size / 1024).toFixed(2)} KB`
      },
    },
    {
      title: '状态',
      dataIndex: 'import_status',
      key: 'import_status',
      width: 120,
      render: (status: string) => {
        const statusConfig = {
          pending: { color: 'default', text: '待处理', icon: null },
          processing: { color: 'processing', text: '处理中', icon: <LoadingOutlined /> },
          completed: { color: 'success', text: '已完成', icon: <CheckCircleOutlined /> },
          failed: { color: 'error', text: '失败', icon: <CloseCircleOutlined /> },
          partial: { color: 'warning', text: '部分成功', icon: null },
        }
        const config = statusConfig[status as keyof typeof statusConfig]
        return (
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
        )
      },
    },
    {
      title: '进度',
      key: 'progress',
      width: 200,
      render: (_, record) => {
        if (record.import_status === 'pending') return '-'
        if (record.import_status === 'processing') {
          return <Progress percent={50} status="active" />
        }
        const percent = record.total_records > 0 
          ? (record.success_records / record.total_records) * 100 
          : 0
        const status = record.import_status === 'failed' ? 'exception' : undefined
        return <Progress percent={Number(percent.toFixed(0))} status={status} />
      },
    },
    {
      title: '记录数',
      key: 'records',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <span className="text-success">{record.success_records}</span>
          /
          <span>{record.total_records}</span>
          {record.failed_records > 0 && (
            <Tag color="error">{record.failed_records} 失败</Tag>
          )}
        </Space>
      ),
    },
    {
      title: '导入时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => {
        if (record.import_status === 'failed' || record.import_status === 'partial') {
          return (
            <Button
              type="link"
              size="small"
              onClick={() => retryMutation.mutate(record.id)}
              loading={retryMutation.isPending}
            >
              重试
            </Button>
          )
        }
        return null
      },
    },
  ]

  return (
    <div className="space-y-4">
      {/* 上传区域 */}
      <Card className="data-card">
        <Dragger {...uploadProps} disabled={uploading} style={{ background: '#1A1F27' }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined className="text-5xl text-primary" />
          </p>
          <p className="text-xl text-text-primary mb-2">
            点击或拖拽文件到此区域上传
          </p>
          <p className="text-text-secondary">
            支持 Excel 格式（.xlsx, .xls），单个文件最大 100MB
          </p>
        </Dragger>
        
        <Alert
          className="mt-4"
          message="文件命名规范"
          description={
            <ul className="list-disc list-inside space-y-1 mt-2">
              <li>文件名应包含测试参数信息，如：19.99V 6.00A data_detail_1_2025-05-09T12-15-19.xlsx</li>
              <li>系统会自动从文件名中提取电压、电流、电阻等参数</li>
              <li>建议使用统一的命名格式以确保数据正确解析</li>
            </ul>
          }
          type="info"
          showIcon
        />
      </Card>

      {/* 导入历史 */}
      <Card 
        title={
          <Space>
            <CloudUploadOutlined className="text-primary" />
            <span>导入历史</span>
          </Space>
        }
        className="data-card"
      >
        <Table
          columns={columns}
          dataSource={importRecords || []}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>
    </div>
  )
}

export default DataImport