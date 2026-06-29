from lib import JSONSchemaValidator


def test_jsonschema():
    data = {  # Example from JSON Pointer RFC
        "foo": ["bar"],
        "": 0,
        "a/b": 1,
        "c%d": 2,
        "e^\nf": 3,
        " ": 7,
        "m~n": 8
    }

    def fail(prop, pos, check={"type": "string"}):
        schema = {"type": "object", "properties": {}}
        schema["properties"][prop] = check
        validator = JSONSchemaValidator(schema)

        errors = validator.validateJSON(data)
        assert len(errors) == 1 and errors[0].position == {"jsonpointer": pos}

    fail("foo", "/foo/0", {"type": "array", "items": {"type": "number"}})
    fail("", "/")
    fail("a/b", "/a~1b")
    fail("c%d", "/c%d")
    fail("e^\nf", "/e^\nf")
    fail(" ", "/ ")
    fail("m~n", "/m~0n")
