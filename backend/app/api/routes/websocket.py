from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.core.security import decode_token
from app.realtime.websocket_manager import ws_manager
from app.core.logging import logger

router = APIRouter()

@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        logger.warning("Rejected unauthenticated WebSocket connection attempt")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    org_id = payload.get("org_id")
    if not org_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(websocket, org_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except (WebSocketDisconnect, RuntimeError):
        ws_manager.disconnect(websocket, org_id)
    except Exception as e:
        logger.debug(f"WebSocket client disconnected: {e}")
        ws_manager.disconnect(websocket, org_id)
