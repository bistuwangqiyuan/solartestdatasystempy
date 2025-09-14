"""
测试记录相关API端点
"""
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client
from loguru import logger

from app.core.database import get_db
from app.core.auth import get_current_active_user, User
from app.models.test_record import (
    TestRecord,
    TestRecordCreate,
    TestRecordUpdate,
    TestRecordWithDetails,
    TestRecordFilter,
    TestDetail,
    TestDetailCreate
)
from app.services.test_record_service import TestRecordService

router = APIRouter()


@router.get("/", response_model=List[TestRecord])
async def get_test_records(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", regex="^(asc|desc)$"),
    filter: TestRecordFilter = Depends(),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取测试记录列表
    
    支持分页、排序和筛选
    """
    service = TestRecordService(db)
    records = await service.get_records(
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        filter_params=filter
    )
    return records


@router.get("/{record_id}", response_model=TestRecordWithDetails)
async def get_test_record(
    record_id: UUID,
    include_details: bool = Query(default=True),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取单个测试记录详情
    
    可选择是否包含测试详细数据
    """
    service = TestRecordService(db)
    record = await service.get_record_by_id(record_id, include_details)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test record not found"
        )
    
    return record


@router.post("/", response_model=TestRecord, status_code=status.HTTP_201_CREATED)
async def create_test_record(
    record: TestRecordCreate,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    创建测试记录
    """
    service = TestRecordService(db)
    new_record = await service.create_record(record, current_user.id)
    return new_record


@router.put("/{record_id}", response_model=TestRecord)
async def update_test_record(
    record_id: UUID,
    record_update: TestRecordUpdate,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    更新测试记录
    """
    service = TestRecordService(db)
    updated_record = await service.update_record(record_id, record_update)
    
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test record not found"
        )
    
    return updated_record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_record(
    record_id: UUID,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    删除测试记录（软删除）
    """
    service = TestRecordService(db)
    success = await service.delete_record(record_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test record not found"
        )
    
    return None


@router.get("/{record_id}/details", response_model=List[TestDetail])
async def get_test_details(
    record_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=1000, ge=1, le=10000),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取测试详细数据
    """
    service = TestRecordService(db)
    details = await service.get_record_details(record_id, skip, limit)
    return details


@router.post("/{record_id}/details", response_model=List[TestDetail], status_code=status.HTTP_201_CREATED)
async def create_test_details(
    record_id: UUID,
    details: List[TestDetailCreate],
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    批量创建测试详细数据
    """
    service = TestRecordService(db)
    
    # 验证记录是否存在
    record = await service.get_record_by_id(record_id, include_details=False)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test record not found"
        )
    
    # 确保所有详情都关联到正确的记录
    for detail in details:
        detail.test_record_id = record_id
    
    new_details = await service.create_details(details)
    return new_details


@router.post("/batch", response_model=List[TestRecord], status_code=status.HTTP_201_CREATED)
async def create_test_records_batch(
    records: List[TestRecordCreate],
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    批量创建测试记录
    """
    service = TestRecordService(db)
    new_records = await service.create_records_batch(records, current_user.id)
    return new_records