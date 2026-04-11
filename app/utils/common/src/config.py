from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    RAPIDAPI_KEY: str
    JOB_CLASSIFICATION_PROMPT: str
    JOB_SEARCH_QUERY: str
    INIT_JOB_SEARCH_MAX_PAGES: int
    JOB_SEARCH_MAX_PAGES: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    LOG_LEVEL: str

    class Config:
        env_file = ".env"

settings = Settings()