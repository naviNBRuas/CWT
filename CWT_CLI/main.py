import argparse
import logging
import os
from .config import load_config
from .logger import setup_logging
from .withdrawal_manager import WithdrawalManager

def main():
    parser = argparse.ArgumentParser(description="Crypto Withdrawal Tool (CWT)")
    parser.add_argument("--config", default="config.ini", help="Path to the configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__)

    logger.info("Starting CWT...")

    config_path = os.path.join(os.path.dirname(__file__), args.config)
    config = load_config(config_path)

    if not config:
        logger.error(f"Failed to load configuration from {config_path}. Exiting.")
        return

    logger.info("Configuration loaded successfully.")

    manager = WithdrawalManager(config)
    manager.process_withdrawals()

    logger.info("CWT finished.")

if __name__ == "__main__":
    main()
