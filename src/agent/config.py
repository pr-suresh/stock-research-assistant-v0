"""
Configuration for the agent module.

Handles environment variables, API keys, and agent settings.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for the stock research agent."""

    # OpenAI settings (inherited from existing config)
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 1000

    # Agent-specific settings
    max_iterations: int = 10  # Max reasoning steps
    enable_cache: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes default

    # API rate limiting
    yfinance_timeout: int = 10  # seconds
    max_retries: int = 3

    # Logging
    verbose: bool = False
    log_reasoning_steps: bool = True

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create config from environment variables."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return cls(
            openai_api_key=openai_api_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
            openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "10")),
            enable_cache=os.getenv("AGENT_ENABLE_CACHE", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("AGENT_CACHE_TTL", "300")),
            yfinance_timeout=int(os.getenv("YFINANCE_TIMEOUT", "10")),
            max_retries=int(os.getenv("AGENT_MAX_RETRIES", "3")),
            verbose=os.getenv("AGENT_VERBOSE", "false").lower() == "true",
            log_reasoning_steps=os.getenv("AGENT_LOG_STEPS", "true").lower() == "true",
        )


# Global config instance
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get or create the global agent configuration."""
    global _config
    if _config is None:
        _config = AgentConfig.from_env()
    return _config


def reset_config():
    """Reset the global configuration (useful for testing)."""
    global _config
    _config = None
