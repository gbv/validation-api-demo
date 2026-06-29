from json import loads, JSONDecodeError
from ..dvrf import ValidationError
from ..parser import AbstractParser


class JSONValidator(AbstractParser):

    def parse(self, data: str):
        try:
            return loads(data), []
        except JSONDecodeError as e:
            pos = {
                "line": str(e.lineno),
                "linecol": f"{e.lineno}:{e.colno}",
                "offset": str(e.pos)
            }
            return None, [ValidationError(e.msg, pos)]
