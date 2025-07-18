import time

import zmq
import threading
import logging
from cryptography.fernet import Fernet
from typing_extensions import override

from src.ids2zmq.manager import ZMQManager
from src.config.settings import settings

logger = logging.getLogger(__name__)

"""
Call this class as : 
def handle_alert(data: str):
    print("Received alert data:", data)

subscriber = ZMQSubscriber(on_message_callback=handle_alert)
subscriber.connect_to_publishers()
subscriber.start()

# Define the on_message_callback function to handle incoming messages and implement your logic.
"""

class ZMQSubscriber(threading.Thread):
    """Subscriber in a separate thread to listen for ZMQ messages."""

    def __init__(self, on_message_callback):
        super().__init__(daemon=True)  # Daemon thread so it closes with main app
        self.context = ZMQManager.get_context()
        self.subscriber_socket: zmq.Socket = self.context.socket(zmq.SUB)
        self._topic = settings.ZMQ_TOPIC_FAIL2BAN_ALERT
        self._running = threading.Event()
        self._running.set()
        self._on_message_callback = on_message_callback
        self._fernet: Fernet = None

    def connect_to_publisher(self, host:str):
        """Connect to publishers using the trusted hosts."""
        try:
            self.subscriber_socket.connect(host)
            logger.info(f"Subscriber bound to {settings.ZMQ_PUBLISHER_BIND_ADDRESS}")
        except zmq.ZMQError as e:
            logger.error(f"Failed to bind subscriber socket: {e}")
            raise

    def connect_to_publisher_with_retries(self, host: str, retries: int = 5, delay: float = 2.0):
        """
        Connect to publisher with retry logic.
        Args:
            host (str): Publisher address.
            retries (int): Number of connection attempts.
            delay (float): Seconds to wait between attempts.
        """
        attempt = 0
        while attempt < retries:
            try:
                self.subscriber_socket.connect(host)
                logger.info(f"Subscriber connected to {host}")
                return
            except zmq.ZMQError as e:
                attempt += 1
                logger.warning(f"Attempt {attempt}/{retries} failed to connect to {host}: {e}")
                if attempt < retries:
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to connect to {host} after {retries} attempts")
                    raise

    def connect_to_publishers(self):
        trusted_hosts = ZMQManager.get_trusted_hosts()
        for host in trusted_hosts:
            try:
                self.connect_to_publisher_with_retries(host=host)

            except zmq.ZMQError as e:
                logger.error(f"Failed to connect to {host}: {e}")
        logger.info(f"Connected to {len(trusted_hosts)} trusted hosts for ZMQ subscriber.")
        self.subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, self._topic)

    def configure_security(self):
        """Configure security settings for the subscriber socket if enabled."""
        if ZMQManager.zmq_security_enabled:
            try :
                self.subscriber_socket.setsockopt(zmq.PLAIN_USERNAME, settings.ZMQ_SECURITY_USERNAME.encode('utf-8'))
                self.subscriber_socket.setsockopt(zmq.PLAIN_PASSWORD, settings.ZMQ_SECURITY_PASSWORD.encode('utf-8'))
                self._fernet = Fernet(key=ZMQManager.load_symmetrical_key(filename=settings.ZMQ_SYMMETRICAL_KEY_FILE))
                logger.info("ZMQ plain security enabled for subscriber socket.")
            except zmq.ZMQError as e:
                logger.error(f"Failed to enable ZMQ plain security for subscriber: {e}")
                raise
            except Exception as e:
                logger.error(f"Error configuring ZMQ security for subscriber: {e}")
                raise RuntimeError(f"Failed to configure ZMQ security for subscriber: {e}")
        else:
            logger.info("ZMQ plain security not enabled for subscriber socket.")

    def run(self):
        """Run the subscriber thread to listen for messages."""
        logger.info("ZMQSubscriber started.")
        received_msg:str = ""
        while self._running.is_set():
            try:
                topic, message = self.subscriber_socket.recv_multipart(flags=zmq.NOBLOCK)
                if ZMQManager.zmq_security_enabled:
                    received_msg = self._fernet.decrypt(message).decode('utf-8')
                    logger.info("Received encrypted message, decrypted successfully.")
                else:
                    received_msg = message.decode('utf-8')
                    logger.info("Received message without encryption.")
                if topic.decode() == self._topic:
                    logger.info(f"Received alert: {received_msg}")
                    self._on_message_callback(received_msg)
            except zmq.Again:
                continue  # No message available yet, just retry
            except Exception as e:
                logger.error(f"Error in ZMQSubscriber: {e}")

    def stop(self):
        self._running.clear()
        self.subscriber_socket.close()
        logger.info("ZMQSubscriber stopped.")