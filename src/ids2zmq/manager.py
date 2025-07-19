import zmq
import logging
import json
import os

from fernet import Fernet
from zmq.auth.thread import ThreadAuthenticator

from src.config.settings import settings
from src.utils.keysManager import KeysManager
from src.ids2zmq.security import ZMQSecurity

logger = logging.getLogger(__name__)

class ZMQManager:
    """
    Manage the ZeroMQ context for the application.
    Attributes:
        _context (zmq.Context): The ZeroMQ context instance.
        _keys_manager (KeysManager): Instance of KeysManager for key management.
        _authenticator (ThreadAuthenticator): The authenticator for PLAIN authentication.
        zmq_security_enabled (bool): Flag to enable or disable ZMQ security.
        zmq_security (ZMQSecurity): Instance of ZMQSecurity for handling security operations.
    Methods:
        get_context(): Get the ZeroMQ context, initializing it if it does not exist.
        terminate_context(): Terminate the ZeroMQ context if it exists.
        reset_context(): Reset the ZeroMQ context, useful for testing or reinitialization.
        get_trusted_hosts(): Get the list of trusted hosts from settings or a configuration file.
        enable_plain_auth(context): Enable PLAIN authentication for ZeroMQ if security is enabled.
        stop_authenticator(): Stop the PLAIN authenticator if it exists.
        generate_key(filename): Generate and store a key in the keys' manager.
        load_certificate(filename): Load a ZMQ certificate from a file.
        generate_symmetrical_key(filename): Generate and store a symmetric key for low encryption.
        load_symmetrical_key(filename): Load the symmetric key from a file.
    """
    _context: zmq.Context = None
    _keys_manager: KeysManager = KeysManager()
    _authenticator: ThreadAuthenticator = None
    zmq_security_enabled: bool = settings.ENABLE_ZMQ_SECURITY
    zmq_security: ZMQSecurity = ZMQSecurity()

    @classmethod
    def get_context(cls) -> zmq.Context:
        """
        Get the ZeroMQ context, initializing it if it does not exist.
        Returns:
            zmq.Context: The ZeroMQ context instance.
        """
        if cls._context is None:
            logger.info("Initializing ZeroMQ context.")
            cls._context = zmq.Context().instance()
        return cls._context

    @classmethod
    def terminate_context(cls):
        """Terminate the ZeroMQ context if it exists."""
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
        """
        Get the list of trusted hosts from settings or a configuration file.
        Returns:
            list[str]: A list of trusted hostnames or IP addresses.
        Raises:
            ValueError: If no trusted hosts are configured.
            Exception: If there is an error parsing the trusted hosts.
        """
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
        """
        Enable PLAIN authentication for ZeroMQ if security is enabled.
        Args:
            context (zmq.Context): The ZeroMQ context to configure.
        Returns:
            ThreadAuthenticator: The authenticator instance if successful, None otherwise.
        Raises:
            Exception: If there is an error enabling the PLAIN authentication server.
        """
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
        """Stop the PLAIN authenticator if it exists."""
        if cls._authenticator:
            cls._authenticator.stop()
            logger.info("ZMQ PLAIN authenticator stopped.")
            cls._authenticator = None

    @classmethod
    def generate_key(cls, filename: str = "default_key") -> tuple[bytes, bytes]:
        """
        Generate and store a key in the keys' manager.
        Args:
            filename (str): The name of the file to store the key.
        Returns:
            tuple[bytes, bytes]: A tuple containing the public and private keys.
        """
        if os.path.exists(settings.ZMQ_CERTS_PATH + filename + ".key_secret"):
            logger.info("ZMQ key pair already exists, loading from file.")
            pub, private = cls.zmq_security.load_certificate(filename=settings.ZMQ_CERTS_PATH + filename + ".key_secret")
        else :
            pub, private = cls.zmq_security.generate_key(filename=filename)
            logger.info("Generated new ZMQ key pair.")
        return pub, private

    @classmethod
    def load_certificate(cls, filename: str) -> tuple[bytes, bytes]:
        """
        Load a ZMQ certificate from a file.
        Args:
            filename (str): The name of the file containing the certificate.
        Returns:
            tuple[bytes, bytes]: A tuple containing the public and private keys.
        Raises:
            FileNotFoundError: If the certificate file does not exist.
        """
        if not os.path.exists(settings.ZMQ_CERTS_PATH + filename + ".key_secret"):
            logger.error(f"Certificate file {filename} does not exist.")
            raise FileNotFoundError(f"Certificate file {filename} does not exist.")
        return cls.zmq_security.load_certificate(filename=settings.ZMQ_CERTS_PATH + filename)

    @classmethod
    def generate_symmetrical_key(cls, filename: str = "default_symmetric_key.key") -> bytes:
        """
        Generate and store a symmetric key for low encryption.
        Args:
            filename (str): The name of the file to store the symmetric key.
        Returns:
            bytes: The generated symmetric key.
        """
        if os.path.exists(settings.ZMQ_CERTS_PATH + filename):
            logger.info("Symmetric key already exists, loading from file.")
            return cls.load_symmetrical_key(filename=filename)
        else:
            key = cls.zmq_security.generate_symmetrical_key(filename=filename)
            logger.info("Generated new symmetric key.")
            return key

    @classmethod
    def load_symmetrical_key(cls, filename: str = "default_symmetric_key.key") -> bytes:
        """
        Load the symmetric key from a file.
        Args:
            filename (str): The name of the file containing the symmetric key.
        Returns:
            bytes: The loaded symmetric key.
        Raises:
            FileNotFoundError: If the symmetric key file does not exist.
        """
        if not os.path.exists(settings.ZMQ_CERTS_PATH + filename):
            logger.error(f"Symmetric key file {filename} does not exist.")
            raise FileNotFoundError(f"Symmetric key file {filename} does not exist.")
        key = cls.zmq_security.load_symmetrical_key(filename=settings.ZMQ_CERTS_PATH + filename)
        logger.info("Loaded symmetric key successfully.")
        return key

