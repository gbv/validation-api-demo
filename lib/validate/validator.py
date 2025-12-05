import json
from pathlib import Path
from .json import parseJSON
from .jsonschema import validateJSON


schema = json.load((Path(__file__).parent / 'profiles-schema.json').open())


class Validator(object):
    def __init__(self, profiles, **config):
        validateJSON(profiles, schema)

        # TODO: check if id is unique
        self.profiles = dict([(p["id"], p) for p in profiles])
        # TODO: compile checks of profiles

        # self.reports = config.get('reports', None)

    def profile(self, id):
        "Returns public metadata of a profile or None."
        p = self.profiles[id]
        fields = ['id', 'title', 'description', 'url']
        return {key: p[key] for key in fields if key in p}

    def profiles_metadata(self):
        "List of profiles reduced to their their public metadata"
        return [self.profile(id) for id in self.profiles]

    def execute(self, profile, data=None, file=None):
        if file:
            data = Path(file).read_bytes()

        checks = self.profiles[profile]['checks']
        for check in checks:
            if check == "json":
                parseJSON(data)
