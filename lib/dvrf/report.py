def list_to_dict(objects):
    return [(e if isinstance(e, dict) else e.to_dict()) for e in objects]


class ValidationReport:
    """A report as defined in Data Validation Report Format."""

    def __init__(self):
        self.errors = []
        self.partial = False

    def add_errors(self, errors):
        self.errors.extend(errors)

    def to_dict(self):
        e = {"errors": list_to_dict(self.errors)}
        if self.partial:
            e["partial"] = list_to_dict(self.partial)
        return e
