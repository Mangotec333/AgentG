"""
Configuration management for AI Workflow Shield.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class GuardianAgentConfig(BaseSettings):
    """Guardian Agent local configuration."""
    # API Configuration
    ingestion_endpoint: str = os.getenv(
        "SHIELD_INGESTION_ENDPOINT",
        "https://shield.mangotec.ai/api/v1/ingest"
    )
    api_key: Optional[str] = os.getenv("SHIELD_API_KEY")
    
    # Agent Identity
    agent_id: str = os.getenv("SHIELD_AGENT_ID", "default_agent")
    workspace_id: str = os.getenv("SHIELD_WORKSPACE_ID", "default_workspace")
    
    # Collection Settings
    batch_size: int = int(os.getenv("SHIELD_BATCH_SIZE", "50"))
    batch_interval_seconds: int = int(os.getenv("SHIELD_BATCH_INTERVAL", "30"))
    max_queue_size: int = int(os.getenv("SHIELD_MAX_QUEUE", "1000"))
    
    # Monitoring Paths
    log_paths: List[str] = [
        "*.jsonl",
        "logs/*.log",
        ".cursor/logs/*.jsonl"
    ]
    
    # Local Risk Thresholds
    risk_threshold_suspicious: int = 4
    risk_threshold_incident: int = 7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BackendConfig(BaseSettings):
    """Backend/Cloud configuration."""
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/shield")
    
    # Redis (optional)
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    api_key_header: str = "X-API-Key"
    
    # LLM Models
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Risk Thresholds
    risk_threshold_normal: int = 3
    risk_threshold_suspicious: int = 6
    risk_threshold_incident: int = 7
    
    # Pattern Matching
    pattern_db_path: str = "patterns/pattern_list.json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

