from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from database import get_db
import models
from services.websocket_manager import manager
from core.oauth2 import get_current_user_ws
import json

router = APIRouter(tags=["WebSocket"])


@router.websocket("/updates")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token")
):
    """
    WebSocket endpoint for real-time updates
    
    Connect with: ws://localhost:8000/ws/updates?token=YOUR_JWT_TOKEN
    
    Message types received:
    - resume_update: Resume processing status
    - job_match_update: Job matching status
    """
    user = None
    
    # Get database session
    db = next(get_db())
    
    try:
        # Authenticate user from token
        user = await get_current_user_ws(token, db)
        
        if not user:
            await websocket.close(code=4001, reason="Invalid authentication")
            return
        
        # Connect the WebSocket
        await manager.connect(websocket, user.user_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": f"Welcome {user.full_name}! Connected successfully.",
            "user_id": user.user_id
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping/pong for keeping connection alive
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        if user:
            manager.disconnect(websocket, user.user_id)
            print(f"User {user.user_id} disconnected")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        if user:
            manager.disconnect(websocket, user.user_id)
        try:
            await websocket.close(code=4000, reason=str(e))
        except:
            pass
    finally:
        db.close()