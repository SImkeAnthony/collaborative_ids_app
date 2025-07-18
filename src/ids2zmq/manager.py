import zmq
import logging
import json
import os

from zmq.auth.thread import ThreadAuthenticator

from src.config.settings import settings
from src.utils.keysManager import KeysManager
from src.ids2zmq.security import ZMQSecurity

logger = logging.getLogger(__name__)

class ZMQManager:
    """Manage the ZeroMQ context for the application."""
    _context: zmq.Context = None
    _keys_manager: KeysManager = KeysManager()
    _authenticator: ThreadAuthenticator = None
    zmq_security_enabled: bool = settings.ENABLE_ZMQ_SECURITY
    zmq_security: ZMQSecurity = ZMQSecurity()

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
                config_path = os.path.join(os.path.dirname(__file__), '..', 'config', str(settings.TRUSTED_HOSTS_FILE))
                config_path = os.path.abspath(config_path)
                with open(config_path, 'r') as file:
                    trusted_hosts = json.load(file)
                logger.info(f"Trusted hosts loaded from file.")
                return trusted_hosts
            except Exception as e:
                logger.error(f"Error loading trusted hosts from file: {e}")
                raise
        logger.error("No trusted hosts configured.")
        raise ValueError("No trusted hosts configured in settings.")

    @classmethod
    def enable_plain_auth(cls, context: zmq.Context) -> ThreadAuthenticator:
        if not cls.zmq_security_enabled:
            logger.warning("ZMQ security is not enabled, skipping PLAIN authentication setup.")
            return None
        try:
            cls._authenticator = ThreadAuthenticator(context)
            cls._authenticator.start()
            cls._authenticator.configure_plain(domain='*', passwords={
                settings.ZMQ_SECURITY_USERNAME: settings.ZMQ_SECURITY_PASSWORD,
            })
            logger.info("PLAIN authentication server enabled.")
            return cls._authenticator
        except Exception as e:
            logger.error(f"Error enabling PLAIN authentication server: {e}")
            raise

    @classmethod
    def stop_authenticator(cls):
        if cls._authenticator:
            cls._authenticator.stop()
            logger.info("ZMQ PLAIN authenticator stopped.")
            cls._authenticator = None

    @classmethod
    def generate_key(cls, filename: str = "default_key") -> tuple[bytes, bytes]:
        """Generate and store a key in the keys' manager."""
        if os.path.exists(settings.ZMQ_CERTS_PATH+ filename + ".key_secret"):
            logger.info("ZMQ key pair already exists, loading from file.")
            pub, private = cls.zmq_security.load_certificate(filename=settings.ZMQ_CERTS_PATH + filename)
        else :
            pub, private = cls.zmq_security.generate_key(filename=filename)
            logger.info("Generated new ZMQ key pair.")
        return pub, private

    @classmethod
    def load_certificate(cls, filename: str) -> tuple[bytes, bytes]:
        """Load a ZMQ certificate from a file."""
        if not os.path.exists(settings.ZMQ_CERTS_PATH + filename + ".key_secret"):
            logger.error(f"Certificate file {filename} does not exist.")
            raise FileNotFoundError(f"Certificate file {filename} does not exist.")
        return cls.zmq_security.load_certificate(filename=settings.ZMQ_CERTS_PATH + filename)

