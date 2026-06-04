from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import re

from .models import PlanResult, PlannedTask, Intent, TaskType
from .prompt import TASK_PROMPT


class TaskPlanner:
    def __init__(self, llm):
        self.chain = (
            ChatPromptTemplate.from_messages([
                ("system", TASK_PROMPT),
                ("human", "Intent:\n{intent}\n\nUser:\n{query}")
            ])
            | llm
            | StrOutputParser()
        )

    async def run(self, query: str, intent: str):
        raw_text = await self.chain.ainvoke({"query": query, "intent": intent})
        
        try:
            data = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except:
                    data = {"intent": intent, "tasks": [{"task": "general_response", "reason": "fallback"}]}
            else:
                data = {"intent": intent, "tasks": [{"task": "general_response", "reason": "fallback"}]}

        intent_str = data.get("intent", intent)
        try:
            parsed_intent = Intent(intent_str)
        except ValueError:
            parsed_intent = Intent.GENERAL

        tasks = []
        for t in data.get("tasks", []):
            if isinstance(t, dict):
                task_str = t.get("task", "general_response")
                try:
                    task_type = TaskType(task_str)
                except ValueError:
                    task_type = TaskType.GENERAL_RESPONSE
                tasks.append(PlannedTask(task=task_type, reason=t.get("reason", "")))

        return PlanResult(intent=parsed_intent, tasks=tasks)