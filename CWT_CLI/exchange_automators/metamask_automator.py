import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import logging
import os

from .base_automator import BaseAutomator
from ..config import get_browser_profile_path, get_chrome_binary_location, get_credential, get_headless_mode

logger = logging.getLogger(__name__)

class MetamaskAutomator(BaseAutomator):
    METAMASK_EXTENSION_ID = "nkbihfbeogaeaoehlefnkodbefgpgknn"

    def __init__(self, config, exchange_name, headless=False, window_position=(2000, 0)): # Default to headed for Metamask
        headless = get_headless_mode(config, exchange_name, default_headless=False) # Metamask default to headed
        chrome_binary_location = get_chrome_binary_location(config, exchange_name)
        super().__init__(config, exchange_name, headless=headless, window_position=window_position, chrome_binary_location=chrome_binary_location)
        self.password = get_credential(config, exchange_name, 'password') # Metamask password
        self.browser_profile_path = get_browser_profile_path(config, exchange_name)

    def _initialize_driver(self):
        if self.driver is None:
            self.logger.info(f"Initializing undetected_chromedriver for Metamask ({self.exchange_name})...")
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            # options.add_argument('--headless') # Metamask often doesn't work well in headless mode

            if self.browser_profile_path:
                if not os.path.exists(self.browser_profile_path):
                    self.logger.warning(f"Browser profile path not found: {self.browser_profile_path}. Metamask might not be pre-configured.")
                options.add_argument(f"--user-data-dir={self.browser_profile_path}")
                self.logger.info(f"Using browser profile: {self.browser_profile_path}")
            else:
                self.logger.warning("No browser profile path provided. Metamask might not be pre-configured.")

            try:
                self.driver = uc.Chrome(options=options)
                self.driver.implicitly_wait(10) # seconds
                self.logger.info("Driver initialized successfully.")
            except WebDriverException as e:
                self.logger.error(f"WebDriver error during initialization for Metamask: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Failed to initialize undetected_chromedriver for Metamask: {e}")
                raise

    def _switch_to_metamask_window(self):
        self.logger.info("Attempting to switch to Metamask window...")
        try:
            WebDriverWait(self.driver, 30).until(EC.number_of_windows_to_be_greater_than(1)) # Wait for popup
            for window_handle in self.driver.window_handles:
                if window_handle != self.driver.current_window_handle:
                    self.driver.switch_to.window(window_handle)
                    self.logger.info("Switched to Metamask window.")
                    return True
            self.logger.error("Could not find Metamask window after waiting.")
            return False
        except TimeoutException:
            self.logger.error("Timed out waiting for Metamask window to appear.")
            return False
        except Exception as e:
            self.logger.error(f"An error occurred while switching to Metamask window: {e}")
            return False

    def login(self):
        self._initialize_driver()
        self.logger.info(f"Attempting to unlock Metamask for {self.exchange_name}...")
        if not self.password:
            self.logger.error("Metamask password not provided. Cannot unlock.")
            return False

        try:
            # Open Metamask extension directly
            self.driver.get(f"chrome-extension://{self.METAMASK_EXTENSION_ID}/home.html")
            
            if not self._switch_to_metamask_window():
                return False

            # Wait for the password input field to be present
            password_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            password_field.send_keys(self.password)

            unlock_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            unlock_button.click()

            # Wait for Metamask to unlock (e.g., dashboard elements appear)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".wallet-overview")) # Example element on dashboard
            )
            self.logger.info(f"Metamask unlocked successfully for {self.exchange_name}.")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Metamask login/unlock elements not found or timed out: {e}")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during Metamask login/unlock: {e}")
            return False

    def withdraw(self, currency, amount, address):
        self._initialize_driver()
        self.logger.info(f"Attempting to withdraw {amount} {currency} to {address} from Metamask ({self.exchange_name})...")
        try:
            if not self.login(): # Ensure Metamask is unlocked
                self.logger.error("Metamask not unlocked. Cannot proceed with withdrawal.")
                return False

            # --- Simulate Transaction Initiation ---
            self.driver.get(f"chrome-extension://{self.METAMASK_EXTENSION_ID}/home.html#send") # Navigate to send screen
            if not self._switch_to_metamask_window():
                return False

            # Enter recipient address
            recipient_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='0x...']"))
            )
            recipient_input.send_keys(address)
            time.sleep(1) # Simulate user typing

            # Enter amount
            amount_input = self.driver.find_element(By.CSS_SELECTOR, "input[data-testid='currency-input']")
            amount_input.send_keys(str(amount))
            time.sleep(1)

            # Click Next button
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='page-container-footer-next']")
            next_button.click()

            # --- Simulate Transaction Confirmation ---
            # Wait for confirmation screen
            confirm_button = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='page-container-footer-next']")) # This is often the same button for confirm
            )
            confirm_button.click()

            self.logger.info(f"Simulated withdrawal of {amount} {currency} to {address} from Metamask ({self.exchange_name}).")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Metamask withdrawal elements not found or timed out: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Metamask withdrawal failed: {e}")
            return False

    def get_balance(self, currency):
        self._initialize_driver()
        self.logger.info(f"Getting balance for {currency} from Metamask ({self.exchange_name})...")
        try:
            if not self.login(): # Ensure Metamask is unlocked
                self.logger.error("Metamask not unlocked. Cannot retrieve balance.")
                return 0.0

            # --- Simulate Balance Retrieval ---
            self.driver.get(f"chrome-extension://{self.METAMASK_EXTENSION_ID}/home.html")
            if not self._switch_to_metamask_window():
                return False

            # Assuming we are on the main assets view, find the balance for the currency
            # This locator is highly dependent on Metamask UI
            balance_element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".currency-display-component__text")) # Example locator for total balance
            )
            balance_text = balance_element.text.replace(currency, '').strip() # Remove currency symbol
            balance = float(balance_text) # Convert to float

            self.logger.info(f"Retrieved balance for {currency} from Metamask ({self.exchange_name}): {balance} (simulated).")
            return balance
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Metamask balance elements not found or timed out: {e}")
            return 0.0
        except Exception as e:
            self.logger.error(f"Metamask balance retrieval failed: {e}")
            return 0.0

    def close(self):
        if self.driver:
            self.logger.info(f"Closing browser for Metamask ({self.exchange_name}).")
            self.driver.quit()
            self.driver = None
