from fastapi import WebSocket
from typing import List
from pymitter import EventEmitter
import asyncio
from app.event.socket import ee


class ConnectionManager:
    def __init__(self, ee: EventEmitter) -> None:
        self.ee = ee
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        await websocket.send_json(message)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)
    
    async def eventHandle(self, websocket: WebSocket, data: dict) -> None:
        print(data)
        self.ee.emit(data["event"], data["payload"], websocket, self)
    
    def send(self, event: str, payload: dict, websocket: WebSocket) -> None:
        print("socketRunning:"+str(len(self.active_connections)))
        asyncio.create_task(self.send_personal_message({"event": event, "payload": payload}, websocket))


manager = ConnectionManager(ee)

