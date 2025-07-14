from fastapi import APIRouter, status
from src.models.alert_model import AlertModel
from src.services.publish_msg_service import PublishMsgService

def get_routes(publisher_service: PublishMsgService):
    router = APIRouter()

    @router.post("/alert", status_code=status.HTTP_202_ACCEPTED)
    def send_alert(alert: AlertModel):
        publisher_service.publish_alert(alert)
        return {"status": "alert published"}

    return router
