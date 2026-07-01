from lib import XMLParser

not_wellformed = [
    ('<a>\n', {  # string
        "message": "Premature end of data in tag a line 1",
        "position": {"line": "2", "linecol": '2:1'}}),
    ('<a x="1"\n木="1" x="2"/>', {  # string
        "message": 'Attribute x redefined',
        "position": {"line": "2", "linecol": "2:12"}}),
    ('<?xml version="1.0"?>\n<木/>?'.encode("UTF-8"), {  # binary
        "message": 'Extra content at the end of the document',
        "position": {"line": "2", "linecol": "2:5"}}),
]

# TODO: check invalid DTD


def test_wellformed():
    assert XMLParser().validate("<x/>") == []


def test_not_wellformed():
    for (data, expect) in not_wellformed:
        errors = XMLParser().validate(data)
        assert len(errors) == 1 and errors[0].to_dict() == expect
