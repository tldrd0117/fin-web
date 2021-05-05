from flask import Flask
from .app_setup import app_setup
from fin_crawling.controllers.CrawlingController import setupCrawlingController
from fin_crawling.controllers.FrontController import setupFrontController

app = Flask(__name__, static_folder='dist', template_folder='dist')
app.config['SECRET_KEY'] = 'secret!'

app, socketio = app_setup(app)
setupCrawlingController(socketio)
setupFrontController(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
