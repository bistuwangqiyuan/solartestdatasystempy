"""
应用配置管理
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import json


class Settings(BaseSettings):
    # 应用基本信息
    app_name: str = Field(default="光伏关断器检测数据管理系统")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="production")
    
    # Supabase配置
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(..., env="SUPABASE_SERVICE_KEY")
    
    # 安全配置
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60)
    
    # CORS配置
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )
    
    # Redis配置
    redis_url: Optional[str] = Field(default=None)
    
    # 文件上传配置
    max_upload_size: int = Field(default=104857600)  # 100MB
    allowed_extensions: List[str] = Field(
        default_factory=lambda: [".xlsx", ".xls", ".csv"]
    )
    
    # API限流配置
    rate_limit_per_minute: int = Field(default=60)
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "cors_origins":
                return json.loads(raw_val)
            if field_name == "allowed_extensions":
                return json.loads(raw_val)
            return raw_val


# 创建全局配置实例
settings = Settings()
