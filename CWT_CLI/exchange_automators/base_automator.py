from abc import ABC, abstractmethod
import logging
import undetected_chromedriver as uc
import os

logger = logging.getLogger(__name__)

class BaseAutomator(ABC):
    def __init__(self, config, exchange_name, headless=True, window_position=(2000, 0), chrome_binary_location=None):
        self.config = config
        self.exchange_name = exchange_name
        self.logger = logging.getLogger(f"{__name__}.{exchange_name}")
        self.driver = None
        self.headless = headless
        self.window_position = window_position
        self.chrome_binary_location = chrome_binary_location

    def _initialize_driver(self):
        if self.driver is None:
            self.logger.info(f"Initializing undetected_chromedriver for {self.exchange_name}...")
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            if self.headless:
                options.add_argument('--headless')
                self.logger.info("Running browser in headless mode.")
            else:
                # Move browser window off-screen if not headless
                options.add_argument(f'--window-position={self.window_position[0]},{self.window_position[1]}')
                options.add_argument('--window-size=1280,800') # Set a default size
                self.logger.info(f"Running browser in headed mode, positioned at {self.window_position}.")

            if self.chrome_binary_location:
                if not os.path.exists(self.chrome_binary_location):
                    self.logger.error(f"Chrome binary not found at specified location: {self.chrome_binary_location}")
                    raise FileNotFoundError(f"Chrome binary not found: {self.chrome_binary_location}")
                options.binary_location = self.chrome_binary_location
                self.logger.info(f"Using Chrome binary at: {self.chrome_binary_location}")

            try:
                self.driver = uc.Chrome(options=options)
                self.driver.implicitly_wait(10) # seconds
                self.logger.info("Driver initialized successfully.")
            except Exception as e:
                self.logger.error(f"Failed to initialize undetected_chromedriver: {e}")
                raise

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
