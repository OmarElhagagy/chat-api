from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime

from app.services.auth import decoded_access_token
from app.services.user_service import get_user_by_id
from app.services.chat_service import create_message, get_room_messages
from app.models.chat import MessageCreate

router = APIRouter()

# Keep track of active connections
class ConnectionManager:
    def __init__(self):
        # Structure: {room_id: {client_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: int, client_id: str):
        """Connect a client to a specific room"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
            
        self.active_connections[room_id][client_id] = websocket
        
    def disconnect(self, room_id: int, client_id: str):
        """Disconnect a client from a room"""
        if room_id in self.active_connections and client_id in self.active_connections[room_id]:
            del self.active_connections[room_id][client_id]
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                
    async def broadcast(self, room_id: int, message: Dict[str, Any]):
        """Broadcast message to all clients in a room"""
        if room_id in self.active_connections:
            disconnected_clients = []
            
            # Convert message to JSON string
            message_json = json.dumps(message)
            
            for client_id, websocket in self.active_connections[room_id].items():
                try:
                    await websocket.send_text(message_json)
                except Exception:
                    disconnected_clients.append((room_id, client_id))
                    
            # Clean up disconnected clients
            for room_id, client_id in disconnected_clients:
                self.disconnect(room_id, client_id)

manager = ConnectionManager()

# WebSocket authentication
async def get_current_user_ws(token: str) -> Dict[str, Any]:
    """Authenticate WebSocket connection"""
    token_data = decoded_access_token(token)
    if token_data is None:
        return None
        
    user = await get_user_by_id(token_data.user_id)
    return user

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int,
    token: str = None
):
    """WebSocket endpoint for real-time chat"""
    # Authenticate user
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    user = await get_current_user_ws(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    # Generate a unique client ID using user_id and timestamp
    client_id = f"{user['id']}_{datetime.now().timestamp()}"
        
    # Accept connection and add to active connections
    await manager.connect(websocket, room_id, client_id)
    
    try:
        # Load room history
        history = await get_room_messages(room_id, page=1, page_size=50)
        await websocket.send_json({
            "type": "history",
            "messages": history
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                
                # Validate message
                if "content" not in message_data:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format"
                    })
                    continue
                    
                # Create message in database
                message = await create_message(
                    MessageCreate(room_id=room_id, content=message_data["content"]),
                    user["id"]
                )
                
                if message:
                    # Broadcast to all clients in the room
                    await manager.broadcast(room_id, {
                        "type": "message",
                        "message": message
                    })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        # Handle disconnection
        manager.disconnect(room_id, client_id)
        
        # Notify other clients about disconnection
        await manager.broadcast(room_id, {
            "type": "system",
            "message": f"User {user['username']} has left the chat"
        })
