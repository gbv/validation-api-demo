from lib import ValidationError, parseJSON


def test_json():
    def fail(data, error):
        try:
            parseJSON(data)
            assert 0 == "ValidationError should have been thrown!"  # pragma: no cover
        except ValidationError as e:
            assert e.to_dict() == error

    fail("{", {
        "message": "Expecting property name enclosed in double quotes",
        "position": {
            "line": "1",
            "linecol": "1:2",
            "offset": "1"
        }
    })

    fail("[0\n, ", {
        "message": "Expecting value",
        "position": {
            "line": "2",
            "linecol": "2:3",
            "offset": "5"
        }
    })
