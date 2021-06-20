from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
import asyncio

from fastapi.params import Depends, Query
from app.event.socket import manager
from app.module.locator import Locator

from app.service.UserService import UserService
from uvicorn.config import logger

router = APIRouter()
userService: UserService = Locator.getInstance().get(UserService)


async def get_token(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
) -> Optional[str]:
    logger.info("TOKEN:"+str(token))
    if token is None or not userService.check_token(token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    return token


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, token: Optional[str] = Depends(get_token)) -> None:
    if token is None:
        return
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            asyncio.create_task(manager.eventHandle(websocket, data))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
