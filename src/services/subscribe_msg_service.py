from src.models.alert_model import AlertModel
import json

class SubscribeMsgService:
    @classmethod
    def process_received_message(cls, message: str):
        try:
            alert_data = json.loads(message)
            alert = AlertModel(**alert_data)
            print(f"Alert received : {alert}")
            # Add another action here
        except Exception as e:
            print(f"Error for parsing message : {e}")
