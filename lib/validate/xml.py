from .error import ValidationError
from xml.dom.minidom import parse, parseString, Document
from xml.parsers.expat import ExpatError
from xml.parsers.expat.errors import messages
from io import IOBase


def parseXML(data) -> Document:
    try:
        if isinstance(data, IOBase):
            return parse(data)
        else:
            return parseString(data)
    except ExpatError as e:
        msg = messages[e.code]
        col = e.offset + 1
        pos = {
            "line": str(e.lineno),
            "linecol": f"{e.lineno}:{col}",
        }
        raise ValidationError(msg, pos)
