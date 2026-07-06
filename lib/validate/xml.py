from ..dvrf import ValidationError, Parser
from .document import DocumentValidator
import re

from lxml import etree


class XMLParser(Parser):

    def parse(self, data: str) -> (any, list[ValidationError]):
        try:
            return etree.fromstring(data), []
        except etree.LxmlSyntaxError as e:
            col = e.offset + 1
            pos = {"line": f"{e.lineno}"}
            pos["linecol"] = f"{e.lineno}:{col}"
            msg = re.sub(', line [0-9]+, column [0-9]+$', '', e.msg)
            return None, [ValidationError(msg, pos)]


class XMLDocumentValidator(XMLParser, DocumentValidator):
    pass
