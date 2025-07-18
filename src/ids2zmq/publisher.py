import zmq
import logging
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

    def bind(self):
        """Bind the ZMQ Publisher to the configured address. And security settings."""
        if ZMQManager.zmq_security_enabled:
            try:
                self.publisher_socket.setsockopt(zmq.PLAIN_SERVER, 1)
                logger.info("ZMQ plain security enabled for publisher socket.")
                ZMQManager.enable_plain_auth(context=ZMQManager.get_context())
            except zmq.ZMQError as e:
                logger.error(f"Failed to enable ZMQ plain security for publisher: {e}")
                raise
        else:
            logger.info("ZMQ plain security not enabled for publisher socket.")
        if not self._is_bound:
            try:
                self.publisher_socket.bind(self._bind_address)
                self._is_bound = True
                logger.info(f"ZMQ Publisher bound to {self._bind_address}")
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
            self.publisher_socket.send_multipart([self._topic.encode('utf-8'), alert.encode('utf-8')])
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