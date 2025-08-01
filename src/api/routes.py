from fastapi import APIRouter, status
from src.models.alert_model import AlertModel
from src.services.publish_msg_service import PublishMsgService
import logging

logger = logging.getLogger(__name__)

def get_routes(publisher_service: PublishMsgService):
    """
    Create and return the API router with the alert route.
    Args:
        publisher_service (PublishMsgService): The service used to publish alerts.
    Returns:
        APIRouter: The FastAPI router with the alert route.
    """
    router = APIRouter()

    @router.post("/alert", status_code=status.HTTP_202_ACCEPTED)
    def send_alert(alert: AlertModel):
        """
        Endpoint to publish an alert.
        Args:
            alert (AlertModel): The alert to be published.
        Returns:
            dict: A response indicating the status of the alert publication.
        """
        try:
            logger.info(f"POST /alert called with alert: {alert}")
            publisher_service.publish_alert(alert)
            return {"status": "alert published"}
        except Exception as e:
            logger.error(f"POST /alert failed: {e}")
            # return the error response
            return {"status": "error", "message": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    return router
