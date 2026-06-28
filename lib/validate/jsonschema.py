from ..dvrf import ValidationError
import json
import jsonschema


class JSONSchemaValidator:

    def __init__(self, schema=None, file=None):
        self.schema = json.load(file.open()) if file else schema

    def validateJSON(self, data):
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
