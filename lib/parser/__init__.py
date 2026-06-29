from abc import ABC, abstractmethod
from ..dvrf import ValidationError


class AbstractParser(ABC):

    @abstractmethod
    def parse(self, doc: str) -> (any, list[ValidationError]):
        """Parse a document given as string."""
        pass  # pragma: no cover

    def validate(self, doc: str) -> list[ValidationError]:
        """Return parsing errors."""
        _, errors = self.parse(doc)
        return errors
