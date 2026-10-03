import os
from typing import List, Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_SECRETS = {
    "change_this_super_secret_jwt_key_in_production_12345",
    "dev-insecure-secret-key-fraudshield-local-development-only-unsafe-for-prod",
    "secret",
    "changeme",
    "default",
    "admin",
    "password",
    ""
}

class Settings(BaseSettings):
    PROJECT_NAME: str = "FraudShield AI"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    # Safe development-only default: explicitly marked as unsafe for deployment
    SECRET_KEY: str = "dev-insecure-secret-key-fraudshield-local-development-only-unsafe-for-prod"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # PostgreSQL / Database
    DATABASE_URL: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Risk Engine Thresholds
    RISK_THRESHOLD_MEDIUM: float = 30.0
    RISK_THRESHOLD_HIGH: float = 70.0

    # Demo / Evaluation Seeding (Disabled by default in production)
    ENABLE_DEMO_SEED: bool = True

    # Rate Limiting
    SCORE_RATE_LIMIT_PER_MINUTE: int = 600
    AUTH_RATE_LIMIT_PER_MINUTE: int = 30

    # Cost-based Decision Engine Defaults
    FALSE_DECLINE_COST: float = 5.0
    MISSED_FRAUD_FIXED_COST: float = 50.0
    STEP_UP_COST: float = 1.0

    # CORS
    CORS_ORIGINS: Optional[str] = None
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    model_config = SettingsConfigDict(
        env_file=[
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
            ".env"
        ],
        case_sensitive=True,
        extra="ignore"
    )

    def is_insecure_secret(self) -> bool:
        if not self.SECRET_KEY or self.SECRET_KEY.strip() in INSECURE_SECRETS:
            return True
        if len(self.SECRET_KEY.strip()) < 32:
            return True
        if "dev-insecure" in self.SECRET_KEY.lower() or "change_this" in self.SECRET_KEY.lower():
            return True
        return False

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        env = (self.ENVIRONMENT or "").strip().lower()
        if env == "production":
            if self.is_insecure_secret():
                raise ValueError(
                    "FATAL: In production ENVIRONMENT, SECRET_KEY must be set to a cryptographically strong secret "
                    "with at least 32 characters, and cannot use default/development strings."
                )
            if self.ENABLE_DEMO_SEED:
                raise ValueError(
                    "FATAL: In production ENVIRONMENT, ENABLE_DEMO_SEED must be False. Demo seeding is strictly forbidden."
                )
            if self.POSTGRES_PASSWORD == "fraudshield_secret_pass":
                raise ValueError(
                    "FATAL: In production ENVIRONMENT, hardcoded database credentials ('fraudshield_secret_pass') cannot be used."
                )
        elif env != "production":
            # For non-production, ensure demo seed is only active if explicitly desired
            pass
        return self

    @property
    def cors_origins(self) -> List[str]:
        origins = list(self.BACKEND_CORS_ORIGINS)
        if self.CORS_ORIGINS:
            for item in self.CORS_ORIGINS.split(","):
                clean = item.strip()
                if clean and clean not in origins:
                    origins.append(clean)
        return origins

    def get_database_url(self) -> str:
        raw_url = self.DATABASE_URL or self.SQLALCHEMY_DATABASE_URI or os.getenv("DATABASE_URL")
        if raw_url:
            # Normalize legacy postgres:// and generic postgresql:// to postgresql+psycopg2://
            if raw_url.startswith("postgres://"):
                raw_url = raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif raw_url.startswith("postgresql://"):
                raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return raw_url

        db_type = os.getenv("DB_TYPE", "").lower()
        if db_type in ("postgres", "postgresql") or os.getenv("POSTGRES_SERVER") or self.POSTGRES_SERVER:
            server = self.POSTGRES_SERVER or "localhost"
            user = self.POSTGRES_USER or "fraudshield"
            password = self.POSTGRES_PASSWORD or ""
            db_name = self.POSTGRES_DB or "fraudshield_db"
            return f"postgresql+psycopg2://{user}:{password}@{server}:{self.POSTGRES_PORT}/{db_name}"
        
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        db_path = os.path.join(project_root, "fraudshield.db").replace("\\", "/")
        return f"sqlite:///{db_path}"

settings = Settings()

