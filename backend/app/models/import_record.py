"""
文件导入记录数据模型
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class ImportRecordBase(BaseModel):
    """导入记录基础模型"""
    file_name: str = Field(..., description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    file_path: Optional[str] = Field(None, description="文件路径")
    import_config: Optional[Dict[str, Any]] = Field(None, description="导入配置")


class ImportRecordCreate(ImportRecordBase):
    """创建导入记录模型"""
    pass


class ImportRecordUpdate(BaseModel):
    """更新导入记录模型"""
    import_status: Optional[str] = Field(None, description="导入状态")
    total_records: Optional[int] = Field(None, description="总记录数")
    success_records: Optional[int] = Field(None, description="成功记录数")
    failed_records: Optional[int] = Field(None, description="失败记录数")
    error_message: Optional[str] = Field(None, description="错误信息")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class ImportRecord(ImportRecordBase):
    """导入记录响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    import_status: str = Field(default="pending", description="导入状态")
    total_records: int = Field(default=0, description="总记录数")
    success_records: int = Field(default=0, description="成功记录数")
    failed_records: int = Field(default=0, description="失败记录数")
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    created_by: Optional[UUID] = None


class ImportProgress(BaseModel):
    """导入进度模型"""
    import_id: UUID
    status: str
    progress: float = Field(ge=0, le=100, description="进度百分比")
    current_record: int = Field(default=0, description="当前处理记录数")
    total_records: int = Field(default=0, description="总记录数")
    message: Optional[str] = Field(None, description="状态消息")