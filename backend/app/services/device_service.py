"""
设备管理服务
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from supabase import Client
from loguru import logger

from app.models.device import (
    Device,
    DeviceCreate,
    DeviceUpdate,
    DeviceWithStats
)


class DeviceService:
    """设备管理服务类"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def get_devices(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        manufacturer: Optional[str] = None
    ) -> List[Device]:
        """获取设备列表"""
        try:
            query = self.db.table("devices").select("*")
            
            if is_active is not None:
                query = query.eq("is_active", is_active)
            
            if manufacturer:
                query = query.eq("manufacturer", manufacturer)
            
            query = query.order("device_model")
            query = query.range(skip, skip + limit - 1)
            
            response = query.execute()
            
            return [Device(**device) for device in response.data]
            
        except Exception as e:
            logger.error(f"Error fetching devices: {str(e)}")
            raise
    
    async def get_devices_with_stats(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[DeviceWithStats]:
        """获取设备列表（包含统计信息）"""
        try:
            # 获取设备列表
            devices = await self.get_devices(skip, limit)
            
            result = []
            for device in devices:
                device_with_stats = DeviceWithStats(**device.dict())
                
                # 获取测试统计信息
                stats_response = self.db.table("test_records")\
                    .select("id, test_date, pass_rate")\
                    .eq("device_model", device.device_model)\
                    .eq("is_deleted", False)\
                    .execute()
                
                if stats_response.data:
                    device_with_stats.test_count = len(stats_response.data)
                    
                    # 最后测试日期
                    test_dates = [record["test_date"] for record in stats_response.data]
                    if test_dates:
                        device_with_stats.last_test_date = max(test_dates)
                    
                    # 平均合格率
                    pass_rates = [
                        record["pass_rate"] 
                        for record in stats_response.data 
                        if record.get("pass_rate") is not None
                    ]
                    if pass_rates:
                        device_with_stats.average_pass_rate = sum(pass_rates) / len(pass_rates)
                
                result.append(device_with_stats)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching devices with stats: {str(e)}")
            raise
    
    async def get_device_by_id(self, device_id: UUID) -> Optional[DeviceWithStats]:
        """根据ID获取设备"""
        try:
            response = self.db.table("devices")\
                .select("*")\
                .eq("id", str(device_id))\
                .single()\
                .execute()
            
            if not response.data:
                return None
            
            device = DeviceWithStats(**response.data)
            
            # 获取统计信息
            stats_response = self.db.table("test_records")\
                .select("id, test_date, pass_rate")\
                .eq("device_model", device.device_model)\
                .eq("is_deleted", False)\
                .execute()
            
            if stats_response.data:
                device.test_count = len(stats_response.data)
                
                test_dates = [record["test_date"] for record in stats_response.data]
                if test_dates:
                    device.last_test_date = max(test_dates)
                
                pass_rates = [
                    record["pass_rate"] 
                    for record in stats_response.data 
                    if record.get("pass_rate") is not None
                ]
                if pass_rates:
                    device.average_pass_rate = sum(pass_rates) / len(pass_rates)
            
            return device
            
        except Exception as e:
            logger.error(f"Error fetching device by ID: {str(e)}")
            return None
    
    async def get_device_by_model(self, device_model: str) -> Optional[DeviceWithStats]:
        """根据型号获取设备"""
        try:
            response = self.db.table("devices")\
                .select("*")\
                .eq("device_model", device_model)\
                .single()\
                .execute()
            
            if not response.data:
                return None
            
            device = DeviceWithStats(**response.data)
            
            # 获取统计信息
            stats_response = self.db.table("test_records")\
                .select("id, test_date, pass_rate")\
                .eq("device_model", device_model)\
                .eq("is_deleted", False)\
                .execute()
            
            if stats_response.data:
                device.test_count = len(stats_response.data)
                
                test_dates = [record["test_date"] for record in stats_response.data]
                if test_dates:
                    device.last_test_date = max(test_dates)
                
                pass_rates = [
                    record["pass_rate"] 
                    for record in stats_response.data 
                    if record.get("pass_rate") is not None
                ]
                if pass_rates:
                    device.average_pass_rate = sum(pass_rates) / len(pass_rates)
            
            return device
            
        except Exception as e:
            logger.error(f"Error fetching device by model: {str(e)}")
            return None
    
    async def create_device(self, device_data: DeviceCreate) -> Device:
        """创建设备"""
        try:
            data = device_data.dict()
            data["created_at"] = datetime.utcnow().isoformat()
            data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.db.table("devices")\
                .insert(data)\
                .execute()
            
            return Device(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error creating device: {str(e)}")
            raise
    
    async def create_devices_batch(self, devices: List[DeviceCreate]) -> List[Device]:
        """批量创建设备"""
        try:
            data_list = []
            for device in devices:
                data = device.dict()
                data["created_at"] = datetime.utcnow().isoformat()
                data["updated_at"] = datetime.utcnow().isoformat()
                data_list.append(data)
            
            response = self.db.table("devices")\
                .insert(data_list)\
                .execute()
            
            return [Device(**device) for device in response.data]
            
        except Exception as e:
            logger.error(f"Error creating devices batch: {str(e)}")
            raise
    
    async def update_device(
        self,
        device_id: UUID,
        update_data: DeviceUpdate
    ) -> Optional[Device]:
        """更新设备信息"""
        try:
            data = update_data.dict(exclude_unset=True)
            if data:
                data["updated_at"] = datetime.utcnow().isoformat()
                
                response = self.db.table("devices")\
                    .update(data)\
                    .eq("id", str(device_id))\
                    .execute()
                
                if response.data:
                    return Device(**response.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating device: {str(e)}")
            return None
    
    async def deactivate_device(self, device_id: UUID) -> bool:
        """停用设备"""
        try:
            response = self.db.table("devices")\
                .update({
                    "is_active": False,
                    "updated_at": datetime.utcnow().isoformat()
                })\
                .eq("id", str(device_id))\
                .execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deactivating device: {str(e)}")
            return False