from ..dvrf import ValidationError
from .xml import XMLValidator
import xmlschema


class XSDValidator:
    def __init__(self, schema):
        self.schema = xmlschema.XMLSchema(schema)

    def validate(self, tree):
        """Validate a parsed XML document."""
        return [
            ValidationError(e.reason, position={"xpath": e.path} if e.path else None)
            for e in self.schema.iter_errors(tree)
        ]

    def validateXML(self, doc: str):
        """Validate an XML document given as string."""
        parsed, errors = XMLValidator().parse(doc)
        return errors if errors else self.validate(parsed)
