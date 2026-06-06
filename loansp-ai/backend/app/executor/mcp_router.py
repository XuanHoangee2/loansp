from app.executor.task_registry import TASK_REGISTRY


class MCPRouter:
    def resolve(self, task_name: str):
        if task_name not in TASK_REGISTRY:
            raise ValueError(f"Unknown task {task_name}")
        return TASK_REGISTRY[task_name]
