from ..dvrf import ValidationError
from .xml import XMLDocumentValidator
import xmlschema


class XSDValidator(XMLDocumentValidator):
    def __init__(self, schema):
        self.schema = xmlschema.XMLSchema(schema)

    def validate_document(self, doc):
        """Validate a parsed XML document."""
        return [
            ValidationError(e.reason, position={"xpath": e.path} if e.path else None)
            for e in self.schema.iter_errors(doc)
        ]
