from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    RAPIDAPI_KEY: str
    JOB_CLASSIFICATION_PROMPT: str
    JOB_SEARCH_QUERY: str
    JOB_SEARCH_MAX_PAGES: int
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()