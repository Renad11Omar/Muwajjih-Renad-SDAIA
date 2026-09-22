from typing import Any, cast

try:
    import redis

    _redis_available: Any = redis
except ImportError:  # pragma: no cover - dev-only environments can use a fake cache
    _redis_available = None


class RedisCache:
    def __init__(self, url: str) -> None:
        if redis is None:
            raise RuntimeError("redis package is required for runtime readiness")
        self._client = redis.Redis.from_url(url, decode_responses=True, socket_timeout=0.8)

    def get(self, key: str) -> str | None:
        return cast(str | None, self._client.get(key))

    def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        self._client.set(name=key, value=value, ex=ttl_seconds)

    def ping(self) -> bool:
        return bool(self._client.ping())

    def close(self) -> None:
        close = getattr(self._client, "close", None)
        if callable(close):
            close()
