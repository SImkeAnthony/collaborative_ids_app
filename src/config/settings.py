import os
from pydantic_settings import BaseSettings, SettingsConfigDict # pydantic-settings

class Settings(BaseSettings):

    if os.path.exists('default.env'):
        model_config = SettingsConfigDict(env_file='default.env', extra='ignore')

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ZMQ_PUBLISHER_BIND_ADDRESS: str = "tcp://*:5556" # ZMQ publisher bind address
    ZMQ_TOPIC_FAIL2BAN_ALERT: str = "FAIL2BAN.ALERT"

    API_KEY: str = "YOUR_SECRET_API_KEY"
    TRUSTED_HOSTS_FILE: str = "trustedHost.json"
    TRUSTED_HOSTS: str = ""

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"


settings = Settings()