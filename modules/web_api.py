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


def run(host: str = '127.0.0.1', port: int = 5000):
    """Start the web API server.

    Parameters
    ----------
    host : str, optional
        Host interface to bind to. Defaults to ``"127.0.0.1"`` so the service
        is only accessible locally. Use ``"0.0.0.0"`` to expose on all
        interfaces if desired.
    port : int, optional
        Port to listen on, by default ``5000``.
    """
    if not Flask:
        raise ImportError(_IMPORT_ERROR)
    app.run(host=host, port=port)


def get_description() -> str:
    return "Simple Flask REST API exposing a /command endpoint."


if __name__ == "__main__":  # pragma: no cover - manual launch
    run()
