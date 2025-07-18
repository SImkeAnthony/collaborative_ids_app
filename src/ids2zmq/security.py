from zmq import auth
from src.config.settings import settings

class ZMQSecurity:
    """
    Class to handle ZeroMQ security features such as key generation and certificate management.
    This class is responsible for generating keys, loading certificates, and managing trusted peers.
    """
    @staticmethod
    def generate_key(filename:str) -> tuple[bytes, bytes]:
        """Generate a new ZMQ key pair. Returns the public and private keys."""
        auth.create_certificates(key_dir=settings.ZMQ_CERTS_PATH, name=filename)
        public_key, private_key = auth.load_certificate(filename=settings.ZMQ_CERTS_PATH + "rasp1.key_secret")
        return public_key, private_key

    @staticmethod
    def load_certificate(filename: str) -> tuple[bytes, bytes]:
        """Load a ZMQ certificate from a file. Returns the public and private keys."""
        return auth.load_certificate(filename=filename+".key_secret")