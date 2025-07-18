import os
from pydantic_settings import BaseSettings, SettingsConfigDict # pydantic-settings

class Settings(BaseSettings):

    if os.path.exists('default.env'):
        model_config = SettingsConfigDict(env_file='default.env', extra='ignore')

    API_HOST: str = "localhost"
    API_PORT: int = 8000
    ZMQ_PUBLISHER_BIND_ADDRESS: str = "tcp://localhost:5556" # ZMQ publisher bind address
    ZMQ_TOPIC_FAIL2BAN_ALERT: str = "FAIL2BAN.ALERT"

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