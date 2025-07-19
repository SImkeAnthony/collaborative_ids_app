from enum import Enum

class Fail2banAction(str, Enum):
    BAN = "banip"
    UNBAN = "unbanip"
    STATUS = "status"
