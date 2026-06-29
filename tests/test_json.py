from lib import JSONValidator


def test_json():
    validator = JSONValidator()

    doc, err = validator.parse("{}")
    assert doc == {} and err == []

    assert validator.validate("{}") == []

    def fail(data, expect):
        errors = validator.validate(data)
        assert len(errors) == 1 and errors[0].to_dict() == expect

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
