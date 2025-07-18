import time

from fastapi import FastAPI
import uvicorn
import logging
from src.config.settings import settings
from src.ids2zmq.manager import ZMQManager
from src.ids2zmq.publisher import ZMQPublisher
from src.ids2zmq.subscriber import ZMQSubscriber
from src.utils.graceful_shutdown_manager import GracefulShutdownManager
from src.services.publish_msg_service import PublishMsgService
from src.services.subscribe_msg_service import SubscribeMsgService
from src.api.routes import get_routes
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)

class Main:
    """
    Main class to initialize the FastAPI application and ZMQ components.
    This class is responsible for setting up the ZMQ publisher and subscriber,
    handling graceful shutdown, and registering API routes.
    """

    def __init__(self):
        self.app = FastAPI()
        self.shutdown_manager = GracefulShutdownManager()

        setup_logging(log_level="INFO", log_file=settings.LOG_FILE)

        # Initialize ZMQ Publisher and Subscriber
        self.publisher = ZMQPublisher()
        self.subscriber_service = SubscribeMsgService()
        self.subscriber = ZMQSubscriber(on_message_callback=self.subscriber_service.process_received_message)

        # Initialize ZMQ context and security if enabled
        if ZMQManager.zmq_security_enabled:
            ZMQManager.generate_symmetrical_key(filename=settings.ZMQ_SYMMETRICAL_KEY_FILE)
            self.publisher.configure_security()
            self.subscriber.configure_security()

        self.publisher.bind()
        self.subscriber.connect_to_publishers()

        # Register shutdown handlers
        self.shutdown_manager.register(self.publisher.close)
        self.shutdown_manager.register(self.subscriber.stop)
        self.shutdown_manager.register(ZMQManager.stop_authenticator)
        self.shutdown_manager.register(ZMQManager.terminate_context)
        logger.info("ZMQ components initialized and shutdown handlers registered.")

        # Add routes to the FastAPI app
        publish_service = PublishMsgService(self.publisher)
        self.app.include_router(get_routes(publish_service))
        logger.info("API routes registered.")

    def run(self):
        """
        Run the FastAPI application with the configured ZMQ components.
        This method is typically called when starting the application.
        """
        try:
            self.shutdown_manager.hook_signals()
            self.subscriber.start()
        except Exception as e:
            logger.error(f"Error starting subscriber: {e}")
            self.shutdown_manager.shutdown()
        try:
            uvicorn.run(self.app, host=settings.API_HOST, port=settings.API_PORT, log_level=settings.LOG_LEVEL.lower())
            logger.info(f"FastAPI app running at {settings.API_HOST}:{settings.API_PORT}")
        except Exception as e:
            logger.error(f"Error running FastAPI app: {e}")
            self.shutdown_manager.shutdown()

if __name__ == "__main__":
    main_app = Main()
    main_app.run()