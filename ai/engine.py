from openai import OpenAI
from config.settings import settings

class AITerminalEngine:
    """Core AI engine to generate realistic shell responses."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)
        self.system_prompt = (
            "You are a sophisticated Ubuntu 22.04 LTS terminal emulator. "
            "Character rules:\n"
            "1. NO explanations. NO helpful tips. ONLY shell output.\n"
            "2. If a command is invalid, return standard bash errors.\n"
            "3. Simulate file content realistically (e.g., /etc/passwd should have standard service accounts).\n"
            "4. Maintain consistency with the provided directory context.\n"
            "5. If a user tries to use 'sudo', mimic a password prompt then fail with 'Permission denied'.\n"
            "6. Network commands (ping/curl) should simulate realistic timeouts or fake data.\n"
            "7. Character: You are a secure, slightly hardened production server."
        )

    def generate_response(self, command: str, context_path: str, history: list) -> str:
        history_snippet = "\n".join([f"$ {h.command}\n{h.timestamp}" for h in history[-5:]])
        
        prompt = (
            f"Environment Context:\n"
            f"Hostname: {settings.HONEYPOT_HOSTNAME}\n"
            f"User: {settings.HONEYPOT_USER}\n"
            f"PWD: {context_path}\n"
            f"Recent History:\n{history_snippet}\n\n"
            f"Input Command: {command}"
        )

        try:
            completion = self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"bash: internal error processing command: {str(e)}"