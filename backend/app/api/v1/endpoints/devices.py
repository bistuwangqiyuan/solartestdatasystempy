"""
设备管理相关API端点
"""
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client
from loguru import logger

from app.core.database import get_db
from app.core.auth import get_current_active_user, User, require_admin
from app.models.device import (
    Device,
    DeviceCreate,
    DeviceUpdate,
    DeviceWithStats
)
from app.services.device_service import DeviceService

router = APIRouter()


@router.get("/", response_model=List[Device])
async def get_devices(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    manufacturer: Optional[str] = None,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取设备列表
    """
    service = DeviceService(db)
    devices = await service.get_devices(
        skip=skip,
        limit=limit,
        is_active=is_active,
        manufacturer=manufacturer
    )
    return devices


@router.get("/with-stats", response_model=List[DeviceWithStats])
async def get_devices_with_stats(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取设备列表（包含统计信息）
    """
    service = DeviceService(db)
    devices = await service.get_devices_with_stats(skip=skip, limit=limit)
    return devices


@router.get("/{device_id}", response_model=DeviceWithStats)
async def get_device(
    device_id: UUID,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取设备详情
    """
    service = DeviceService(db)
    device = await service.get_device_by_id(device_id)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return device


@router.get("/model/{device_model}", response_model=DeviceWithStats)
async def get_device_by_model(
    device_model: str,
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    根据型号获取设备
    """
    service = DeviceService(db)
    device = await service.get_device_by_model(device_model)
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return device


@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
async def create_device(
    device: DeviceCreate,
    db: Client = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    创建设备（需要管理员权限）
    """
    service = DeviceService(db)
    
    # 检查设备型号是否已存在
    existing = await service.get_device_by_model(device.device_model)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device model already exists"
        )
    
    new_device = await service.create_device(device)
    return new_device


@router.put("/{device_id}", response_model=Device)
async def update_device(
    device_id: UUID,
    device_update: DeviceUpdate,
    db: Client = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    更新设备信息（需要管理员权限）
    """
    service = DeviceService(db)
    updated_device = await service.update_device(device_id, device_update)
    
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return updated_device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID,
    db: Client = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    删除设备（需要管理员权限）
    
    设备将被标记为不活跃，而不是物理删除
    """
    service = DeviceService(db)
    success = await service.deactivate_device(device_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return None


@router.post("/batch", response_model=List[Device], status_code=status.HTTP_201_CREATED)
async def create_devices_batch(
    devices: List[DeviceCreate],
    db: Client = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Any:
    """
    批量创建设备（需要管理员权限）
    """
    service = DeviceService(db)
    new_devices = await service.create_devices_batch(devices)
    return new_devices