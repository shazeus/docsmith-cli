from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, abort, send_from_directory

from .renderer import build_site


def create_app(source: str | Path) -> Flask:
    temp_dir = Path(tempfile.mkdtemp(prefix="docsmith-site-"))
    site_dir, _ = build_site(source, temp_dir)
    app = Flask(__name__)

    @app.get("/")
    def index():
        return send_from_directory(site_dir, "index.html")

    @app.get("/<path:asset>")
    def asset(asset: str):
        requested = site_dir / asset
        if not requested.exists():
            abort(404)
        return send_from_directory(site_dir, asset)

    return app

