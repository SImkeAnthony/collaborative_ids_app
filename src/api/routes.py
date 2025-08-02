from fastapi import APIRouter, status
from src.models.alert_model import AlertModel
from src.services.publish_msg_service import PublishMsgService
from src.shared.custom_cache import is_duplicate
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
            if is_duplicate(ip=alert.ip, action=alert.action, jail=alert.jail):
                # If the alert is a duplicate, log it and return a response
                logger.info(f"HTTP STATUS 208 - Duplicate alert detected: {alert}")
                return {"status": "duplicate", "message": f"Alert ({alert.ip}, {alert.action}, {alert.jail}) already processed"}, status.HTTP_208_ALREADY_REPORTED
            else:
                logger.info(f"HTTP STATUS 202 - POST /alert called with alert: {alert}")
                publisher_service.publish_alert(alert)
                return {"status": "alert published"}
        except Exception as e:
            logger.error(f"POST /alert failed: {e}")
            # return the error response
            return {"status": "error", "HTTP ERROR 500": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    return router
