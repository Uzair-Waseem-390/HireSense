from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store connections by user_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        print(f"✅ WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Clean up empty lists
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        print(f"❌ WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to all connections of a specific user"""
        if user_id not in self.active_connections:
            return
        
        # Remove closed connections
        dead_connections = []
        
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"⚠️ Failed to send message to user {user_id}: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead_conn in dead_connections:
            self.disconnect(dead_conn, user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)
    
    def get_connection_count(self, user_id: int) -> int:
        """Get number of active connections for a user"""
        return len(self.active_connections.get(user_id, []))


# Global instance
manager = ConnectionManager()


# Helper functions for sending specific message types
async def send_resume_status(user_id: int, resume_id: int, status: str, message: str, progress: int = 0, data: dict = None):
    """Send resume processing status update"""
    await manager.send_personal_message({
        "type": "resume_update",
        "resume_id": resume_id,
        "status": status,
        "message": message,
        "progress": progress,
        "data": data or {},
        "timestamp": asyncio.get_event_loop().time()
    }, user_id)


async def send_job_match_status(user_id: int, job_id: int, resume_id: int, status: str, message: str, progress: int = 0, data: dict = None):
    """Send job matching status update"""
    await manager.send_personal_message({
        "type": "job_match_update",
        "job_id": job_id,
        "resume_id": resume_id,
        "status": status,
        "message": message,
        "progress": progress,
        "data": data or {},
        "timestamp": asyncio.get_event_loop().time()
    }, user_id)