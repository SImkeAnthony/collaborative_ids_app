import zmq
import threading
import logging
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

    def connect_to_publisher(self, host:str):
        """Connect to publishers using the trusted hosts."""
        try:
            self.subscriber_socket.connect(host)
            logger.info(f"Subscriber bound to {settings.ZMQ_PUBLISHER_BIND_ADDRESS}")
        except zmq.ZMQError as e:
            logger.error(f"Failed to bind subscriber socket: {e}")
            raise

    def connect_to_publishers(self):
        trusted_hosts = ZMQManager.get_trusted_hosts()
        for host in trusted_hosts:
            try:
                self.connect_to_publisher(host=host)
                logger.info(f"Connected to publisher: {host}")
            except zmq.ZMQError as e:
                logger.error(f"Failed to connect to {host}: {e}")

        self.subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, self._topic)

    def run(self):
        logger.info("ZMQSubscriber started.")
        while self._running.is_set():
            try:
                topic, message = self.subscriber_socket.recv_multipart(flags=zmq.NOBLOCK)
                if topic.decode() == self._topic:
                    logger.info(f"Received alert: {message.decode()}")
                    self._on_message_callback(message.decode())
            except zmq.Again:
                continue  # No message available yet, just retry
            except Exception as e:
                logger.error(f"Error in ZMQSubscriber: {e}")

    def stop(self):
        self._running.clear()
        self.subscriber_socket.close()
        logger.info("ZMQSubscriber stopped.")