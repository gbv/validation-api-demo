from lib import XSDValidator, SchematronValidator
from pathlib import Path
import json

root = Path(__file__).parent
with (root / "validator-suite.json").open() as f:
    suite = json.load(f)


def run_case(validator, case):
    for test in case["tests"]:
        data = test["data"] if "data" in test else (root / test["file"]).read_text()
        errors = validator.validate(data)
        assert [e.to_dict() for e in errors] == test["errors"]


def test_xsd():
    for case in suite["xsd"]:
        validator = XSDValidator(root / case["schema"])
        run_case(validator, case)


def test_schematron():
    for case in suite["schematron"]:
        validator = SchematronValidator(root / case["schema"])
        run_case(validator, case)
