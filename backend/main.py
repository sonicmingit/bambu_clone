"""Application entrypoint for running the Flask app with a WSGI server."""

from __future__ import annotations

from .app import create_app

app = create_app()


@app.route("/health")
def healthcheck() -> dict[str, str]:
    """Simple healthcheck endpoint used by infrastructure checks."""

    return {"status": "ok"}
