import json

import fastapi

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[fastapi.WebSocket] = []

    async def connect(self, websocket: fastapi.WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: fastapi.WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: fastapi.WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, type: str, data: dict):
        message = {
            "type": type,
            "data": data
        }
        json_message = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(json_message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()
