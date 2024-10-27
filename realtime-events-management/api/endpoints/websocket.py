import fastapi

from core import ws_manager

router = fastapi.APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: fastapi.WebSocket):
    await ws_manager.manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except fastapi.websockets.WebSocketDisconnect:
        ws_manager.manager.disconnect(websocket)
