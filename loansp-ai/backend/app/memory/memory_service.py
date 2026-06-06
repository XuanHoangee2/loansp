from .models import ActiveTask

from .profile_memory import ProfileMemory

from .task_memory import TaskMemory

from .conversation_memory import ConversationMemory


class MemoryService:
    def __init__(
        self,
        profile_memory: ProfileMemory,
        task_memory: TaskMemory,
        conversation_memory: ConversationMemory,
    ):
        self.profile = profile_memory

        self.task = task_memory

        self.conversation = conversation_memory

    async def update_profile(
        self,
        session_id: str,
        updates: dict,
    ):
        return await self.profile.update(
            session_id,
            updates,
        )

    async def get_profile(
        self,
        session_id: str,
    ):
        return await self.profile.get(session_id)

    async def save_active_task(
        self,
        session_id: str,
        task_name: str,
        missing_fields: list[str],
    ):

        task = ActiveTask(
            task=task_name,
            missing_fields=missing_fields,
            status="waiting",
        )

        await self.task.save(
            session_id,
            task,
        )

    async def get_active_task(
        self,
        session_id: str,
    ):
        return await self.task.get(session_id)

    async def clear_task(
        self,
        session_id: str,
    ):
        await self.task.clear(session_id)
