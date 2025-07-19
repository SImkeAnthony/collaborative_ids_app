import json
import logging
from src.models.alert_model import AlertModel
from src.fail2ban.fail2ban_client import Fail2banClient
from src.config.settings import settings

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

            logger.info(f"Received alert: {alert}")

            # Perform the ban action using Fail2banClient
            success = self._fail2ban_client.execute_action(
                action=alert.action,
                jail=alert.jail,
                ip=alert.ip
            )

            if success:
                logger.info(f"Ban successful for IP: {alert.ip}")
                return success
            else:
                logger.warning(f"Failed to ban IP: {alert.ip}")
                return success

        except Exception as e:
            logger.error(f"Failed to parse or process alert message: {e}")
            return False
