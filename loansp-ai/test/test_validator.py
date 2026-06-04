from app.validator.validator import TaskValidator
from app.validator.models import ValidationResult, ValidationStatus
from app.validator.tool_requirements import TOOL_REQUIREMENTS
from app.validator.validation_service import ValidationService
from app.validator.question_generator import QuestionGenerator


class TestTaskValidator:
    """Tests for TaskValidator class."""

    def setup_method(self):
        self.validator = TaskValidator()

    def test_validate_all_fields_present(self):
        """Test validation when all required fields are present."""
        profile = {
            "income": 15000000,
            "loan_amount": 500000000,
            "loan_year": 10,
            "loan_purpose": "mua_nha"
        }
        result = self.validator.validate("recommend_loan", profile)
        assert isinstance(result, ValidationResult)
        assert result.status == ValidationStatus.VALID
        assert result.task == "recommend_loan"
        assert result.missing_fields == []
        assert set(result.available_fields) == {"income", "loan_amount", "loan_year", "loan_purpose"}

    def test_validate_missing_fields(self):
        """Test validation when some required fields are missing."""
        profile = {
            "income": 15000000,
            "loan_purpose": "mua_nha"
        }
        result = self.validator.validate("recommend_loan", profile)
        assert result.status == ValidationStatus.MISSING_DATA
        assert result.task == "recommend_loan"
        assert "loan_amount" in result.missing_fields
        assert "loan_year" in result.missing_fields
        assert "income" in result.available_fields
        assert "loan_purpose" in result.available_fields

    def test_validate_empty_profile(self):
        """Test validation with completely empty profile."""
        result = self.validator.validate("calculate_dti", {})
        assert result.status == ValidationStatus.MISSING_DATA
        assert "income" in result.missing_fields
        assert "monthly_debt" in result.missing_fields

    def test_validate_no_required_fields(self):
        """Test validation for tasks with no required fields."""
        result = self.validator.validate("faq_search", {})
        assert result.status == ValidationStatus.VALID
        assert result.missing_fields == []

    def test_validate_unknown_task(self):
        """Test validation for unknown task defaults to empty requirements."""
        result = self.validator.validate("unknown_task", {"income": 1000000})
        assert result.status == ValidationStatus.VALID
        assert result.missing_fields == []

    def test_validate_calculate_ltv(self):
        """Test LTV calculation requirements."""
        profile = {
            "loan_amount": 500000000,
            "asset_value": 1000000000
        }
        result = self.validator.validate("calculate_ltv", profile)
        assert result.status == ValidationStatus.VALID
        assert result.missing_fields == []

    def test_validate_calculate_ltv_missing(self):
        """Test LTV calculation with missing asset_value."""
        profile = {"loan_amount": 500000000}
        result = self.validator.validate("calculate_ltv", profile)
        assert result.status == ValidationStatus.MISSING_DATA
        assert "asset_value" in result.missing_fields
        assert "loan_amount" in result.available_fields

    def test_validate_none_values(self):
        """Test that None values are treated as missing."""
        profile = {
            "income": 15000000,
            "loan_amount": None,
            "loan_year": 10,
            "loan_purpose": "mua_nha"
        }
        result = self.validator.validate("recommend_loan", profile)
        assert result.status == ValidationStatus.MISSING_DATA
        assert "loan_amount" in result.missing_fields


class TestValidationService:
    """Tests for ValidationService class."""

    def setup_method(self):
        self.service = ValidationService()

    def test_validate_plan_all_valid(self):
        """Test validation service when all tasks are valid."""
        from app.planner.models import PlanResult, PlannedTask, TaskType, Intent
        plan = PlanResult(
            intent=Intent.LOAN_RECOMMENDATION,
            tasks=[PlannedTask(task=TaskType.RECOMMEND_LOAN, reason="user wants loan")]
        )
        profile = {
            "income": 15000000,
            "loan_amount": 500000000,
            "loan_year": 10,
            "loan_purpose": "mua_nha"
        }
        result = self.service.validate_plan(plan, profile)
        assert result["status"] == "valid"
        assert result["missing_fields"] == []
        assert len(result["task_results"]) == 1

    def test_validate_plan_missing_data(self):
        """Test validation service when some tasks have missing data."""
        from app.planner.models import PlanResult, PlannedTask, TaskType, Intent
        plan = PlanResult(
            intent=Intent.LOAN_RECOMMENDATION,
            tasks=[PlannedTask(task=TaskType.RECOMMEND_LOAN, reason="user wants loan")]
        )
        profile = {"income": 15000000}
        result = self.service.validate_plan(plan, profile)
        assert result["status"] == "missing_data"
        assert "loan_amount" in result["missing_fields"]
        assert "loan_year" in result["missing_fields"]

    def test_build_missing_question(self):
        """Test building missing questions."""
        from app.validator.models import ValidationResult, ValidationStatus
        validation_result = ValidationResult(
            status=ValidationStatus.MISSING_DATA,
            task="recommend_loan",
            missing_fields=["income", "loan_amount"]
        )
        question = self.service.build_missing_question(validation_result)
        assert "1." in question
        assert "2." in question


class TestQuestionGenerator:
    """Tests for QuestionGenerator class."""

    def setup_method(self):
        self.generator = QuestionGenerator()

    def test_build_question(self):
        """Test generating questions for missing fields."""
        question = self.generator.build_question(["income", "loan_amount"])
        assert "1." in question
        assert "2." in question

    def test_build_question_empty(self):
        """Test generating questions with no missing fields."""
        question = self.generator.build_question([])
        assert question == ""

    def test_build_question_unknown_field(self):
        """Test that unknown fields are skipped."""
        question = self.generator.build_question(["income", "unknown_field"])
        assert "1." in question
        assert "2." not in question
