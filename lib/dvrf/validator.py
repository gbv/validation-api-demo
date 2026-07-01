from abc import abstractmethod
from .error import ValidationError


class Validator:
    """Provides methods to validate data."""

    @abstractmethod
    def validate(self, doc: str) -> list[ValidationError]:
        """Validate a document given as string."""
        pass  # pragma: no cover
