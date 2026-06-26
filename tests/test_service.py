import pytest
import json
from tempfile import TemporaryDirectory
from lib import ValidationService
from pathlib import Path


def test_config():

    with pytest.raises(Exception):
        service = ValidationService()

    service = ValidationService(profiles=[])
    assert service.profiles() == []

    profiles = [{
        "id": "json",
        "checks": ["json"],
        "url": "https://json.org/"
    }, {
        "id": "xml",
        "checks": ["xml"]
    }]

    service = ValidationService(profiles=profiles)

    assert service.profiles() == [
        {"id": "json", "url": "https://json.org/"}, {"id": "xml"}]

    with pytest.raises(Exception, match=r"This service does not support passing data via URL"):
        service.validate('json', url="http://example.org/")

    with pytest.raises(Exception, match=r"This service does not support passing data at server"):
        service.validate('json', file="example.json")

    with pytest.raises(Exception, match=r"Data must be string, bytes or IOBase"):
        service.validate('json', data=42)

    assert service.validate('xml', data="\n") == [
        {'message': 'no element found', 'position': {'line': '2', 'linecol': '2:1'}}]

    assert service.validate('xml', data="<root/>") == []

    with TemporaryDirectory() as path:
        service = ValidationService(files=path, profiles=[])

        with pytest.raises(FileNotFoundError, match=r"Missing files directory:"):
            service = ValidationService(files=f"{path}/XXX", profiles=[])

        service = ValidationService(profiles=profiles, downloads=path)

        with pytest.raises(Exception, match=r"URL invalid or too long"):
            service.validate('json', url="example.org")

    path = Path(__file__).parent
    service = ValidationService(path / "example.json")

    assert service.validate('json', url="http://example.org/") == [
        {'message': 'Expecting value',
         'position': {'line': '1', 'linecol': '1:1', 'offset': '0'}}]

    assert service.validate('json', url="http://example.org/valid.json") == []

    # malformed configuration

    with pytest.raises(Exception, match="Unknown check: y"):
        ValidationService(profiles=[{"id": "x", "checks": ["y"]}])

    with pytest.raises(Exception, match='Unkown check: {"foo": 3}'):
        ValidationService(profiles=[{"id": "x", "checks": [{"foo": 3}]}])

    with pytest.raises(Exception, match='Profiles must have unique ids'):
        ValidationService(profiles=[{"id": "x"}, {"id": "x"}])

    with pytest.raises(Exception, match="Unsupported schema language: 42"):
        ValidationService(profiles=[{"id": "x", "checks": [{"schema": "42", "location": "."}]}])


def test_files():
    files = Path(__file__).parent / "files"
    service = ValidationService(profiles=[{"id": "xml", "checks": ["xml"]}], files=files)

    assert service.validate('xml', file="valid.xml") == []
    assert service.validate('xml', data=open(files / "valid.xml")) == []
    assert service.validate('xml', data=open(files / "broken.xml")) == [
        {'message': 'not well-formed (invalid token)', 'position': {'line': '1', 'linecol': '1:2'}}]


def test_schemas():
    path = Path(__file__).parent
    config = json.load((path / "example.json").open())
    service = ValidationService(config, root=path)
    assert service.profiles() == [{"id": "json"}, {"id": "ap"}, {"id": "my-xml"}, {"id": "sch"}]

    # validate JSON against a JSON Schema

    assert service.validate('ap', data=json.dumps(config["profiles"])) == []

    assert service.validate('ap', url="http://example.org/valid.json") == [
        {'message': "'id' is a required property", 'position': {'jsonpointer': '/0'}}]

    # validate XML against an XML Schema

    assert service.validate('my-xml', data='<a><b id="1"/><b id="2"/></a>') == []

    assert service.validate('my-xml', data="<a/>") == [{
        "message": "The content of element 'a' is not complete. Tag 'b' expected.",
        'position': {'xpath': '/a'}
    }]
    assert service.validate('my-xml', data='<a><b id="x"/></a>') == [
        {'message': "attribute id='x': invalid literal for int() with base 10: 'x'",
         'position': {'xpath': '/a/b'}},
        {'message': "The content of element 'a' is not complete. Tag 'b' expected.", 'position': {'xpath': '/a'}}
    ]

    # validate XML against an Schematron Schema

    assert service.validate('sch', data='<a id="1"></a>') == []
    assert service.validate('sch', data='<a><b/></a>') == [
        {'message': "There must be an id", 'position': {'xpath': '/a[1]/b[1]'}}
    ]
