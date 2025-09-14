# 光伏关断器检测数据管理系统

一个专业的光伏关断器检测数据管理平台，提供数据导入、分析、可视化和报表功能。

## 功能特性

- 📊 **数据可视化大屏** - 实时展示关键性能指标
- 📁 **Excel数据导入** - 支持批量导入测试数据
- 📈 **统计分析** - 多维度数据分析和趋势预测
- 🔧 **设备管理** - 设备信息维护和性能跟踪
- 📱 **响应式设计** - 支持PC、平板和移动设备
- 🔐 **安全认证** - 基于JWT的用户认证系统

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- Supabase (PostgreSQL)
- Pandas / NumPy
- WebSocket

### 前端
- React 18
- TypeScript
- Ant Design
- ECharts
- TailwindCSS
- Vite

## 快速开始

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 Supabase 连接信息

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 API 地址

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## 部署指南

### Netlify 部署（前端）

1. 将代码推送到 GitHub
2. 在 Netlify 中导入项目
3. 设置构建命令：`npm run build`
4. 设置发布目录：`frontend/dist`
5. 配置环境变量

### 后端部署选项

- **Heroku**: 使用 Procfile 配置
- **Railway**: 直接部署 FastAPI 应用
- **Docker**: 使用提供的 Dockerfile

## 数据库结构

主要数据表：
- `test_records` - 测试记录主表
- `test_details` - 测试详细数据
- `devices` - 设备信息
- `import_records` - 导入记录

## API 文档

启动后端服务后，访问以下地址查看 API 文档：
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## 截图

![数据大屏](docs/screenshots/dashboard.png)
![测试记录](docs/screenshots/records.png)
![统计分析](docs/screenshots/statistics.png)

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请提交 Issue 或联系维护者。