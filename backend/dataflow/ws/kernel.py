"""WebSocket endpoint for kernel messages."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dataflow.server.state import AppState

router = APIRouter()


@router.websocket("/ws/kernel")
async def kernel_ws(websocket: WebSocket) -> None:
    state: AppState = websocket.app.state.app_state
    assert state.ws_manager is not None
    manager = state.ws_manager

    await manager.connect_kernel(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_kernel(websocket)
