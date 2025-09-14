"""
测试记录数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class TestRecordBase(BaseModel):
    """测试记录基础模型"""
    file_name: str = Field(..., description="文件名")
    test_date: datetime = Field(..., description="测试日期")
    voltage: Optional[float] = Field(None, description="电压(V)")
    current: Optional[float] = Field(None, description="电流(A)")
    resistance: Optional[float] = Field(None, description="电阻(Ω)")
    power: Optional[float] = Field(None, description="功率(W)")
    device_model: Optional[str] = Field(None, description="设备型号")
    batch_number: Optional[str] = Field(None, description="批次号")
    operator: Optional[str] = Field(None, description="操作员")
    status: str = Field(default="completed", description="状态")
    test_duration: Optional[int] = Field(None, description="测试时长(秒)")
    sample_count: Optional[int] = Field(None, description="采样点数")
    pass_rate: Optional[float] = Field(None, description="合格率(%)")
    notes: Optional[str] = Field(None, description="备注")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始数据")


class TestRecordCreate(TestRecordBase):
    """创建测试记录模型"""
    pass


class TestRecordUpdate(BaseModel):
    """更新测试记录模型"""
    device_model: Optional[str] = None
    batch_number: Optional[str] = None
    operator: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    pass_rate: Optional[float] = None


class TestRecord(TestRecordBase):
    """测试记录响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    is_deleted: bool = False


class TestDetailBase(BaseModel):
    """测试详情基础模型"""
    time_point: float = Field(..., description="时间点(秒)")
    voltage_value: Optional[float] = Field(None, description="电压值(V)")
    current_value: Optional[float] = Field(None, description="电流值(A)")
    power_value: Optional[float] = Field(None, description="功率值(W)")
    resistance_value: Optional[float] = Field(None, description="电阻值(Ω)")
    temperature: Optional[float] = Field(None, description="温度(℃)")
    humidity: Optional[float] = Field(None, description="湿度(%)")
    status: Optional[str] = Field(None, description="状态")


class TestDetailCreate(TestDetailBase):
    """创建测试详情模型"""
    test_record_id: UUID = Field(..., description="测试记录ID")


class TestDetail(TestDetailBase):
    """测试详情响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    test_record_id: UUID
    created_at: datetime


class TestRecordWithDetails(TestRecord):
    """包含详情的测试记录模型"""
    details: Optional[List[TestDetail]] = Field(default_factory=list)
    detail_count: int = Field(default=0)


class TestRecordStatistics(BaseModel):
    """测试记录统计模型"""
    total_count: int = Field(default=0, description="总记录数")
    today_count: int = Field(default=0, description="今日记录数")
    week_count: int = Field(default=0, description="本周记录数")
    month_count: int = Field(default=0, description="本月记录数")
    pass_count: int = Field(default=0, description="合格数")
    fail_count: int = Field(default=0, description="不合格数")
    average_pass_rate: float = Field(default=0.0, description="平均合格率")
    device_distribution: Dict[str, int] = Field(default_factory=dict, description="设备型号分布")
    daily_trend: List[Dict[str, Any]] = Field(default_factory=list, description="日趋势数据")


class TestRecordFilter(BaseModel):
    """测试记录筛选条件"""
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    device_model: Optional[str] = Field(None, description="设备型号")
    batch_number: Optional[str] = Field(None, description="批次号")
    operator: Optional[str] = Field(None, description="操作员")
    status: Optional[str] = Field(None, description="状态")
    min_voltage: Optional[float] = Field(None, description="最小电压")
    max_voltage: Optional[float] = Field(None, description="最大电压")
    min_current: Optional[float] = Field(None, description="最小电流")
    max_current: Optional[float] = Field(None, description="最大电流")
    keyword: Optional[str] = Field(None, description="关键词搜索")