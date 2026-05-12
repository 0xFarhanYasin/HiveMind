import sys
import uuid
import signal
from datetime import datetime
from typing import NoReturn

# Internal Module Imports
from config.settings import settings
from models.schemas import LogEntry, CommandContext
from core.filesystem import VirtualFileSystem
from core.intelligence import AttackClassifier
from core.session import SessionManager, Session
from ai.engine import AITerminalEngine
from telemetry.logger import TelemetrySystem

class HoneypotServer:
    """
    The Primary Orchestrator for the AI-Driven SSH Honeypot.
    Coordinates between the virtual environment, AI deception, and telemetry.
    """

    def __init__(self):
        # Initialize Core Components
        self.session_manager = SessionManager()
        self.vfs = VirtualFileSystem()
        self.ai_engine = AITerminalEngine()
        self.classifier = AttackClassifier()
        self.telemetry = TelemetrySystem(settings.LOG_FILE)
        
        # Create the primary session for the current connection
        self.session: Session = self.session_manager.create_session(
            username=settings.HONEYPOT_USER
        )

        # Register signal handlers for clean exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, sig, frame) -> NoReturn:
        """Handles exit signals to ensure telemetry is flushed."""
        print("\n\r[!] System shutdown initiated. Closing session...")
        self.session_manager.end_session(self.session.session_id)
        sys.exit(0)

    def _display_banner(self) -> None:
        """Displays a realistic Ubuntu login banner."""
        banner = (
            f"Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-generic x86_64)\r\n"
            f" * Documentation:  https://help.ubuntu.com\r\n"
            f" * Management:     https://landscape.canonical.com\r\n"
            f" * Support:        https://ubuntu.com/advantage\r\n"
            f"\r\n"
            f"  System information as of {datetime.now().strftime('%a %b %d %H:%M:%S UTC %Y')}\r\n"
            f"\r\n"
            f"  System load:  0.08               Processes:             102\r\n"
            f"  Usage of /:   12.4% of 19.56GB   Users logged in:       1\r\n"
            f"  Memory usage: 18%                IPv4 address for eth0: 192.168.1.105\r\n"
            f"  Swap usage:   0%\r\n"
            f"\r\n"
            f"0 updates can be applied immediately.\r\n"
            f"\r\n"
            f"Last login: {datetime.now().strftime('%a %b %d %H:%M:%S')} from 10.0.0.15\r\n"
        )
        print(banner)

    def _process_command(self, cmd: str) -> str:
        """
        Routes commands to either the internal VFS or the AI engine.
        """
        # 1. Update Session History
        self.session.add_command(cmd, self.vfs.get_pwd())

        # 2. Logic Routing
        cmd_parts = cmd.split()
        base_cmd = cmd_parts[0] if cmd_parts else ""

        # Handle Internal VFS Navigation
        if base_cmd == "cd":
            target = cmd_parts[1] if len(cmd_parts) > 1 else "/home/" + settings.HONEYPOT_USER
            new_path = self.vfs.change_directory(target)
            return "" # cd produces no output on success

        elif base_cmd == "pwd":
            return self.vfs.get_pwd()

        elif base_cmd == "ls":
            # Simple 'ls' handled by VFS, but complex flags (ls -laR) go to AI
            if len(cmd_parts) == 1:
                return self.vfs.list_dir()
            return self.ai_engine.generate_response(cmd, self.vfs.get_pwd(), self.session.history)

        elif base_cmd in ["exit", "logout"]:
            print("logout")
            self.session_manager.end_session(self.session.session_id)
            sys.exit(0)

        # 3. Fallback to AI Engine for high-fidelity deception
        return self.ai_engine.generate_response(
            cmd, 
            self.vfs.get_pwd(), 
            self.session.history
        )

    def _log_interaction(self, cmd: str, response: str) -> None:
        """
        Analyzes the command for MITRE techniques and logs to telemetry.
        """
        # Perform security analysis
        attack_tags, risk_inc = self.classifier.analyze(cmd)
        self.session.update_threat_profile(attack_tags, risk_inc)

        # Construct structured log
        log_entry = LogEntry(
            session_id=self.session.session_id,
            timestamp=datetime.now().isoformat(),
            user=settings.HONEYPOT_USER,
            hostname=settings.HONEYPOT_HOSTNAME,
            directory=self.vfs.get_pwd(),
            command=cmd,
            response=response,
            risk_score=self.session.risk_score,
            attack_tags=attack_tags,
            metadata={
                "source_ip": self.session.source_ip,
                "terminal_type": "xterm-256color"
            }
        )
        
        # Write to JSON file and mirror to internal monitor
        self.telemetry.log(log_entry)

    def run(self) -> None:
        """Main execution loop."""
        self._display_banner()

        while True:
            try:
                # Build Prompt String
                user = settings.HONEYPOT_USER
                host = settings.HONEYPOT_HOSTNAME
                cwd = self.vfs.get_pwd()
                
                # Simple home directory tilde replacement
                home_path = f"/home/{user}"
                display_cwd = cwd.replace(home_path, "~") if cwd.startswith(home_path) else cwd
                
                prompt = f"{user}@{host}:{display_cwd}$ "
                
                # Capture Input
                cmd_input = input(prompt).strip()

                if not cmd_input:
                    continue

                # Process and Respond
                response = self._process_command(cmd_input)
                if response:
                    print(response)

                # Log to Telemetry
                self._log_interaction(cmd_input, response)

            except EOFError:
                # Handle Ctrl+D
                print("logout")
                break
            except Exception as e:
                # Production-level error masking (don't break character)
                error_msg = f"bash: {cmd_input.split()[0] if cmd_input else 'system'}: command execution error"
                print(error_msg)
                # Log the actual error for the researcher
                self._log_interaction(f"SYSTEM_ERROR: {str(e)}", error_msg)

if __name__ == "__main__":
    server = HoneypotServer()
    server.run()