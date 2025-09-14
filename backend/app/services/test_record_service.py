"""
测试记录服务
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import Client
from loguru import logger

from app.models.test_record import (
    TestRecord,
    TestRecordCreate,
    TestRecordUpdate,
    TestRecordFilter,
    TestRecordWithDetails,
    TestDetail,
    TestDetailCreate
)


class TestRecordService:
    """测试记录服务类"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def get_records(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        filter_params: Optional[TestRecordFilter] = None
    ) -> List[TestRecord]:
        """获取测试记录列表"""
        try:
            query = self.db.table("test_records").select("*")
            
            # 应用过滤条件
            if filter_params:
                if filter_params.start_date:
                    query = query.gte("test_date", filter_params.start_date.isoformat())
                if filter_params.end_date:
                    query = query.lte("test_date", filter_params.end_date.isoformat())
                if filter_params.device_model:
                    query = query.eq("device_model", filter_params.device_model)
                if filter_params.batch_number:
                    query = query.eq("batch_number", filter_params.batch_number)
                if filter_params.operator:
                    query = query.eq("operator", filter_params.operator)
                if filter_params.status:
                    query = query.eq("status", filter_params.status)
                if filter_params.min_voltage is not None:
                    query = query.gte("voltage", filter_params.min_voltage)
                if filter_params.max_voltage is not None:
                    query = query.lte("voltage", filter_params.max_voltage)
                if filter_params.min_current is not None:
                    query = query.gte("current", filter_params.min_current)
                if filter_params.max_current is not None:
                    query = query.lte("current", filter_params.max_current)
                if filter_params.keyword:
                    query = query.or_(
                        f"file_name.ilike.%{filter_params.keyword}%,"
                        f"notes.ilike.%{filter_params.keyword}%"
                    )
            
            # 排除已删除的记录
            query = query.eq("is_deleted", False)
            
            # 排序
            query = query.order(sort_by, desc=(sort_order == "desc"))
            
            # 分页
            query = query.range(skip, skip + limit - 1)
            
            response = query.execute()
            
            return [TestRecord(**record) for record in response.data]
            
        except Exception as e:
            logger.error(f"Error fetching test records: {str(e)}")
            raise
    
    async def get_record_by_id(
        self,
        record_id: UUID,
        include_details: bool = True
    ) -> Optional[TestRecordWithDetails]:
        """根据ID获取测试记录"""
        try:
            # 获取主记录
            response = self.db.table("test_records")\
                .select("*")\
                .eq("id", str(record_id))\
                .eq("is_deleted", False)\
                .single()\
                .execute()
            
            if not response.data:
                return None
            
            record = TestRecordWithDetails(**response.data)
            
            # 获取详细数据
            if include_details:
                details_response = self.db.table("test_details")\
                    .select("*")\
                    .eq("test_record_id", str(record_id))\
                    .order("time_point")\
                    .execute()
                
                record.details = [TestDetail(**detail) for detail in details_response.data]
                record.detail_count = len(record.details)
            
            return record
            
        except Exception as e:
            logger.error(f"Error fetching test record by ID: {str(e)}")
            return None
    
    async def create_record(
        self,
        record_data: TestRecordCreate,
        user_id: str
    ) -> TestRecord:
        """创建测试记录"""
        try:
            data = record_data.dict()
            data["created_by"] = user_id
            data["created_at"] = datetime.utcnow().isoformat()
            data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.db.table("test_records")\
                .insert(data)\
                .execute()
            
            return TestRecord(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error creating test record: {str(e)}")
            raise
    
    async def create_records_batch(
        self,
        records: List[TestRecordCreate],
        user_id: str
    ) -> List[TestRecord]:
        """批量创建测试记录"""
        try:
            data_list = []
            for record in records:
                data = record.dict()
                data["created_by"] = user_id
                data["created_at"] = datetime.utcnow().isoformat()
                data["updated_at"] = datetime.utcnow().isoformat()
                data_list.append(data)
            
            response = self.db.table("test_records")\
                .insert(data_list)\
                .execute()
            
            return [TestRecord(**record) for record in response.data]
            
        except Exception as e:
            logger.error(f"Error creating test records batch: {str(e)}")
            raise
    
    async def update_record(
        self,
        record_id: UUID,
        update_data: TestRecordUpdate
    ) -> Optional[TestRecord]:
        """更新测试记录"""
        try:
            # 准备更新数据
            data = update_data.dict(exclude_unset=True)
            if data:
                data["updated_at"] = datetime.utcnow().isoformat()
                
                response = self.db.table("test_records")\
                    .update(data)\
                    .eq("id", str(record_id))\
                    .eq("is_deleted", False)\
                    .execute()
                
                if response.data:
                    return TestRecord(**response.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating test record: {str(e)}")
            return None
    
    async def delete_record(self, record_id: UUID) -> bool:
        """删除测试记录（软删除）"""
        try:
            response = self.db.table("test_records")\
                .update({
                    "is_deleted": True,
                    "updated_at": datetime.utcnow().isoformat()
                })\
                .eq("id", str(record_id))\
                .execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting test record: {str(e)}")
            return False
    
    async def get_record_details(
        self,
        record_id: UUID,
        skip: int = 0,
        limit: int = 1000
    ) -> List[TestDetail]:
        """获取测试详细数据"""
        try:
            response = self.db.table("test_details")\
                .select("*")\
                .eq("test_record_id", str(record_id))\
                .order("time_point")\
                .range(skip, skip + limit - 1)\
                .execute()
            
            return [TestDetail(**detail) for detail in response.data]
            
        except Exception as e:
            logger.error(f"Error fetching test details: {str(e)}")
            raise
    
    async def create_details(
        self,
        details: List[TestDetailCreate]
    ) -> List[TestDetail]:
        """批量创建测试详细数据"""
        try:
            data_list = [detail.dict() for detail in details]
            
            response = self.db.table("test_details")\
                .insert(data_list)\
                .execute()
            
            return [TestDetail(**detail) for detail in response.data]
            
        except Exception as e:
            logger.error(f"Error creating test details: {str(e)}")
            raise