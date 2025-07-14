import zmq
import logging
import json
from src.config.settings import settings
import socket

logger = logging.getLogger(__name__)

class ZMQManager:
    """Manage the ZeroMQ context for the application."""
    _context: zmq.Context = None

    @classmethod
    def get_context(cls) -> zmq.Context:
        if cls._context is None:
            logger.info("Initializing ZeroMQ context.")
            cls._context = zmq.Context().instance()
        return cls._context

    @classmethod
    def terminate_context(cls):
        if cls._context:
            logger.info("Terminating ZeroMQ context.")
            cls._context.term()
            cls._context = None

    @classmethod
    def reset_context(cls):
        """Reset the ZeroMQ context, useful for testing or reinitialization."""
        logger.info("Resetting ZeroMQ context.")
        cls.terminate_context()
        cls._context = None
        cls.get_context()

    @classmethod
    def get_trusted_hosts(cls) -> list[str]:
        """Return a list of trusted hosts for ZeroMQ connections."""
        if settings.TRUSTED_HOSTS != "":
            try:
                trusted_hosts = settings.TRUSTED_HOSTS.split(',')
                logger.info(f"Trusted hosts loaded.")
                return trusted_hosts
            except Exception as e:
                logger.error(f"Error parsing trusted hosts: {e}")
                raise
        elif settings.TRUSTED_HOSTS_FILE != "":
            try:
                with open(settings.TRUSTED_HOSTS_FILE, 'r') as file:
                    trusted_hosts = json.load(file)
                logger.info(f"Trusted hosts loaded from file.")
                return trusted_hosts
            except Exception as e:
                logger.error(f"Error loading trusted hosts from file: {e}")
                raise
        logger.error("No trusted hosts configured.")
        raise ValueError("No trusted hosts configured in settings.")
