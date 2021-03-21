from ..service.CrawlingService import CrawlingService
from pymitter import EventEmitter

class CrawlingController:
    def __init__(self, app, socketio):
        self.app = app
        self.crawlingService = CrawlingService()
        self.ee = EventEmitter()
        self.createRoutes(app, socketio)
        self.createEvents(app, socketio)

    def createRoutes(self, app, socketio):
        @socketio.on("message")
        def message(data):
            print(data)
        @socketio.on("runCrawling")
        def runCrawling(data):
            print(data)
            self.crawlingService.runCrawling("http://webdriver:4444", data["index"], data["startDate"], data["endDate"], self.ee)

    def createEvents(self, app, socketio):
        @self.ee.on("taskComplete")
        def taskComplete(data):
            socketio.emit("taskComplete", data.toDict())
        
        @self.ee.on("crawlingComplete")
        def crawlingComplete(data):
            socketio.emit("crawlingComplete", data.toDict())
        
    


