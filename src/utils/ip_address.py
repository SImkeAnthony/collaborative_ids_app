import socket
import logging

logger = logging.getLogger(__name__)

def get_local_ip():
    """
    Get the local IP address of the machine.

    Returns:
        str|IPvAnyAddress: The local IP address of the machine.
    Raises:
        Exception: If there is an error retrieving the local IP address.
    """
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

def extract_ip_address_from_socket_address(socket_address: str) -> str:
    """
    Extract the IP address from a socket address string.

    Args:
        socket_address (str): The socket address in the format 'IP:PORT'.

    Returns:
        str: The extracted IP address.

    Raises:
        ValueError: If the socket address is not in the correct format.
    """
    try:
        proto, socket_addr = socket_address.split('://')
        if proto not in ['tcp', 'udp']:
            raise ValueError("Protocol must be either 'tcp' or 'udp'.")
        if ':' not in socket_addr:
            raise ValueError("Socket address must contain an IP and port separated by a colon.")
        ip_addr, port = socket_addr.split(':')
        if not ip_addr or not port.isdigit():
            raise ValueError("Invalid socket address format.")
        return ip_addr
    except ValueError as e:
        logger.error("Invalid socket address format: %s", e)
        raise ValueError("Socket address must be in the format 'PROTO//IP:PORT'.")