class ValidationError(Exception):
    """An error as defined in Data Validation Report Format."""

    def __init__(self, message: str, position=None):
        super().__init__(message)
        self.position = position

#    def wrapInFile(self, file: str):
#        message = f"{str(self)} in {file}"
#        position = [{
#            "dimension": "file",
#            "address": file,
#            "errors": [self.to_dict()]
#        }]
#        return ValidationError(message, position)

    def to_dict(self) -> dict:
        e = {"message": str(self)}
        if self.position:
            e["position"] = self.position
        return e

# TODO: used in RDF parser errors
#
#    def fromException(error):
#        msg = str(error)
#        pos = None
#        if type(error) is SyntaxError and error.lineno:
#            pos = {"line": error.lineno}
#            if error.offset:
#                pos["linecol"] = f"{error.lineno}:{error.offset}"
#            # remove location from message
#            msg = re.sub(f"^[^:]+line {error.lineno}[^:]*: ", "", msg)
#            msg = re.sub(f"\\s*\\([^)]*line {error.lineno}[^)]*\\)$", "", msg)
#        return ValidationError(msg, pos)
