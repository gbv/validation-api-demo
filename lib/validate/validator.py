import json
from pathlib import Path
from .json import JSONValidator
from .xml import XMLValidator
from .jsonschema import JSONSchemaValidator
from .xmlschema import XSDValidator
from .schematron import SchematronValidator
from ..dvrf import ValidationError

schema = json.load((Path(__file__).parent / 'profiles-schema.json').open())


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
            if check == "json":
                validator = JSONValidator()
            elif check == "xml":
                validator = XMLValidator()
            else:
                # TODO: allow to reference another profile
                raise Exception(f"Unknown check: {check}")
            return lambda data: validator.validate(data)

        if "schema" in check and "location" in check:
            # TODO: support URL in addition to local file
            schema = resolve(check["location"], self.root)

            match check["schema"]:
                case "json-schema":
                    validator = JSONSchemaValidator(file=schema)
                    return lambda data: validator.validateJSON(data)
                case "xsd":
                    validator = XSDValidator(schema)
                    return lambda data: validator.validateXML(data)
                case "schematron":
                    # FIXME: catch parseXML errors
                    validator = SchematronValidator(schema)
                    # TODO: test XML syntax errors
                    return lambda data: validator.validateXML(data)
                # TODO: DTD validation with embedded DTD (with lxml)
                case _:
                    raise Exception(f"Unsupported schema language: {check['schema']}")

        raise Exception(f"Unkown check: {json.dumps(check)}")
