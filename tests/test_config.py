import unittest
import os
from CWT_CLI.config import load_config, get_config_value, ConfigError
import configparser

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.test_config_path = "test_config.ini"
        with open(self.test_config_path, "w") as f:
            f.write("[DEFAULT]\n")
            f.write("main_withdrawal_address = test_main_address\n")
            f.write("[EXCHANGE_TEST]\n")
            f.write("type = TestAutomator\n")
            f.write("username = test_user\n")
            f.write("password = test_pass\n")
            f.write("currency = BTC\n")
            f.write("amount = 0.005\n")

    def tearDown(self):
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    def test_load_config_success(self):
        config = load_config(self.test_config_path)
        self.assertIsNotNone(config)
        self.assertIsInstance(config, configparser.ConfigParser)
        self.assertIn("main_withdrawal_address", config["DEFAULT"])
        self.assertTrue(config.has_section("EXCHANGE_TEST"))

    def test_load_config_file_not_found(self):
        with self.assertRaises(ConfigError):
            load_config("non_existent_config.ini")

    def test_get_config_value_existing(self):
        config = load_config(self.test_config_path)
        self.assertEqual(get_config_value(config, "DEFAULT", "main_withdrawal_address"), "test_main_address")
        self.assertEqual(get_config_value(config, "EXCHANGE_TEST", "username"), "test_user")

    def test_get_config_value_non_existing_key(self):
        config = load_config(self.test_config_path)
        self.assertIsNone(get_config_value(config, "EXCHANGE_TEST", "non_existent_key"))

    def test_get_config_value_non_existing_section(self):
        config = load_config(self.test_config_path)
        self.assertIsNone(get_config_value(config, "NON_EXISTENT_SECTION", "key"))

    def test_get_config_value_with_default(self):
        config = load_config(self.test_config_path)
        self.assertEqual(get_config_value(config, "EXCHANGE_TEST", "non_existent_key", default="default_value"), "default_value")

if __name__ == '__main__':
    unittest.main()
