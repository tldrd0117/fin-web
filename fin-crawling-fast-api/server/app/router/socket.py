from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.event.manager import manager

router = APIRouter()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            asyncio.create_task(manager.eventHandle(websocket, data))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
