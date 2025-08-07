import json
import logging
from datetime import datetime, UTC
from src.models.alert_model import AlertModel
from src.fail2ban.fail2ban_client import Fail2banClient
from src.shared.custom_cache import register_alert

logger = logging.getLogger(__name__)

class SubscribeMsgService:
    """
    SubscribeMsgService listens for messages from the ZMQ subscriber and processes them.
    Attributes:
        _fail2ban_client (Fail2banClient): An instance of Fail2banClient to handle ban actions.
    Methods:
        process_received_message(message: str) -> bool | None:
            Processes the received message and performs the ban action if applicable.
    """

    def __init__(self):
        self._fail2ban_client: Fail2banClient = Fail2banClient()

    def process_received_message(self, message: str) -> bool | None:
        """
        Processes the received message from the ZMQ subscriber.
        Args:
            message (str): The message received from the ZMQ subscriber.
        Returns:
            bool | None: True if the ban action was successful, False if it failed, None if the message was invalid.
        """
        try:
            alert_data = json.loads(message)
            alert = AlertModel(**alert_data)
            alert.timestamp = datetime.now(UTC)

            logger.info(f"Received alert: {alert}")

            # Register the alert in the custom cache
            register_alert(ip=alert.ip, action=alert.action, jail=alert.jail)
            logger.info(f"Alert registered in cache: {alert.ip}, {alert.action}, {alert.jail}")

            # Perform the ban action using Fail2banClient
            success = self._fail2ban_client.execute_action(
                action=alert.action,
                jail=alert.jail,
                ip=str(alert.ip)
            )

            if success:
                logger.info(f"{alert.action} successful for IP: {alert.ip}")
                return success
            else:
                logger.warning(f"Failed to {alert.action} IP: {alert.ip}")
                return success

        except Exception as e:
            logger.error(f"Failed to parse or process alert message: {e}")
            return False
