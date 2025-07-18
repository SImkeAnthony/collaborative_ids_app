import signal
import logging
from typing import List, Callable

logger = logging.getLogger(__name__)

"""
Use this class to manage graceful shutdowns in your application.
Call it as follows:
# Register cleanup functions
shutdown_manager.register(subscriber.stop)
shutdown_manager.register(publisher.close)  

# Hook signals for graceful shutdown
shutdown_manager.hook_signals()
"""
class GracefulShutdownManager:
    def __init__(self):
        self._cleanup_callbacks: List[Callable] = []

    def register(self, cleanup_callable: Callable):
        """
        Register a cleanup function to be called on shutdown.
        """
        self._cleanup_callbacks.append(cleanup_callable)

    def shutdown(self, *args):
        logger.info("Received shutdown signal, starting graceful shutdown...")
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
        logger.info("All cleanup functions executed successfully.")
        exit(0)

    def hook_signals(self):
        """
        Configure signal handlers for graceful shutdown.
        """
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
