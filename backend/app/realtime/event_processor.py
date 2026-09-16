import json
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

_redis_client = None
_connection_attempted = False

def get_redis_client():
    global _redis_client, _connection_attempted
    if settings.ENVIRONMENT == "testing" or not HAS_REDIS:
        return None

    if not _connection_attempted:
        _connection_attempted = True
        try:
            client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=0.2,
                socket_connect_timeout=0.2
            )
            client.ping()
            _redis_client = client
            logger.info("Connected to Redis event bus")
        except Exception as e:
            logger.debug(f"Redis connection skipped: {e}")
            _redis_client = None
    return _redis_client

def publish_event(event_type: str, payload: Dict[str, Any], channel: str = "fraudshield_events"):
    redis_cli = get_redis_client()
    if redis_cli:
        try:
            event_data = {
                "event_type": event_type,
                "payload": payload,
                "timestamp": payload.get("timestamp")
            }
            redis_cli.publish(channel, json.dumps(event_data, default=str))
            logger.info(f"Published event {event_type} to Redis channel {channel}")
        except Exception as e:
            logger.warning(f"Failed to publish Redis event {event_type}: {e}")
