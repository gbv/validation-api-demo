from json import loads, JSONDecodeError
from .error import ValidationError


def parseJSON(data):
    try:
        return loads(data)
    except JSONDecodeError as e:
        pos = {
            "line": str(e.lineno),
            "linecol": f"{e.lineno}:{e.colno}",
            "offset": str(e.pos)
        }
        raise ValidationError(e.msg, pos)
