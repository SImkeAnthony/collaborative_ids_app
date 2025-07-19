import os
from pydantic_settings import BaseSettings, SettingsConfigDict # pydantic-settings

class Settings(BaseSettings):
    """
    Application settings for the Fail2Ban API.
    Attributes:
        API_HOST (str): Host for the API server.
        API_PORT (int): Port for the API server.
        ZMQ_PUBLISHER_BIND_ADDRESS (str): Address for the ZMQ publisher.
        ZMQ_TOPIC_FAIL2BAN_ALERT (str): Topic for Fail2Ban alerts.
        ZMQ_ROUTER_BIND_ADDRESS (str): Address for the ZMQ router.
        API_KEY (str): Secret API key for authentication.
        LOG_LEVEL (str): Logging level.
        LOG_FILE (str): Log file path.
        ENABLE_ZMQ_SECURITY (bool): Enable ZMQ security features.
        ZMQ_SECURITY_USERNAME (str): Username for ZMQ security.
        ZMQ_SECURITY_PASSWORD (str): Password for ZMQ security.
        ZMQ_CERTS_PATH (str): Path to ZMQ certificates.
        ZMQ_CERTS_NAME (str): Name of the ZMQ certificates.
        ZMQ_TRUSTED_PEERS_CERTS_PATH (str): Path to trusted peers' certificates.
        ZMQ_SYMMETRICAL_KEY_FILE (str): File containing the symmetric key for encryption.
        TRUSTED_HOSTS_FILE (str): File containing trusted hosts.
        TRUSTED_HOSTS (str): Comma-separated list of trusted hosts.
    Uses:
        pydantic_settings.BaseSettings for configuration management.
    Example:
        settings = Settings()
        print(settings.API_HOST)
    """

    if os.path.exists('default.env'):
        model_config = SettingsConfigDict(env_file='default.env', extra='ignore')

    API_HOST: str = "localhost"
    API_PORT: int = 8000
    ZMQ_PUBLISHER_BIND_ADDRESS: str = "tcp://localhost:5556"
    ZMQ_TOPIC_FAIL2BAN_ALERT: str = "FAIL2BAN.ALERT"
    ZMQ_ROUTER_BIND_ADDRESS: str = "tcp://localhost:5555"

    API_KEY: str = "YOUR_SECRET_API_KEY"

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"

    # ZMQ configuration
    ENABLE_ZMQ_SECURITY: bool = True
    ZMQ_SECURITY_USERNAME: str = "zmq_user"
    ZMQ_SECURITY_PASSWORD: str = "zmq_password"
    ZMQ_CERTS_PATH: str = "certs/"
    ZMQ_CERTS_NAME: str = "local"
    ZMQ_TRUSTED_PEERS_CERTS_PATH: str = "certs/authorized_clients/"
    ZMQ_SYMMETRICAL_KEY_FILE: str = "symmetric_key.key"

    TRUSTED_HOSTS_FILE: str = "trustedHost.json"
    TRUSTED_HOSTS: str = ""

settings = Settings()