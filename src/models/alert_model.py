from pydantic import BaseModel
from typing import Optional
from datetime import datetime, UTC

class AlertModel(BaseModel):
    source_ip: str
    target_ip: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = "tcp"
    alert_type: str = "network"
    severity: str = "medium"
    action: str = "ban"
    reason: str
    timestamp: datetime = datetime.now(UTC)
