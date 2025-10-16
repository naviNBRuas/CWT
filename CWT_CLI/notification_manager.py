import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from .config import get_config_value, get_credential

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, config):
        self.config = config
        self.email_enabled = get_config_value(config, "NOTIFICATIONS", "email_enabled", default="False").lower() == 'true'
        if self.email_enabled:
            self.smtp_server = get_config_value(config, "NOTIFICATIONS", "smtp_server")
            self.smtp_port = int(get_config_value(config, "NOTIFICATIONS", "smtp_port", default="587"))
            self.smtp_username = get_credential(config, "NOTIFICATIONS", "smtp_username")
            self.smtp_password = get_credential(config, "NOTIFICATIONS", "smtp_password")
            self.recipient_email = get_config_value(config, "NOTIFICATIONS", "recipient_email")

            if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.recipient_email]):
                logger.warning("Email notifications are enabled but SMTP credentials or recipient email are incomplete. Disabling email notifications.")
                self.email_enabled = False
            else:
                logger.info("Email notifications initialized.")
        else:
            logger.info("Email notifications are disabled.")

    def send_email(self, subject, body):
        if not self.email_enabled:
            logger.debug("Email notifications are disabled. Not sending email.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls() # Secure the connection
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            logger.info(f"Email notification sent to {self.recipient_email} with subject: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    # Placeholder for other notification types (e.g., Telegram, Discord)
    def send_telegram_message(self, message):
        logger.warning("Telegram notifications not yet implemented.")
        pass

    def send_discord_message(self, message):
        logger.warning("Discord notifications not yet implemented.")
        pass
