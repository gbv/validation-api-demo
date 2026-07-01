from ..dvrf import ValidationError
from ..parser import AbstractParser
import re

from lxml import etree


class XMLValidator(AbstractParser):

    def parse(self, data: str):
        try:
            xml = etree.fromstring(data)
            return xml, []
        except etree.LxmlSyntaxError as e:
            col = e.offset + 1
            pos = {"line": f"{e.lineno}"}
            pos["linecol"] = f"{e.lineno}:{col}"
            msg = re.sub(', line [0-9]+, column [0-9]+$', '', e.msg)
            return None, [ValidationError(msg, pos)]
