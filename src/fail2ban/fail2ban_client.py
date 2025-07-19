import subprocess
import logging

logger = logging.getLogger(__name__)


class Fail2banClient:
    """
    Fail2banClient interacts with the local fail2ban-server to manage IP bans.
    Methods:
        execute_action(action, jail, ip): Executes a Fail2ban action (ban/unban) on a specified jail for a given IP address.
    """

    @classmethod
    def execute_action(cls, action: str, jail: str = None, ip: str = None) -> bool:
        """
        Execute a Fail2ban action on a specified jail for a given IP address.

        Args:
            action (str): The action to perform (e.g., "ban", "unban").
            jail (str): The jail to target (e.g., "sshd").
            ip (str): The IP address to ban or unban. If None, the action applies to all IPs in the jail.
        Returns:
            bool: True if the action was successfully executed, False otherwise.
        """
        cmd = ["fail2ban-client", "set", jail, action, ip]
        if ip:
            cmd.append(ip)

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode == 0:
                logger.info(f"Successfully executed action '{action}' on jail '{jail}' for IP: {ip or 'N/A'}")
                logger.debug(result.stdout)
                return True
            else:
                logger.error(f"Error executing action '{action}' on jail '{jail}' for IP: {ip or 'N/A'}")
                return False

        except Exception as e:
            logger.error("Error executing Fail2ban command: %s", e)
            return False
