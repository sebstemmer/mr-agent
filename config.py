from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    RAPIDAPI_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()