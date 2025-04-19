#!/usr/bin/env python3

# Config File to add the OPENAI API key and other configurations

import os
import sys
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("code-reviewer")

class Config:
    """Configuration manager for Code Reviewer."""

    def __init__(self, config_path: str):
        """Initialize the configuration manager.

        Args:
            config_path: Path to the config file
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from the config file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found at {self.config_path}. Using default configuration.")
            return {
                "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
                "model": "gpt-4o",
                "temperature": 0.1,
                "max_file_size": 100000,  # 100KB
                "max_files": 100,
            }

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            sys.exit(1)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: The configuration key
            default: Default value if key is not found

        Returns:
            The configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: The configuration key
            value: The configuration value
        """
        self.config[key] = value

    def save(self) -> None:
        """Save the configuration to the config file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            sys.exit(1)

    def update(self, new_config: Dict[str, Any]) -> None:
        """Update multiple configuration values.

        Args:
            new_config: Dictionary of new configuration values
        """
        self.config.update(new_config)
