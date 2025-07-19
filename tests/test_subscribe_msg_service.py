import unittest
from unittest.mock import patch

from src.services.subscribe_msg_service import SubscribeMsgService


class TestSubscribeMsgService(unittest.TestCase):
    def setUp(self):
        self.service = SubscribeMsgService()

    @patch("src.services.subscribe_msg_service.Fail2banClient.execute_action")
    def test_process_valid_message_successful_ban(self, mock_execute):
        mock_execute.return_value = True

        message = '{"action": "ban", "jail": "ssh", "ip": "192.168.1.1", "source_ip": "192.168.1.1"}'

        result = self.service.process_received_message(message)

        mock_execute.assert_called_once_with(action="ban", jail="ssh", ip="192.168.1.1")
        self.assertTrue(result)

    @patch("src.services.subscribe_msg_service.Fail2banClient.execute_action")
    def test_process_valid_message_failed_ban(self, mock_execute):
        mock_execute.return_value = False

        message = '{"action": "ban", "jail": "ssh", "ip": "192.168.1.1", "source_ip": "192.168.1.1"}'

        result = self.service.process_received_message(message)

        mock_execute.assert_called_once_with(action="ban", jail="ssh", ip="192.168.1.1")
        self.assertFalse(result)

    def test_process_invalid_json_message(self):
        # Invalid JSON
        message = 'not-a-valid-json'

        result = self.service.process_received_message(message)

        self.assertFalse(result)

    def test_process_invalid_model_missing_field(self):
        # Missing source_ip -> should raise validation error
        message = '{"action": "ban", "jail": "ssh", "ip": "192.168.1.1"}'

        result = self.service.process_received_message(message)

        self.assertFalse(result)

    @patch("src.services.subscribe_msg_service.Fail2banClient.execute_action", side_effect=Exception("boom"))
    def test_execute_action_raises_exception(self, mock_execute):
        # Mock complete alert, but Fail2ban fails internally
        message = '{"action": "ban", "jail": "ssh", "ip": "192.168.1.1", "source_ip": "192.168.1.1"}'

        result = self.service.process_received_message(message)

        mock_execute.assert_called_once()
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()