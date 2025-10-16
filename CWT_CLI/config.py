import configparser
import os
import logging

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass

def load_config(config_path):
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        raise ConfigError(f"Configuration file not found: {config_path}")
    try:
        config.read(config_path)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration from {config_path}: {e}")
        raise ConfigError(f"Error loading configuration from {config_path}: {e}")

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

def get_browser_profile_path(config, section, default_path=None):
    env_var_name = f"CWT_{section.upper()}_BROWSER_PROFILE_PATH"
    env_value = os.getenv(env_var_name)
    if env_value:
        logger.debug(f"Using browser profile path from environment variable: {env_var_name}")
        return env_value
    
    config_value = get_config_value(config, section, "browser_profile_path", default=default_path)
    if config_value:
        logger.debug(f"Using browser profile path from config: {config_value}")
        return config_value
    
    logger.warning(f"No browser profile path found for section {section}. Using default: {default_path}")
    return default_path

def get_chrome_binary_location(config, section, default_location=None):
    env_var_name = "CWT_CHROME_BINARY_LOCATION"
    env_value = os.getenv(env_var_name)
    if env_value:
        logger.debug(f"Using Chrome binary location from environment variable: {env_var_name}")
        return env_value
    
    config_value = get_config_value(config, section, "chrome_binary_location", default=default_location)
    if config_value:
        logger.debug(f"Using Chrome binary location from config: {config_value}")
        return config_value
    
    logger.debug(f"No Chrome binary location found for section {section}. Using default: {default_location}")
    return default_location

def get_credential(config, section, key, default=None):
    env_var_name = f"CWT_{section.upper()}_{key.upper()}"
    env_value = os.getenv(env_var_name)
    if env_value:
        logger.debug(f"Using credential '{key}' from environment variable: {env_var_name}")
        return env_value
    
    config_value = get_config_value(config, section, key, default=default)
    if config_value:
        logger.debug(f"Using credential '{key}' from config: {config_value}")
        return config_value
    
    logger.warning(f"Credential '{key}' not found for section '{section}'. Using default: {default}")
    return default

def get_headless_mode(config, section, default_headless=True):
    env_var_name = "CWT_HEADLESS_MODE"
    env_value = os.getenv(env_var_name)
    if env_value is not None:
        logger.debug(f"Using headless mode from environment variable: {env_var_name}")
        return env_value.lower() == 'true'
    
    config_value = get_config_value(config, section, "headless", default=str(default_headless))
    if config_value is not None:
        logger.debug(f"Using headless mode from config: {config_value}")
        return str(config_value).lower() == 'true'
    
    logger.debug(f"No headless mode setting found for section {section}. Using default: {default_headless}")
    return default_headless

def validate_config(config):
    # Validate DEFAULT section
    main_withdrawal_address = get_config_value(config, "DEFAULT", "main_withdrawal_address")
    if not main_withdrawal_address:
        raise ConfigError("'main_withdrawal_address' is missing in the [DEFAULT] section or CWT_MAIN_WITHDRAWAL_ADDRESS environment variable.")

    # Validate each automator section
    for section in config.sections():
        if section.startswith("EXCHANGE_") or section.endswith("_WALLET"):
            automator_type = get_config_value(config, section, 'type')
            if not automator_type:
                raise ConfigError(f"'type' is missing for section [{section}].")
            
            # Basic validation for credentials (username/password) if applicable
            if automator_type not in ["MetamaskAutomator"]:
                username = get_credential(config, section, 'username')
                password = get_credential(config, section, 'password')
                if not username or not password:
                    logger.warning(f"Username or password missing for section [{section}]. Ensure they are set via config or environment variables.")
            else: # Metamask specific validation
                password = get_credential(config, section, 'password')
                if not password:
                    raise ConfigError(f"'password' is missing for Metamask wallet [{section}].")

            currency = get_config_value(config, section, 'currency')
            amount = get_config_value(config, section, 'amount')
            if not currency or not amount:
                logger.warning(f"Currency or amount missing for section [{section}].")
            try:
                if amount: float(amount) # Check if amount is a valid float
            except ValueError:
                raise ConfigError(f"'amount' for section [{section}] is not a valid number.")

    logger.info("Configuration validated successfully.")

def validate_config(config):
    # Validate DEFAULT section
    main_withdrawal_address = get_config_value(config, "DEFAULT", "main_withdrawal_address")
    if not main_withdrawal_address:
        raise ConfigError("'main_withdrawal_address' is missing in the [DEFAULT] section or CWT_MAIN_WITHDRAWAL_ADDRESS environment variable.")

    # Validate each automator section
    for section in config.sections():
        if section.startswith("EXCHANGE_") or section.endswith("_WALLET"):
            automator_type = get_config_value(config, section, 'type')
            if not automator_type:
                raise ConfigError(f"'type' is missing for section [{section}].")
            
            # Basic validation for credentials (username/password) if applicable
            if automator_type not in ["MetamaskAutomator"]:
                username = get_credential(config, section, 'username')
                password = get_credential(config, section, 'password')
                if not username or not password:
                    logger.warning(f"Username or password missing for section [{section}]. Ensure they are set via config or environment variables.")
            else: # Metamask specific validation
                password = get_credential(config, section, 'password')
                if not password:
                    raise ConfigError(f"'password' is missing for Metamask wallet [{section}].")

            currency = get_config_value(config, section, 'currency')
            amount = get_config_value(config, section, 'amount')
            if not currency or not amount:
                logger.warning(f"Currency or amount missing for section [{section}].")
            try:
                if amount: float(amount) # Check if amount is a valid float
            except ValueError:
                raise ConfigError(f"'amount' for section [{section}] is not a valid number.")

    logger.info("Configuration validated successfully.")
