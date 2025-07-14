# Write a test for publisher.py from zmq package
import unittest
from unittest.mock import patch, MagicMock
from src.zmq.publisher import ZMQPublisher

class TestZMQPublisher(unittest.TestCase):
    @patch('src.zmq.publisher.zmq.Publisher')
    def setUp(self, mock_publisher):
        """Set up the ZMQPublisher instance for testing."""
        self.publisher = ZMQPublisher()
        self.publisher.socket = mock_publisher.return_value

    @patch('src.zmq.publisher.ZMQManager.get_context')
    def test_bind(self, mock_publisher_socket):
        """Test if the publisher binds to the correct address."""
        self.publisher.bind()
        mock_publisher_socket.bind.assert_called_once_with("tcp://*:5555")

    @patch('src.zmq.publisher.ZMQManager.get_context')
    def test_publish_message(self, mock_publisher_socket):
        """Test if the publisher sends a message correctly."""
        message = "test message"
        self.publisher.publish_alert(message)
        mock_publisher_socket.send_multipart.assert_called_once_with(message)

    @patch('src.zmq.publisher.ZMQManager.get_context')
    def test_close(self, mock_publisher_socket):
        """Test if the publisher socket is closed correctly."""
        self.publisher.close()
        mock_publisher_socket.close.assert_called_once()