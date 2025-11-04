from typing import Any, Generator

import redis


class RedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db)

    def set(self, key: str, value: Any, ttl: int | None = None):
        """Set a key-value pair, optionally with TTL (seconds)."""
        self.client.set(key, value)
        if ttl is not None:
            try:
                ttl = int(ttl)
                self.client.expire(key, ttl)
            except ValueError:
                print("WARNING: Provided TTL is not an integer")

    def get(self, key: str) -> str | None:
        """Get a value by key (decoded to UTF-8)."""
        value = self.client.get(key)
        return value.decode("utf-8") if value else None

    def find(self, pattern: str) -> Generator[str, None, None]:
        """Find keys by a given pattern (generator)."""
        keys = self.client.keys(pattern)
        for key in keys:
            yield key.decode("utf-8")

    def get_keys_by_root(self, root: str) -> Generator[str, None, None]:
        """Get all keys that start with a given root prefix (e.g. 'user:*')."""
        keys = self.client.keys(f"{root}:*")
        for key in keys:
            yield key.decode("utf-8")

    def delete(self, key: str) -> None:
        """Delete a key."""
        self.client.delete(key)
