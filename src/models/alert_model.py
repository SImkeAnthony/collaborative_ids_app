from pydantic import BaseModel, IPvAnyAddress, field_validator
from typing import Optional
from datetime import datetime, UTC
from src.fail2ban.jail import get_active_jails
from src.fail2ban.action import Fail2banAction

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
    hostname: Optional[str] = "N/A"
    source_ip: Optional[IPvAnyAddress] = None
    target_ip: Optional[IPvAnyAddress] = None
    port: Optional[int] = None
    protocol: Optional[str] = "ssh"
    alert_type: str = "ssh_brute_force"
    severity: str = "medium"
    jail: str = "sshd"
    action: Fail2banAction = "banip"
    ip: Optional[IPvAnyAddress] = None
    reason: str = "N/A"
    timestamp: datetime = datetime.now(UTC)

    @field_validator("jail")
    def validate_jail(cls, v):
        if v not in get_active_jails():
            raise ValueError(f"Jail is not authorized : {v}")
        return v

    @field_validator("action")
    def validate_action(cls, v, values):
        action = values.data.get("action")
        if action in {Fail2banAction.BAN, Fail2banAction.UNBAN} and v is None:
            raise ValueError("A valid action is required for ban or unban operations.")
        return v

    def __str__(self):
        return f"AlertModel(source_ip={self.source_ip}, target_ip={self.target_ip}, port={self.port}, protocol={self.protocol}, alert_type={self.alert_type}, severity={self.severity}, action={self.action}, jail={self.jail}, ip={self.ip}, reason={self.reason}, timestamp={self.timestamp})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Convert the AlertModel instance to a dictionary.
        Returns:
            dict: Dictionary representation of the AlertModel instance.
        """
        return self.model_dump(mode="json", exclude_none=True)

    def to_json(self):
        """
        Convert the AlertModel instance to a JSON string.
        Returns:
            str: JSON string representation of the AlertModel instance.
        """
        return self.model_dump_json(exclude_none=True)

    @classmethod
    def from_json(cls, json_str: str) -> "AlertModel":
        """
        Create an AlertModel instance from a JSON string.
        Args:
            json_str (str): JSON string representation of the AlertModel.
        Returns:
            AlertModel: An instance of AlertModel created from the JSON string.
        """
        return cls.model_validate_json(json_str)