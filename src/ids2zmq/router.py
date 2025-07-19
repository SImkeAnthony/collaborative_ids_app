import zmq
import threading
import logging
from src.config.settings import settings
from src.ids2zmq.manager import ZMQManager
logger = logging.getLogger(__name__)

class ZMQRouter:
    """
    ZMQRouter is a class that implements a ZeroMQ ROUTER socket.
    Attributes:
        context (zmq.Context): The ZeroMQ context for creating sockets.
        socket (zmq.Socket): The ROUTER socket for receiving and sending messages.
        bind_address (str): The address to which the ROUTER socket binds.
        running (bool): A flag indicating whether the router is running.
    Methods:
        start(): Starts the ROUTER socket, binds it to the address, and listens for incoming messages.
        stop(): Stops the ROUTER socket and closes it.
        run_in_thread(): Runs the ROUTER in a separate thread to allow asynchronous operation.
    """

    def __init__(self):
        self.context = ZMQManager.get_context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.bind_address = settings.ZMQ_ROUTER_BIND_ADDRESS
        self.running = False

    def start(self):
        """
        Starts the ROUTER socket, binds it to the specified address, and listens for incoming messages.
        Raises:
            zmq.ZMQError: If there is an error in binding or receiving messages.
        """
        self.socket.bind(self.bind_address)
        self.running = True
        logger.info(f"ROUTER socket bound to {self.bind_address}")
        while self.running:
            try:
                identity, empty, message = self.socket.recv_multipart()
                logger.info(f"Received message from {identity.decode()}: {message.decode()}")
                self.socket.send_multipart([identity, b"", b"ACK"])
            except zmq.ZMQError as e:
                logger.error(f"ROUTER error: {e}")
                break

    def stop(self):
        """Stops the ROUTER socket and closes it."""
        self.running = False
        self.socket.close()
        logger.info("ROUTER socket closed")

    def run_in_thread(self):
        """Runs the ROUTER in a separate thread to allow asynchronous operation."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()