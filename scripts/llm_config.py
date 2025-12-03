"""
Centralized LLM Configuration Module

This module provides a unified interface for LLM configuration,
supporting multiple providers (Anthropic, TrueFoundry, OpenAI).

Usage:
    from llm_config import get_lm, configure_dspy
    
    # Configure DSPy globally (only needed once)
    configure_dspy()
    
    # Or get the LM instance directly
    lm = get_lm()

For provider-specific configuration, use llm_provider module:
    from llm_provider import LLMConfig, get_llm_provider
    
    config = LLMConfig.truefoundry(api_key="...", model="...")
    provider = get_llm_provider(config)
"""
import logging
from typing import Optional

import dspy

# Import from the provider module
from llm_provider import (
    LLMConfig,
    LLMProvider,
    LLMProviderType,
    get_llm_provider,
    configure_dspy_from_env,
    reset_provider,
    get_dspy_lm,
)

logger = logging.getLogger(__name__)

# Re-export for convenience
__all__ = [
    'LLMConfig',
    'LLMProvider', 
    'LLMProviderType',
    'get_llm_provider',
    'get_lm',
    'configure_dspy',
    'get_llm_settings',
    'reset_lm',
]


def get_lm(force_new: bool = False) -> dspy.LM:
    """
    Get a DSPy LM instance.
    
    Args:
        force_new: If True, create a new instance (ignores singleton).
    
    Returns:
        Configured dspy.LM instance
    """
    if force_new:
        reset_provider()
    return get_dspy_lm()


def configure_dspy(force: bool = False) -> None:
    """
    Configure DSPy with the LLM provider.
    
    Args:
        force: If True, reconfigure even if already configured.
    """
    if force:
        reset_provider()
    configure_dspy_from_env()


def get_llm_settings() -> LLMConfig:
    """Get the current LLM configuration."""
    return LLMConfig.from_env()


def reset_lm() -> None:
    """Reset the LM instance. Useful for testing."""
    reset_provider()


def create_extractor(signature_class: type, use_chain_of_thought: bool = True):
    """
    Create a DSPy extractor for a given signature.
    
    Args:
        signature_class: The DSPy Signature class to use
        use_chain_of_thought: Whether to use ChainOfThought (default) or Predict
    
    Returns:
        Configured DSPy module
    """
    configure_dspy()
    
    if use_chain_of_thought:
        return dspy.ChainOfThought(signature_class)
    return dspy.Predict(signature_class)
