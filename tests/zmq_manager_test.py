# Write a  test for manager.py from zmq package
import unittest
from unittest.mock import patch, MagicMock
from src.zmq.manager import ZMQManager

class TestZMQManager(unittest.TestCase):
    @patch('src.zmq.manager.zmq.Context')
    def test_create_context(self, mock_context):
        """Test if the ZMQ context is created correctly."""
        manager = ZMQManager()
        self.assertIsNotNone(manager.get_context())
        mock_context.assert_called_once()

    @patch('src.zmq.manager.zmq.Context')
    def test_terminate_context(self, mock_context):
        """Test if the ZMQ context is terminated correctly."""
        manager = ZMQManager()
        manager.terminate_context()
        mock_context.return_value.term.assert_called_once()

    @patch('src.zmq.manager.zmq.Context')
    def test_get_context(self, mock_context):
        """Test if the ZMQ context is retrieved correctly."""
        manager = ZMQManager()
        context = manager.get_context()
        self.assertEqual(context, mock_context.return_value)
        mock_context.assert_called_once()

if __name__ == '__main__':
    unittest.main()
