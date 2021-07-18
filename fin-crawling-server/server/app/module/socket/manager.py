from fastapi import WebSocket
from typing import List
from pymitter import EventEmitter
from app.model.dto import SocketResponse
import asyncio
from uvicorn.config import logger


class ConnectionManager:
    def __init__(self) -> None:
        self.ee = EventEmitter()
        self.loop = asyncio.get_running_loop()
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def _send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def _broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)
    
    async def eventHandle(self, websocket: WebSocket, data: dict) -> None:
        logger.info("receive:"+str(data))
        self.ee.emit(data["event"], data["payload"], websocket)
    
    def send(self, event: str, payload: dict, websocket: WebSocket) -> None:
        print("socketRunning:"+str(len(self.active_connections)))
        res = SocketResponse(**{
            "event": event,
            "payload": payload
        })
        logger.info("send:"+res.json())
        self.loop.create_task(self._send_personal_message(res.json(), websocket))
    
    def sendBroadCast(self, event: str, payload: dict) -> None:
        res = SocketResponse(**{
            "event": event,
            "payload": payload
        })
        logger.info("sendBroadCast:"+res.json())
        self.loop.create_task(self._broadcast(res.json()))
