from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = "mock-key"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    DATABASE_URL: str = "sqlite:///./data.db"
    COLLECTION_NAME: str = "docs"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()