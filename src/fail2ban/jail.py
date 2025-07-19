import subprocess
import logging

logger = logging.getLogger(__name__)

def get_active_jails():
    try:
        result = subprocess.run(
            ["fail2ban-client", "status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        for line in result.stdout.splitlines():
            if "Jail list:" in line:
                return set(map(str.strip, line.split(":", 1)[1].split(",")))
    except Exception as e:
        logger.error(f"Error retrieving active jails: {e}")
    return {"sshd"}  # fallback