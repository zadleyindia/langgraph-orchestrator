"""
Flexible LLM Configuration System
Supports multiple LLM providers and easy switching
"""

import os
from typing import Any, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.language_model import BaseLanguageModel
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class LLMConfig:
    """Central configuration for LLM providers"""
    
    # Supported providers
    PROVIDERS = {
        "openai": {
            "class": ChatOpenAI,
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "env_key": "OPENAI_API_KEY"
        },
        "anthropic": {
            "class": ChatAnthropic,
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "env_key": "ANTHROPIC_API_KEY"
        },
        "google": {
            "class": ChatGoogleGenerativeAI,
            "models": ["gemini-pro", "gemini-pro-vision"],
            "env_key": "GOOGLE_API_KEY"
        }
    }
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.model = os.getenv("LLM_MODEL", "gpt-4")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate the LLM configuration"""
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Supported: {list(self.PROVIDERS.keys())}")
        
        provider_info = self.PROVIDERS[self.provider]
        api_key = os.getenv(provider_info["env_key"])
        
        if not api_key:
            raise ValueError(f"Missing API key for {self.provider}. Please set {provider_info['env_key']} in .env")
        
        if self.model not in provider_info["models"]:
            logger.warning(f"Model {self.model} not in predefined list for {self.provider}. Proceeding anyway.")
    
    def get_llm(self, **kwargs) -> BaseLanguageModel:
        """
        Get configured LLM instance
        
        Args:
            **kwargs: Additional parameters to override defaults
            
        Returns:
            Configured LLM instance
        """
        provider_info = self.PROVIDERS[self.provider]
        llm_class = provider_info["class"]
        api_key = os.getenv(provider_info["env_key"])
        
        # Default parameters
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # Provider-specific parameters
        if self.provider == "openai":
            params["api_key"] = api_key
        elif self.provider == "anthropic":
            params["anthropic_api_key"] = api_key
        elif self.provider == "google":
            params["google_api_key"] = api_key
            params["model"] = params.pop("model")  # Google uses 'model' not 'model_name'
        
        # Override with any provided kwargs
        params.update(kwargs)
        
        logger.info(f"Creating {self.provider} LLM with model {params.get('model', self.model)}")
        return llm_class(**params)
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration information"""
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "available_providers": list(self.PROVIDERS.keys()),
            "available_models": self.PROVIDERS[self.provider]["models"]
        }


# Global configuration instance
llm_config = LLMConfig()


def get_default_llm(**kwargs) -> BaseLanguageModel:
    """
    Get the default configured LLM
    
    Args:
        **kwargs: Additional parameters to override defaults
        
    Returns:
        Configured LLM instance
    """
    return llm_config.get_llm(**kwargs)


def switch_provider(provider: str, model: Optional[str] = None):
    """
    Switch to a different LLM provider
    
    Args:
        provider: New provider name
        model: Optional model name (uses default if not provided)
    """
    global llm_config
    
    # Update environment variables
    os.environ["LLM_PROVIDER"] = provider
    if model:
        os.environ["LLM_MODEL"] = model
    
    # Recreate configuration
    llm_config = LLMConfig()
    logger.info(f"Switched to {provider} provider" + (f" with model {model}" if model else ""))


def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """Get information about all available providers"""
    return LLMConfig.PROVIDERS