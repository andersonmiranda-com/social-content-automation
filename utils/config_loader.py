"""
Configuration loader for YAML files.
"""

import os
from pathlib import Path

import yaml


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

    return config
