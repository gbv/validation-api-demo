from abc import abstractmethod
from .error import ValidationError
from .validator import Validator


class Parser(Validator):
    """A validator that can also parse a string into a document."""

    @abstractmethod
    def parse(self, doc: str) -> (any, list[ValidationError]):
        """Parse a document given as string."""
        pass  # pragma: no cover

    def validate(self, doc: str) -> list[ValidationError]:
        """Parse a document and return parsing errors (aka syntax errors)."""
        _, errors = self.parse(doc)
        return errors
