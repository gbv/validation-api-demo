import json
from pathlib import Path
from .json import parseJSON
from .jsonschema import validateJSON
from .xml import parseXML


schema = json.load((Path(__file__).parent / 'profiles-schema.json').open())


class Check(object):
    def __init__(self, config):
        if type(config) == str:
            match config:
                case "json":
                    self.method = parseJSON
                case "xml":
                    self.method = parseXML
                case _:
                    # TODO: allow to reference another profile
                    raise Exception(f"Unknown check: {config}")
        elif "schema" in config and "language" in config:
            match config["language"]:
                case "xsd":
                    pass  # TODO: load as local file or from URL with cache
                case "jsonschema":
                    pass  # TODO
                case _:
                    raise Exception(f"Unsupported schema language: {config['language']}")

        else:
            raise Exception(f"Unkown check: {json.dumps(config)}")

    def execute(self, data):
        self.method(data)


class Validator(object):
    def __init__(self, profiles, **config):
        validateJSON(profiles, schema)

        checks = {p["id"]: p.get("checks", []) for p in profiles}
        if len(checks) != len(profiles):
            raise ValueError("Profiles must have unique ids")

        self.profiles = {}
        for p in profiles:
            id = p["id"]

            # TODO: support reference to profile as check
            checks[id] = [Check(c) for c in checks[id]]

            about = ['id', 'title', 'description', 'url']
            self.profiles[id] = {key: p[key] for key in about if p.get(key, False)}

        self.checks = checks

    def profile(self, id) -> dict:
        return self.profiles[id]

    def execute(self, profile, data=None, file=None):
        if file:
            data = Path(file).read_bytes()
        for check in self.checks[profile]:
            check.execute(data)
