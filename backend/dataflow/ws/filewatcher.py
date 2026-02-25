"""WebSocket endpoint for file watcher events."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dataflow.server.state import AppState

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/filewatcher")
async def filewatcher_ws(websocket: WebSocket) -> None:
    state: AppState = websocket.app.state.app_state
    assert state.ws_manager is not None
    manager = state.ws_manager

    await manager.connect_filewatcher(websocket)
    try:
        while True:
            await websocket.receive_text()
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        manager.disconnect_filewatcher(websocket)
        logger.info("Filewatcher WebSocket disconnected")
