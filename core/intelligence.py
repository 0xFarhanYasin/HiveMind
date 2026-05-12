import re
from typing import List
from models.schemas import MitreAttack

class AttackClassifier:
    """Classifies commands into MITRE ATT&CK tactics and calculates risk."""
    
    PATTERNS = {
        r"whoami|id|hostname|uname": MitreAttack(tactic="Discovery", technique_id="T1033", description="System Owner/User Discovery"),
        r"ls -la|find|locate": MitreAttack(tactic="Discovery", technique_id="T1083", description="File and Directory Discovery"),
        r"cat /etc/passwd|cat /etc/shadow": MitreAttack(tactic="Credential Access", technique_id="T1552", description="Unsecured Credentials"),
        r"sudo|su root|chmod 777": MitreAttack(tactic="Privilege Escalation", technique_id="T1548", description="Abuse Elevation Control Mechanism"),
        r"curl|wget|scp|ftp": MitreAttack(tactic="Exfiltration/Ingress", technique_id="T1105", description="Ingress Tool Transfer"),
        r"rm -rf /|unset HISTFILE": MitreAttack(tactic="Defense Evasion", technique_id="T1562", description="Impair Defenses"),
    }

    @classmethod
    def analyze(cls, command: str) -> (List[MitreAttack], int):
        tags = []
        score = 0
        for pattern, attack in cls.PATTERNS.items():
            if re.search(pattern, command):
                tags.append(attack)
                score += 20
        
        # Baseline risk for any interaction
        score = min(score + 5, 100) 
        return tags, score