from ..dvrf import ValidationError
from pyschematron import DirectModeSchematronValidatorFactory
from lxml import etree

nsmap = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}


def error(failed_assert):
    location = failed_assert.get('location')
    location = location.replace('Q{}', '')
    text_elem = failed_assert.find('svrl:text', nsmap)
    message = text_elem.text if text_elem is not None else "assertion failed"
    return ValidationError(message, position={"xpath": location})


class SchematronValidator:
    def __init__(self, schema):
        validator_factory = DirectModeSchematronValidatorFactory()
        validator_factory.set_schema(schema)
        self.validator = validator_factory.build()

    def validateXML(self, xml):
        """Validate a parsed XML document."""

        # see <https://github.com/robbert-harms/pyschematron/issues/21>
        root = etree.fromstring(xml)
        xml = etree._ElementTree()
        xml._setroot(root)
        result = self.validator.validate(xml)
        if result.is_valid():
            return []
        # TODO: use get_validation_events instead to include pattern id
        failed = result.get_svrl().findall('.//svrl:failed-assert', nsmap)
        return [error(e) for e in failed]
