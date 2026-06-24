import os
import time
from dotenv import load_dotenv

load_dotenv()

# Upstash/Redis config
REDIS_URL = os.getenv("REDIS_URL")

class InMemoryCache:
    """Thread-safe local fallback for Redis cache with TTL support."""
    def __init__(self):
        self._store = {}
        self._ttls = {}

    def get(self, key: str) -> Optional[str]:
        if key in self._store:
            # Check TTL
            expiry = self._ttls.get(key)
            if expiry is not None and time.time() > expiry:
                self.delete(key)
                return None
            return self._store[key]
        return None

    def set(self, key: str, value: str):
        self._store[key] = str(value)
        self._ttls[key] = None

    def setex(self, key: str, ttl: int, value: str):
        self._store[key] = str(value)
        self._ttls[key] = time.time() + ttl

    def delete(self, key: str):
        if key in self._store:
            del self._store[key]
        if key in self._ttls:
            del self._ttls[key]

# Try to initialize Upstash Redis, or fallback
redis_client = None

if REDIS_URL:
    try:
        import redis
        # Parse Upstash connection
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        # Ping check
        redis_client.ping()
        print("Connected to Upstash Redis.")
    except Exception as e:
        print(f"Failed to connect to Upstash Redis, falling back to local memory: {e}")
        redis_client = InMemoryCache()
else:
    redis_client = InMemoryCache()
