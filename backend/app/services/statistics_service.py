"""
统计分析服务
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
import json
import pandas as pd
from supabase import Client
from loguru import logger

from app.models.test_record import TestRecordStatistics


class StatisticsService:
    """统计分析服务类"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def get_summary_statistics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        device_model: Optional[str] = None
    ) -> TestRecordStatistics:
        """获取统计摘要"""
        try:
            # 基础查询
            query = self.db.table("test_records").select("*").eq("is_deleted", False)
            
            # 应用过滤条件
            if start_date:
                query = query.gte("test_date", start_date.isoformat())
            if end_date:
                query = query.lte("test_date", end_date.isoformat())
            if device_model:
                query = query.eq("device_model", device_model)
            
            response = query.execute()
            records = response.data
            
            # 计算统计数据
            stats = TestRecordStatistics()
            stats.total_count = len(records)
            
            # 今日、本周、本月统计
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)
            
            for record in records:
                test_date = datetime.fromisoformat(record["test_date"]).date()
                
                if test_date == today:
                    stats.today_count += 1
                if test_date >= week_start:
                    stats.week_count += 1
                if test_date >= month_start:
                    stats.month_count += 1
                
                # 合格率统计
                if record.get("pass_rate") is not None:
                    if record["pass_rate"] >= 95:  # 假设95%以上为合格
                        stats.pass_count += 1
                    else:
                        stats.fail_count += 1
                
                # 设备分布
                if record.get("device_model"):
                    model = record["device_model"]
                    stats.device_distribution[model] = stats.device_distribution.get(model, 0) + 1
            
            # 计算平均合格率
            pass_rates = [r["pass_rate"] for r in records if r.get("pass_rate") is not None]
            if pass_rates:
                stats.average_pass_rate = sum(pass_rates) / len(pass_rates)
            
            # 获取日趋势数据（最近30天）
            stats.daily_trend = await self._get_daily_trend(30, device_model)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting summary statistics: {str(e)}")
            raise
    
    async def get_trends_data(
        self,
        period: str = "day",
        days: int = 30,
        device_model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取趋势数据"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.table("test_records")\
                .select("test_date, pass_rate")\
                .gte("test_date", start_date.isoformat())\
                .eq("is_deleted", False)
            
            if device_model:
                query = query.eq("device_model", device_model)
            
            response = query.execute()
            records = response.data
            
            # 转换为DataFrame进行分组统计
            if not records:
                return []
            
            df = pd.DataFrame(records)
            df['test_date'] = pd.to_datetime(df['test_date'])
            
            # 根据周期分组
            if period == "hour":
                df['period'] = df['test_date'].dt.floor('H')
            elif period == "day":
                df['period'] = df['test_date'].dt.date
            elif period == "week":
                df['period'] = df['test_date'].dt.to_period('W').apply(lambda r: r.start_time)
            elif period == "month":
                df['period'] = df['test_date'].dt.to_period('M').apply(lambda r: r.start_time)
            
            # 分组统计
            grouped = df.groupby('period').agg({
                'test_date': 'count',
                'pass_rate': 'mean'
            }).reset_index()
            
            grouped.columns = ['period', 'count', 'average_pass_rate']
            
            # 转换为字典列表
            result = []
            for _, row in grouped.iterrows():
                result.append({
                    'period': row['period'].isoformat() if hasattr(row['period'], 'isoformat') else str(row['period']),
                    'count': int(row['count']),
                    'average_pass_rate': float(row['average_pass_rate']) if pd.notna(row['average_pass_rate']) else 0
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting trends data: {str(e)}")
            raise
    
    async def get_distribution_data(
        self,
        metric: str = "voltage",
        bins: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        device_model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取数据分布"""
        try:
            query = self.db.table("test_records")\
                .select(f"{metric}")\
                .eq("is_deleted", False)\
                .not_.is_(metric, "null")
            
            if start_date:
                query = query.gte("test_date", start_date.isoformat())
            if end_date:
                query = query.lte("test_date", end_date.isoformat())
            if device_model:
                query = query.eq("device_model", device_model)
            
            response = query.execute()
            
            if not response.data:
                return []
            
            # 提取数值
            values = [r[metric] for r in response.data if r.get(metric) is not None]
            
            if not values:
                return []
            
            # 计算直方图
            df = pd.DataFrame({metric: values})
            hist, bin_edges = pd.cut(df[metric], bins=bins, retbins=True)
            value_counts = hist.value_counts().sort_index()
            
            # 构建结果
            result = []
            for i, (interval, count) in enumerate(value_counts.items()):
                result.append({
                    'range': f"{interval.left:.2f}-{interval.right:.2f}",
                    'min': float(interval.left),
                    'max': float(interval.right),
                    'count': int(count),
                    'percentage': float(count / len(values) * 100)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting distribution data: {str(e)}")
            raise
    
    async def get_realtime_statistics(self) -> Dict[str, Any]:
        """获取实时统计数据"""
        try:
            now = datetime.now()
            today = now.date()
            hour_ago = now - timedelta(hours=1)
            
            # 今日测试数
            today_query = self.db.table("test_records")\
                .select("id", count="exact")\
                .gte("test_date", today.isoformat())\
                .eq("is_deleted", False)
            today_response = today_query.execute()
            today_count = today_response.count or 0
            
            # 最近一小时测试数
            hour_query = self.db.table("test_records")\
                .select("id", count="exact")\
                .gte("test_date", hour_ago.isoformat())\
                .eq("is_deleted", False)
            hour_response = hour_query.execute()
            hour_count = hour_response.count or 0
            
            # 今日合格率
            pass_query = self.db.table("test_records")\
                .select("pass_rate")\
                .gte("test_date", today.isoformat())\
                .eq("is_deleted", False)\
                .not_.is_("pass_rate", "null")
            pass_response = pass_query.execute()
            
            today_pass_rate = 0
            if pass_response.data:
                pass_rates = [r["pass_rate"] for r in pass_response.data]
                today_pass_rate = sum(pass_rates) / len(pass_rates)
            
            # 活跃设备数
            device_query = self.db.table("test_records")\
                .select("device_model")\
                .gte("test_date", today.isoformat())\
                .eq("is_deleted", False)
            device_response = device_query.execute()
            
            active_devices = len(set(r["device_model"] for r in device_response.data if r.get("device_model")))
            
            # 最近测试记录
            recent_query = self.db.table("test_records")\
                .select("id, file_name, test_date, device_model, pass_rate")\
                .eq("is_deleted", False)\
                .order("test_date", desc=True)\
                .limit(10)
            recent_response = recent_query.execute()
            
            return {
                "current_time": now.isoformat(),
                "today_count": today_count,
                "hour_count": hour_count,
                "today_pass_rate": round(today_pass_rate, 2),
                "active_devices": active_devices,
                "recent_tests": recent_response.data
            }
            
        except Exception as e:
            logger.error(f"Error getting realtime statistics: {str(e)}")
            raise
    
    async def get_device_comparison(
        self,
        device_models: List[str],
        metric: str = "pass_rate",
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """设备对比分析"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            result = []
            
            for model in device_models:
                query = self.db.table("test_records")\
                    .select("*")\
                    .eq("device_model", model)\
                    .gte("test_date", start_date.isoformat())\
                    .eq("is_deleted", False)
                
                response = query.execute()
                records = response.data
                
                if not records:
                    result.append({
                        "device_model": model,
                        "metric": metric,
                        "value": 0,
                        "count": 0
                    })
                    continue
                
                # 计算指标
                if metric == "pass_rate":
                    pass_rates = [r["pass_rate"] for r in records if r.get("pass_rate") is not None]
                    value = sum(pass_rates) / len(pass_rates) if pass_rates else 0
                elif metric == "avg_voltage":
                    voltages = [r["voltage"] for r in records if r.get("voltage") is not None]
                    value = sum(voltages) / len(voltages) if voltages else 0
                elif metric == "avg_current":
                    currents = [r["current"] for r in records if r.get("current") is not None]
                    value = sum(currents) / len(currents) if currents else 0
                elif metric == "test_count":
                    value = len(records)
                else:
                    value = 0
                
                result.append({
                    "device_model": model,
                    "metric": metric,
                    "value": round(value, 2),
                    "count": len(records)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting device comparison: {str(e)}")
            raise
    
    async def get_quality_metrics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """获取质量指标"""
        try:
            query = self.db.table("test_records")\
                .select("*")\
                .eq("is_deleted", False)
            
            if start_date:
                query = query.gte("test_date", start_date.isoformat())
            if end_date:
                query = query.lte("test_date", end_date.isoformat())
            
            response = query.execute()
            records = response.data
            
            if not records:
                return {
                    "total_tests": 0,
                    "pass_rate": 0,
                    "cpk": 0,
                    "ppm": 0,
                    "first_pass_yield": 0
                }
            
            # 基础统计
            total_tests = len(records)
            pass_rates = [r["pass_rate"] for r in records if r.get("pass_rate") is not None]
            average_pass_rate = sum(pass_rates) / len(pass_rates) if pass_rates else 0
            
            # 计算PPM (每百万缺陷数)
            fail_count = sum(1 for r in records if r.get("pass_rate", 100) < 95)
            ppm = (fail_count / total_tests) * 1000000 if total_tests > 0 else 0
            
            # 简化的CPK计算（需要更多数据才能准确计算）
            cpk = 1.33 if average_pass_rate >= 95 else 0.67
            
            return {
                "total_tests": total_tests,
                "pass_rate": round(average_pass_rate, 2),
                "cpk": round(cpk, 2),
                "ppm": round(ppm, 0),
                "first_pass_yield": round(average_pass_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting quality metrics: {str(e)}")
            raise
    
    async def export_statistics(
        self,
        format: str = "json",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_details: bool = False
    ) -> Any:
        """导出统计数据"""
        try:
            # 获取统计数据
            stats = await self.get_summary_statistics(start_date, end_date)
            quality_metrics = await self.get_quality_metrics(start_date, end_date)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "summary": stats.dict(),
                "quality_metrics": quality_metrics
            }
            
            if include_details:
                # 获取详细记录
                query = self.db.table("test_records")\
                    .select("*")\
                    .eq("is_deleted", False)
                
                if start_date:
                    query = query.gte("test_date", start_date.isoformat())
                if end_date:
                    query = query.lte("test_date", end_date.isoformat())
                
                response = query.execute()
                export_data["details"] = response.data
            
            # 根据格式返回数据
            if format == "json":
                return export_data
            elif format == "csv":
                # 转换为CSV（简化版）
                df = pd.DataFrame([export_data["summary"]])
                csv_path = f"/tmp/statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(csv_path, index=False)
                return csv_path
            elif format == "excel":
                # 转换为Excel（简化版）
                with pd.ExcelWriter(f"/tmp/statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx") as writer:
                    pd.DataFrame([export_data["summary"]]).to_excel(writer, sheet_name="Summary", index=False)
                    pd.DataFrame([quality_metrics]).to_excel(writer, sheet_name="Quality", index=False)
                return writer.path
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting statistics: {str(e)}")
            raise
    
    async def _get_daily_trend(self, days: int, device_model: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取日趋势数据（内部方法）"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.table("test_records")\
                .select("test_date, pass_rate")\
                .gte("test_date", start_date.isoformat())\
                .eq("is_deleted", False)
            
            if device_model:
                query = query.eq("device_model", device_model)
            
            response = query.execute()
            
            if not response.data:
                return []
            
            # 按日期分组
            daily_data = {}
            for record in response.data:
                date = datetime.fromisoformat(record["test_date"]).date()
                if date not in daily_data:
                    daily_data[date] = {"count": 0, "pass_rates": []}
                
                daily_data[date]["count"] += 1
                if record.get("pass_rate") is not None:
                    daily_data[date]["pass_rates"].append(record["pass_rate"])
            
            # 构建结果
            result = []
            current_date = start_date
            while current_date <= end_date:
                if current_date in daily_data:
                    data = daily_data[current_date]
                    avg_pass_rate = sum(data["pass_rates"]) / len(data["pass_rates"]) if data["pass_rates"] else 0
                    result.append({
                        "date": current_date.isoformat(),
                        "count": data["count"],
                        "pass_rate": round(avg_pass_rate, 2)
                    })
                else:
                    result.append({
                        "date": current_date.isoformat(),
                        "count": 0,
                        "pass_rate": 0
                    })
                
                current_date += timedelta(days=1)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting daily trend: {str(e)}")
            return []