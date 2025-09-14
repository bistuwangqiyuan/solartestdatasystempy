# 光伏关断器检测数据管理系统 - 快速启动指南

## 前提条件
- Python 3.11+
- Node.js 16+
- pnpm 或 npm
- Supabase 账号和项目

## 快速启动步骤

### 1. 克隆项目
```bash
git clone <repository-url>
cd solartestdatasystempy
```

### 2. 配置数据库

#### 选项A: 使用现有Supabase项目
需要在Supabase管理界面创建以下表：

```sql
-- 设备表
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_name VARCHAR(255) NOT NULL,
    device_model VARCHAR(255),
    manufacturer VARCHAR(255),
    serial_number VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 导入记录表
CREATE TABLE import_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(500) NOT NULL,
    import_status VARCHAR(50) DEFAULT 'pending',
    records_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 测试记录表
CREATE TABLE test_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id),
    test_name VARCHAR(255) NOT NULL,
    test_date TIMESTAMPTZ NOT NULL,
    voltage DECIMAL(10,4),
    current DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 测试详细数据表
CREATE TABLE test_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_record_id UUID REFERENCES test_records(id),
    timestamp TIMESTAMPTZ NOT NULL,
    voltage DECIMAL(10,4),
    current DECIMAL(10,4),
    power DECIMAL(10,4)
);
```

#### 选项B: 创建新的Supabase项目
1. 访问 https://supabase.com
2. 创建新项目
3. 获取项目URL和API密钥
4. 更新 backend/start_test.py 中的配置

### 3. 启动后端服务

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python start_test.py
```

后端服务将在 http://localhost:8000 启动
API文档: http://localhost:8000/api/v1/docs

### 4. 启动前端服务

新开一个终端窗口：

```bash
# 进入前端目录
cd frontend

# 安装依赖（使用pnpm）
pnpm install
# 或使用npm
npm install

# 启动开发服务器
pnpm run dev
# 或
npm run dev
```

前端服务将在 http://localhost:3000 启动

### 5. 访问系统

打开浏览器访问 http://localhost:3000

默认页面包括：
- `/` - 首页
- `/login` - 登录页
- `/dashboard` - 数据大屏
- `/devices` - 设备管理
- `/import` - 数据导入
- `/records` - 测试记录
- `/statistics` - 统计分析

### 6. 测试数据

项目包含测试数据文件：
- `data/19.99V 6.00A data_detail_1_2025-05-09T12-15-19.xlsx`
- `data/20.2V  19.8Ω 1.3Adata_detail_1_2025-05-02T06-23-00.xlsx`
- `data/39.9V 9.02A data_detail_1_2025-05-09T13-02-36.xlsx`

可通过数据导入功能上传这些文件进行测试。

## 常见问题

### Q: 数据库连接失败
A: 检查 backend/start_test.py 中的 Supabase 配置是否正确

### Q: 前端无法访问后端API
A: 确保后端服务在 8000 端口运行，检查 vite.config.ts 中的代理配置

### Q: 数据导入失败
A: 确保数据库表已创建，检查Excel文件格式是否正确

## 开发模式

### 后端开发
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd frontend
pnpm run dev
```

### 运行测试
```bash
python test_system.py
```

## 生产部署

参考 DEPLOYMENT_GUIDE.md 文件

## 获取帮助

- 查看 README.md 了解项目详情
- 查看 TEST_REPORT.md 了解测试状态
- 提交 Issue 报告问题
