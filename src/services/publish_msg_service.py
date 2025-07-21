from datetime import datetime

from pydantic import IPvAnyAddress

from src.models.alert_model import AlertModel
from src.ids2zmq.publisher import ZMQPublisher

class PublishMsgService:
    """
    Service for publishing alert messages using a ZMQ publisher.
    Args:
        publisher (ZMQPublisher): An instance of ZMQPublisher to handle message publishing.
    Attributes:
        publisher (ZMQPublisher): The ZMQPublisher instance used to publish messages.
    Methods:
        publish_alert(alert: AlertModel): Publishes an alert message with a timestamp.
    """
    def __init__(self, publisher: ZMQPublisher):
        self.publisher = publisher

    def publish_alert(self, alert: AlertModel):
        alert.timestamp = datetime.now()
        alert.target_ip = IPvAnyAddress("0.0.0.0") if alert.target_ip is None else alert.target_ip
        payload = alert.to_json()
        self.publisher.publish_alert(alert=payload)
