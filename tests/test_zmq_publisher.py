import unittest
from unittest.mock import MagicMock, patch
import zmq

from src.ids2zmq.publisher import ZMQPublisher

class DummyFernet:
    def __init__(self, key):
        self.key = key
    def encrypt(self, data):
        return b"encrypted_" + data

class TestZMQPublisher(unittest.TestCase):
    def setUp(self):
        # Patch ZMQManager and settings for all tests
        patcher_mgr = patch('src.ids2zmq.publisher.ZMQManager')
        patcher_settings = patch('src.ids2zmq.publisher.settings')
        patcher_fernet = patch('src.ids2zmq.publisher.Fernet', DummyFernet)
        self.mock_mgr = patcher_mgr.start()
        self.addCleanup(patcher_mgr.stop)
        self.mock_settings = patcher_settings.start()
        self.addCleanup(patcher_settings.stop)
        patcher_fernet.start()
        self.addCleanup(patcher_fernet.stop)

        self.mock_mgr.zmq_security_enabled = True
        self.mock_mgr.get_context.return_value.socket.return_value = MagicMock(spec=zmq.Socket)
        self.mock_mgr.enable_plain_auth.return_value = None
        self.mock_mgr.load_symmetrical_key.return_value = b'dummy-key'

        self.mock_settings.ZMQ_PUBLISHER_BIND_ADDRESS = "tcp://*:9999"
        self.mock_settings.ZMQ_TOPIC_FAIL2BAN_ALERT = "mytopic"
        self.mock_settings.ZMQ_SYMMETRICAL_KEY_FILE = "/dev/null"

        self.publisher = ZMQPublisher()
        self.publisher.publisher_socket = MagicMock(spec=zmq.Socket)
        self.publisher._fernet = DummyFernet(b'dummy-key')
        self.publisher._topic = self.mock_settings.ZMQ_TOPIC_FAIL2BAN_ALERT

    def test_configure_security_enabled(self):
        self.publisher.publisher_socket.setsockopt = MagicMock()
        self.publisher._fernet = None
        self.publisher.configure_security()
        self.publisher.publisher_socket.setsockopt.assert_called()
        self.assertIsNotNone(self.publisher._fernet)

    def test_configure_security_disabled(self):
        self.mock_mgr.zmq_security_enabled = False
        self.publisher.configure_security()
        # Nothing should be set if security is disabled

    def test_bind_success(self):
        self.publisher._is_bound = False
        self.publisher.publisher_socket.bind = MagicMock()
        self.publisher.bind()
        self.publisher.publisher_socket.bind.assert_called_once()

    def test_bind_warning(self):
        self.publisher._is_bound = True
        with self.assertLogs(level='WARNING') as cm:
            self.publisher.bind()
        found = any('already bound' in msg for msg in cm.output)
        self.assertTrue(found)

    def test_publish_alert_encrypted(self):
        self.publisher._is_bound = True
        self.publisher._fernet = DummyFernet(b'dummy')
        self.publisher.publisher_socket.send_multipart = MagicMock()
        self.mock_mgr.zmq_security_enabled = True
        self.publisher.publish_alert("hello!")
        self.publisher.publisher_socket.send_multipart.assert_called()

    def test_publish_alert_no_encryption(self):
        self.publisher._is_bound = True
        self.mock_mgr.zmq_security_enabled = False
        self.publisher.publisher_socket.send_string = MagicMock()
        self.publisher.publish_alert("hello world")
        self.publisher.publisher_socket.send_string.assert_called()

    def test_publish_alert_not_bound_raises(self):
        self.publisher._is_bound = False
        with self.assertRaises(RuntimeError):
            self.publisher.publish_alert("alert")

    def test_close_socket(self):
        self.publisher.publisher_socket.close = MagicMock()
        self.publisher._is_bound = True
        self.publisher.close()
        self.publisher.publisher_socket.close.assert_called()
        self.assertFalse(self.publisher._is_bound)

if __name__ == "__main__":
    unittest.main()
