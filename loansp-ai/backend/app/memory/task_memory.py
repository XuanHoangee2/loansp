from .models import ActiveTask


class TaskMemory:

    TASK_TTL = 60 * 60 * 24

    def __init__(self, redis):
        self.redis = redis

    def _key(
        self,
        session_id: str,
    ):
        return (
            f"active_task:{session_id}"
        )

    async def get(
        self,
        session_id: str,
    ):

        data = await self.redis.get(
            self._key(session_id)
        )

        if not data:
            return None

        return ActiveTask.model_validate_json(
            data
        )

    async def save(
        self,
        session_id: str,
        task: ActiveTask,
    ):

        await self.redis.set(
            self._key(session_id),
            task.model_dump_json(),
            ex=self.TASK_TTL,
        )

    async def clear(
        self,
        session_id: str,
    ):
        await self.redis.delete(
            self._key(session_id)
        )