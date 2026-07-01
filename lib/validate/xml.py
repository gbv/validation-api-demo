from ..dvrf import ValidationError, Parser
from .document import DocumentValidator
import re

from lxml import etree


class XMLParser(Parser):

    def parse(self, data: str) -> (any, list[ValidationError]):
        try:
            root = etree.fromstring(data)

            # See <https://github.com/robbert-harms/pyschematron/issues/21> for reason
            doc = etree._ElementTree()
            doc._setroot(root)

            return doc, []
        except etree.LxmlSyntaxError as e:
            col = e.offset + 1
            pos = {"line": f"{e.lineno}"}
            pos["linecol"] = f"{e.lineno}:{col}"
            msg = re.sub(', line [0-9]+, column [0-9]+$', '', e.msg)
            return None, [ValidationError(msg, pos)]


class XMLDocumentValidator(XMLParser, DocumentValidator):
    pass
