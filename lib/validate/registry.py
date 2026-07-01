import json
from pathlib import Path
from .json import JSONParser
from .xml import XMLParser
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


class ValidationRegistry(object):
    """A a set of application profiles to validate data against."""

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
        self.checks[id] = [self.create_validator(c) for c in checks]

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

    def create_validator(self, check):
        validator = None

        if type(check) is str:
            if check == "json":
                validator = JSONParser()
            elif check == "xml":
                validator = XMLParser()
            else:
                # TODO: allow to reference another profile
                raise Exception(f"Unknown check: {check}")

        if "schema" in check and "location" in check:
            # TODO: support URL in addition to local file
            schema = resolve(check["location"], self.root)

            match check["schema"]:
                case "json-schema":
                    validator = JSONSchemaValidator(file=schema)
                case "xsd":
                    validator = XSDValidator(schema)
                case "schematron":
                    validator = SchematronValidator(schema)
                # TODO: DTD validation with embedded DTD (with lxml)
                case _:
                    raise Exception(f"Unsupported schema language: {check['schema']}")

        if validator is not None:
            return lambda data: validator.validate(data)

        raise Exception(f"Unkown check: {json.dumps(check)}")
