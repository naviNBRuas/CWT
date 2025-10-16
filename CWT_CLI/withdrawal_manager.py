import logging
import importlib
import re
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

from .config import get_config_value

logger = logging.getLogger(__name__)

def _camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

@dataclass
class WithdrawalTask:
    currency: str
    amount: float
    destination_address: str
    source_automators: List[str] = field(default_factory=list) # List of automator names to try
    current_attempt: int = 0
    max_attempts: int = 3
    status: str = "PENDING"
    message: str = ""

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
            if section.startswith("EXCHANGE_") or section.endswith("_WALLET"):
                exchange_name = section
                automator_type = get_config_value(self.config, exchange_name, 'type')
                if not automator_type:
                    logger.warning(f"No 'type' specified for {exchange_name}. Skipping automator loading.")
                    continue

                try:
                    module_name = _camel_to_snake(automator_type)
                    module = importlib.import_module(f".exchange_automators.{module_name}", package='CWT_CLI')
                    automator_class = getattr(module, automator_type)
                    self.automators[exchange_name] = automator_class(self.config, exchange_name)
                    logger.info(f"Loaded automator {automator_type} for {exchange_name}")
                except (ImportError, AttributeError) as e:
                    logger.error(f"Failed to load automator {automator_type} for {exchange_name}: {e}")
                except Exception as e:
                    logger.error(f"An unexpected error occurred while loading automator {automator_type} for {exchange_name}: {e}")

    def _execute_withdrawal_attempt(self, automator_name, automator, task: WithdrawalTask) -> bool:
        """Executes a single withdrawal attempt for a given automator and task."""
        logger.info(f"Attempting withdrawal from {automator_name} for {task.amount} {task.currency} to {task.destination_address} (Attempt {task.current_attempt + 1}/{task.max_attempts})...")
        try:
            if automator.login():
                logger.info(f"Successfully logged into {automator_name}. Initiating withdrawal...")
                if automator.withdraw(task.currency, task.amount, task.destination_address):
                    logger.info(f"Withdrawal from {automator_name} successful (simulated).")
                    task.status = "COMPLETED"
                    task.message = "Withdrawal successful"
                    return True
                else:
                    task.message = "Withdrawal failed at automator level"
                    logger.error(f"Withdrawal from {automator_name} failed (simulated). {task.message}")
            else:
                task.message = "Login failed"
                logger.error(f"Login failed for {automator_name}. {task.message}")
        except Exception as e:
            task.message = f"An error occurred: {e}"
            logger.error(f"An error occurred during withdrawal from {automator_name}: {e}")
        finally:
            automator.close()
        return False

    def process_withdrawals(self):
        logger.info("Starting withdrawal process...")
        if not self.automators:
            logger.warning("No automators loaded. Exiting withdrawal process.")
            return

        withdrawal_tasks: List[WithdrawalTask] = []
        # Populate withdrawal tasks from config
        for exchange_name in self.automators.keys():
            currency = get_config_value(self.config, exchange_name, 'currency')
            amount = get_config_value(self.config, exchange_name, 'amount')
            
            if not all([currency, amount]):
                logger.warning(f"Skipping task creation for {exchange_name}: Missing currency or amount in configuration.")
                continue
            
            withdrawal_tasks.append(WithdrawalTask(
                currency=currency,
                amount=float(amount),
                destination_address=self.main_withdrawal_address,
                source_automators=[exchange_name] # For now, each task has one source
            ))

        final_successful_withdrawals = []
        final_failed_withdrawals = []

        for task in withdrawal_tasks:
            logger.info(f"Processing withdrawal task for {task.amount} {task.currency}...")
            task_completed = False
            for automator_name in task.source_automators:
                if automator_name not in self.automators:
                    logger.warning(f"Automator {automator_name} not loaded. Skipping for this task.")
                    continue

                automator = self.automators[automator_name]
                for attempt in range(task.max_attempts):
                    task.current_attempt = attempt
                    if self._execute_withdrawal_attempt(automator_name, automator, task):
                        task_completed = True
                        break # Break from retry loop
                    else:
                        logger.warning(f"Attempt {attempt + 1} failed for {automator_name}. Retrying in 5 seconds...")
                        time.sleep(5) # Simple backoff
                
                if task_completed:
                    break # Break from automator loop if task completed
            
            if task_completed:
                final_successful_withdrawals.append(task)
            else:
                task.status = "FAILED"
                final_failed_withdrawals.append(task)

        logger.info("Withdrawal process finished.")
        logger.info(f"Successful withdrawals: {final_successful_withdrawals}")
        logger.info(f"Failed withdrawals: {final_failed_withdrawals}")

    def close_all_automators(self):
        logger.info("Closing all active automator browser instances...")
        for automator in self.automators.values():
            try:
                automator.close()
            except Exception as e:
                logger.error(f"Error closing automator {automator.exchange_name}: {e}")