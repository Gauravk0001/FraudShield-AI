import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket, status
from app.core.security import decode_token
from app.core.logging import logger

class ConnectionManager:
    def __init__(self):
        # Map organization_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, organization_id: str):
        await websocket.accept()
        if organization_id not in self.active_connections:
            self.active_connections[organization_id] = set()
        self.active_connections[organization_id].add(websocket)
        logger.info(f"WebSocket client connected for org {organization_id}. Active: {len(self.active_connections[organization_id])}")

    def disconnect(self, websocket: WebSocket, organization_id: str):
        if organization_id in self.active_connections:
            self.active_connections[organization_id].discard(websocket)
            if not self.active_connections[organization_id]:
                del self.active_connections[organization_id]
        logger.info(f"WebSocket client disconnected for org {organization_id}")

    async def broadcast_to_organization(self, organization_id: str, message: dict):
        if organization_id in self.active_connections:
            stale_websockets = []
            for websocket in self.active_connections[organization_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending WebSocket payload to client: {e}")
                    stale_websockets.append(websocket)
            
            for stale in stale_websockets:
                self.disconnect(stale, organization_id)

ws_manager = ConnectionManager()
