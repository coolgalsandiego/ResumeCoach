"""
Configuration management for Resume Coach application
"""
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Resume Coach"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # SageMaker
    SAGEMAKER_ENDPOINT_NAME: str = "llama2-13b-chat-endpoint"

    # S3
    S3_BUCKET_RESUMES: str = "resume-coach-resumes"
    S3_BUCKET_JOBS: str = "resume-coach-jobs"

    # DynamoDB
    DYNAMODB_TABLE_USERS: str = "resume-coach-users"
    DYNAMODB_TABLE_ANALYSES: str = "resume-coach-analyses"
    DYNAMODB_TABLE_SESSIONS: str = "resume-coach-sessions"

    # LLM Settings
    DEFAULT_TEMPERATURE: float = 0.5
    DEFAULT_MAX_TOKENS: int = 800
    CONTEXT_WINDOW_SIZE: int = 4096

    # OpenAI (for development/fallback)
    OPENAI_API_KEY: Optional[str] = None
    USE_OPENAI_FALLBACK: bool = True
    
    # Ollama (local LLM - free, no API key needed)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"  # Options: mistral (fast), llama2, codellama, etc.

    # Redis (caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "pdf,docx,txt"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env file

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed file extensions as list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]


# Create global settings instance
settings = Settings()
