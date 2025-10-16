import configparser
import os
import logging

logger = logging.getLogger(__name__)

def load_config(config_path):
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        # Create an empty config object if file not found, so we can still check env vars
        return config
    try:
        config.read(config_path)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        return None

def get_config_value(config, section, key, default=None):
    # Prioritize environment variables for sensitive keys like main_withdrawal_address
    if key == "main_withdrawal_address":
        env_var_name = "CWT_MAIN_WITHDRAWAL_ADDRESS"
        env_value = os.getenv(env_var_name)
        if env_value:
            logger.debug(f"Using {env_var_name} from environment variables.")
            return env_value

    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        logger.warning(f"Configuration key '{key}' not found in section '{section}'. Using default: {default}")
        return default
