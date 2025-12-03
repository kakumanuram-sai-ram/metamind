"""
Application Settings - Centralized Configuration with Validation

This module provides type-safe, validated configuration management for MetaMind.
"""
from dataclasses import dataclass, field
from typing import Optional
import os
from pathlib import Path
from enum import Enum


class Environment(Enum):
    """Application environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class AppSettings:
    """
    Application configuration with validation.
    Immutable to prevent accidental modifications.
    """
    
    # API Settings
    superset_base_url: str
    superset_cookie: str
    superset_csrf_token: str
    
    # LLM Settings
    llm_api_key: str
    llm_model: str = "anthropic/claude-sonnet-4"
    llm_base_url: str = "https://cst-ai-proxy.paytm.com"
    llm_max_retries: int = 3
    llm_timeout: int = 300
    
    # Storage Settings
    base_dir: Path = field(default_factory=lambda: Path("extracted_meta"))
    merged_dir: Path = field(default_factory=lambda: Path("extracted_meta/merged_metadata"))
    kb_dir: Path = field(default_factory=lambda: Path("extracted_meta/knowledge_base"))
    progress_file: Path = field(default_factory=lambda: Path("extracted_meta/progress.json"))
    logs_dir: Path = field(default_factory=lambda: Path("logs"))
    
    # Processing Settings
    max_concurrent_dashboards: int = 5
    chart_batch_size: int = 10
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    request_timeout: int = 30
    
    # Feature Flags
    enable_llm_extraction: bool = True
    enable_trino_enrichment: bool = True
    enable_quality_judge: bool = False
    enable_parallel_processing: bool = True
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Validate required fields
        if not self.superset_base_url:
            raise ValueError("superset_base_url is required")
        if not self.superset_cookie:
            raise ValueError("superset_cookie is required (set SUPERSET_COOKIE env var)")
        if not self.llm_api_key:
            raise ValueError("llm_api_key is required (set ANTHROPIC_API_KEY env var)")
        
        # Create directories (using object.__setattr__ for frozen dataclass)
        for dir_attr in ['base_dir', 'merged_dir', 'kb_dir', 'logs_dir']:
            dir_path = getattr(self, dir_attr)
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'AppSettings':
        """
        Load configuration from environment variables.
        Falls back to legacy config.py for backwards compatibility.
        """
        # Try to import from legacy config
        try:
            from config import (
                BASE_URL, HEADERS, LLM_API_KEY, 
                LLM_MODEL, LLM_BASE_URL
            )
            legacy_base_url = BASE_URL
            legacy_cookie = HEADERS.get('Cookie', '')
            legacy_csrf = HEADERS.get('X-CSRFToken', '')
            legacy_llm_key = LLM_API_KEY
            legacy_llm_model = LLM_MODEL
            legacy_llm_base = LLM_BASE_URL
        except ImportError:
            legacy_base_url = ''
            legacy_cookie = ''
            legacy_csrf = ''
            legacy_llm_key = ''
            legacy_llm_model = 'anthropic/claude-sonnet-4'
            legacy_llm_base = 'https://cst-ai-proxy.paytm.com'
        
        return cls(
            # Superset Settings - prefer env vars
            superset_base_url=os.getenv('SUPERSET_BASE_URL', legacy_base_url),
            superset_cookie=os.getenv('SUPERSET_COOKIE', legacy_cookie),
            superset_csrf_token=os.getenv('SUPERSET_CSRF_TOKEN', legacy_csrf),
            
            # LLM Settings
            llm_api_key=os.getenv('ANTHROPIC_API_KEY', legacy_llm_key),
            llm_model=os.getenv('LLM_MODEL', legacy_llm_model),
            llm_base_url=os.getenv('LLM_BASE_URL', legacy_llm_base),
            llm_max_retries=int(os.getenv('LLM_MAX_RETRIES', '3')),
            llm_timeout=int(os.getenv('LLM_TIMEOUT', '300')),
            
            # Storage Settings
            base_dir=Path(os.getenv('BASE_DIR', 'extracted_meta')),
            merged_dir=Path(os.getenv('MERGED_DIR', 'extracted_meta/merged_metadata')),
            kb_dir=Path(os.getenv('KB_DIR', 'extracted_meta/knowledge_base')),
            progress_file=Path(os.getenv('PROGRESS_FILE', 'extracted_meta/progress.json')),
            logs_dir=Path(os.getenv('LOGS_DIR', 'logs')),
            
            # Processing Settings
            max_concurrent_dashboards=int(os.getenv('MAX_CONCURRENT_DASHBOARDS', '5')),
            chart_batch_size=int(os.getenv('CHART_BATCH_SIZE', '10')),
            enable_caching=os.getenv('ENABLE_CACHING', 'true').lower() == 'true',
            cache_ttl_seconds=int(os.getenv('CACHE_TTL_SECONDS', '300')),
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            
            # Feature Flags
            enable_llm_extraction=os.getenv('ENABLE_LLM_EXTRACTION', 'true').lower() == 'true',
            enable_trino_enrichment=os.getenv('ENABLE_TRINO_ENRICHMENT', 'true').lower() == 'true',
            enable_quality_judge=os.getenv('ENABLE_QUALITY_JUDGE', 'false').lower() == 'true',
            enable_parallel_processing=os.getenv('ENABLE_PARALLEL_PROCESSING', 'true').lower() == 'true',
            
            # Environment
            environment=Environment(os.getenv('ENVIRONMENT', 'development')),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
        )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT


# Global settings instance - loaded once at startup
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """
    Get the global settings instance.
    Creates it on first access using environment variables.
    """
    global _settings
    if _settings is None:
        _settings = AppSettings.from_env()
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)"""
    global _settings
    _settings = None


