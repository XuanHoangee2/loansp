from .validator import (
    TaskValidator
)

from .question_generator import (
    QuestionGenerator
)

from .models import (
    ValidationStatus
)


class ValidationService:

    def __init__(self):

        self.validator = (
            TaskValidator()
        )

        self.question_generator = (
            QuestionGenerator()
        )

    def validate_plan(self, plan, customer_profile):
        results = []
        all_missing_fields = []

        for task in plan.tasks:
            result = self.validator.validate(
                task=task.task,
                customer_profile=customer_profile
            )
            results.append(result)
            if result.status == ValidationStatus.MISSING_DATA:
                all_missing_fields.extend(result.missing_fields)

        # Loại bỏ trùng lặp giữ nguyên thứ tự
        all_missing_fields = list(dict.fromkeys(all_missing_fields))

        if all_missing_fields:
            return {
                "status": "missing_data",
                "missing_fields": all_missing_fields,
                "task_results": results
            }

        return {
            "status": "valid",
            "missing_fields": [],
            "task_results": results
        }

    def build_missing_question(
        self,
        validation_result
    ):

        return (
            self.question_generator
            .build_question(
                validation_result.missing_fields
            )
        )