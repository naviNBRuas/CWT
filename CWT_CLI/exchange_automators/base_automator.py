from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseAutomator(ABC):
    def __init__(self, config, exchange_name):
        self.config = config
        self.exchange_name = exchange_name
        self.logger = logging.getLogger(f"{__name__}.{exchange_name}")

    @abstractmethod
    def login(self):
        """Logs into the exchange."""
        pass

    @abstractmethod
    def withdraw(self, currency, amount, address):
        """Initiates a withdrawal from the exchange."""
        pass

    @abstractmethod
    def get_balance(self, currency):
        """Gets the balance of a specific currency."""
        pass

    @abstractmethod
    def close(self):
        """Closes any open connections or browser instances."""
        pass
