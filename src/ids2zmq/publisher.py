import zmq
import logging

from cryptography.fernet import Fernet

from src.ids2zmq.manager import ZMQManager
from src.config.settings import settings

logger = logging.getLogger(__name__)

class ZMQPublisher:
    """Manage the ZMQ message publishing for Fail2Ban alerts."""
    def __init__(self):
        self.context = ZMQManager.get_context()
        self.publisher_socket: zmq.Socket = self.context.socket(zmq.PUB)
        self._bind_address = settings.ZMQ_PUBLISHER_BIND_ADDRESS
        self._topic = settings.ZMQ_TOPIC_FAIL2BAN_ALERT
        self._is_bound = False
        self._fernet: Fernet = None

    def configure_security(self):
        """Configure security settings for the publisher socket if enabled."""
        if ZMQManager.zmq_security_enabled:
            try:
                self.publisher_socket.setsockopt(zmq.PLAIN_SERVER, 1)
                logger.info("ZMQ plain security enabled for publisher socket.")
                ZMQManager.enable_plain_auth(context=ZMQManager.get_context())
                self._fernet = Fernet(ZMQManager.load_symmetrical_key(filename=settings.ZMQ_SYMMETRICAL_KEY_FILE))
            except zmq.ZMQError as e:
                logger.error(f"Failed to enable ZMQ plain security for publisher: {e}")
                raise
            except Exception as e:
                logger.error(f"Error configuring ZMQ security for publisher: {e}")
                raise RuntimeError(f"Failed to configure ZMQ security for publisher: {e}")
        else:
            logger.info("ZMQ plain security not enabled for publisher socket.")

    def bind(self):
        """Bind the ZMQ Publisher to the configured address."""
        if not self._is_bound:
            try:
                self.publisher_socket.bind(self._bind_address)
                self._is_bound = True
                logger.info("ZMQ Publisher bound to address: %s", settings.ZMQ_PUBLISHER_BIND_ADDRESS)
            except zmq.ZMQError as e:
                logger.error(f"Failed to bind ZMQ Publisher to {self._bind_address}: {e}")
                raise
        else:
            logger.warning("ZMQ Publisher already bound.")

    def publish_alert(self, alert: str):
        """Publish a Fail2Ban alert to the ZMQ topic."""
        if not self._is_bound:
            logger.error("Attempted to publish without binding the ZMQ Publisher.")
            raise RuntimeError("ZMQ Publisher not bound.")

        try:
            if ZMQManager.zmq_security_enabled :
                encrypted_alert = self._fernet.encrypt(alert.encode('utf-8'))
                logger.info("Alert encrypted before publishing.")
                self.publisher_socket.send_multipart([self._topic.encode('utf-8'), encrypted_alert])
            else:
                self.publisher_socket.send_string(f"{self._topic} {alert}")
                logger.info("Alert sent without encryption.")
            logger.info(f"Published alert on topic '{self._topic}'")
        except zmq.ZMQError as e:
            logger.error(f"Error publishing ZMQ message: {e}")
            raise

    def close(self):
        """Close the ZMQ Publisher socket."""
        if self.publisher_socket:
            logger.info("Closing ZMQ Publisher socket.")
            self.publisher_socket.close()
            self._is_bound = False