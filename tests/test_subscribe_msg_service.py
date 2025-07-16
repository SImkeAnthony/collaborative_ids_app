import unittest
from unittest.mock import patch, MagicMock
from src.services.subscribe_msg_service import SubscribeMsgService

class TestSubscribeMsgService(unittest.TestCase):
    @patch('src.services.subscribe_msg_service.AlertModel')
    @patch('builtins.print')
    def test_process_received_message_valid(self, mock_print, mock_alert_model):
        message = '{"field1": "value1", "field2": "value2"}'
        mock_alert_instance = MagicMock()
        mock_alert_model.return_value = mock_alert_instance

        SubscribeMsgService.process_received_message(message)

        mock_alert_model.assert_called_once_with(field1="value1", field2="value2")
        mock_print.assert_called_with(f"Alert received : {mock_alert_instance}")

    @patch('builtins.print')
    def test_process_received_message_invalid_json(self, mock_print):
        message = '{"field1": "value1", "field2": value2}'  # invalid JSON

        SubscribeMsgService.process_received_message(message)

        self.assertTrue(any("Error for parsing message" in args[0] for args, _ in mock_print.call_args_list))

    @patch('src.services.subscribe_msg_service.AlertModel', side_effect=Exception("init error"))
    @patch('builtins.print')
    def test_process_received_message_alertModel_exception(self, mock_print, mock_alert_model):
        message = '{"field1": "value1", "field2": "value2"}'

        SubscribeMsgService.process_received_message(message)

        self.assertTrue(any("Error for parsing message" in args[0] for args, _ in mock_print.call_args_list))

if __name__ == "__main__":
    unittest.main()