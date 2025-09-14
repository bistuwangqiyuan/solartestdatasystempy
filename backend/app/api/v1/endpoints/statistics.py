"""
统计分析相关API端点
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from supabase import Client

from app.core.database import get_db
from app.core.auth import get_current_active_user, User
from app.models.test_record import TestRecordStatistics
from app.services.statistics_service import StatisticsService

router = APIRouter()


@router.get("/summary", response_model=TestRecordStatistics)
async def get_statistics_summary(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    device_model: Optional[str] = Query(None, description="设备型号"),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取统计摘要
    
    包括总数、合格率、设备分布等统计信息
    """
    service = StatisticsService(db)
    stats = await service.get_summary_statistics(
        start_date=start_date,
        end_date=end_date,
        device_model=device_model
    )
    return stats


@router.get("/trends")
async def get_trends_data(
    period: str = Query("day", regex="^(hour|day|week|month)$", description="统计周期"),
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    device_model: Optional[str] = Query(None, description="设备型号"),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取趋势数据
    
    返回指定时间段内的测试数量、合格率等趋势
    """
    service = StatisticsService(db)
    trends = await service.get_trends_data(
        period=period,
        days=days,
        device_model=device_model
    )
    return trends


@router.get("/distribution")
async def get_distribution_data(
    metric: str = Query("voltage", regex="^(voltage|current|power|resistance)$", description="统计指标"),
    bins: int = Query(10, ge=5, le=50, description="分组数量"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    device_model: Optional[str] = Query(None, description="设备型号"),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取数据分布
    
    返回指定指标的分布情况
    """
    service = StatisticsService(db)
    distribution = await service.get_distribution_data(
        metric=metric,
        bins=bins,
        start_date=start_date,
        end_date=end_date,
        device_model=device_model
    )
    return distribution


@router.get("/realtime")
async def get_realtime_statistics(
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取实时统计数据
    
    用于数据大屏展示
    """
    service = StatisticsService(db)
    realtime_stats = await service.get_realtime_statistics()
    return realtime_stats


@router.get("/device-comparison")
async def get_device_comparison(
    device_models: List[str] = Query(..., description="要比较的设备型号列表"),
    metric: str = Query("pass_rate", regex="^(pass_rate|avg_voltage|avg_current|test_count)$"),
    days: int = Query(30, ge=1, le=365),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    设备对比分析
    
    比较不同设备型号的性能指标
    """
    service = StatisticsService(db)
    comparison = await service.get_device_comparison(
        device_models=device_models,
        metric=metric,
        days=days
    )
    return comparison


@router.get("/quality-metrics")
async def get_quality_metrics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    获取质量指标
    
    包括CPK、PPM、合格率等质量管理指标
    """
    service = StatisticsService(db)
    metrics = await service.get_quality_metrics(
        start_date=start_date,
        end_date=end_date
    )
    return metrics


@router.get("/export")
async def export_statistics(
    format: str = Query("json", regex="^(json|csv|excel)$", description="导出格式"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    include_details: bool = Query(False, description="是否包含详细数据"),
    db: Client = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    导出统计数据
    
    支持JSON、CSV、Excel格式
    """
    service = StatisticsService(db)
    export_data = await service.export_statistics(
        format=format,
        start_date=start_date,
        end_date=end_date,
        include_details=include_details
    )
    
    # 根据格式设置响应头
    if format == "csv":
        return FileResponse(
            export_data,
            media_type="text/csv",
            filename=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    elif format == "excel":
        return FileResponse(
            export_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
    else:
        return export_data