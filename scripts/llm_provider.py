"""
LLM Provider Configuration Module

This module provides a flexible, provider-agnostic interface for LLM configuration.
Supports multiple providers:
- Anthropic (via proxy)
- TrueFoundry (OpenAI-compatible)
- OpenAI (direct)
- Custom providers

Usage:
    from llm_provider import LLMConfig, get_llm_provider, configure_dspy_from_env
    
    # Option 1: Auto-configure from environment variables
    configure_dspy_from_env()
    
    # Option 2: Manual configuration
    config = LLMConfig.truefoundry(
        api_key="your-api-key",
        model="pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0"
    )
    provider = get_llm_provider(config)
"""
import logging
import os
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

import dspy

logger = logging.getLogger(__name__)

# Thread-safe singleton for DSPy LM
_dspy_lm: Optional[dspy.LM] = None
_dspy_lock = threading.Lock()


class LLMProviderType(Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    TRUEFOUNDRY = "truefoundry"
    OPENAI = "openai"
    CUSTOM = "custom"


@dataclass
class LLMConfig:
    """
    Immutable configuration for LLM providers.
    
    Attributes:
        provider: The type of LLM provider
        api_key: API key or bearer token for authentication
        model: Model identifier (provider-specific)
        base_url: API endpoint URL
        max_retries: Maximum retry attempts for failed requests
        timeout: Request timeout in seconds
        extra_params: Additional provider-specific parameters
    """
    provider: LLMProviderType
    api_key: str
    model: str
    base_url: str
    max_retries: int = 3
    timeout: int = 300
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def anthropic(
        cls,
        api_key: str,
        model: str = "anthropic/claude-sonnet-4",
        base_url: str = "https://cst-ai-proxy.paytm.com"
    ) -> "LLMConfig":
        """Create configuration for Anthropic (via proxy)."""
        return cls(
            provider=LLMProviderType.ANTHROPIC,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
    
    @classmethod
    def truefoundry(
        cls,
        api_key: str,
        model: str = "pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0",
        base_url: str = "https://tfy.internal.ap-south-1.production.apps.pai.mypaytm.com/api/llm/api/inference/openai"
    ) -> "LLMConfig":
        """Create configuration for TrueFoundry (OpenAI-compatible)."""
        return cls(
            provider=LLMProviderType.TRUEFOUNDRY,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
    
    @classmethod
    def openai(
        cls,
        api_key: str,
        model: str = "gpt-4",
        base_url: str = "https://api.openai.com/v1"
    ) -> "LLMConfig":
        """Create configuration for OpenAI (direct)."""
        return cls(
            provider=LLMProviderType.OPENAI,
            api_key=api_key,
            model=model,
            base_url=base_url
        )
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        """
        Create configuration from environment variables.
        
        Environment variables:
            LLM_PROVIDER: Provider type (anthropic, truefoundry, openai)
            LLM_API_KEY: API key or bearer token
            LLM_MODEL: Model identifier
            LLM_BASE_URL: API endpoint URL
            LLM_MAX_RETRIES: Maximum retry attempts (default: 3)
            LLM_TIMEOUT: Request timeout in seconds (default: 300)
        """
        provider_str = os.getenv("LLM_PROVIDER", "anthropic").lower()
        api_key = os.getenv("LLM_API_KEY", "")
        
        # Map provider string to enum
        provider_map = {
            "anthropic": LLMProviderType.ANTHROPIC,
            "truefoundry": LLMProviderType.TRUEFOUNDRY,
            "openai": LLMProviderType.OPENAI,
            "custom": LLMProviderType.CUSTOM,
        }
        provider = provider_map.get(provider_str, LLMProviderType.ANTHROPIC)
        
        # Get provider-specific defaults
        if provider == LLMProviderType.ANTHROPIC:
            default_model = "anthropic/claude-sonnet-4"
            default_base_url = "https://cst-ai-proxy.paytm.com"
        elif provider == LLMProviderType.TRUEFOUNDRY:
            default_model = "pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0"
            default_base_url = "https://tfy.internal.ap-south-1.production.apps.pai.mypaytm.com/api/llm/api/inference/openai"
        elif provider == LLMProviderType.OPENAI:
            default_model = "gpt-4"
            default_base_url = "https://api.openai.com/v1"
        else:
            default_model = ""
            default_base_url = ""
        
        model = os.getenv("LLM_MODEL", default_model)
        base_url = os.getenv("LLM_BASE_URL", default_base_url)
        max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        timeout = int(os.getenv("LLM_TIMEOUT", "300"))
        
        return cls(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout
        )


class LLMProvider:
    """
    Wrapper class for LLM providers that handles DSPy integration.
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._lm: Optional[dspy.LM] = None
    
    def get_dspy_lm(self) -> dspy.LM:
        """
        Get a DSPy Language Model instance configured for the provider.
        """
        if self._lm is not None:
            return self._lm
        
        if self.config.provider == LLMProviderType.TRUEFOUNDRY:
            # TrueFoundry uses OpenAI-compatible endpoint
            self._lm = dspy.LM(
                model=f"openai/{self.config.model}",
                api_key=self.config.api_key,
                api_base=self.config.base_url,
                max_tokens=4096,
                temperature=0.1,
            )
            logger.info(f"Initialized TrueFoundry LM: {self.config.model}")
            
        elif self.config.provider == LLMProviderType.ANTHROPIC:
            # Anthropic via LiteLLM proxy (cst-ai-proxy)
            # The proxy expects the model in format: anthropic/claude-sonnet-4
            self._lm = dspy.LM(
                model=self.config.model,  # e.g., anthropic/claude-sonnet-4
                api_key=self.config.api_key,  # Must start with 'sk-'
                api_base=self.config.base_url,  # https://cst-ai-proxy.paytm.com
                max_tokens=4096,
                temperature=0.1,
            )
            logger.info(f"Initialized Anthropic LM via LiteLLM proxy: {self.config.model}")
            
        elif self.config.provider == LLMProviderType.OPENAI:
            # Direct OpenAI
            self._lm = dspy.LM(
                model=f"openai/{self.config.model}",
                api_key=self.config.api_key,
                api_base=self.config.base_url,
                max_tokens=4096,
                temperature=0.1,
            )
            logger.info(f"Initialized OpenAI LM: {self.config.model}")
            
        else:
            # Custom provider - try OpenAI-compatible
            self._lm = dspy.LM(
                model=f"openai/{self.config.model}",
                api_key=self.config.api_key,
                api_base=self.config.base_url,
                max_tokens=4096,
                temperature=0.1,
            )
            logger.info(f"Initialized Custom LM: {self.config.model}")
        
        return self._lm
    
    def configure_dspy(self) -> None:
        """Configure DSPy to use this provider's LM."""
        lm = self.get_dspy_lm()
        dspy.configure(lm=lm)
        logger.info("DSPy configured with LLM provider")


def get_llm_provider(config: Optional[LLMConfig] = None) -> LLMProvider:
    """
    Get an LLM provider instance.
    
    Args:
        config: Optional LLMConfig. If not provided, loads from environment.
    
    Returns:
        Configured LLMProvider instance
    """
    if config is None:
        config = LLMConfig.from_env()
    return LLMProvider(config)


def configure_dspy_from_env() -> None:
    """
    Configure DSPy using environment variables.
    Thread-safe singleton pattern.
    """
    global _dspy_lm
    
    with _dspy_lock:
        if _dspy_lm is not None:
            return  # Already configured
        
        config = LLMConfig.from_env()
        provider = LLMProvider(config)
        _dspy_lm = provider.get_dspy_lm()
        dspy.configure(lm=_dspy_lm)
        
        logger.info(
            f"DSPy configured - Provider: {config.provider.value}, "
            f"Model: {config.model}, Base URL: {config.base_url}"
        )


def get_dspy_lm() -> dspy.LM:
    """
    Get the configured DSPy LM instance.
    Configures from environment if not already configured.
    """
    global _dspy_lm
    
    with _dspy_lock:
        if _dspy_lm is None:
            configure_dspy_from_env()
        return _dspy_lm


def reset_provider() -> None:
    """Reset the provider (useful for testing or reconfiguration)."""
    global _dspy_lm
    
    with _dspy_lock:
        _dspy_lm = None
        logger.info("LLM provider reset")


# Convenience function for backward compatibility
def get_llm_settings() -> Dict[str, str]:
    """Get LLM settings as a dictionary (for backward compatibility)."""
    config = LLMConfig.from_env()
    return {
        "provider": config.provider.value,
        "api_key": config.api_key,
        "model": config.model,
        "base_url": config.base_url,
    }
