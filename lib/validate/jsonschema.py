from ..dvrf import Validator, ValidationError
import json
import jsonschema
from .json import JSONParser
from .document import DocumentValidator


class JSONSchemaValidator(JSONParser, DocumentValidator):

    def __init__(self, schema=None, file=None):
        self.schema = json.load(file.open()) if file else schema

    def validate_document(self, data):
        """Validate a parsed JSON value."""
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.ValidationError as err:
            pos = ""
            for elem in err.absolute_path:
                if isinstance(elem, int):
                    pos += "/" + str(elem)
                else:
                    pos += "/" + elem.replace("~", "~0").replace("/", "~1")
            pos = {"jsonpointer": pos}
            return [ValidationError(err.message, pos)]
        return []
