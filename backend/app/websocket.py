"""
WebSocket连接管理
"""
from typing import List, Dict, Any
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from loguru import logger
import asyncio

from app.core.auth import get_current_user
from app.services.statistics_service import StatisticsService
from app.core.database import get_db

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """建立连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"WebSocket connected: {user_id or 'anonymous'}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        """断开连接"""
        self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected: {user_id or 'anonymous'}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """发送个人消息"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """广播消息"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
    
    async def broadcast_to_group(self, message: dict, group: str):
        """向特定组广播消息"""
        # 这里可以实现更复杂的分组逻辑
        await self.broadcast(message)


# 创建全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    数据大屏WebSocket连接
    
    推送实时统计数据
    """
    await manager.connect(websocket)
    
    try:
        # 创建数据库连接和服务
        db = get_db()
        stats_service = StatisticsService(await db)
        
        # 定期推送数据
        while True:
            try:
                # 获取实时统计数据
                realtime_data = await stats_service.get_realtime_statistics()
                
                # 构建消息
                message = {
                    "type": "realtime_update",
                    "data": realtime_data
                }
                
                # 发送数据
                await websocket.send_json(message)
                
                # 等待5秒后再次推送
                await asyncio.sleep(5)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in dashboard websocket: {str(e)}")
                await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """
    用户通知WebSocket连接
    
    推送个人通知和警报
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            # 处理心跳
            if data == "ping":
                await websocket.send_text("pong")
            else:
                # 处理其他消息
                logger.info(f"Received message from {user_id}: {data}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        manager.disconnect(websocket, user_id)


async def send_import_progress(import_id: str, progress: dict):
    """发送导入进度更新"""
    message = {
        "type": "import_progress",
        "import_id": import_id,
        "data": progress
    }
    await manager.broadcast(message)


async def send_alert(alert_type: str, message: str, severity: str = "info"):
    """发送系统警报"""
    alert = {
        "type": "alert",
        "alert_type": alert_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(alert)