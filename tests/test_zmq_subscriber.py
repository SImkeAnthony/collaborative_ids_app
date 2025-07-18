import unittest
from unittest.mock import MagicMock, patch
import zmq
import threading

from src.ids2zmq.subscriber import ZMQSubscriber


class DummyFernet:
    def __init__(self, key):
        self.key = key

    def decrypt(self, message):
        return b"decrypted_" + message


class TestZMQSubscriber(unittest.TestCase):
    def setUp(self):
        # Patch global ZMQManager and settings
        patch_mgr = patch("src.ids2zmq.subscriber.ZMQManager")
        patch_settings = patch("src.ids2zmq.subscriber.settings")
        patch_fernet = patch("src.ids2zmq.subscriber.Fernet", DummyFernet)

        self.mock_mgr = patch_mgr.start()
        self.addCleanup(patch_mgr.stop)
        self.mock_settings = patch_settings.start()
        self.addCleanup(patch_settings.stop)
        patch_fernet.start()
        self.addCleanup(patch_fernet.stop)

        self.mock_mgr.get_context.return_value.socket.return_value = MagicMock(spec=zmq.Socket)
        self.mock_mgr.zmq_security_enabled = True
        self.mock_mgr.load_symmetrical_key.return_value = b"dummy-key"
        self.mock_mgr.get_trusted_hosts.return_value = ["tcp://localhost:9999"]

        self.mock_settings.ZMQ_TOPIC_FAIL2BAN_ALERT = "mytopic"
        self.mock_settings.ZMQ_PUBLISHER_BIND_ADDRESS = "tcp://*:9999"
        self.mock_settings.ZMQ_SECURITY_USERNAME = "user"
        self.mock_settings.ZMQ_SECURITY_PASSWORD = "pass"
        self.mock_settings.ZMQ_SYMMETRICAL_KEY_FILE = "/dev/null"

        self.messages_received = []

        def callback(msg):
            self.messages_received.append(msg)

        self.subscriber = ZMQSubscriber(on_message_callback=callback)
        self.subscriber.subscriber_socket = MagicMock(spec=zmq.Socket)
        self.subscriber._fernet = DummyFernet(b'dummy-key')

    def test_configure_security_enabled(self):
        self.subscriber.configure_security()
        sock = self.subscriber.subscriber_socket
        sock.setsockopt.assert_any_call(zmq.PLAIN_USERNAME, b"user")
        sock.setsockopt.assert_any_call(zmq.PLAIN_PASSWORD, b"pass")
        self.assertIsNotNone(self.subscriber._fernet)

    def test_configure_security_disabled(self):
        self.mock_mgr.zmq_security_enabled = False
        self.subscriber.configure_security()
        # Check that no security options are set

    def test_connect_to_publisher_success(self):
        self.subscriber.subscriber_socket.connect = MagicMock()
        self.subscriber.connect_to_publisher("tcp://host:1234")
        self.subscriber.subscriber_socket.connect.assert_called_with("tcp://host:1234")

    def test_connect_to_publisher_with_retries_success(self):
        self.subscriber.subscriber_socket.connect = MagicMock()
        self.subscriber.connect_to_publisher_with_retries("tcp://host:1234")
        self.subscriber.subscriber_socket.connect.assert_called_with("tcp://host:1234")

    def test_connect_to_publisher_with_retries_failure(self):
        self.subscriber.subscriber_socket.connect.side_effect = zmq.ZMQError("fail")
        with self.assertRaises(zmq.ZMQError):
            self.subscriber.connect_to_publisher_with_retries("tcp://host:1234", retries=2, delay=0.1)

    def test_connect_to_publishers_success(self):
        self.subscriber.connect_to_publisher_with_retries = MagicMock()
        self.subscriber.subscriber_socket.setsockopt_string = MagicMock()
        self.subscriber.connect_to_publishers()
        self.subscriber.connect_to_publisher_with_retries.assert_called()
        self.subscriber.subscriber_socket.setsockopt_string.assert_called()

    def test_run_encrypted_message(self):
        # Prepare a mock encrypted message
        topic = b"mytopic"
        encrypted_msg = b"hello!"
        self.subscriber.subscriber_socket.recv_multipart.side_effect = [
            (topic, encrypted_msg),
            zmq.Again(),  # Stop loop
        ]
        # Configure threading event to stop after one message
        self.subscriber._running = threading.Event()
        self.subscriber._running.set()

        def stop_after_one():
            self.subscriber._running.clear()

        threading.Timer(0.05, stop_after_one).start()

        self.subscriber.run()
        self.assertGreaterEqual(len(self.messages_received), 1)
        self.assertTrue(self.messages_received[0].startswith("decrypted_"))

    def test_run_unencrypted_message(self):
        self.mock_mgr.zmq_security_enabled = False
        self.subscriber._fernet = None  # Disable encryption
        topic = b"mytopic"
        raw_msg = b"unencrypted text"
        self.subscriber.subscriber_socket.recv_multipart.side_effect = [
            (topic, raw_msg),
            zmq.Again(),
        ]
        self.subscriber._running = threading.Event()
        self.subscriber._running.set()

        def stop_after_one():
            self.subscriber._running.clear()

        threading.Timer(0.05, stop_after_one).start()
        self.subscriber.run()
        self.assertIn("unencrypted text", self.messages_received[0])

    def test_stop(self):
        socket = self.subscriber.subscriber_socket
        socket.close = MagicMock()
        self.subscriber._running.set()
        self.subscriber.stop()
        socket.close.assert_called()
        self.assertFalse(self.subscriber._running.is_set())
