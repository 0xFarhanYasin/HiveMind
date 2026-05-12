from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class CommandContext(BaseModel):
    command: str
    timestamp: datetime = Field(default_factory=datetime.now)
    directory: str
    user: str

class MitreAttack(BaseModel):
    tactic: str
    technique_id: str
    description: str

class LogEntry(BaseModel):
    session_id: str
    timestamp: str
    user: str
    hostname: str
    directory: str
    command: str
    response: str
    risk_score: int
    attack_tags: List[MitreAttack]
    metadata: Dict[str, str]

class SessionProfile(BaseModel):
    session_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    commands_executed: List[CommandContext] = []
    risk_score: int = 0