from flask import render_template
from flask.app import Flask
from typing import Any


def setupFrontController(app: Flask) -> None:

    @app.route('/')
    def sendIndex() -> Any:
        return render_template("index.html")
