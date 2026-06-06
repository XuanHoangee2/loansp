import pytest
from unittest.mock import AsyncMock, MagicMock

from app.planner.models import PlanResult, TaskType, Intent, IntentResult
from app.planner.intent_planner import IntentPlanner
from app.planner.task_planner import TaskPlanner
from app.planner.planner_service import PlannerService


class TestIntentPlanner:
    """Tests for IntentPlanner class."""

    def test_init(self):
        planner = IntentPlanner(MagicMock())
        assert planner.chain is not None

    @pytest.mark.asyncio
    async def test_run_valid_json(self):
        planner = IntentPlanner(MagicMock())
        planner.chain = AsyncMock()
        planner.chain.ainvoke.return_value = (
            '{"intent": "loan_recommendation", "confidence": 0.95}'
        )
        result = await planner.run("I want to buy a house")
        assert isinstance(result, IntentResult)
        assert result.intent == Intent.LOAN_RECOMMENDATION
        assert result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_run_json_with_markdown(self):
        planner = IntentPlanner(MagicMock())
        planner.chain = AsyncMock()
        planner.chain.ainvoke.return_value = (
            '```json\n{"intent": "faq", "confidence": 0.8}\n```'
        )
        result = await planner.run("What are your working hours?")
        assert result.intent == Intent.FAQ

    @pytest.mark.asyncio
    async def test_run_invalid_json_fallback(self):
        planner = IntentPlanner(MagicMock())
        planner.chain = AsyncMock()
        planner.chain.ainvoke.return_value = "some random text without json"
        result = await planner.run("hello")
        assert result.intent == Intent.GENERAL
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_run_unknown_intent(self):
        planner = IntentPlanner(MagicMock())
        planner.chain = AsyncMock()
        planner.chain.ainvoke.return_value = (
            '{"intent": "some_unknown_intent", "confidence": 0.5}'
        )
        result = await planner.run("random query")
        assert result.intent == Intent.GENERAL


class TestTaskPlanner:
    """Tests for TaskPlanner class."""

    def test_init(self):
        planner = TaskPlanner(MagicMock())
        assert planner.chain is not None

    @pytest.mark.asyncio
    async def test_run_valid_json(self):
        planner = TaskPlanner(MagicMock())
        planner.chain = AsyncMock()
        planner.chain.ainvoke.return_value = '{"intent": "loan_recommendation", "tasks": [{"task": "recommend_loan", "reason": "user wants a loan"}]}'
        result = await planner.run("I want a home loan", "loan_recommendation")
        assert isinstance(result, PlanResult)
        assert result.intent == Intent.LOAN_RECOMMENDATION
        assert len(result.tasks) == 1
        assert result.tasks[0].task == TaskType.RECOMMEND_LOAN

    @pytest.mark.asyncio
    async def test_run_invalid_json_fallback(self):
        planner = TaskPlanner(MagicMock())
        planner.chain = AsyncMock()
        planner.chain.ainvoke.return_value = "invalid response"
        result = await planner.run("hello", "general")
        assert result.intent == Intent.GENERAL
        assert len(result.tasks) == 1
        assert result.tasks[0].task == TaskType.GENERAL_RESPONSE

    @pytest.mark.asyncio
    async def test_run_unknown_task(self):
        planner = TaskPlanner(MagicMock())
        planner.chain = AsyncMock()
        planner.chain.ainvoke.return_value = '{"intent": "loan_recommendation", "tasks": [{"task": "unknown_task", "reason": "test"}]}'
        result = await planner.run("query", "loan_recommendation")
        assert result.tasks[0].task == TaskType.GENERAL_RESPONSE


class TestPlannerService:
    """Tests for PlannerService class."""

    @pytest.mark.asyncio
    async def test_plan(self):
        mock_llm = MagicMock()
        service = PlannerService(mock_llm)
        service.intent_planner.chain = AsyncMock()
        service.intent_planner.chain.ainvoke.return_value = (
            '{"intent": "loan_recommendation", "confidence": 0.95}'
        )
        service.task_planner.chain = AsyncMock()
        service.task_planner.chain.ainvoke.return_value = '{"intent": "loan_recommendation", "tasks": [{"task": "recommend_loan", "reason": "user wants a loan"}]}'
        result = await service.plan("I want a home loan")
        assert isinstance(result, PlanResult)
        assert result.intent == Intent.LOAN_RECOMMENDATION
