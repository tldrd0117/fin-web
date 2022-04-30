from typing import Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
import asyncio

from fastapi.params import Depends, Query
from app.module.socket.manager import ConnectionManager
from app.module.locator import Locator

from app.service.api.UserApiService import UserApiService
from app.model.user import User
from uvicorn.config import logger


router = APIRouter()
userService: UserApiService = Locator.getInstance().get(UserApiService)
manager: ConnectionManager = Locator.getInstance().get(ConnectionManager)


async def get_token(
    websocket: WebSocket,
    token: Any = Query(None),
) -> Optional[str]:
    logger.info("TOKEN:"+str(token))
    if token is None or not userService.check_token(token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
    return token 


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, user: User = Depends(userService.validateToken)) -> None:
    if user is None:
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

