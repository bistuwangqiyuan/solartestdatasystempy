"""
数据导入相关API端点
"""
from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from supabase import Client
from loguru import logger

from app.core.database import get_db
from app.core.auth import get_current_active_user, User
from app.core.config import settings
from app.models.import_record import (
    ImportRecord,
    ImportProgress
)
from app.services.import_service import ImportService
from app.utils.file_utils import validate_file_extension, save_upload_file

router = APIRouter()


@router.post("/excel", response_model=ImportRecord, status_code=status.HTTP_202_ACCEPTED)
async def import_excel_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    导入Excel文件
    
    支持的格式：.xlsx, .xls
    文件大小限制：100MB
    
    导入过程将在后台异步执行，返回导入记录ID用于查询进度
    """
    # 验证文件类型
    if not validate_file_extension(file.filename, settings.allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {', '.join(settings.allowed_extensions)}"
        )
    
    # 验证文件大小
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # 重置文件指针
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024:.0f}MB"
        )
    
    # 保存文件
    file_path = await save_upload_file(file, current_user.id)
    
    # 创建导入记录
    service = ImportService(db)
    import_record = await service.create_import_record(
        file_name=file.filename,
        file_size=file_size,
        file_path=file_path,
        user_id=current_user.id
    )
    
    # 添加后台任务处理导入
    background_tasks.add_task(
        service.process_import,
        import_record.id,
        file_path
    )
    
    return import_record


@router.get("/", response_model=List[ImportRecord])
async def get_import_records(
    skip: int = 0,
    limit: int = 100,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取导入记录列表
    """
    service = ImportService(db)
    records = await service.get_import_records(
        user_id=current_user.id if not current_user.is_superuser else None,
        skip=skip,
        limit=limit
    )
    return records


@router.get("/{import_id}", response_model=ImportRecord)
async def get_import_record(
    import_id: UUID,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取导入记录详情
    """
    service = ImportService(db)
    record = await service.get_import_record_by_id(import_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import record not found"
        )
    
    # 检查权限
    if not current_user.is_superuser and record.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return record


@router.get("/{import_id}/progress", response_model=ImportProgress)
async def get_import_progress(
    import_id: UUID,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取导入进度
    """
    service = ImportService(db)
    progress = await service.get_import_progress(import_id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import record not found"
        )
    
    return progress


@router.post("/{import_id}/retry", response_model=ImportRecord)
async def retry_import(
    import_id: UUID,
    background_tasks: BackgroundTasks,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    重试失败的导入
    """
    service = ImportService(db)
    record = await service.get_import_record_by_id(import_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import record not found"
        )
    
    # 检查权限
    if not current_user.is_superuser and record.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # 检查状态
    if record.import_status not in ["failed", "partial"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed or partial imports"
        )
    
    # 重置状态
    updated_record = await service.reset_import_status(import_id)
    
    # 添加后台任务重新处理
    background_tasks.add_task(
        service.process_import,
        import_id,
        record.file_path
    )
    
    return updated_record


@router.delete("/{import_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_import_record(
    import_id: UUID,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    删除导入记录
    
    同时删除关联的文件
    """
    service = ImportService(db)
    record = await service.get_import_record_by_id(import_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Import record not found"
        )
    
    # 检查权限
    if not current_user.is_superuser and record.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # 删除记录和文件
    success = await service.delete_import_record(import_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete import record"
        )
    
    return None