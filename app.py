from flask import Flask, jsonify, render_template, request
from waitress import serve
from lib import ValidationService
from pathlib import Path
import json
import argparse

app = Flask(__name__)
app.json.compact = False

service = None


def init(config):
    global service

    app.debug = config.get("debug", False)
    app.config['title'] = config.get('title', 'Validation Service')

    service = ValidationService(**config)


class ApiError(Exception):
    code = 400


class NotFound(ApiError):
    code = 404


@app.errorhandler(ApiError)
def handle_apierror(e):
    body = {
        "code": type(e).code,
        "message": str(e)
    }
    return jsonify(body), body['code']

# TODO: handle internal server errors


@app.route('/')
def get_index():
    return render_template('index.html', **app.config)


@app.route('/profiles')
def get_profiles():
    return service.profiles()


@app.route('/<profile>/validate', methods=['GET', 'POST'])
def get_validate(profile):
    try:
        service.profile(profile)
    except Exception:
        raise NotFound(f"Profile not found: {profile}")

    if request.method == 'GET':
        params = ['data', 'url', 'file']
        args = dict([(k, request.args.get(k)) for k in params if k in request.args])

        try:
            return service.validate(profile, **args)
        except ValueError as e:
            raise ApiError(str(e))
        except LookupError as e:
            raise NotFound(str(e))

    else:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            if 'file' not in request.files:
                raise ApiError("Missing file upload")
            data = request.files['file'].stream
        else:
            data = request.data
        return service.validate(profile, data=data)


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wsgi', action=argparse.BooleanOptionalAction, help="Use WSGI")
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction)

    config_file = "config.json" if Path('config.json').exists() else "config.default.json"
    parser.add_argument('config', help="Config file", default=config_file, nargs='?')
    args = parser.parse_args()

    print(f"Loading configuration from {args.config}")
    config = json.load(Path(args.config).open())

    config['debug'] = args.debug
    port = config.get('port', 7007)
    init(config)

    if args.wsgi:
        print(f"Starting WSGI server at http://localhost:{args.port}/")
        serve(app, host="0.0.0.0", port=port, threads=8)
    else:
        app.run(host="0.0.0.0", port=port, debug=args.debug)
