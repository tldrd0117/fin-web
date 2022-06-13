from fastapi import WebSocket
from typing import List

from app.model.dto import SocketResponse
import asyncio
from uvicorn.config import logger
from app.util.events import eventManage
from app.util.decorator import eventsDecorator as ed, EventEmitter


class ConnectionManager:
    ee = None
    def __init__(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.active_connections: List[WebSocket] = []
        # self.threadExcutor = ThreadPoolExecutor(max_workers=10)
    
    def setEventEmitter(self, instance):
        print("setEventEmitter")
        self.ee = EventEmitter(instance, eventManage())

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
        await self.ee.emit(data["event"], data["payload"], websocket)
    
    def send(self, event: str, payload: dict, websocket: WebSocket) -> None:
        print("socketRunning:"+str(len(self.active_connections)))
        res = SocketResponse(**{
            "event": event,
            "payload": payload
        })
        logger.info("send:"+res.json())
        # with ThreadPoolExecutor() as ex:
        #     ex.submit(self.__send_personal_message, res.json(), websocket)
        # asyncio.ensure_future(self._send_personal_message(res.json(), websocket))
        self.loop.create_task(self._send_personal_message(res.json(), websocket))
    
    def sendBroadCast(self, event: str, payload: dict) -> None:
        res = SocketResponse(**{
            "event": event,
            "payload": payload
        })
        logger.info("sendBroadCast:"+res.json())
        # with ThreadPoolExecutor() as ex:
        #     ex.submit(self.__broadcast, res.json())
        # asyncio.ensure_future(self._broadcast(res.json()))
        self.loop.create_task(self._broadcast(res.json()))
