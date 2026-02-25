"""WebSocket endpoint for kernel messages."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dataflow.server.state import AppState

logger = logging.getLogger(__name__)
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
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        manager.disconnect_kernel(websocket)
        logger.info("Kernel WebSocket disconnected")
