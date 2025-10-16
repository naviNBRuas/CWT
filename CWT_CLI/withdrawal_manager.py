import logging
import importlib
from .config import get_config_value

logger = logging.getLogger(__name__)

class WithdrawalManager:
    def __init__(self, config):
        self.config = config
        self.automators = {}
        self.main_withdrawal_address = get_config_value(self.config, "DEFAULT", "main_withdrawal_address")
        if not self.main_withdrawal_address:
            logger.error("Main withdrawal address not found in DEFAULT section of config. Exiting.")
            raise ValueError("Main withdrawal address is required.")
        self._load_automators()

    def _load_automators(self):
        for section in self.config.sections():
            if section.startswith("EXCHANGE_"):
                exchange_name = section
                automator_type = get_config_value(self.config, exchange_name, 'type')
                if not automator_type:
                    logger.warning(f"No 'type' specified for {exchange_name}. Skipping automator loading.")
                    continue

                try:
                    # Dynamically import the automator class
                    module = importlib.import_module(f".exchange_automators.{automator_type.lower()}_automator", package='CWT_CLI')
                    automator_class = getattr(module, automator_type)
                    self.automators[exchange_name] = automator_class(self.config, exchange_name)
                    logger.info(f"Loaded automator {automator_type} for {exchange_name}")
                except (ImportError, AttributeError) as e:
                    logger.error(f"Failed to load automator {automator_type} for {exchange_name}: {e}")
                except Exception as e:
                    logger.error(f"An unexpected error occurred while loading automator {automator_type} for {exchange_name}: {e}")

    def process_withdrawals(self):
        logger.info("Starting withdrawal process...")
        if not self.automators:
            logger.warning("No automators loaded. Exiting withdrawal process.")
            return

        for exchange_name, automator in self.automators.items():
            currency = get_config_value(self.config, exchange_name, 'currency')
            amount = get_config_value(self.config, exchange_name, 'amount')

            if not all([currency, amount]):
                logger.warning(f"Skipping {exchange_name}: Missing currency or amount in configuration. Closing automator.")
                automator.close()
                continue

            try:
                logger.info(f"Attempting to log into {exchange_name}...")
                if automator.login():
                    logger.info(f"Successfully logged into {exchange_name}. Attempting withdrawal...")
                    if automator.withdraw(currency, float(amount), self.main_withdrawal_address):
                        logger.info(f"Withdrawal of {amount} {currency} from {exchange_name} to {self.main_withdrawal_address} successful (simulated).")
                        # Fallback logic: if successful, we can potentially stop or mark as done
                    else:
                        logger.error(f"Withdrawal from {exchange_name} failed (simulated). Trying next if available.")
                else:
                    logger.error(f"Login failed for {exchange_name}. Skipping withdrawal and trying next if available.")
            except Exception as e:
                logger.error(f"An error occurred during withdrawal from {exchange_name}: {e}. Trying next if available.")
            finally:
                automator.close()
        logger.info("Withdrawal process finished.")