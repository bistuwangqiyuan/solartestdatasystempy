"""
数据导入服务
"""
import os
import asyncio
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import pandas as pd
from supabase import Client
from loguru import logger

from app.models.import_record import (
    ImportRecord,
    ImportRecordCreate,
    ImportRecordUpdate,
    ImportProgress
)
from app.models.test_record import TestRecordCreate, TestDetailCreate
from app.services.test_record_service import TestRecordService
from app.utils.excel_parser import ExcelParser


class ImportService:
    """数据导入服务类"""
    
    def __init__(self, db: Client):
        self.db = db
        self.progress_cache = {}  # 简单的进度缓存
    
    async def create_import_record(
        self,
        file_name: str,
        file_size: int,
        file_path: str,
        user_id: str
    ) -> ImportRecord:
        """创建导入记录"""
        try:
            data = {
                "file_name": file_name,
                "file_size": file_size,
                "file_path": file_path,
                "import_status": "pending",
                "created_by": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.db.table("import_records")\
                .insert(data)\
                .execute()
            
            return ImportRecord(**response.data[0])
            
        except Exception as e:
            logger.error(f"Error creating import record: {str(e)}")
            raise
    
    async def get_import_records(
        self,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ImportRecord]:
        """获取导入记录列表"""
        try:
            query = self.db.table("import_records").select("*")
            
            if user_id:
                query = query.eq("created_by", user_id)
            
            query = query.order("created_at", desc=True)
            query = query.range(skip, skip + limit - 1)
            
            response = query.execute()
            
            return [ImportRecord(**record) for record in response.data]
            
        except Exception as e:
            logger.error(f"Error fetching import records: {str(e)}")
            raise
    
    async def get_import_record_by_id(self, import_id: UUID) -> Optional[ImportRecord]:
        """根据ID获取导入记录"""
        try:
            response = self.db.table("import_records")\
                .select("*")\
                .eq("id", str(import_id))\
                .single()\
                .execute()
            
            if response.data:
                return ImportRecord(**response.data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching import record by ID: {str(e)}")
            return None
    
    async def update_import_status(
        self,
        import_id: UUID,
        status: str,
        **kwargs
    ) -> Optional[ImportRecord]:
        """更新导入状态"""
        try:
            data = {
                "import_status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            data.update(kwargs)
            
            response = self.db.table("import_records")\
                .update(data)\
                .eq("id", str(import_id))\
                .execute()
            
            if response.data:
                return ImportRecord(**response.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating import status: {str(e)}")
            return None
    
    async def process_import(self, import_id: UUID, file_path: str):
        """处理导入任务"""
        try:
            # 更新状态为处理中
            await self.update_import_status(
                import_id,
                "processing",
                started_at=datetime.utcnow().isoformat()
            )
            
            # 更新进度
            self.progress_cache[str(import_id)] = ImportProgress(
                import_id=import_id,
                status="processing",
                progress=0,
                message="开始解析文件..."
            )
            
            # 解析Excel文件
            parser = ExcelParser()
            parse_result = await parser.parse_file(file_path)
            
            if not parse_result["success"]:
                # 解析失败
                await self.update_import_status(
                    import_id,
                    "failed",
                    error_message=parse_result.get("error", "文件解析失败"),
                    completed_at=datetime.utcnow().isoformat()
                )
                return
            
            # 获取解析的数据
            records_data = parse_result["records"]
            details_data = parse_result["details"]
            total_records = len(records_data)
            
            # 更新进度
            self.progress_cache[str(import_id)] = ImportProgress(
                import_id=import_id,
                status="processing",
                progress=20,
                total_records=total_records,
                message=f"已解析 {total_records} 条记录，开始导入..."
            )
            
            # 创建测试记录服务
            record_service = TestRecordService(self.db)
            
            success_count = 0
            failed_count = 0
            
            # 批量导入记录
            for i, record_data in enumerate(records_data):
                try:
                    # 创建测试记录
                    record = TestRecordCreate(**record_data)
                    new_record = await record_service.create_record(
                        record,
                        user_id=str(import_id)  # 临时使用import_id作为用户ID
                    )
                    
                    # 导入详细数据
                    if str(new_record.id) in details_data:
                        details = [
                            TestDetailCreate(
                                test_record_id=new_record.id,
                                **detail
                            )
                            for detail in details_data[str(new_record.id)]
                        ]
                        await record_service.create_details(details)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error importing record: {str(e)}")
                    failed_count += 1
                
                # 更新进度
                progress = 20 + (i + 1) / total_records * 70
                self.progress_cache[str(import_id)] = ImportProgress(
                    import_id=import_id,
                    status="processing",
                    progress=progress,
                    current_record=i + 1,
                    total_records=total_records,
                    message=f"正在导入第 {i + 1}/{total_records} 条记录..."
                )
            
            # 更新最终状态
            final_status = "completed" if failed_count == 0 else "partial"
            await self.update_import_status(
                import_id,
                final_status,
                total_records=total_records,
                success_records=success_count,
                failed_records=failed_count,
                completed_at=datetime.utcnow().isoformat()
            )
            
            # 更新进度缓存
            self.progress_cache[str(import_id)] = ImportProgress(
                import_id=import_id,
                status=final_status,
                progress=100,
                current_record=total_records,
                total_records=total_records,
                message=f"导入完成：成功 {success_count} 条，失败 {failed_count} 条"
            )
            
        except Exception as e:
            logger.error(f"Error processing import: {str(e)}")
            await self.update_import_status(
                import_id,
                "failed",
                error_message=str(e),
                completed_at=datetime.utcnow().isoformat()
            )
    
    async def get_import_progress(self, import_id: UUID) -> Optional[ImportProgress]:
        """获取导入进度"""
        # 先从缓存获取
        if str(import_id) in self.progress_cache:
            return self.progress_cache[str(import_id)]
        
        # 从数据库获取
        record = await self.get_import_record_by_id(import_id)
        if record:
            progress = 0
            if record.import_status == "completed":
                progress = 100
            elif record.import_status == "processing":
                if record.total_records > 0 and record.success_records is not None:
                    progress = (record.success_records / record.total_records) * 100
            
            return ImportProgress(
                import_id=import_id,
                status=record.import_status,
                progress=progress,
                current_record=record.success_records or 0,
                total_records=record.total_records,
                message=record.error_message if record.import_status == "failed" else None
            )
        
        return None
    
    async def reset_import_status(self, import_id: UUID) -> Optional[ImportRecord]:
        """重置导入状态"""
        return await self.update_import_status(
            import_id,
            "pending",
            error_message=None,
            started_at=None,
            completed_at=None,
            total_records=0,
            success_records=0,
            failed_records=0
        )
    
    async def delete_import_record(self, import_id: UUID) -> bool:
        """删除导入记录"""
        try:
            # 获取记录以获取文件路径
            record = await self.get_import_record_by_id(import_id)
            if not record:
                return False
            
            # 删除文件
            if record.file_path and os.path.exists(record.file_path):
                try:
                    os.remove(record.file_path)
                except Exception as e:
                    logger.error(f"Error deleting file: {str(e)}")
            
            # 删除数据库记录
            response = self.db.table("import_records")\
                .delete()\
                .eq("id", str(import_id))\
                .execute()
            
            # 清理进度缓存
            if str(import_id) in self.progress_cache:
                del self.progress_cache[str(import_id)]
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting import record: {str(e)}")
            return False