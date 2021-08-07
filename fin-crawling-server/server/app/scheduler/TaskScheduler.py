from typing import Callable, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job
from pymongo.mongo_client import MongoClient


class TaskScheduler(object):
    def __init__(self, client: MongoClient) -> None:
        super().__init__()
        self.store = MongoDBJobStore(client=client)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_jobstore(self.store)
        self.jobs: list = []
        self.jobLengthMax = 0
    
    def addJob(self, job: Callable, year: str, month: str, day: str, hour: str, minute: str, second: str, target: str, args: List = None) -> Job:
        trigger = CronTrigger(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
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

