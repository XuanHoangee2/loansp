import json

from .models import CustomerProfile


class ProfileMemory:

    PROFILE_TTL = 60 * 60 * 24 * 7

    def __init__(self, redis):
        self.redis = redis

    def _key(self,session_id: str):
        return (f"customer_profile:{session_id}")

    async def get(self,session_id: str) -> CustomerProfile:

        data = await self.redis.get(self._key(session_id))

        if not data:
            return CustomerProfile()

        return CustomerProfile.model_validate_json(data)

    async def save(self,session_id: str,profile: CustomerProfile):
        await self.redis.set(self._key(session_id),profile.model_dump_json(),ex=self.PROFILE_TTL)

    async def update(self,session_id: str,updates: dict) -> CustomerProfile:

        profile = await self.get(session_id)

        current = profile.model_dump()

        current.update(
            {
                k: v
                for k, v in updates.items()
                if v is not None
            }
        )

        updated = CustomerProfile(**current)

        await self.save( session_id,updated)

        return updated

    async def delete(self,session_id: str):
        await self.redis.delete(self._key(session_id))