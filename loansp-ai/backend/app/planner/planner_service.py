from .intent_planner import IntentPlanner

from .task_planner import TaskPlanner


class PlannerService:
    def __init__(self, llm):

        self.intent_planner = IntentPlanner(llm)

        self.task_planner = TaskPlanner(llm)

    async def plan(self, user_query: str):

        intent_result = await self.intent_planner.run(user_query)

        plan_result = await self.task_planner.run(
            query=user_query, intent=intent_result.intent
        )

        return plan_result
