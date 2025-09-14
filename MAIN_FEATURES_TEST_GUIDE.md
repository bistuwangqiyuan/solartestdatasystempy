# 光伏关断器检测数据管理系统 - 主要功能测试指南

## 测试环境准备

### 1. 数据库配置
在Supabase控制台执行以下SQL创建表结构：
```sql
-- 执行 database/create_tables.sql 文件内容
```

### 2. 启动服务
运行批处理文件：
```batch
start_services.bat
```

或手动启动：
```bash
# 后端
cd backend
set SUPABASE_URL=https://zzyueuweeoakopuuwfau.supabase.co
set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
set SECRET_KEY=solar-test-data-system-secret-key-2025
python -m uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 主要功能测试清单

### 1. 用户认证功能 🔐

#### 测试步骤：
1. 访问 http://localhost:3000/login
2. 测试用户登录：
   - 用户名：admin@solar.com
   - 密码：admin123
3. 验证功能：
   - [ ] 表单验证
   - [ ] 登录成功跳转
   - [ ] JWT令牌存储
   - [ ] 记住密码功能

### 2. 数据可视化大屏 📊

#### 测试步骤：
1. 访问 http://localhost:3000/dashboard
2. 验证功能：
   - [ ] 关键指标卡片显示
   - [ ] 实时数据更新（5秒刷新）
   - [ ] ECharts图表渲染
   - [ ] 响应式布局

#### 预期展示内容：
- 今日测试数
- 设备在线数
- 合格率
- 平均功率
- 功率趋势图
- 设备状态分布

### 3. 设备管理功能 🔧

#### 测试步骤：
1. 访问 http://localhost:3000/devices
2. 测试CRUD操作：
   
**创建设备：**
```json
{
  "device_name": "测试光伏关断器-001",
  "device_model": "PV-SD-3000",
  "manufacturer": "阳光电源",
  "serial_number": "SN2025091401",
  "status": "active"
}
```

3. 验证功能：
   - [ ] 设备列表展示
   - [ ] 新增设备
   - [ ] 编辑设备信息
   - [ ] 删除设备（带确认）
   - [ ] 搜索筛选
   - [ ] 分页功能

### 4. Excel数据导入 📁

#### 测试步骤：
1. 访问 http://localhost:3000/import
2. 使用测试文件：
   - `data/19.99V 6.00A data_detail_1_2025-05-09T12-15-19.xlsx`
   - `data/20.2V  19.8Ω 1.3Adata_detail_1_2025-05-02T06-23-00.xlsx`
   - `data/39.9V 9.02A data_detail_1_2025-05-09T13-02-36.xlsx`

3. 验证功能：
   - [ ] 文件拖拽上传
   - [ ] 上传进度显示
   - [ ] 数据解析验证
   - [ ] 导入成功提示
   - [ ] 导入历史记录

### 5. 测试记录查看 📋

#### 测试步骤：
1. 访问 http://localhost:3000/records
2. 验证功能：
   - [ ] 记录列表展示
   - [ ] 详情查看（点击行）
   - [ ] 日期范围筛选
   - [ ] 数据图表展示
   - [ ] 导出Excel功能
   - [ ] 打印功能

### 6. 统计分析功能 📈

#### 测试步骤：
1. 访问 http://localhost:3000/statistics
2. 验证功能：
   - [ ] 统计概览卡片
   - [ ] 趋势分析图表
   - [ ] 时间维度选择（日/周/月/年）
   - [ ] 设备对比分析
   - [ ] 报表生成

### 7. API接口测试 🔌

#### 测试步骤：
1. 访问 http://localhost:8000/api/v1/docs
2. 测试主要接口：

**认证接口：**
```bash
# 登录
POST /api/v1/auth/login
{
  "username": "admin@solar.com",
  "password": "admin123"
}

# 获取当前用户
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**设备接口：**
```bash
# 获取设备列表
GET /api/v1/devices

# 创建设备
POST /api/v1/devices
{
  "device_name": "新设备",
  "device_model": "PV-SD-2000",
  "manufacturer": "制造商"
}
```

**数据导入接口：**
```bash
# 上传文件
POST /api/v1/imports/upload
Content-Type: multipart/form-data
file: {Excel文件}
```

### 8. 响应式设计测试 📱

#### 测试设备：
1. **PC端** (1920x1080)
   - [ ] 完整侧边栏
   - [ ] 多列布局
   - [ ] 大屏图表

2. **平板端** (768x1024)
   - [ ] 可收缩菜单
   - [ ] 自适应布局
   - [ ] 触摸操作

3. **手机端** (375x667)
   - [ ] 底部导航
   - [ ] 单列布局
   - [ ] 手势支持

## 测试数据验证

### Excel文件格式要求：
- 必须包含列：Time(S), Voltage(V), Current(A)
- 支持格式：.xlsx, .xls
- 最大文件：100MB

### 性能指标：
- 页面加载时间 < 3秒
- API响应时间 < 500ms
- 数据刷新间隔：5秒

## 常见问题解决

### 1. 服务无法启动
- 检查端口占用：8000（后端）、3000（前端）
- 确认Python和Node.js版本
- 检查依赖安装

### 2. 数据库连接失败
- 验证Supabase URL和密钥
- 确认表结构已创建
- 检查网络连接

### 3. 数据导入失败
- 确认Excel文件格式
- 检查文件大小限制
- 验证数据列名称

## 测试完成标准

✅ 所有页面可正常访问
✅ CRUD操作正常工作
✅ 数据导入导出成功
✅ 图表正确显示数据
✅ 响应式布局正常
✅ API接口响应正确

---
测试指南创建时间：2025-09-14
