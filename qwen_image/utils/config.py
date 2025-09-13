"""
Configuration management for Qwen Image API.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from .exceptions import QwenAPIConfigurationError

class QwenAPIConfig:
    """Configuration class for Qwen Image API."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file. If None, will look for .env in current directory.
        """
        # Load environment variables
        if env_file:
            load_dotenv(dotenv_path=env_file)
        else:
            # Try to load .env file from the current directory first
            env_path = Path(__file__).parent.parent / '.env'
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
            else:
                # Fallback to default behavior
                load_dotenv()
        
        self._api_key = self._get_api_key()
        self._validate_config()
    
    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if api_key:
            # Strip any extra quotes or whitespace
            return api_key.strip().strip('"\'')
        return None
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if not self._api_key:
            raise QwenAPIConfigurationError(
                "DASHSCOPE_API_KEY environment variable not set. "
                "Please set it before using this node."
            )
    
    @property
    def api_key(self) -> str:
        """Get the API key."""
        return self._api_key
    
    @property
    def t2i_api_url(self) -> str:
        """Get the text-to-image API URL."""
        return "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    @property
    def i2i_api_url(self) -> str:
        """Get the image-to-image API URL."""
        return "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"