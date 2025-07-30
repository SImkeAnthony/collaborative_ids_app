import time

import zmq
import threading
import logging
from cryptography.fernet import Fernet

from src.ids2zmq.manager import ZMQManager
from src.config.settings import settings
from src.models.alert_model import AlertModel
from src.utils.ip_address import get_local_ip
from src.utils.ip_address import extract_ip_address_from_socket_address

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
    """
    Subscriber in a separate thread to listen for ZMQ messages.
    Args:
        on_message_callback (callable): Function to call when a message is received.
    Attributes:
        on_message_callback (callable): Function to call when a message is received.
        subscriber_socket (zmq.Socket): ZMQ socket for subscribing to messages.
        _topic (str): Topic to subscribe to.
        _running (threading.Event): Event to control the running state of the thread.
        _fernet (Fernet): Fernet instance for decrypting messages if security is enabled.
    Methods:
        connect_to_publisher(host: str): Connect to a specific publisher.
        connect_to_publisher_with_retries(host: str, retries: int = 5, delay: float = 2.0): Connect to a publisher with retry logic.
        connect_to_publishers(): Connect to all trusted publishers defined in the ZMQManager.
        configure_security(): Configure security settings for the subscriber socket if enabled.
        run(): Run the subscriber thread to listen for messages.
        stop(): Stop the subscriber thread and close the socket.
    """

    def __init__(self, on_message_callback: callable):
        super().__init__(daemon=True)  # Daemon thread so it closes with main app
        self.context = ZMQManager.get_context()
        self.subscriber_socket: zmq.Socket = self.context.socket(zmq.SUB)
        self._topic = settings.ZMQ_TOPIC_FAIL2BAN_ALERT
        self._running = threading.Event()
        self._running.set()
        self._on_message_callback = on_message_callback
        self._fernet: Fernet = None

    def connect_to_publisher(self, host:str):
        """
        Connect to publishers using the trusted hosts.
        Args:
            host (str): Publisher address to connect to.
        Raises:
            zmq.ZMQError: If the connection fails.
        """
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
        Raises:
            zmq.ZMQError: If the connection fails after all retries.
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
        """
        Connect to all trusted publishers defined in the ZMQManager.
        Raises:
            zmq.ZMQError: If the connection to any publisher fails.
        """
        trusted_hosts = ZMQManager.get_trusted_hosts()
        count = 0
        for host in trusted_hosts:
            try:
                if extract_ip_address_from_socket_address(socket_address=host) == get_local_ip():
                    logger.info(f"Skipping connection to self: {host}")
                    continue
                else:
                    self.connect_to_publisher_with_retries(host=host)
                    count += 1
            except zmq.ZMQError as e:
                logger.error(f"Failed to connect to {host}: {e}")
        logger.info(f"Connected to {count} trusted hosts for ZMQ subscriber.")
        self.subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, self._topic)

    def configure_security(self):
        """
        Configure security settings for the subscriber socket if enabled.
        Raises:
            RuntimeError: If there is an error configuring ZMQ security.
            zmq.ZMQError: If setting socket options fails.
        """
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
        """
        Run the subscriber thread to listen for messages.
        Raises:
            zmq.Again: If no message is available (non-blocking mode).
            Exception: For any other errors during message processing.
        """
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
                    alert_received: AlertModel = AlertModel.from_json(json_str=received_msg)
                    alert_received.target_ip = get_local_ip()
                    logger.info(f"Received alert: {received_msg}")
                    self._on_message_callback(received_msg)
            except zmq.Again:
                continue  # No message available yet, just retry
            except Exception as e:
                logger.error(f"Error in ZMQSubscriber: {e}")

    def stop(self):
        """
        Stop the subscriber thread and close the socket.
        """
        self._running.clear()
        self.subscriber_socket.close()
        logger.info("ZMQSubscriber stopped.")