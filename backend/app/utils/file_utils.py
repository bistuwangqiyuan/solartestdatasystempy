"""
文件处理工具
"""
import os
import shutil
from typing import List
from datetime import datetime
from pathlib import Path
from fastapi import UploadFile
import aiofiles
from loguru import logger


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """验证文件扩展名"""
    if not filename:
        return False
    
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions


async def save_upload_file(
    upload_file: UploadFile,
    user_id: str,
    upload_dir: str = "uploads"
) -> str:
    """保存上传的文件"""
    try:
        # 创建上传目录
        base_dir = Path(upload_dir)
        user_dir = base_dir / user_id
        date_dir = user_dir / datetime.now().strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = Path(upload_file.filename).suffix
        safe_filename = f"{timestamp}_{upload_file.filename}"
        file_path = date_dir / safe_filename
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            content = await upload_file.read()
            await f.write(content)
        
        # 重置文件指针
        await upload_file.seek(0)
        
        logger.info(f"File saved: {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error saving upload file: {str(e)}")
        raise


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return False


def get_file_size(file_path: str) -> int:
    """获取文件大小"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


def clean_old_files(upload_dir: str = "uploads", days: int = 30) -> int:
    """清理旧文件"""
    try:
        count = 0
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    count += 1
        
        logger.info(f"Cleaned {count} old files")
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning old files: {str(e)}")
        return 0