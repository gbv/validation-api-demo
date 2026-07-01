from json import loads, JSONDecodeError
from ..dvrf import ValidationError, Parser


class JSONParser(Parser):

    def parse(self, data: str) -> (any, list[ValidationError]):
        try:
            return loads(data), []
        except JSONDecodeError as e:
            pos = {
                "line": str(e.lineno),
                "linecol": f"{e.lineno}:{e.colno}",
                "offset": str(e.pos)
            }
            return None, [ValidationError(e.msg, pos)]
