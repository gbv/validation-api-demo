from ..dvrf import ValidationError
import xml.etree.ElementTree as ET
from xml.parsers.expat import ErrorString
from ..parser import AbstractParser


class XMLValidator(AbstractParser):

    def parse(self, data: str):
        try:
            return ET.fromstring(data), []
        except ET.ParseError as e:
            line, col = e.position
            pos = {"line": f"{line}"}
            pos["linecol"] = f"{line}:{col + 1}"
            code = e.code
            return None, [ValidationError(ErrorString(code), pos)]
