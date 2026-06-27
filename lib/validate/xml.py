from .error import ValidationError
import xml.etree.ElementTree as ET
from xml.parsers.expat import ErrorString


def parseXML(data) -> ET.Element:
    try:
        return ET.fromstring(data)
    except ET.ParseError as e:
        line, col = e.position
        pos = {"line": f"{line}"}
        pos["linecol"] = f"{line}:{col + 1}"
        code = e.code
        raise ValidationError(ErrorString(code), pos)
