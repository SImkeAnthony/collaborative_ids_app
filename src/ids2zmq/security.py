from zmq import auth
import logging
from src.config.settings import settings
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class ZMQSecurity:
    """
    Class to handle ZeroMQ security features such as key generation and certificate management.
    This class is responsible for generating keys, loading certificates, and managing trusted peers.
    Methods:
        generate_key(filename): Generates a new ZMQ key pair and stores it in the specified directory.
        load_certificate(filename): Loads a ZMQ certificate from a file.
        generate_symmetrical_key(filename): Generates a new symmetric key for low encryption and stores it in a file.
        load_symmetrical_key(filename): Loads the symmetric key from a file.
    """
    @staticmethod
    def generate_key(filename:str) -> tuple[bytes, bytes]:
        """
        Generate a new ZMQ key pair. Returns the public and private keys.
        Args:
            filename (str): The name of the file to store the key pair.
        Returns:
            tuple[bytes, bytes]: A tuple containing the public and private keys.
        Raises:
            RuntimeError: If there is an error generating the key pair or storing it.
        """
        try:
            auth.create_certificates(key_dir=settings.ZMQ_CERTS_PATH, name=filename)
            public_key, private_key = auth.load_certificate(filename=settings.ZMQ_CERTS_PATH + filename +".key_secret")
            logger.info(f"ZMQ key pair generated and stored in {settings.ZMQ_CERTS_PATH + filename}.key_secret")
            return public_key, private_key
        except Exception as e:
            logger.error(f"Error generating ZMQ key pair: {e}")
            raise RuntimeError(f"Failed to generate ZMQ key pair: {e}")

    @staticmethod
    def load_certificate(filename: str) -> tuple[bytes, bytes]:
        """
        Load a ZMQ certificate from a file. Returns the public and private keys.
        Args:
            filename (str): The name of the file containing the ZMQ certificate.
        Returns:
            tuple[bytes, bytes]: A tuple containing the public and private keys.
        Raises:
            RuntimeError: If there is an error loading the certificate.
        """
        try:
            return auth.load_certificate(filename=filename+".key_secret")
        except Exception as e:
            logger.error(f"Error loading ZMQ certificate from {filename}: {e}")
            raise RuntimeError(f"Failed to load ZMQ certificate: {e}")

    @staticmethod
    def generate_symmetrical_key(filename:str) -> bytes:
        """
        Generate a new symmetric key for low encryption.
        Args:
            filename (str): The name of the file to store the symmetric key.
        Returns:
            bytes: The generated symmetric key.
        Raises:
            RuntimeError: If there is an error generating the symmetric key or storing it.
        """
        try:
            key = Fernet.generate_key()
            with open(settings.ZMQ_CERTS_PATH + filename, "wb") as key_file:
                key_file.write(key)
            return key
        except Exception as e:
            logger.error(f"Error generating symmetric key: {e}")
            raise RuntimeError(f"Failed to generate symmetric key: {e}")

    @staticmethod
    def load_symmetrical_key(filename:str) -> bytes:
        """
        Load the symmetric key from a file.
        Args:
            filename (str): The name of the file containing the symmetric key.
        Returns:
            bytes: The loaded symmetric key.
        Raises:
            RuntimeError: If there is an error loading the symmetric key.
        """
        try:
            with open(filename, "rb") as key_file:
                return key_file.read()
        except Exception as e:
            logger.error(f"Error loading symmetric key: {e}")
            raise RuntimeError(f"Failed to load symmetric key: {e}")