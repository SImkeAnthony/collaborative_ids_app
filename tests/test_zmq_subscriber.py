# Write a test for subscriber.py from zmq package
import unittest
import zmq
import unittest.mock
class TestZMQSubscriber(unittest.TestCase):

    def setUp(self):
        self.mock_context = unittest.mock.Mock()
        self.mock_socket = unittest.mock.Mock()
        self.mock_context.socket.return_value = self.mock_socket
        self.mock_callback = unittest.mock.Mock()
        self.patcher_manager = unittest.mock.patch('src.zmq.manager.ZMQManager.get_context',
                                                   return_value=self.mock_context)
        self.patcher_hosts = unittest.mock.patch('src.zmq.manager.ZMQManager.get_trusted_hosts',
                                                 return_value=['tcp://localhost:5555'])
        self.patcher_settings = unittest.mock.patch('src.config.settings.settings.ZMQ_TOPIC_FAIL2BAN_ALERT', 'ALERT')
        self.patcher_bind = unittest.mock.patch('src.config.settings.settings.ZMQ_PUBLISHER_BIND_ADDRESS',
                                                'tcp://localhost:5555')
        self.patcher_manager.start()
        self.patcher_hosts.start()
        self.patcher_settings.start()
        self.patcher_bind.start()
        self.subscriber = __import__('src.zmq.subscriber').zmq.subscriber.ZMQSubscriber(self.mock_callback)

    def tearDown(self):
        self.patcher_manager.stop()
        self.patcher_hosts.stop()
        self.patcher_settings.stop()
        self.patcher_bind.stop()

    def test_connect_to_publisher_success(self):
        self.subscriber.connect_to_publisher('tcp://localhost:5555')
        self.mock_socket.connect.assert_called_with('tcp://localhost:5555')

    def test_connect_to_publisher_failure(self):
        self.mock_socket.connect.side_effect = zmq.ZMQError('fail')
        with self.assertRaises(zmq.ZMQError):
            self.subscriber.connect_to_publisher('tcp://localhost:5555')

    def test_connect_to_publishers(self):
        self.subscriber.connect_to_publishers()
        self.mock_socket.connect.assert_called_with('tcp://localhost:5555')
        self.mock_socket.setsockopt_string.assert_called_with(zmq.SUBSCRIBE, 'ALERT')

    def test_run_receives_message(self):
        self.mock_socket.recv_multipart.side_effect = [
            [b'ALERT', b'test_message'],
            zmq.Again,
            Exception('stop')
        ]
        self.subscriber._running.is_set = unittest.mock.Mock(side_effect=[True, True, False])
        with unittest.mock.patch.object(self.subscriber, '_on_message_callback') as mock_cb:
            self.subscriber.run()
            mock_cb.assert_called_with('test_message')

    def test_stop(self):
        self.subscriber.stop()
        self.assertFalse(self.subscriber._running.is_set())
        self.mock_socket.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()