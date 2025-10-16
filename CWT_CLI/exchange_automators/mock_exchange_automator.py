import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

from .base_automator import BaseAutomator
from ..config import get_chrome_binary_location, get_credential, get_headless_mode, get_headless_mode

logger = logging.getLogger(__name__)

class MockExchangeAutomator(BaseAutomator):
    def __init__(self, config, exchange_name, window_position=(2000, 0)):
        headless = get_headless_mode(config, exchange_name, default_headless=True)
        chrome_binary_location = get_chrome_binary_location(config, exchange_name)
        super().__init__(config, exchange_name, headless=headless, window_position=window_position, chrome_binary_location=chrome_binary_location)
        self.base_url = self.config.get(exchange_name, 'base_url', fallback='http://mockexchange.com')
        self.username = get_credential(config, exchange_name, 'username')
        self.password = get_credential(config, exchange_name, 'password')

    def _initialize_driver(self):
        if self.driver is None:
            self.logger.info(f"Initializing undetected_chromedriver for {self.exchange_name}...")
            options = uc.ChromeOptions()
            # options.add_argument('--headless') # Run in headless mode (no GUI) for server environments
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            try:
                self.driver = uc.Chrome(options=options)
                self.driver.implicitly_wait(10) # seconds
                self.logger.info("Driver initialized successfully.")
            except Exception as e:
                self.logger.error(f"Failed to initialize undetected_chromedriver: {e}")
                raise

    def login(self):
        self._initialize_driver()
        self.logger.info(f"Attempting to log into {self.exchange_name} at {self.base_url}...")
        try:
            self.driver.get(self.base_url + "/login")
            
            # Simulate finding elements and entering credentials
            username_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "username_input"))
            )
            password_field = self.driver.find_element(By.ID, "password_input")
            login_button = self.driver.find_element(By.ID, "login_button")

            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            login_button.click()

            # Simulate waiting for login to complete
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("/dashboard") or EC.url_contains("/home")
            )
            self.logger.info(f"Successfully logged into {self.exchange_name}.")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Login elements not found or timed out for {self.exchange_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Login failed for {self.exchange_name}: {e}")
            return False

    def withdraw(self, currency, amount, address):
        self._initialize_driver()
        self.logger.info(f"Attempting to withdraw {amount} {currency} to {address} from {self.exchange_name}...")
        try:
            self.driver.get(self.base_url + "/withdraw")

            # Simulate finding withdrawal elements and filling details
            currency_select = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "currency_select"))
            )
            # In a real scenario, you'd use Select(currency_select).select_by_value(currency)
            # For mock, we just simulate interaction
            currency_select.send_keys(currency) # Simulate selecting currency

            amount_field = self.driver.find_element(By.ID, "amount_input")
            amount_field.send_keys(str(amount))

            address_field = self.driver.find_element(By.ID, "address_input")
            address_field.send_keys(address)

            confirm_button = self.driver.find_element(By.ID, "confirm_withdrawal_button")
            confirm_button.click()

            # Simulate waiting for withdrawal confirmation
            WebDriverWait(self.driver, 30).until(
                EC.url_contains("/withdrawal_success") or EC.presence_of_element_located((By.ID, "withdrawal_confirmation_message"))
            )
            self.logger.info(f"Withdrawal of {amount} {currency} to {address} from {self.exchange_name} initiated (mocked).")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Withdrawal elements not found or timed out for {self.exchange_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Withdrawal failed for {self.exchange_name}: {e}")
            return False

    def get_balance(self, currency):
        self._initialize_driver()
        self.logger.info(f"Getting balance for {currency} from {self.exchange_name}...")
        try:
            self.driver.get(self.base_url + "/balances")

            # Simulate finding balance element
            balance_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@data-currency='{currency}']"))
            )
            balance = float(balance_element.text) # Assuming text is the balance
            self.logger.info(f"Retrieved balance for {currency} from {self.exchange_name}: {balance} (mocked).")
            return balance
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Balance element not found or timed out for {self.exchange_name}: {e}")
            return 0.0
        except Exception as e:
            self.logger.error(f"Failed to get balance for {currency} from {self.exchange_name}: {e}")
            return 0.0

    def close(self):
        if self.driver:
            self.logger.info(f"Closing browser for {self.exchange_name}.")
            self.driver.quit()
            self.driver = None
