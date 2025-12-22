from flask import Flask, jsonify, render_template, request
from waitress import serve
from lib import ValidationService
from pathlib import Path
from werkzeug import exceptions
import json
import argparse

app = Flask(__name__)
app.json.compact = False

service = None


def init(config):
    global service
    service = ValidationService(**config)
    app.config['title'] = config.get('title', 'Validation Service')
    return config.get('port', 7007)


@app.errorhandler(Exception)
def handle_apierror(e):
    if type(e) is LookupError or type(e) is exceptions.NotFound:
        code = 404
    elif type(e) is ValueError:
        code = 400
    else:
        code = 500
    return jsonify({"code": code, "message": str(e)}), code


@app.route('/')
def get_index():
    if (app.debug or app.testing) and request.args.get("crash"):
        raise Exception("boom!")
    return render_template('index.html', **app.config)


@app.route('/profiles')
def get_profiles():
    return service.profiles()


@app.route('/<profile>/validate', methods=['GET', 'POST'])
def validate(profile):
    if not service.has(profile):
        raise LookupError(f"Profile not found: {profile}")

    if request.method == 'GET':
        params = ['data', 'url', 'file']
        args = dict([(k, request.args.get(k)) for k in params if k in request.args])
    else:
        mime = request.content_type or ''
        if mime.startswith('multipart/form-data'):
            if 'file' not in request.files:
                raise ValueError("Missing file upload")
            args = {"data": request.files['file'].stream}
        else:
            args = {"data": request.get_data()}

    return service.validate(profile, **args)


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--wsgi', action=argparse.BooleanOptionalAction, help="Use WSGI")
    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction)

    config_file = "config.default.json"
    for file in [Path("config.json"), Path("config") / "config.json"]:
        if file.exists():
            config_file = file

    parser.add_argument('config', help="Config file or directory", default=config_file, nargs='?')
    args = parser.parse_args()

    if Path(args.config).is_dir():
        args.config = Path(args.config) / "config.json"

    print(f"Loading configuration from {args.config}")
    port = init(json.load(Path(args.config).open()))

    app.debug = args.debug

    if args.wsgi:
        print(f"Starting WSGI server at http://localhost:{args.port}/")
        serve(app, host="0.0.0.0", port=port, threads=8)
    else:
        app.run(host="0.0.0.0", port=port, debug=args.debug)
