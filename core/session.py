import uuid
from datetime import datetime
from typing import Dict, List, Optional
from models.schemas import SessionProfile, CommandContext, MitreAttack

class Session:
    """
    Represents an individual attacker's connection.
    Maintains state, command history, and cumulative threat intelligence.
    """
    def __init__(self, username: str, source_ip: str = "127.0.0.1"):
        self.session_id: str = str(uuid.uuid4())
        self.start_time: datetime = datetime.now()
        self.username: str = username
        self.source_ip: str = source_ip
        self.history: List[CommandContext] = []
        self.risk_score: int = 0
        self.observed_techniques: List[MitreAttack] = []
        self.is_active: bool = True

    def add_command(self, command: str, directory: str):
        """Adds a command to the history context."""
        context = CommandContext(
            command=command,
            directory=directory,
            user=self.username,
            timestamp=datetime.now()
        )
        self.history.append(context)

    def update_threat_profile(self, tags: List[MitreAttack], score_increment: int):
        """Updates the session's risk score and unique MITRE techniques."""
        self.risk_score = min(self.risk_score + score_increment, 100)
        
        # Only add unique techniques to the profile to avoid redundancy
        existing_ids = {t.technique_id for t in self.observed_techniques}
        for tag in tags:
            if tag.technique_id not in existing_ids:
                self.observed_techniques.append(tag)

    def to_profile(self) -> SessionProfile:
        """Exports the session state to a serializable Pydantic model."""
        return SessionProfile(
            session_id=self.session_id,
            start_time=self.start_time,
            commands_executed=self.history,
            risk_score=self.risk_score
        )

class SessionManager:
    """
    Architectural layer to manage multiple concurrent honeypot sessions.
    Essential for scaling to a real SSH daemon (e.g., via Paramiko).
    """
    def __init__(self):
        self._active_sessions: Dict[str, Session] = {}

    def create_session(self, username: str, source_ip: str = "192.168.1.45") -> Session:
        """Initializes and tracks a new session."""
        new_session = Session(username=username, source_ip=source_ip)
        self._active_sessions[new_session.session_id] = new_session
        return new_session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieves a session by ID."""
        return self._active_sessions.get(session_id)

    def end_session(self, session_id: str):
        """Cleanly closes a session for telemetry finalization."""
        if session_id in self._active_sessions:
            self._active_sessions[session_id].is_active = False
            # In a real production system, we might move this to a DB or cache here
            del self._active_sessions[session_id]

    @property
    def active_count(self) -> int:
        return len(self._active_sessions)