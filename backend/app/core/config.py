"""Application configuration using pydantic-settings."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load backend/.env; override=False so Docker/compose env vars take precedence
_backend_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(_backend_dir / ".env", override=False)


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Gravitational Physics Simulations Platform"
    debug: bool = False

    # Database (use sqlite+aiosqlite for local dev without PostgreSQL)
    # PostgreSQL: postgresql+asyncpg://user:pass@host:5432/db
    # WO-1: Aurora PostgreSQL connection pooling, SSL
    database_url: str = "sqlite+aiosqlite:///./gravitational.db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_ssl_mode: str = "prefer"  # require, verify-full for Aurora

    # Redis (for Celery, rate limiting)
    redis_url: str = "redis://localhost:6379/0"
    # Dedicated Celery queue to avoid conflicts with other apps sharing Redis
    celery_queue: str = "gravitational"

    # AWS
    aws_region: str = "us-east-1"
    s3_bucket: str = "gravitational-simulations"
    s3_presigned_expiry: int = 3600
    # Optional: set for LocalStack (e.g. http://localhost:4566)
    aws_endpoint_url: str | None = None

    # Cognito
    cognito_region: str = "us-east-1"
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    cognito_jwks_url: str = ""

    # CORS (include common Vite dev ports; 127.0.0.1 for some browsers)
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ]

    # Logging
    log_level: str = "INFO"

    # API Keys (WO-48)
    api_key_default_rate_limit: int = 1000  # requests per hour
    api_key_expiry_days: int = 365  # 1 year

    # Neo4j (WO-3) - theory lineage, provenance graph (7688 to avoid port conflict)
    neo4j_uri: str = "bolt://localhost:7688"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "gravitational"

    # DGX GPU cluster - remote execution, health, rate limit fallback
    dgx_host: str = "10.88.111.9"
    dgx_base_url: str = ""  # e.g. http://10.88.111.9:8000; empty = http://{dgx_host}:8000
    dgx_health_path: str = "/health"
    dgx_timeout: float = 5.0
    dgx_enabled: bool = False  # Set True when orchestrator is running on DGX
    dgx_celery_queue: str = ""  # e.g. "dgx" to route GPU tasks; empty = default queue


settings = Settings()
