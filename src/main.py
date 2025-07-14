from fastapi import FastAPI
import uvicorn
from src.config.settings import settings
from src.zmq.manager import ZMQManager
from src.zmq.publisher import ZMQPublisher
from src.zmq.subscriber import ZMQSubscriber
from src.utils.gracefull_shutdown_manager import GracefulShutdownManager
from src.services.publish_msg_service import PublishMsgService
from src.services.subscribe_msg_service import SubscribeMsgService
from src.api.routes import get_routes
from src.utils.logger import setup_logging

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
        self.publisher.bind()
        self.subscriber_service = SubscribeMsgService()
        self.subscriber = ZMQSubscriber(on_message_callback=self.subscriber_service.process_received_message)
        self.subscriber.connect_to_publishers()

        # Register shutdown handlers
        self.shutdown_manager.register(self.publisher.close)
        self.shutdown_manager.register(self.subscriber.stop)
        self.shutdown_manager.register(ZMQManager.terminate_context())

        # Add routes to the FastAPI app
        publish_service = PublishMsgService(self.publisher)
        self.app.include_router(get_routes(publish_service))

    def run(self):
        """
        Run the FastAPI application with the configured ZMQ components.
        This method is typically called when starting the application.
        """
        self.shutdown_manager.hook_signals()
        self.subscriber.start()
        uvicorn.run(self.app, host=settings.API_HOST, port=settings.API_PORT, log_level=settings.LOG_LEVEL.lower())

if __name__ == "__main__":
    main_app = Main()
    main_app.run()