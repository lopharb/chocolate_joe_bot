import redis


class RedisDB:
    def __init__(self, host="redis", port=6379):
        self.host = host
        self.port = port
        self.client = redis.Redis(host=self.host, port=self.port)

    def set(self, key, value):
        self.client.set(key, value)

    def get(self, key) -> str | None:
        value = self.client.get(key)
        if value is not None:
            return value.decode("utf-8")  # pyright: ignore[reportAttributeAccessIssue]

        return None

    def get_keys_by_root(self, root: str) -> list[str]:
        keys = []
        for key in self.client.keys(f"{root}:*"):  # pyright: ignore[reportGeneralTypeIssues]
            keys.append(key.decode("utf-8"))

        return keys

    def delete(self, key):
        self.client.delete(key)
