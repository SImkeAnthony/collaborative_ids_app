import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.ids2zmq.manager import ZMQManager

class TestZMQManager(unittest.TestCase):
    @patch('src.ids2zmq.manager.zmq.Context')
    def test_get_context_initializes_and_returns_context(self, mock_context):
        mock_instance = MagicMock()
        mock_context.return_value.instance.return_value = mock_instance
        ZMQManager._context = None
        context = ZMQManager.get_context()
        self.assertIs(context, mock_instance)
        mock_context.return_value.instance.assert_called_once()

    @patch('src.ids2zmq.manager.zmq.Context')
    def test_get_context_returns_existing_context(self, mock_context):
        mock_instance = MagicMock()
        ZMQManager._context = mock_instance
        context = ZMQManager.get_context()
        self.assertIs(context, mock_instance)
        mock_context.return_value.instance.assert_not_called()

    @patch('src.ids2zmq.manager.zmq.Context')
    def test_terminate_context(self, mock_context):
        mock_instance = MagicMock()
        ZMQManager._context = mock_instance
        ZMQManager.terminate_context()
        mock_instance.term.assert_called_once()
        self.assertIsNone(ZMQManager._context)

    def test_terminate_context_no_context(self):
        ZMQManager._context = None
        ZMQManager.terminate_context()
        self.assertIsNone(ZMQManager._context)

    @patch('src.ids2zmq.manager.zmq.Context')
    def test_reset_context(self, mock_context):
        mock_instance = MagicMock()
        mock_context.return_value.instance.return_value = mock_instance
        ZMQManager._context = MagicMock()
        ZMQManager.reset_context()
        self.assertIs(ZMQManager._context, mock_instance)

    @patch('src.ids2zmq.manager.settings')
    def test_get_trusted_hosts_from_settings(self, mock_settings):
        mock_settings.TRUSTED_HOSTS = "192.168.1.1,192.168.1.2"
        mock_settings.TRUSTED_HOSTS_FILE = ""
        hosts = ZMQManager.get_trusted_hosts()
        self.assertEqual(hosts, ["192.168.1.1", "192.168.1.2"])

    @patch('src.ids2zmq.manager.settings')
    @patch('builtins.open', new_callable=mock_open, read_data='["10.0.0.1","10.0.0.2"]')
    @patch('src.ids2zmq.manager.json.load')
    def test_get_trusted_hosts_from_file(self, mock_json_load, mock_open_file, mock_settings):
        mock_settings.TRUSTED_HOSTS = ""
        mock_settings.TRUSTED_HOSTS_FILE = "trusted_hosts.json"
        mock_json_load.return_value = ["10.0.0.1", "10.0.0.2"]
        hosts = ZMQManager.get_trusted_hosts()
        self.assertEqual(hosts, ["10.0.0.1", "10.0.0.2"])
        mock_open_file.assert_called_once()
        mock_json_load.assert_called_once()

    @patch('src.ids2zmq.manager.settings')
    def test_get_trusted_hosts_no_configured(self, mock_settings):
        mock_settings.TRUSTED_HOSTS = ""
        mock_settings.TRUSTED_HOSTS_FILE = ""
        with self.assertRaises(ValueError):
            ZMQManager.get_trusted_hosts()

    @patch('src.ids2zmq.manager.settings')
    def test_get_trusted_hosts_invalid_hosts(self, mock_settings):
        mock_settings.TRUSTED_HOSTS = None
        mock_settings.TRUSTED_HOSTS_FILE = ""
        with self.assertRaises(Exception):
            ZMQManager.get_trusted_hosts()

    @patch('src.ids2zmq.manager.settings')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_trusted_hosts_file_exception(self, mock_open_file, mock_settings):
        mock_settings.TRUSTED_HOSTS = ""
        mock_settings.TRUSTED_HOSTS_FILE = "trusted_hosts.json"
        mock_open_file.side_effect = IOError("File not found")
        with self.assertRaises(Exception):
            ZMQManager.get_trusted_hosts()

if __name__ == '__main__':
    unittest.main()