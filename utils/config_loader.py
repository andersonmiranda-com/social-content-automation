"""
Configuration loader for YAML files.
"""

import os
from pathlib import Path
import re
import yaml

from utils.logger import setup_logger

logger = setup_logger(__name__)

CONFIG_CACHE = {}


def _replace_env_vars(config: dict) -> dict:
    """Recursively replaces environment variable placeholders in the config."""
    env_var_pattern = re.compile(r"\$\{(.*?)\}")

    for key, value in config.items():
        if isinstance(value, str):
            match = env_var_pattern.match(value)
            if match:
                env_var_name = match.group(1)
                env_var_value = os.getenv(env_var_name)
                if env_var_value is None:
                    logger.warning(f"Environment variable '{env_var_name}' not found.")
                config[key] = env_var_value
        elif isinstance(value, dict):
            _replace_env_vars(value)
    return config


def load_config(config_name: str) -> dict:
    """
    Loads a specific YAML configuration file from the 'configs' directory,
    and merges it with the 'defaults.yaml' configuration.

    Args:
        config_name: The base name of the configuration file (e.g., 'generate_text').

    Returns:
        A dictionary containing the merged configuration.
    """
    config_path = Path("configs")

    # Load default configuration
    defaults_file = config_path / "defaults.yaml"
    if defaults_file.exists():
        with open(defaults_file, "r") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    # Load specific configuration and merge it
    specific_file = config_path / f"{config_name}.yaml"
    if specific_file.exists():
        with open(specific_file, "r") as f:
            specific_config = yaml.safe_load(f) or {}
        config.update(specific_config)

    return _replace_env_vars(config)
