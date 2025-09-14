# API接口测试文档

## 测试概述
- **系统名称**: 光伏关断器检测数据管理系统
- **API框架**: FastAPI
- **基础URL**: http://localhost:8000
- **认证方式**: JWT Bearer Token

## API接口清单

### 1. 认证相关接口

#### 1.1 用户登录
- **接口**: `POST /api/v1/auth/login`
- **描述**: 用户登录获取JWT令牌
- **请求体**:
```json
{
  "username": "admin@solar.com",
  "password": "admin123"
}
```
- **响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@solar.com",
    "username": "admin"
  }
}
```

#### 1.2 用户注册
- **接口**: `POST /api/v1/auth/register`
- **描述**: 新用户注册
- **请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "username": "newuser"
}
```

#### 1.3 获取当前用户
- **接口**: `GET /api/v1/auth/me`
- **描述**: 获取当前登录用户信息
- **认证**: 需要Bearer Token

### 2. 设备管理接口

#### 2.1 获取设备列表
- **接口**: `GET /api/v1/devices`
- **描述**: 获取所有设备列表
- **查询参数**:
  - `page`: 页码 (默认: 1)
  - `limit`: 每页数量 (默认: 10)
  - `search`: 搜索关键词
- **响应示例**:
```json
{
  "items": [
    {
      "id": "uuid",
      "device_name": "光伏关断器-001",
      "device_model": "PV-SD-2000",
      "manufacturer": "阳光电源",
      "serial_number": "SN202501001",
      "status": "active"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 10
}
```

#### 2.2 创建设备
- **接口**: `POST /api/v1/devices`
- **描述**: 创建新设备
- **请求体**:
```json
{
  "device_name": "光伏关断器-新设备",
  "device_model": "PV-SD-3000",
  "manufacturer": "制造商名称",
  "serial_number": "SN202501002",
  "status": "active",
  "description": "设备描述"
}
```

#### 2.3 更新设备
- **接口**: `PUT /api/v1/devices/{device_id}`
- **描述**: 更新设备信息

#### 2.4 删除设备
- **接口**: `DELETE /api/v1/devices/{device_id}`
- **描述**: 删除设备

### 3. 数据导入接口

#### 3.1 上传Excel文件
- **接口**: `POST /api/v1/imports/upload`
- **描述**: 上传并导入Excel测试数据
- **请求格式**: multipart/form-data
- **表单字段**:
  - `file`: Excel文件 (.xlsx, .xls)
- **响应**:
```json
{
  "id": "uuid",
  "file_name": "test_data.xlsx",
  "records_count": 102,
  "import_status": "completed",
  "message": "数据导入成功"
}
```

#### 3.2 获取导入历史
- **接口**: `GET /api/v1/imports`
- **描述**: 获取所有导入记录

### 4. 测试记录接口

#### 4.1 获取测试记录列表
- **接口**: `GET /api/v1/test-records`
- **描述**: 获取测试记录列表
- **查询参数**:
  - `start_date`: 开始日期
  - `end_date`: 结束日期
  - `device_id`: 设备ID
  - `page`: 页码
  - `limit`: 每页数量

#### 4.2 获取测试记录详情
- **接口**: `GET /api/v1/test-records/{record_id}`
- **描述**: 获取单条测试记录详情

#### 4.3 获取测试详细数据
- **接口**: `GET /api/v1/test-records/{record_id}/details`
- **描述**: 获取测试的详细数据点
- **响应示例**:
```json
{
  "record_id": "uuid",
  "details": [
    {
      "timestamp": "2025-01-01T10:00:00",
      "voltage": 399.8,
      "current": 9.02,
      "power": 3605.96,
      "resistance": 44.3
    }
  ]
}
```

### 5. 统计分析接口

#### 5.1 获取统计概览
- **接口**: `GET /api/v1/statistics/overview`
- **描述**: 获取系统统计概览数据
- **响应示例**:
```json
{
  "total_tests": 1568,
  "total_devices": 89,
  "pass_rate": 98.7,
  "average_power": 3605.5,
  "today_tests": 156,
  "active_devices": 85
}
```

#### 5.2 获取趋势分析
- **接口**: `GET /api/v1/statistics/trends`
- **描述**: 获取指定时间范围的趋势数据
- **查询参数**:
  - `period`: 时间周期 (day/week/month/year)
  - `metric`: 指标类型 (power/voltage/current/efficiency)

#### 5.3 获取设备性能统计
- **接口**: `GET /api/v1/statistics/device-performance`
- **描述**: 获取各设备的性能统计数据

### 6. WebSocket接口

#### 6.1 实时数据推送
- **接口**: `ws://localhost:8000/ws`
- **描述**: WebSocket连接，接收实时测试数据
- **消息格式**:
```json
{
  "type": "test_update",
  "data": {
    "device_id": "uuid",
    "voltage": 399.8,
    "current": 9.02,
    "timestamp": "2025-01-01T10:00:00"
  }
}
```

## 错误响应格式

所有API错误响应遵循统一格式：
```json
{
  "detail": "错误描述信息",
  "status_code": 400,
  "error_code": "INVALID_REQUEST"
}
```

## 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| UNAUTHORIZED | 401 | 未授权，需要登录 |
| FORBIDDEN | 403 | 无权限访问 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 422 | 请求参数验证失败 |
| SERVER_ERROR | 500 | 服务器内部错误 |

## 测试工具推荐

1. **Postman** - API测试和文档管理
2. **Swagger UI** - 访问 `/api/v1/docs`
3. **ReDoc** - 访问 `/api/v1/redoc`
4. **httpx** - Python HTTP客户端
5. **pytest** - 自动化测试框架

## 测试用例示例

```python
import httpx
import pytest

BASE_URL = "http://localhost:8000"

@pytest.fixture
def auth_headers():
    """获取认证头"""
    response = httpx.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": "admin@solar.com", "password": "admin123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_devices(auth_headers):
    """测试获取设备列表"""
    response = httpx.get(
        f"{BASE_URL}/api/v1/devices",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "items" in response.json()
```

## 性能指标

- 平均响应时间: < 100ms
- 并发连接数: 1000+
- 文件上传限制: 100MB
- API速率限制: 60次/分钟

## 安全考虑

1. 所有API使用HTTPS（生产环境）
2. JWT令牌过期时间：60分钟
3. 密码使用bcrypt加密
4. 支持CORS配置
5. SQL注入防护（参数化查询）
6. XSS防护（输入验证）
