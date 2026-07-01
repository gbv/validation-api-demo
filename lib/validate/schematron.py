from ..dvrf import ValidationError
from .xml import XMLDocumentValidator
from pyschematron import DirectModeSchematronValidatorFactory

nsmap = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}


def error(failed_assert):
    location = failed_assert.get('location')
    location = location.replace('Q{}', '')
    text_elem = failed_assert.find('svrl:text', nsmap)
    message = text_elem.text if text_elem is not None else "assertion failed"
    return ValidationError(message, position={"xpath": location})


class SchematronValidator(XMLDocumentValidator):

    def __init__(self, schema):
        validator_factory = DirectModeSchematronValidatorFactory()
        validator_factory.set_schema(schema)
        self.validator = validator_factory.build()

    def validate_document(self, doc):
        """Validate a parsed XML document."""

        result = self.validator.validate(doc)
        if result.is_valid():
            return []
        # TODO: use get_validation_events instead to include pattern id
        failed = result.get_svrl().findall('.//svrl:failed-assert', nsmap)
        return [error(e) for e in failed]
