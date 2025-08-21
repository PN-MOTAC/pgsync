"""PGSync RedisQueue."""

import json
import logging
import typing as t

from redis import Redis
from redis.exceptions import ConnectionError, RedisClusterException

from .settings import (
    REDIS_READ_CHUNK_SIZE,
    REDIS_RETRY_ON_TIMEOUT,
    REDIS_SOCKET_TIMEOUT,
    REDIS_CLUSTER,
)
from .urls import get_redis_url

logger = logging.getLogger(__name__)


def _create_redis_client(url: str, **kwargs) -> Redis:
    """
    Create Redis client based on configuration.
    Supports both cluster and non-cluster deployments.
    """
    if REDIS_CLUSTER:
        # Try to import RedisCluster for cluster support
        try:
            from redis import RedisCluster
            logger.info("Creating Redis cluster client")
            return RedisCluster.from_url(
                url,
                socket_timeout=REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=REDIS_RETRY_ON_TIMEOUT,
                **kwargs
            )
        except ImportError:
            logger.warning("Redis cluster support not available (redis-py < 4.0), falling back to single Redis")
            return Redis.from_url(
                url,
                socket_timeout=REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=REDIS_RETRY_ON_TIMEOUT,
                **kwargs
            )
    else:
        # Use regular Redis client for non-cluster deployments
        logger.info("Creating single Redis instance client")
        return Redis.from_url(
            url,
            socket_timeout=REDIS_SOCKET_TIMEOUT,
            retry_on_timeout=REDIS_RETRY_ON_TIMEOUT,
            **kwargs
        )


class RedisQueue(object):
    """Simple Queue with Redis Backend."""

    def __init__(self, name: str, namespace: str = "queue", **kwargs):
        """Init Simple Queue with Redis Backend."""
        url: str = get_redis_url(**kwargs)
        self.key: str = f"{namespace}:{name}"
        self._meta_key: str = f"{self.key}:meta"
        
        try:
            self.__db: Redis = _create_redis_client(url, **kwargs)
            self.__db.ping()
            logger.info(f"Successfully connected to Redis ({'cluster' if REDIS_CLUSTER else 'single instance'})")
            
        except (ConnectionError, RedisClusterException) as e:
            logger.exception(f"Redis server is not running: {e}")
            raise

    @property
    def qsize(self) -> int:
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def pop(self, chunk_size: t.Optional[int] = None) -> t.List[dict]:
        """Remove and return multiple items from the queue."""
        chunk_size = chunk_size or REDIS_READ_CHUNK_SIZE
        if self.qsize > 0:
            pipeline = self.__db.pipeline()
            pipeline.lrange(self.key, 0, chunk_size - 1)
            pipeline.ltrim(self.key, chunk_size, -1)
            items: t.List = pipeline.execute()
            logger.debug(f"pop size: {len(items[0])}")
            return list(map(lambda value: json.loads(value), items[0]))

    def push(self, items: t.List) -> None:
        """Push multiple items onto the queue."""
        self.__db.rpush(self.key, *map(json.dumps, items))

    def delete(self) -> None:
        """Delete all items from the named queue."""
        logger.info(f"Deleting redis key: {self.key}")
        self.__db.delete(self.key)

    def set_meta(self, value: t.Any) -> None:
        """Store an arbitrary JSON-serialisable value in a dedicated key."""
        self.__db.set(self._meta_key, json.dumps(value))

    def get_meta(self, default: t.Any = None) -> t.Any:
        """Retrieve the stored value (or *default* if nothing is set)."""
        raw = self.__db.get(self._meta_key)
        return json.loads(raw) if raw is not None else default
