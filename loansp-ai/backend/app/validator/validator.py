from .models import (
    ValidationResult,
    ValidationStatus
)

from .tool_requirements import (
    TOOL_REQUIREMENTS
)


class TaskValidator:

    def validate(
        self,
        task: str,
        customer_profile: dict
    ) -> ValidationResult:

        required_fields = (
            TOOL_REQUIREMENTS.get(
                task,
                []
            )
        )

        missing_fields = []

        available_fields = []

        for field in required_fields:

            value = customer_profile.get(
                field
            )

            if value is None:
                missing_fields.append(
                    field
                )
            else:
                available_fields.append(
                    field
                )

        if missing_fields:

            return ValidationResult(
                status=ValidationStatus.MISSING_DATA,
                task=task,
                missing_fields=missing_fields,
                available_fields=available_fields
            )

        return ValidationResult(
            status=ValidationStatus.VALID,
            task=task,
            missing_fields=[],
            available_fields=available_fields
        )