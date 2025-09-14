"""
设备信息数据模型
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class DeviceBase(BaseModel):
    """设备基础模型"""
    device_model: str = Field(..., description="设备型号")
    device_name: Optional[str] = Field(None, description="设备名称")
    manufacturer: Optional[str] = Field(None, description="制造商")
    rated_voltage: Optional[float] = Field(None, description="额定电压(V)")
    rated_current: Optional[float] = Field(None, description="额定电流(A)")
    rated_power: Optional[float] = Field(None, description="额定功率(W)")
    specifications: Optional[Dict[str, Any]] = Field(None, description="技术规格")
    description: Optional[str] = Field(None, description="描述")


class DeviceCreate(DeviceBase):
    """创建设备模型"""
    pass


class DeviceUpdate(BaseModel):
    """更新设备模型"""
    device_name: Optional[str] = None
    manufacturer: Optional[str] = None
    rated_voltage: Optional[float] = None
    rated_current: Optional[float] = None
    rated_power: Optional[float] = None
    specifications: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Device(DeviceBase):
    """设备响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class DeviceWithStats(Device):
    """包含统计信息的设备模型"""
    test_count: int = Field(default=0, description="测试次数")
    last_test_date: Optional[datetime] = Field(None, description="最后测试日期")
    average_pass_rate: float = Field(default=0.0, description="平均合格率")