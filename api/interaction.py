from http import HTTPStatus
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.app.services.langgraph_agent import build_interaction_plan

app = FastAPI(title="AI-first HCP CRM", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InteractionRequest(BaseModel):
    hcp_name: Optional[str] = None
    specialty: Optional[str] = None
    objective: Optional[str] = None
    notes: Optional[str] = None
    channel: Optional[str] = None
    next_step: Optional[str] = None
    follow_up_date: Optional[str] = None
    chat_message: Optional[str] = None


@app.get("/")
@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "ai-first-hcp-crm"}


@app.post("/")
@app.post("/api/interaction")
def log_interaction(payload: InteractionRequest) -> Dict[str, Any]:
    structured_payload = {
        "hcp_name": payload.hcp_name or "Unknown HCP",
        "specialty": payload.specialty or "General Medicine",
        "objective": payload.objective or "Capture a follow-up discussion",
        "notes": payload.notes or "",
        "channel": payload.channel or "phone",
        "next_step": payload.next_step or "Follow up within 72 hours",
        "follow_up_date": payload.follow_up_date or "",
    }
    raw_input = payload.chat_message or ""
    result = build_interaction_plan(structured_payload, raw_input)
    return JSONResponse(status_code=HTTPStatus.OK, content={"success": True, **result})
