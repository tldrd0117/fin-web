from typing import Callable, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
from pymongo.mongo_client import MongoClient
from app.base.BaseComponent import BaseComponent
from app.datasource.StockMongoDataSource import StockMongoDataSource


class TaskScheduler(BaseComponent):
    
    def onComponentResisted(self) -> None:
        mongod = self.get(StockMongoDataSource)
        self.store = MongoDBJobStore(client=mongod.client)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_jobstore(self.store)
        self.jobs: list = []
        self.jobLengthMax = 0
        return super().onComponentResisted()
    
    def addJob(self, job: Callable, year: str, month: str, dayOfWeek: str, day: str, hour: str, minute: str, second: str, target: str, args: List = None) -> Job:
        trigger = CronTrigger(year=year, month=month, day_of_week=dayOfWeek, day=day, hour=hour, minute=minute, second=second)
        try:
            nextLength = self.jobLengthMax + 1
            job = self.scheduler.add_job(job, args=args, trigger=trigger, id=f"{target}-{nextLength}")
            self.jobLengthMax = nextLength
            return job
        except Exception as e:
            print(e)
    
    def removeJob(self, id: str) -> None:
        self.scheduler.remove_job(id)
    
    def setupJobs(self) -> None:
        jobs = self.scheduler.get_jobs()
        for i in range(len(jobs)):
            id: str = jobs[i].id
            idSplit = id.split("-")
            if not len(idSplit) > 1:
                continue
            if self.jobLengthMax < int(idSplit[1]):
                self.jobLengthMax = int(idSplit[1])
            self.jobs.append({"target": idSplit[0], "numId": idSplit[1]})
    
    def getJobs(self) -> list:
        return self.scheduler.get_jobs()

    def start(self) -> None:
        self.scheduler.start()
        self.setupJobs()

