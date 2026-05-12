import json
import os
from datetime import datetime
from models.schemas import LogEntry

class TelemetrySystem:
    """Handles structured logging for SIEM ingestion."""
    
    def __init__(self, log_file: str):
        self.log_file = log_file

    def log(self, entry: LogEntry):
        data = entry.model_dump()
        with open(self.log_file, "a") as f:
            f.write(json.dumps(data) + "\n")

    @staticmethod
    def format_console_output(entry: LogEntry):
        # Professional console logging for the honeypot operator
        print(f"\033[94m[{entry.timestamp}]\033[0m \033[93m{entry.command}\033[0m -> Risk: {entry.risk_score}")