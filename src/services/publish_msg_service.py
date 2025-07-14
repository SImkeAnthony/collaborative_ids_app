from src.models.alert_model import AlertModel
from src.zmq.publisher import ZMQPublisher

class PublishMsgService:
    def __init__(self, publisher: ZMQPublisher):
        self.publisher = publisher

    def publish_alert(self, alert: AlertModel):
        payload = alert.model_dump_json()
        self.publisher.publish_alert(alert=payload)
