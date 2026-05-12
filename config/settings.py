from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    AI_MODEL: str = "deepseek-v4-pro" # or deepseek-reasoner
    
    HONEYPOT_HOSTNAME: str = "prod-web-01"
    HONEYPOT_USER: str = "web-admin"
    
    LOG_FILE: str = "telemetry_logs.json"
    MAX_HISTORY_CONTEXT: int = 10

settings = Settings()