# write a test for the ZMQPublisher class using unittest and mock
import unittest
from unittest.mock import patch, MagicMock
import zmq
from src.ids2zmq.publisher import ZMQPublisher

class TestZMQPublisher(unittest.TestCase):
    @patch('src.ids2zmq.publisher.ZMQManager.get_context')
    @patch('src.ids2zmq.publisher.settings')
    def setUp(self, mock_settings, mock_get_context):
        self.mock_context = MagicMock()
        self.mock_socket = MagicMock()
        mock_get_context.return_value = self.mock_context
        self.mock_context.socket.return_value = self.mock_socket
        mock_settings.ZMQ_PUBLISHER_BIND_ADDRESS = "tcp://*:5556"
        mock_settings.ZMQ_TOPIC_FAIL2BAN_ALERT = "fail2ban.alert"
        self.publisher = ZMQPublisher()

    def test_bind_success(self):
        self.publisher._is_bound = False
        self.publisher.bind()
        self.mock_socket.bind.assert_called_once_with("tcp://*:5556")
        self.assertTrue(self.publisher._is_bound)

    @patch('src.ids2zmq.publisher.logger')
    def test_bind_already_bound(self, mock_logger):
        self.publisher._is_bound = True
        self.publisher.bind()
        mock_logger.warning.assert_called_once_with("ZMQ Publisher already bound.")

    @patch('src.ids2zmq.publisher.logger')
    def test_bind_failure(self, mock_logger):
        self.publisher._is_bound = False
        self.mock_socket.bind.side_effect = zmq.ZMQError("Bind error")
        with self.assertRaises(zmq.ZMQError):
            self.publisher.bind()
        mock_logger.error.assert_called()

    def test_publish_alert_success(self):
        self.publisher._is_bound = True
        self.publisher.publish_alert("Test alert")
        self.mock_socket.send_multipart.assert_called_once_with(
            [b"fail2ban.alert", b"Test alert"]
        )

    @patch('src.ids2zmq.publisher.logger')
    def test_publish_alert_not_bound(self, mock_logger):
        self.publisher._is_bound = False
        with self.assertRaises(RuntimeError):
            self.publisher.publish_alert("Test alert")
        mock_logger.error.assert_called_once_with("Attempted to publish without binding the ZMQ Publisher.")

    @patch('src.ids2zmq.publisher.logger')
    def test_publish_alert_zmqerror(self, mock_logger):
        self.publisher._is_bound = True
        self.mock_socket.send_multipart.side_effect = zmq.ZMQError("Send error")
        with self.assertRaises(zmq.ZMQError):
            self.publisher.publish_alert("Test alert")
        mock_logger.error.assert_called()

    @patch('src.ids2zmq.publisher.logger')
    def test_close(self, mock_logger):
        self.publisher._is_bound = True
        self.publisher.close()
        self.mock_socket.close.assert_called_once()
        self.assertFalse(self.publisher._is_bound)
        mock_logger.info.assert_called_with("Closing ZMQ Publisher socket.")

if __name__ == '__main__':
    unittest.main()
