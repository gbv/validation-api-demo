class ValidationReport:
    """A report as defined in [Data Validation Report Format](https://gbv.github.io/data-validation-report-format/#reports)."""

    def __init__(self):
        self.errors = []
        self.partial = False

    def add_errors(self, errors):
        self.errors.extend(errors)

    def to_dict(self):
        errors = [(e if isinstance(e, dict) else e.to_dict()) for e in self.errors]
        e = {"errors": errors}
        if self.partial:
            e["partial"] = self.partial
        return e
