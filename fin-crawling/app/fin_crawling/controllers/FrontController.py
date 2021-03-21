from flask import Flask, render_template

class FrontController:
    def __init__(self, app):
        self.app = app
        self.createRoutes(app)

    def createRoutes(self, app):
        @app.route('/')
        def sendIndex():
            return render_template("index.html")

        @app.route('/<path:path>')
        def sendStatic(path):
            return app.send_static_file(path)
        