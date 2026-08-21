from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEVELOPMENT_JWT_SECRET = "development-only-secret-change-before-deploy"


class Settings(BaseSettings):
    APP_NAME: str = "AI Knowledge Backend"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/ai_knowledge"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET_KEY: str = DEVELOPMENT_JWT_SECRET
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    JWT_ISSUER: str = "ai-knowledge-platform"
    JWT_AUDIENCE: str = "ai-knowledge-api"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)

    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "mock-model"
    LLM_BASE_URL: str = "http://ollama:11434"

    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "mock-embedding-model"

    VECTOR_STORE: str = "pgvector"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def reject_weak_production_secret(self) -> "Settings":
        if self.APP_ENV.lower() == "production" and (
            self.JWT_SECRET_KEY == DEVELOPMENT_JWT_SECRET or len(self.JWT_SECRET_KEY) < 32
        ):
            raise ValueError("Production JWT secret must contain at least 32 characters")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
