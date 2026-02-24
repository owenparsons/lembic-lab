"""Data profiling endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dataflow.models.profile import DataProfile
from dataflow.server.dependencies import get_state
from dataflow.server.state import AppState
from dataflow.services.profiler import generate_profile_code, parse_profile_result

router = APIRouter(prefix="/api", tags=["profile"])


class ProfileRequest(BaseModel):
    variable_name: str


@router.post("/profile", response_model=DataProfile)
async def profile_variable(
    body: ProfileRequest,
    state: AppState = Depends(get_state),
) -> DataProfile:
    if state.kernel_manager is None or not state.kernel_manager.is_started:
        raise HTTPException(status_code=400, detail="Kernel not running")

    code = generate_profile_code(body.variable_name)
    output_text = ""

    async for msg in state.kernel_manager.execute(code):
        if msg.get("msg_type") == "stream" and msg.get("content", {}).get("name") == "stdout":
            output_text += msg["content"]["text"]

    profile = parse_profile_result(output_text)
    if profile is None:
        raise HTTPException(status_code=422, detail="Failed to profile variable")

    return profile
