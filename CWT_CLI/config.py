import configparser
import os
import logging

logger = logging.getLogger(__name__)

def load_config(config_path):
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        return None
    try:
        config.read(config_path)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        return None

def get_config_value(config, section, key, default=None):
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        logger.warning(f"Configuration key '{key}' not found in section '{section}'. Using default: {default}")
        return default
