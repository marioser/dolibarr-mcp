"""Configuration management for Dolibarr MCP Server."""

import os
from typing import Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Configuration for Dolibarr MCP Server."""
    
    dolibarr_url: str = Field(
        description="Dolibarr API URL",
        default_factory=lambda: os.getenv("DOLIBARR_URL", "")
    )
    
    api_key: str = Field(
        description="Dolibarr API key",
        default_factory=lambda: os.getenv("DOLIBARR_API_KEY", "")
    )
    
    log_level: str = Field(
        description="Logging level",
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    
    def validate_config(self) -> None:
        """Validate that required configuration is present."""
        if not self.dolibarr_url:
            raise ValueError("DOLIBARR_URL environment variable is required")
        
        if not self.api_key:
            raise ValueError("DOLIBARR_API_KEY environment variable is required")
        
        if not self.dolibarr_url.startswith(('http://', 'https://')):
            raise ValueError("DOLIBARR_URL must start with http:// or https://")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        config = cls()
        config.validate_config()
        return config
