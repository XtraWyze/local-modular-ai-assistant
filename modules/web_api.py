"""Flask-based web API for sending commands to the assistant."""

try:
    from flask import Flask, request, jsonify
except Exception as e:  # pragma: no cover - optional dependency
    Flask = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None

MODULE_NAME = "web_api"
app = Flask(__name__) if Flask else None

__all__ = ["run", "command_route"]

@app.route('/command', methods=['POST'])
def command_route():
    if not Flask:
        return jsonify({'error': str(_IMPORT_ERROR)}), 500
    data = request.get_json(force=True)
    cmd = data.get('command', '')
    from assistant import process_input
    process_input(cmd, None)  # type: ignore[arg-type]
    return jsonify({'status': 'queued'})


def run(host: str = '0.0.0.0', port: int = 5000):
    if not Flask:
        raise ImportError(_IMPORT_ERROR)
    app.run(host=host, port=port)


def get_description() -> str:
    return "Simple Flask REST API exposing a /command endpoint."
