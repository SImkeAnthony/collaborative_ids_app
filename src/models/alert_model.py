from pydantic import BaseModel
from typing import Optional
from datetime import datetime, UTC

class AlertModel(BaseModel):
    """
    Represents an alert model for Fail2Ban notifications.

    Attributes:
        source_ip (str): The source IP address of the alert.
        target_ip (Optional[str]): The target IP address, if applicable.
        port (Optional[int]): The port number associated with the alert.
        protocol (Optional[str]): The protocol used, default is "tcp".
        alert_type (str): The type of alert, default is "network".
        severity (str): The severity level of the alert, default is "medium".
        action (str): The action to be taken, default is "ban".
        jail (str): The jail name for Fail2Ban, default is "sshd".
        ip (str): The IP address to be banned.
        reason (str): The reason for the ban.
        timestamp (datetime): The timestamp of the alert, defaults to current time in UTC.
    """
    source_ip: str
    target_ip: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = "tcp"
    alert_type: str = "network"
    severity: str = "medium"
    action: str = "ban"
    jail: str = "sshd"
    ip: str = ""
    reason: str = ""
    timestamp: datetime = datetime.now(UTC)
