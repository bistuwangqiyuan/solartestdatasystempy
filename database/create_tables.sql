-- 光伏关断器检测数据管理系统数据库表结构
-- 请在Supabase SQL编辑器中执行此脚本

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 创建设备表
CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_name VARCHAR(255) NOT NULL,
    device_model VARCHAR(255),
    manufacturer VARCHAR(255),
    serial_number VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    description TEXT,
    specifications JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 创建导入记录表
CREATE TABLE IF NOT EXISTS import_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000),
    file_size BIGINT,
    records_count INTEGER DEFAULT 0,
    import_status VARCHAR(50) DEFAULT 'pending' CHECK (import_status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    imported_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 3. 创建测试记录主表
CREATE TABLE IF NOT EXISTS test_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES devices(id) ON DELETE SET NULL,
    import_record_id UUID REFERENCES import_records(id) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    test_date TIMESTAMPTZ NOT NULL,
    tester VARCHAR(255),
    test_result VARCHAR(50) CHECK (test_result IN ('pass', 'fail', 'pending')),
    test_duration INTEGER, -- 测试持续时间（秒）
    voltage DECIMAL(10,4),
    current DECIMAL(10,4),
    power DECIMAL(10,4),
    resistance DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 创建测试详细数据表
CREATE TABLE IF NOT EXISTS test_details (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_record_id UUID REFERENCES test_records(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    voltage DECIMAL(10,4),
    current DECIMAL(10,4),
    power DECIMAL(10,4),
    resistance DECIMAL(10,4),
    temperature DECIMAL(10,4),
    frequency DECIMAL(10,4),
    efficiency DECIMAL(10,4),
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 创建用户表（如果不存在）
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引以提高查询性能
CREATE INDEX idx_devices_serial_number ON devices(serial_number);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_test_records_device_id ON test_records(device_id);
CREATE INDEX idx_test_records_test_date ON test_records(test_date);
CREATE INDEX idx_test_details_test_record_id ON test_details(test_record_id);
CREATE INDEX idx_test_details_timestamp ON test_details(timestamp);
CREATE INDEX idx_import_records_status ON import_records(import_status);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间触发器
CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_records_updated_at BEFORE UPDATE ON test_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 启用RLS (Row Level Security) - 可选
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE import_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略（暂时允许所有操作）
CREATE POLICY "Enable all operations for authenticated users" ON devices
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable all operations for authenticated users" ON import_records
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable all operations for authenticated users" ON test_records
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable all operations for authenticated users" ON test_details
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Enable all operations for authenticated users" ON users
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- 插入测试数据（可选）
-- INSERT INTO devices (device_name, device_model, manufacturer, serial_number, status) VALUES
-- ('光伏关断器-001', 'PV-SD-2000', '阳光电源', 'SN202501001', 'active'),
-- ('光伏关断器-002', 'PV-SD-3000', '华为技术', 'SN202501002', 'active'),
-- ('光伏关断器-003', 'PV-SD-1500', '正泰电器', 'SN202501003', 'maintenance');

-- 完成提示
-- 表创建成功！
