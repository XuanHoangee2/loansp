import json


class ConversationMemory:

    WINDOW_SIZE = 10

    def __init__(self,redis):
        self.redis = redis

    def _key(self,session_id):
        return (
            f"conversation:{session_id}"
        )

    async def append(self,session_id: str,role: str,content: str):
        item = {
            "role": role,
            "content": content,
        }

        key = self._key(
            session_id
        )

        await self.redis.rpush(key,json.dumps(item))

        await self.redis.ltrim(key,-self.WINDOW_SIZE,-1)

    async def get(self,session_id: str):

        items = await self.redis.lrange(self._key(session_id),0,-1)

        return [
            json.loads(item)
            for item in items
        ]