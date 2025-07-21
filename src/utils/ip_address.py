import socket
import logging

logger = logging.getLogger(__name__)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception as e:
        logger.error("Failed to get local IP address: %s", e)
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip