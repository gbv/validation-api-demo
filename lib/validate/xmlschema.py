from ..dvrf import ValidationError
import xmlschema


class XSDValidator:
    def __init__(self, schema):
        self.schema = xmlschema.XMLSchema(schema)

    def validateXML(self, tree):
        return [
            ValidationError(e.reason, position={"xpath": e.path} if e.path else None)
            for e in self.schema.iter_errors(tree)
        ]
