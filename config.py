from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    #openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()