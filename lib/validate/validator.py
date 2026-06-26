import json
from pathlib import Path
from .json import parseJSON
from .xml import parseXML
from .jsonschema import JSONSchemaValidator
from .xmlschema import XSDValidator
from .schematron import SchematronValidator

schema = json.load((Path(__file__).parent / 'profiles-schema.json').open())


def parse(data, fmt):
    if fmt == "json":
        parseJSON(data)
    if fmt == "xml":
        parseXML(data)


def resolve(path, root):
    path = Path(path)
    if path.is_absolute() or not root:
        return path
    else:
        return root / path


def compile(check, root):
    if type(check) is str:
        if check == "json" or check == "xml":
            return lambda data: parse(data, check)
        else:
            # TODO: allow to reference another profile
            raise Exception(f"Unknown check: {check}")

    if "schema" in check and "location" in check:
        # TODO: support URL in addition to local file
        schema = resolve(check["location"], root)

        match check["schema"]:
            case "json-schema":
                validator = JSONSchemaValidator(file=schema)
                return lambda data: validator.validateJSON(parseJSON(data))
            case "xsd":
                validator = XSDValidator(schema)
                return lambda data: validator.validateXML(parseXML(data))
            case "schematron":
                validator = SchematronValidator(schema)
                return lambda data: validator.validateXML(data)
            # TODO: DTD validation with embedded DTD (with lxml)
            case _:
                raise Exception(f"Unsupported schema language: {check['schema']}")

    raise Exception(f"Unkown check: {json.dumps(check)}")


class Validator(object):
    def __init__(self, profiles, **config):
        # TODO: validate profiles against profiles schema

        root = config.get("root")

        checks = {p["id"]: p.get("checks", []) for p in profiles}
        if len(checks) != len(profiles):
            raise ValueError("Profiles must have unique ids")

        self.profiles = {}
        for p in profiles:
            id = p["id"]

            # TODO: support reference to profile as check
            checks[id] = [compile(c, root) for c in checks[id]]

            about = ['id', 'title', 'description', 'url', 'report']
            self.profiles[id] = {key: p[key] for key in about if p.get(key, False)}

        self.checks = checks

    # may throw an error or return an array of errors
    def execute(self, profile, data=None, file=None):
        if file:
            data = Path(file).read_bytes()
        for check in self.checks[profile]:
            errors = check(data)
            if errors is not None and len(errors):
                return errors
