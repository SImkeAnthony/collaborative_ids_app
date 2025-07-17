import unittest
from unittest.mock import MagicMock
from src.models.alert_model import AlertModel
from src.ids2zmq.publisher import ZMQPublisher
from src.services.publish_msg_service import PublishMsgService

class TestPublishMsgService(unittest.TestCase):
    def setUp(self):
        self.mock_publisher = MagicMock(spec=ZMQPublisher)
        self.service = PublishMsgService(self.mock_publisher)

    def test_publish_alert(self):
        mock_alert = MagicMock(spec=AlertModel)
        mock_alert.model_dump_json.return_value = '{"id": 1, "msg": "test"}'
        self.service.publish_alert(mock_alert)
        self.mock_publisher.publish_alert.assert_called_once_with(alert='{"id": 1, "msg": "test"}')

if __name__ == "__main__":
    unittest.main()