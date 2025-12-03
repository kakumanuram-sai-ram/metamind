# LLM Provider Configuration Guide

## Overview

MetaMind now supports multiple LLM providers through a flexible, decoupled configuration system.

## Supported Providers

| Provider | Type | Status |
|----------|------|--------|
| TrueFoundry | OpenAI-compatible | Default |
| Anthropic (via proxy) | Direct | Legacy |
| OpenAI | Direct | Supported |

## Configuration

### Environment Variables

Set these in your `.env` file or export them:

```bash
# Provider selection (truefoundry, anthropic, openai)
export LLM_PROVIDER=truefoundry

# API credentials
export LLM_API_KEY=your_api_key_or_token

# Model (provider-specific)
export LLM_MODEL=pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0

# Endpoint URL
export LLM_BASE_URL=https://tfy.internal.ap-south-1.production.apps.pai.mypaytm.com/api/llm/api/inference/openai
```

### TrueFoundry Setup

1. Get your JWT token from TrueFoundry console
2. Set environment variables:

```bash
export LLM_PROVIDER=truefoundry
export LLM_API_KEY="eyJhbGciOi...your_jwt_token"
export LLM_MODEL=pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0
export LLM_BASE_URL=https://tfy.internal.ap-south-1.production.apps.pai.mypaytm.com/api/llm/api/inference/openai
```

### Anthropic Setup (Legacy)

```bash
export LLM_PROVIDER=anthropic
export LLM_API_KEY="your_anthropic_api_key"
export LLM_MODEL=anthropic/claude-sonnet-4
export LLM_BASE_URL=https://cst-ai-proxy.paytm.com
```

## Architecture

```
┌─────────────────────┐
│   Application       │
│  (llm_extractor.py) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    llm_config.py    │ ◄── Centralized interface
│  (configure_dspy)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   llm_provider.py   │ ◄── Provider abstraction
│  (LLMProvider,      │
│   LLMConfig)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│           DSPy LM                    │
├──────────┬──────────┬───────────────┤
│TrueFoundry│ Anthropic│   OpenAI     │
│(OpenAI-  │  (Proxy)  │  (Direct)    │
│compatible)│          │              │
└──────────┴──────────┴───────────────┘
```

## Files Modified

| File | Purpose |
|------|---------|
| `scripts/llm_provider.py` | Provider abstraction layer |
| `scripts/llm_config.py` | Centralized DSPy configuration |
| `scripts/config.py` | Environment variable loading |
| `scripts/dspy_extractors.py` | Factory for DSPy extractors |
| `env.example` | Template for environment variables |

## Usage in Code

### Option 1: Auto-configure from Environment

```python
from llm_config import configure_dspy

# Configure DSPy once at startup
configure_dspy()

# Use DSPy as normal
import dspy
predictor = dspy.Predict(MySignature)
result = predictor(input="...")
```

### Option 2: Manual Configuration

```python
from llm_provider import LLMConfig, get_llm_provider

# Create specific provider config
config = LLMConfig.truefoundry(
    api_key="your_token",
    model="pi-agentic/us-anthropic-claude-sonnet-4-20250514-v1-0"
)

provider = get_llm_provider(config)
provider.configure_dspy()
```

### Option 3: Use Pre-configured Extractors

```python
from dspy_extractors import Extractors

# Get pre-configured extractors (auto-configures DSPy)
extractor = Extractors.table_column()
result = extractor(sql_query="...", chart_metadata="...")
```

## Adding a New Provider

To add a new LLM provider:

1. Add to `LLMProviderType` enum in `llm_provider.py`:

```python
class LLMProviderType(Enum):
    TRUEFOUNDRY = "truefoundry"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    NEW_PROVIDER = "new_provider"  # Add new provider
```

2. Add factory method to `LLMConfig` class:

```python
@classmethod
def new_provider(
    cls,
    api_key: str,
    model: str = "default-model",
    base_url: str = "https://api.newprovider.com/v1"
) -> "LLMConfig":
    """Create configuration for New Provider."""
    return cls(
        provider=LLMProviderType.NEW_PROVIDER,
        api_key=api_key,
        model=model,
        base_url=base_url
    )
```

3. Add DSPy LM initialization in `LLMProvider.get_dspy_lm()`:

```python
elif self.config.provider == LLMProviderType.NEW_PROVIDER:
    self._lm = dspy.LM(
        model=f"openai/{self.config.model}",  # or appropriate prefix
        api_key=self.config.api_key,
        api_base=self.config.base_url,
        max_tokens=4096,
        temperature=0.1,
    )
```

4. Update `LLMConfig.from_env()` with new defaults if needed.

## Testing

Test the configuration with:

```bash
python scripts/test_truefoundry.py
```

**Note**: The TrueFoundry endpoint is an internal URL. Ensure you're on the Paytm network or VPN before testing.

## Troubleshooting

### Connection Timeout

If you see connection timeouts, ensure:
1. You're on the correct network/VPN
2. The endpoint URL is correct
3. Your API key/token is valid

### Invalid API Key

If you see 401/403 errors:
1. Check your token hasn't expired
2. Ensure the token has necessary permissions
3. Verify the model name is correct

### DSPy Configuration Errors

If DSPy fails to configure:
1. Ensure environment variables are set
2. Check `llm_provider.py` for any import errors
3. Verify DSPy is installed: `pip install dspy-ai`


