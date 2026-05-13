import json
from pathlib import Path
from .json import parseJSON
from .jsonschema import validateJSON
from .xml import parseXML
from .xmlschema import validateXML


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
        # TODO: support URL in additio to local file
        schema = resolve(check["location"], root)

        match check["schema"]:
            # TODO: parse and compile XML Schema instead of re-reading each time
            case "json-schema":
                schema = json.load(schema.open())
                return lambda data: validateJSON(parseJSON(data), schema)
            case "xsd":
                return lambda data: validateXML(parseXML(data), schema)

            case _:
                raise Exception(f"Unsupported schema language: {check['schema']}")

    raise Exception(f"Unkown check: {json.dumps(check)}")


class Validator(object):
    def __init__(self, profiles, **config):
        validateJSON(profiles, schema)

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

    def profile(self, id) -> dict:
        return self.profiles[id]

    # may throw an error or return an array of errors
    def execute(self, profile, data=None, file=None):
        if file:
            data = Path(file).read_bytes()
        for check in self.checks[profile]:
            errors = check(data)
            if errors is not None and len(errors):
                return errors
