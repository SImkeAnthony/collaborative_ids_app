import unittest
from unittest.mock import patch

from src.services.subscribe_msg_service import SubscribeMsgService


class TestSubscribeMsgService(unittest.TestCase):
    def setUp(self):
        self.service = SubscribeMsgService()
        self.valid_message = {
            "source_ip": "10.0.0.1",
            "target_ip": "192.168.1.123",
            "port": 22,
            "protocol": "tcp",
            "alert_type": "network",
            "severity": "high",
            "action": "banip",
            "jail": "sshd",
            "ip": "192.168.1.123",
            "reason": "test reason",
        }

    @patch("src.fail2ban.fail2ban_client.Fail2banClient.execute_action")
    @patch("src.fail2ban.jail.get_active_jails", return_value=["sshd"])
    def test_process_valid_message_success(self, mock_jails, mock_exec):
        mock_exec.return_value = True

        json_str = self._to_json(self.valid_message)
        result = self.service.process_received_message(json_str)

        # Solution 1 : exact match with Fail2banAction
        from src.fail2ban.action import Fail2banAction
        from ipaddress import IPv4Address
        mock_exec.assert_called_once_with(
            action=Fail2banAction.BAN,
            jail="sshd",
            ip=IPv4Address("192.168.1.123")
        )

        # Solution 2 : easier test with str and kwargs
        # args, kwargs = mock_exec.call_args
        # self.assertEqual(str(kwargs["ip"]), "192.168.1.123")
        # self.assertEqual(str(kwargs["action"]), "banip")
        # self.assertEqual(kwargs["jail"], "sshd")

        self.assertTrue(result)

    @patch("src.fail2ban.fail2ban_client.Fail2banClient.execute_action")
    @patch("src.fail2ban.jail.get_active_jails", return_value=["sshd"])
    def test_process_valid_message_ban_fails(self, mock_jails, mock_exec):
        mock_exec.return_value = False

        json_str = self._to_json(self.valid_message)
        result = self.service.process_received_message(json_str)

        mock_exec.assert_called_once()
        self.assertFalse(result)

    @patch("src.fail2ban.jail.get_active_jails", return_value=["sshd"])
    def test_message_with_missing_fields(self, mock_jails):
        # Remove IP, which is required for "banip"
        broken_data = self.valid_message.copy()
        del broken_data["ip"]

        result = self.service.process_received_message(self._to_json(broken_data))
        self.assertFalse(result)

    @patch("src.fail2ban.jail.get_active_jails", return_value=["sshd"])
    def test_message_with_invalid_jail(self, mock_jails):
        # Jail is not in get_active_jails()
        bad_data = self.valid_message.copy()
        bad_data["jail"] = "unknownjail"

        result = self.service.process_received_message(self._to_json(bad_data))
        self.assertFalse(result)

    def test_invalid_json_string(self):
        invalid_json = "This is not JSON"

        result = self.service.process_received_message(invalid_json)
        self.assertFalse(result)

    @patch("src.fail2ban.fail2ban_client.Fail2banClient.execute_action", side_effect=Exception("Boom"))
    @patch("src.fail2ban.jail.get_active_jails", return_value=["sshd"])
    def test_execution_fails_with_exception(self, mock_jails, mock_exec):
        json_str = self._to_json(self.valid_message)
        result = self.service.process_received_message(json_str)

        mock_exec.assert_called_once()
        self.assertFalse(result)

    def _to_json(self, data_dict):
        """Helper to convert dict to JSON with timestamp added."""
        import json
        from datetime import datetime, UTC
        data_dict = data_dict.copy()
        data_dict["timestamp"] = datetime.now(UTC).isoformat()
        return json.dumps(data_dict)

if __name__ == "__main__":
    unittest.main()