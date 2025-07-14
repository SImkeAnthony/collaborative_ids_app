# Write a test for subscriber.py from zmq package
import unittest
from unittest.mock import patch, MagicMock
from src.zmq.subscriber import ZMQSubscriber

class TestZMQSubscriber(unittest.TestCase):
    @patch('src.zmq.subscriber.zmq.Context')
    @patch('src.zmq.subscriber.zmq.Socket')
    def setUp(self, mock_socket, mock_context):
        """Set up the ZMQSubscriber instance for testing."""
        self.subscriber = ZMQSubscriber(on_message_callback=MagicMock())
        self.subscriber.socket = mock_socket.return_value
        self.subscriber.context = mock_context.return_value

    @patch('src.zmq.subscriber.ZMQManager.get_context')
    def test_connect_to_publishers(self, mock_subscriber_socket):
        """Test if the subscriber connects to the correct publishers."""
        self.subscriber.connect_to_publishers()
        mock_subscriber_socket.connect.assert_called_with("tcp://192.168.0.201:5555")

    @patch('src.zmq.subscriber.ZMQManager.get_context')
    def test_start(self, mock_subscriber_socket):
        """Test if the subscriber starts receiving messages."""
        self.subscriber.start()
        mock_subscriber_socket.recv_multipart.assert_called()

    @patch('src.zmq.subscriber.ZMQManager.get_context')
    def test_stop(self, mock_subscriber_socket):
        """Test if the subscriber stops correctly."""
        self.subscriber.stop()
        mock_subscriber_socket.close.assert_called_once()