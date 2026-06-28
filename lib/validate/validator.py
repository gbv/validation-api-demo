import json
from pathlib import Path
from .json import parseJSON
from .xml import parseXML
from .jsonschema import JSONSchemaValidator
from .xmlschema import XSDValidator
from .schematron import SchematronValidator
from .error import ValidationError

schema = json.load((Path(__file__).parent / 'profiles-schema.json').open())


def parseable(data, fmt):
    try:
        if fmt == "json":
            parsed = parseJSON(data)
        if fmt == "xml":
            parsed = parseXML(data)
    except ValidationError as e:
        return [e]
    return []


def resolve(path, root):
    path = Path(path)
    if path.is_absolute() or not root:
        return path
    else:
        return root / path


class Validator(object):
    """Combines a set of application profiles to validate data against."""

    def __init__(self, profiles, **config):
        self.root = config.get("root")
        self.profiles = {}
        self.checks = {}

        # TODO: validate profiles against profiles schema

        for p in profiles:
            self.add(p)

    def add(self, profile):
        """Add a profile to the validator."""

        id = profile["id"]
        if id in self.profiles:
            raise ValueError(f"Profile already defined: {id}")

        checks = profile.get("checks", [])

        # TODO: support reference to profile as check
        self.checks[id] = [self.compile(c) for c in checks]

        about = ['id', 'title', 'description', 'url', 'report']
        self.profiles[id] = {key: profile[key] for key in about if profile.get(key, False)}

    def execute(self, profile, data=None, file=None) -> list[ValidationError]:
        """
        Validate data, given directly or as file reference, against a profile.

        Validation is performed sequentially against all checks of the profile.
        If any check fails, the validation stops and the errors are returned.

        Returns:
            list[ValidationError]: list of errors (empty list if no errors found)

        Raises:
            BaseException: if profile not found or validation process failed
        """

        if file:
            data = Path(file).read_bytes()
        for check in self.checks[profile]:
            errors = check(data)
            if errors is not None and len(errors):
                return errors

    def compile(self, check):
        if type(check) is str:
            if check == "json" or check == "xml":
                return lambda data: parseable(data, check)
            else:
                # TODO: allow to reference another profile
                raise Exception(f"Unknown check: {check}")

        if "schema" in check and "location" in check:
            # TODO: support URL in addition to local file
            schema = resolve(check["location"], self.root)

            match check["schema"]:
                case "json-schema":
                    validator = JSONSchemaValidator(file=schema)
                    # FIXME: catch parseJSON errors
                    return lambda data: validator.validateJSON(parseJSON(data))
                case "xsd":
                    validator = XSDValidator(schema)
                    # FIXME: catch parseXML errors
                    return lambda data: validator.validateXML(parseXML(data))
                case "schematron":
                    validator = SchematronValidator(schema)
                    # TODO: test XML syntax errors
                    return lambda data: validator.validateXML(data)
                # TODO: DTD validation with embedded DTD (with lxml)
                case _:
                    raise Exception(f"Unsupported schema language: {check['schema']}")

        raise Exception(f"Unkown check: {json.dumps(check)}")
