from pydantic import BaseModel
from typing import Optional, Dict


class ChatRequest(BaseModel):
    message: str
    session_id: str
    patient_name: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent: str
    patient_data: Optional[Dict] = None
    sources: Optional[Dict] = None

class ResetRequest(BaseModel):
    session_id: str