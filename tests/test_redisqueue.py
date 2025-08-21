"""RedisQueues tests."""

import pytest
from mock import patch
from redis.exceptions import ConnectionError

from pgsync.redisqueue import RedisQueue, _create_redis_client


class TestRedisQueue(object):
    """Redis Queue tests."""

    @patch("pgsync.redisqueue.logger")
    def test_redis_conn(self, mock_logger, mocker):
        """Test the redis constructor."""
        mock_get_redis_url = mocker.patch(
            "pgsync.redisqueue.get_redis_url",
            return_value="redis://kermit:frog@some-host:6379/0",
        )
        mock_ping = mocker.patch("redis.Redis.ping", return_value=True)
        queue = RedisQueue("something", namespace="foo")
        assert queue.key == "foo:something"
        mock_get_redis_url.assert_called_once()
        mock_ping.assert_called_once()
        mock_logger.exception.assert_not_called()

    @patch("pgsync.redisqueue.logger")
    def test_redis_conn_fail(self, mock_logger, mocker):
        """Test the redis constructor fails."""
        mock_get_redis_url = mocker.patch(
            "pgsync.redisqueue.get_redis_url",
            return_value="redis://kermit:frog@some-host:6379/0",
        )
        mock_ping = mocker.patch(
            "redis.Redis.ping", side_effect=ConnectionError("pong")
        )
        with pytest.raises(ConnectionError):
            RedisQueue("something", namespace="foo")
        mock_get_redis_url.assert_called_once()
        mock_ping.assert_called_once()
        mock_logger.exception.assert_called_once_with(
            "Redis server is not running: pong"
        )

    def test_qsize(self, mocker):
        """Test the redis qsize."""
        queue = RedisQueue("something")
        queue.delete()
        assert queue.qsize == 0
        queue.push([1, 2])
        assert queue.qsize == 2
        queue.delete()
        assert queue.qsize == 0

    def test_push(self):
        """Test the redis push."""
        queue = RedisQueue("something")
        queue.delete()
        queue.push([1, 2])
        assert queue.qsize == 2

    def test_pop(self):
        """Test the redis pop."""
        queue = RedisQueue("something")
        queue.delete()
        queue.push([1, 2])
        items = queue.pop()
        assert items == [1, 2]
        assert queue.qsize == 0

    def test_delete(self):
        """Test the redis delete."""
        queue = RedisQueue("something")
        queue.delete()
        assert queue.qsize == 0

    def test_meta(self):
        """Test the redis meta."""
        queue = RedisQueue("something")
        queue.set_meta({"foo": "bar"})
        assert queue.get_meta() == {"foo": "bar"}

    def test_meta_default(self):
        """Test the redis meta default."""
        queue = RedisQueue("something")
        assert queue.get_meta("default") == "default"


class TestRedisClusterSupport(object):
    """Redis Cluster support tests."""

    @patch("pgsync.redisqueue.REDIS_CLUSTER", True)
    @patch("pgsync.redisqueue.logger")
    def test_create_redis_cluster_client_success(self, mock_logger, mocker):
        """Test successful Redis cluster client creation."""
        mock_redis_cluster = mocker.patch("redis.RedisCluster")
        mock_redis_cluster.from_url.return_value = "cluster_client"
        
        client = _create_redis_client("redis://localhost:6379")
        
        assert client == "cluster_client"
        mock_redis_cluster.from_url.assert_called_once()
        mock_logger.info.assert_called_with("Creating Redis cluster client")

    @patch("pgsync.redisqueue.REDIS_CLUSTER", True)
    @patch("pgsync.redisqueue.logger")
    def test_create_redis_cluster_client_fallback(self, mock_logger, mocker):
        """Test fallback to single Redis when cluster import fails."""
        mocker.patch("redis.RedisCluster", side_effect=ImportError("No module named 'redis'"))
        mock_redis = mocker.patch("redis.Redis")
        mock_redis.from_url.return_value = "single_client"
        
        client = _create_redis_client("redis://localhost:6379")
        
        assert client == "single_client"
        mock_redis.from_url.assert_called_once()
        mock_logger.warning.assert_called_with(
            "Redis cluster support not available (redis-py < 4.0), falling back to single Redis"
        )

    @patch("pgsync.redisqueue.REDIS_CLUSTER", False)
    @patch("pgsync.redisqueue.logger")
    def test_create_single_redis_client(self, mock_logger, mocker):
        """Test single Redis client creation."""
        mock_redis = mocker.patch("redis.Redis")
        mock_redis.from_url.return_value = "single_client"
        
        client = _create_redis_client("redis://localhost:6379")
        
        assert client == "single_client"
        mock_redis.from_url.assert_called_once()
        mock_logger.info.assert_called_with("Creating single Redis instance client")
