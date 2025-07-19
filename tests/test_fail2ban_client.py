import unittest
from unittest.mock import patch, MagicMock
from src.fail2ban.fail2ban_client import Fail2banClient

class TestFail2banClient(unittest.TestCase):
    @patch("src.fail2ban.fail2ban_client.subprocess.run")
    def test_execute_action_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = Fail2banClient.execute_action("ban", jail="ssh", ip="1.2.3.4")
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertIn("fail2ban-client", cmd)
        self.assertIn("set", cmd)
        self.assertIn("ssh", cmd)
        self.assertIn("ban", cmd)
        self.assertIn("1.2.3.4", cmd)

    @patch("src.fail2ban.fail2ban_client.subprocess.run")
    def test_execute_action_failure_nonzero_returncode(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error"
        mock_run.return_value = mock_result

        result = Fail2banClient.execute_action("unban", jail="ssh", ip="1.2.3.4")
        self.assertFalse(result)

    @patch("src.fail2ban.fail2ban_client.subprocess.run", side_effect=Exception("OS error"))
    def test_execute_action_raises_exception(self, mock_run):
        result = Fail2banClient.execute_action("ban", jail="ssh", ip="1.2.3.4")
        self.assertFalse(result)

    @patch("src.fail2ban.fail2ban_client.subprocess.run")
    def test_execute_action_ip_is_none(self, mock_run):
        # ip est None : on ne doit pas l'ajouter à la commande
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = Fail2banClient.execute_action("status", jail="ssh", ip=None)
        self.assertTrue(result)
        cmd = mock_run.call_args[0][0]
        self.assertNotIn(None, cmd)
        self.assertNotIn("None", map(str, cmd))
        self.assertEqual(cmd, ["fail2ban-client", "set", "ssh", "status"])

if __name__ == "__main__":
    unittest.main()