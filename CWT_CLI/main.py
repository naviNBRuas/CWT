import argparse
import logging
import os
import signal
import sys
from .config import load_config, validate_config, ConfigError
from .logger import setup_logging
from .withdrawal_manager import WithdrawalManager
from .nft_manager import NFTManager

def main():
    parser = argparse.ArgumentParser(description="Crypto Withdrawal Tool (CWT)")
    parser.add_argument("--config", default="config.ini", help="Path to the configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__)

    logger.info("Starting CWT...")

    config_path = os.path.join(os.path.dirname(__file__), args.config)
    try:
        config = load_config(config_path)
        validate_config(config)
    except ConfigError as e:
        logger.error(f"Configuration error: {e}. Exiting.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during configuration loading or validation: {e}. Exiting.")
        sys.exit(1)

    logger.info("Configuration loaded and validated successfully.")

    manager = WithdrawalManager(config)

    # Register signal handler for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Termination signal received. Initiating graceful shutdown...")
        manager.close_all_automators()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # --- Demonstrate NFTManager usage ---
    nft_manager = NFTManager(config)
    mock_contract_address = "0x1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b"
    mock_token_id = 123
    nft_metadata = nft_manager.get_nft_metadata(mock_contract_address, mock_token_id)
    if nft_metadata and "image" in nft_metadata:
        logger.info(f"NFT Metadata: {nft_metadata}")
        # Create a directory to save NFT images if it doesn't exist
        nft_images_dir = os.path.join(os.path.dirname(__file__), "nft_images")
        os.makedirs(nft_images_dir, exist_ok=True)
        image_path = os.path.join(nft_images_dir, f"nft_{mock_token_id}.png")
        nft_manager.download_nft_image(nft_metadata["image"], image_path)
    else:
        logger.warning("Could not retrieve NFT metadata or image URL.")

    manager.process_withdrawals()

    logger.info("CWT finished.")

if __name__ == "__main__":
    main()
