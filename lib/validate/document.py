from abc import abstractmethod
from ..dvrf import ValidationError, Parser


class DocumentValidator(Parser):

    @abstractmethod
    def validate_document(self, doc: str) -> list[ValidationError]:
        """Validate a parsed document."""
        pass  # pragma: no cover

    def validate(self, doc: str) -> list[ValidationError]:
        """Parse and validate a document given as string."""
        doc, errors = self.parse(doc)
        return errors if errors else self.validate_document(doc)
