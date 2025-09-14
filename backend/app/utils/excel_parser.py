"""
Excel文件解析器
"""
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from loguru import logger


class ExcelParser:
    """Excel文件解析器"""
    
    def __init__(self):
        self.voltage_pattern = re.compile(r'(\d+\.?\d*)\s*V')
        self.current_pattern = re.compile(r'(\d+\.?\d*)\s*A')
        self.resistance_pattern = re.compile(r'(\d+\.?\d*)\s*Ω')
        self.power_pattern = re.compile(r'(\d+\.?\d*)\s*W')
    
    async def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析Excel文件"""
        try:
            # 从文件名提取参数
            file_info = self._parse_filename(file_path)
            
            # 读取Excel文件
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # 清理数据
            df = self._clean_dataframe(df)
            
            # 解析数据
            records = []
            details = {}
            
            # 创建主记录
            record = {
                "file_name": Path(file_path).name,
                "test_date": file_info.get("test_date", datetime.now()),
                "voltage": file_info.get("voltage"),
                "current": file_info.get("current"),
                "resistance": file_info.get("resistance"),
                "power": file_info.get("power"),
                "device_model": file_info.get("device_model", "Unknown"),
                "sample_count": len(df),
                "raw_data": {
                    "columns": df.columns.tolist(),
                    "shape": df.shape
                }
            }
            
            # 计算合格率（示例逻辑）
            if "pass" in df.columns.str.lower():
                pass_col = df.columns[df.columns.str.lower().str.contains("pass")][0]
                pass_count = df[pass_col].sum()
                record["pass_rate"] = (pass_count / len(df)) * 100 if len(df) > 0 else 0
            
            records.append(record)
            
            # 解析详细数据
            detail_list = []
            for idx, row in df.iterrows():
                detail = self._parse_detail_row(row, idx)
                if detail:
                    detail_list.append(detail)
            
            # 使用临时ID关联详情
            details["temp_id"] = detail_list
            
            return {
                "success": True,
                "records": records,
                "details": details
            }
            
        except Exception as e:
            logger.error(f"Error parsing Excel file: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "records": [],
                "details": {}
            }
    
    def _parse_filename(self, file_path: str) -> Dict[str, Any]:
        """从文件名解析参数"""
        filename = Path(file_path).stem
        result = {}
        
        # 解析电压
        voltage_match = self.voltage_pattern.search(filename)
        if voltage_match:
            result["voltage"] = float(voltage_match.group(1))
        
        # 解析电流
        current_match = self.current_pattern.search(filename)
        if current_match:
            result["current"] = float(current_match.group(1))
        
        # 解析电阻
        resistance_match = self.resistance_pattern.search(filename)
        if resistance_match:
            result["resistance"] = float(resistance_match.group(1))
        
        # 解析功率
        power_match = self.power_pattern.search(filename)
        if power_match:
            result["power"] = float(power_match.group(1))
        
        # 解析日期
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
        date_match = date_pattern.search(filename)
        if date_match:
            try:
                result["test_date"] = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            except:
                result["test_date"] = datetime.now()
        else:
            result["test_date"] = datetime.now()
        
        # 解析设备型号（简化逻辑）
        if "data_detail" in filename:
            parts = filename.split("_")
            if len(parts) > 2:
                result["device_model"] = f"PV-Shutoff-{parts[2]}"
        
        return result
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理数据框"""
        # 删除全空行
        df = df.dropna(how='all')
        
        # 删除全空列
        df = df.dropna(axis=1, how='all')
        
        # 标准化列名
        df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
        
        # 转换数据类型
        for col in df.columns:
            if df[col].dtype == 'object':
                # 尝试转换为数值
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
        
        return df
    
    def _parse_detail_row(self, row: pd.Series, index: int) -> Optional[Dict[str, Any]]:
        """解析详细数据行"""
        try:
            detail = {
                "time_point": index * 0.1,  # 假设每行代表0.1秒
            }
            
            # 查找电压列
            voltage_cols = [col for col in row.index if 'voltage' in col or 'v' in col.lower()]
            if voltage_cols:
                detail["voltage_value"] = float(row[voltage_cols[0]]) if pd.notna(row[voltage_cols[0]]) else None
            
            # 查找电流列
            current_cols = [col for col in row.index if 'current' in col or 'a' in col.lower()]
            if current_cols:
                detail["current_value"] = float(row[current_cols[0]]) if pd.notna(row[current_cols[0]]) else None
            
            # 计算功率
            if detail.get("voltage_value") and detail.get("current_value"):
                detail["power_value"] = detail["voltage_value"] * detail["current_value"]
            
            # 计算电阻
            if detail.get("voltage_value") and detail.get("current_value") and detail["current_value"] != 0:
                detail["resistance_value"] = detail["voltage_value"] / detail["current_value"]
            
            # 温度和湿度（如果存在）
            temp_cols = [col for col in row.index if 'temp' in col.lower()]
            if temp_cols:
                detail["temperature"] = float(row[temp_cols[0]]) if pd.notna(row[temp_cols[0]]) else None
            
            humid_cols = [col for col in row.index if 'humid' in col.lower()]
            if humid_cols:
                detail["humidity"] = float(row[humid_cols[0]]) if pd.notna(row[humid_cols[0]]) else None
            
            return detail
            
        except Exception as e:
            logger.error(f"Error parsing detail row: {str(e)}")
            return None
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证数据有效性"""
        errors = []
        warnings = []
        
        # 检查必要列
        required_cols = ['voltage', 'current']
        missing_cols = [col for col in required_cols if col not in df.columns.str.lower()]
        if missing_cols:
            warnings.append(f"Missing columns: {', '.join(missing_cols)}")
        
        # 检查数据范围
        if 'voltage' in df.columns:
            invalid_voltage = df[(df['voltage'] < 0) | (df['voltage'] > 1000)].shape[0]
            if invalid_voltage > 0:
                errors.append(f"{invalid_voltage} rows with invalid voltage values")
        
        if 'current' in df.columns:
            invalid_current = df[(df['current'] < 0) | (df['current'] > 100)].shape[0]
            if invalid_current > 0:
                errors.append(f"{invalid_current} rows with invalid current values")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }