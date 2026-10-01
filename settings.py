from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_API_KEY: str
    LLM_BASE_URL: str
    SERVER_PORT: int

    class Config:
        env_file = ".env"

settings = Settings()
