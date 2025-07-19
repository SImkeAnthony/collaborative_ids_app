import zmq
import logging
from src.ids2zmq.manager import ZMQManager

logger = logging.getLogger(__name__)

class ZMQDealer:
    """
    A class that implements a ZeroMQ DEALER socket for sending messages to a server.
    Args:
        connect_address (str): The address to connect to the server.
        identity (str): The identity of the DEALER socket, used for routing messages.
    Attributes:
        context (zmq.Context): The ZeroMQ context for managing sockets.
        socket (zmq.Socket): The DEALER socket used for sending messages.
        connect_address (str): The address to connect to the server.
    Methods:
        start(message: str): Connects the DEALER socket to the server and sends a message.
        stop(): Closes the DEALER socket.
    """
    def __init__(self, connect_address: str, identity: str):
        self.context = ZMQManager.get_context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.setsockopt_string(zmq.IDENTITY, identity)
        self.connect_address = connect_address

    def start(self, message: str):
        """
        Connects the DEALER socket to the server and sends a message.
        Args:
            message (str): The message to send to the server.
        """
        self.socket.connect(self.connect_address)
        logger.info(f"DEALER socket connected to {self.connect_address} with identity {self.socket.getsockopt(zmq.IDENTITY)}")

        self.socket.send_multipart([b"", message.encode()])
        reply = self.socket.recv_multipart()
        logger.info(f"Received reply: {reply[-1].decode()}")

    def stop(self):
        """ Closes the DEALER socket. """
        self.socket.close()
        logger.info("DEALER socket closed")
