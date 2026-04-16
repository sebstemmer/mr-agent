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
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    MICROSOFT_REFRESH_TOKEN: str
    MICROSOFT_TODO_LIST_ID: str
    MORNING_BRIEFING_GREETING: str
    MORNING_BRIEFING_WEATHER_LOCATION: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()