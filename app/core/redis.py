import redis.asyncio as redis
from app.config import settings

# Initialize Redis client
# You might want to add REDIS_URL to your settings
redis_client = redis.from_url(getattr(settings, "redis_url", "redis://localhost:6379/0"), encoding="utf-8", decode_responses=True)

async def get_redis_client():
    return redis_client
