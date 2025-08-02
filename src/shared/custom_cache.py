# src/shared/alert_dedup.py
from cachetools import TTLCache
from threading import Lock
from pydantic import IPvAnyAddress
from src.fail2ban.action import Fail2banAction

# TTL de 60 secondes
alert_cache = TTLCache(maxsize=1000, ttl=60)
alert_cache_lock = Lock()

def is_duplicate(ip: str|IPvAnyAddress, jail: str, action: str|Fail2banAction) -> bool:
    key = f"{action}:{jail}:{ip}"
    with alert_cache_lock:
        return key in alert_cache

def register_alert(ip: str|IPvAnyAddress, jail: str, action: str|Fail2banAction):
    key = f"{action}:{jail}:{ip}"
    with alert_cache_lock:
        alert_cache[key] = True