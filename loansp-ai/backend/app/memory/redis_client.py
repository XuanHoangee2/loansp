from redis.asyncio import Redis


class RedisClient:

    def __init__(
        self,
        host: str,
        port: int,
        db: int = 0,
    ):
        self.redis = Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
        )

    async def ping(self):
        return await self.redis.ping()