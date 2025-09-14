# 光伏关断器检测数据管理系统 - 部署指南

## 目录
1. [环境准备](#环境准备)
2. [Supabase配置](#supabase配置)
3. [后端部署](#后端部署)
4. [前端部署](#前端部署)
5. [生产环境配置](#生产环境配置)
6. [故障排除](#故障排除)

## 环境准备

### 系统要求
- Python 3.11+
- Node.js 18+
- Git

### 克隆代码
```bash
git clone <your-repository-url>
cd pv-shutoff-data-management
```

## Supabase配置

### 1. 创建Supabase项目
访问 [Supabase](https://supabase.com) 并创建新项目（如果还没有）。

### 2. 数据库初始化
在Supabase SQL编辑器中执行以下SQL来创建必要的表：

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建测试记录表
CREATE TABLE IF NOT EXISTS test_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(255) NOT NULL,
    test_date TIMESTAMP NOT NULL,
    voltage DECIMAL(10,2),
    current DECIMAL(10,2),
    resistance DECIMAL(10,2),
    power DECIMAL(10,2),
    device_model VARCHAR(100),
    batch_number VARCHAR(100),
    operator VARCHAR(100),
    status VARCHAR(50) DEFAULT 'completed',
    test_duration INTEGER,
    sample_count INTEGER,
    pass_rate DECIMAL(5,2),
    notes TEXT,
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 创建测试详情表
CREATE TABLE IF NOT EXISTS test_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_record_id UUID NOT NULL REFERENCES test_records(id) ON DELETE CASCADE,
    time_point DECIMAL(10,3) NOT NULL,
    voltage_value DECIMAL(10,4),
    current_value DECIMAL(10,4),
    power_value DECIMAL(10,4),
    resistance_value DECIMAL(10,4),
    temperature DECIMAL(10,2),
    humidity DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建设备信息表
CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_model VARCHAR(100) UNIQUE NOT NULL,
    device_name VARCHAR(200),
    manufacturer VARCHAR(200),
    rated_voltage DECIMAL(10,2),
    rated_current DECIMAL(10,2),
    rated_power DECIMAL(10,2),
    specifications JSONB,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- 创建导入记录表
CREATE TABLE IF NOT EXISTS import_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    file_path VARCHAR(500),
    import_status VARCHAR(50) DEFAULT 'pending',
    total_records INTEGER DEFAULT 0,
    success_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    error_message TEXT,
    import_config JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- 创建索引
CREATE INDEX idx_test_records_test_date ON test_records(test_date);
CREATE INDEX idx_test_records_device_model ON test_records(device_model);
CREATE INDEX idx_test_details_record_id ON test_details(test_record_id);
CREATE INDEX idx_import_records_status ON import_records(import_status);
```

### 3. 配置RLS（行级安全）
```sql
-- 启用RLS
ALTER TABLE test_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE import_records ENABLE ROW LEVEL SECURITY;

-- 创建策略（根据需要调整）
CREATE POLICY "Enable read access for all users" ON test_records
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON test_records
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
```

## 后端部署

### 本地开发
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，填入您的Supabase凭据

# 运行开发服务器
uvicorn app.main:app --reload
```

### Docker部署
```bash
# 构建镜像
docker build -t pv-backend ./backend

# 运行容器
docker run -d \
  --name pv-backend \
  -p 8000:8000 \
  --env-file ./backend/.env \
  -v $(pwd)/backend/uploads:/app/uploads \
  -v $(pwd)/backend/logs:/app/logs \
  pv-backend
```

### Heroku部署
1. 创建 `Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

2. 部署:
```bash
heroku create your-app-name
heroku config:set SUPABASE_URL=your-url
heroku config:set SUPABASE_ANON_KEY=your-key
heroku config:set SUPABASE_SERVICE_KEY=your-service-key
git push heroku main
```

## 前端部署

### 本地开发
```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑.env文件

# 运行开发服务器
npm run dev
```

### Netlify部署

#### 方法1：通过Netlify CLI
```bash
# 安装Netlify CLI
npm install -g netlify-cli

# 构建项目
cd frontend
npm run build

# 部署
netlify deploy --prod --dir=dist
```

#### 方法2：通过GitHub集成
1. 将代码推送到GitHub
2. 登录Netlify Dashboard
3. 点击 "New site from Git"
4. 选择您的仓库
5. 配置构建设置：
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
6. 添加环境变量：
   - `VITE_API_BASE_URL`: 您的后端API地址

### Docker Compose部署
```bash
# 使用docker-compose运行整个应用
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 生产环境配置

### 1. 环境变量设置
后端必需的环境变量：
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
SECRET_KEY=your-secret-key-for-jwt
ENVIRONMENT=production
DEBUG=False
```

前端必需的环境变量：
```
VITE_API_BASE_URL=https://your-backend-api.com
```

### 2. HTTPS配置
- 使用Netlify自动提供的HTTPS
- 后端使用反向代理（如Nginx）配置SSL证书

### 3. 性能优化
- 启用Gzip压缩
- 配置CDN
- 设置适当的缓存策略
- 使用Redis缓存（可选）

### 4. 监控和日志
- 配置Sentry错误追踪
- 设置日志轮转
- 配置健康检查端点

## 故障排除

### 常见问题

#### 1. 数据库连接失败
- 检查Supabase URL和密钥是否正确
- 确保网络连接正常
- 检查Supabase项目是否处于活动状态

#### 2. CORS错误
- 确保后端CORS配置包含前端域名
- 检查API请求URL是否正确

#### 3. 文件上传失败
- 检查文件大小限制
- 确保uploads目录有写入权限
- 验证文件格式是否支持

#### 4. WebSocket连接失败
- 检查WebSocket代理配置
- 确保使用正确的协议（ws:// 或 wss://）

### 日志查看
```bash
# 查看后端日志
docker logs pv-backend

# 查看前端日志
docker logs pv-frontend

# 查看应用日志文件
tail -f backend/logs/app_*.log
```

### 性能调试
1. 使用浏览器开发者工具的Network标签
2. 检查API响应时间
3. 使用Lighthouse进行性能审计

## 备份和恢复

### 数据库备份
Supabase提供自动备份功能，也可以手动导出：
```bash
# 使用pg_dump导出
pg_dump -h your-db-host -U postgres -d postgres > backup.sql
```

### 文件备份
定期备份uploads目录中的文件：
```bash
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/
```

## 安全建议

1. **定期更新依赖**
```bash
# 后端
pip list --outdated
pip install --upgrade package-name

# 前端
npm outdated
npm update
```

2. **使用强密码和密钥**
- 使用至少32字符的SECRET_KEY
- 定期轮换API密钥

3. **限制API访问**
- 实施速率限制
- 使用IP白名单（如果适用）

4. **数据加密**
- 使用HTTPS传输
- 敏感数据加密存储

## 支持

如遇到问题，请：
1. 查看日志文件
2. 检查环境变量配置
3. 参考本指南的故障排除部分
4. 提交GitHub Issue

祝您部署顺利！🚀