"""
数据库连接和初始化
"""
from supabase import create_client, Client
from app.core.config import settings
import asyncio
from typing import Optional
from loguru import logger


class SupabaseClient:
    """Supabase客户端管理"""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
        
    @property
    def client(self) -> Client:
        """获取普通客户端（使用anon key）"""
        if not self._client:
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            logger.info("Supabase client initialized")
        return self._client
    
    @property
    def service_client(self) -> Client:
        """获取服务客户端（使用service key）"""
        if not self._service_client:
            self._service_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            logger.info("Supabase service client initialized")
        return self._service_client
    
    async def init_database(self):
        """初始化数据库表结构"""
        try:
            # 创建测试记录表
            await self.create_test_records_table()
            # 创建测试详情表
            await self.create_test_details_table()
            # 创建设备信息表
            await self.create_devices_table()
            # 创建文件导入记录表
            await self.create_import_records_table()
            
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def create_test_records_table(self):
        """创建测试记录表"""
        sql = """
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
        
        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_test_records_test_date ON test_records(test_date);
        CREATE INDEX IF NOT EXISTS idx_test_records_device_model ON test_records(device_model);
        CREATE INDEX IF NOT EXISTS idx_test_records_status ON test_records(status);
        CREATE INDEX IF NOT EXISTS idx_test_records_created_at ON test_records(created_at);
        """
        
        # 使用service client执行SQL
        self.service_client.postgrest.rpc('exec_sql', {'query': sql}).execute()
    
    async def create_test_details_table(self):
        """创建测试详情表"""
        sql = """
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
        
        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_test_details_record_id ON test_details(test_record_id);
        CREATE INDEX IF NOT EXISTS idx_test_details_time_point ON test_details(time_point);
        """
        
        self.service_client.postgrest.rpc('exec_sql', {'query': sql}).execute()
    
    async def create_devices_table(self):
        """创建设备信息表"""
        sql = """
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
        
        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_devices_model ON devices(device_model);
        CREATE INDEX IF NOT EXISTS idx_devices_manufacturer ON devices(manufacturer);
        """
        
        self.service_client.postgrest.rpc('exec_sql', {'query': sql}).execute()
    
    async def create_import_records_table(self):
        """创建文件导入记录表"""
        sql = """
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
        CREATE INDEX IF NOT EXISTS idx_import_records_status ON import_records(import_status);
        CREATE INDEX IF NOT EXISTS idx_import_records_created_at ON import_records(created_at);
        """
        
        self.service_client.postgrest.rpc('exec_sql', {'query': sql}).execute()


# 创建全局数据库客户端实例
db_client = SupabaseClient()


async def get_db() -> Client:
    """获取数据库客户端依赖"""
    return db_client.client


async def get_service_db() -> Client:
    """获取服务数据库客户端依赖"""
    return db_client.service_client