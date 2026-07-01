from ..dvrf import Validator, ValidationError


class CrashingValidator(Validator):
    """A validator that does not execute properly but always crashes."""

    def validate(self, doc: str) -> list[ValidationError]:
        raise Exception("validator crashed")
