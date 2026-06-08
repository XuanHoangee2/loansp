from typing import Any, Dict, List

from app.executor.models import ExecutionResult
from app.planner.models import PlanResult


class ExecutorService:
    def __init__(self, task_executor, result_builder):
        self.task_executor = task_executor
        self.result_builder = result_builder

    async def execute_plan(
        self, plan: PlanResult, customer_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Thực thi tất cả tasks trong plan và build response.
        """
        execution_results: List[ExecutionResult] = []

        for task in plan.tasks:
            task_name = (
                task.task.value if hasattr(task.task, "value") else str(task.task)
            )
            if not task_name:
                continue

            result = await self.task_executor.execute(
                task_name=task_name, customer_profile=customer_profile
            )
            execution_results.append(result)

        response = await self.result_builder.build(
            execution_results,
            user_query=customer_profile.get("last_query", ""),
        )

        return {
            "response": response,
            "results": [r.model_dump() for r in execution_results],
        }
