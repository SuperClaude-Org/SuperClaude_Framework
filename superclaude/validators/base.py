"""Base validator classes and utilities"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ValidationStatus(Enum):
    """Validation result status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a validation check"""
    status: ValidationStatus
    validator_name: str
    message: str
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

    @property
    def passed(self) -> bool:
        """Check if validation passed"""
        return self.status == ValidationStatus.PASSED

    @property
    def failed(self) -> bool:
        """Check if validation failed"""
        return self.status == ValidationStatus.FAILED

    def __str__(self) -> str:
        """String representation"""
        symbol = {
            ValidationStatus.PASSED: "✅",
            ValidationStatus.FAILED: "❌",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.SKIPPED: "⏭️"
        }[self.status]

        lines = [f"{symbol} {self.validator_name}: {self.message}"]

        if self.details:
            lines.append(f"  Details: {self.details}")

        if self.suggestions:
            lines.append("  Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"    - {suggestion}")

        return "\n".join(lines)


class Validator(ABC):
    """Base validator class"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate against context.

        Args:
            context: Validation context (changes, contract, etc.)

        Returns:
            ValidationResult
        """
        pass

    def _pass(self, message: str, **kwargs) -> ValidationResult:
        """Create a PASSED result"""
        return ValidationResult(
            status=ValidationStatus.PASSED,
            validator_name=self.name,
            message=message,
            **kwargs
        )

    def _fail(self, message: str, **kwargs) -> ValidationResult:
        """Create a FAILED result"""
        return ValidationResult(
            status=ValidationStatus.FAILED,
            validator_name=self.name,
            message=message,
            **kwargs
        )

    def _warning(self, message: str, **kwargs) -> ValidationResult:
        """Create a WARNING result"""
        return ValidationResult(
            status=ValidationStatus.WARNING,
            validator_name=self.name,
            message=message,
            **kwargs
        )

    def _skip(self, message: str, **kwargs) -> ValidationResult:
        """Create a SKIPPED result"""
        return ValidationResult(
            status=ValidationStatus.SKIPPED,
            validator_name=self.name,
            message=message,
            **kwargs
        )


class ValidatorChain:
    """Chain of validators that runs in sequence"""

    def __init__(self, validators: List[Validator]):
        self.validators = validators

    def validate(self, context: Dict[str, Any]) -> List[ValidationResult]:
        """Run all validators"""
        results = []
        for validator in self.validators:
            result = validator.validate(context)
            results.append(result)

        return results

    def validate_with_early_stop(self, context: Dict[str, Any]) -> List[ValidationResult]:
        """Run validators until first failure"""
        results = []
        for validator in self.validators:
            result = validator.validate(context)
            results.append(result)

            # Stop on first failure
            if result.failed:
                break

        return results

    @property
    def all_passed(self) -> bool:
        """Check if all validations passed"""
        return all(not r.failed for r in self.validate({}))
