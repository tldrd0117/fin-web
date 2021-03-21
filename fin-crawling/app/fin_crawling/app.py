from flask import Flask, render_template
from fin_crawling.controllers.CrawlingController import CrawlingController
from fin_crawling.controllers.FrontController import FrontController
from flask_socketio import SocketIO

app = Flask(__name__,static_folder='dist',template_folder='dist')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

def run():
    setupController(app, socketio)
    app.run("0.0.0.0")
    socketio.run(app)
    print("run")

def setupController(app, socketio):
    crawlingController = CrawlingController(app, socketio)
    frontController = FrontController(app)

run()


