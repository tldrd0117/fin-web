from app.scheduler.TaskScheduler import TaskScheduler
from app.datasource.StockMongoDataSource import StockMongoDataSource
import asyncio
from app.util.DateUtils import getNow


async def taskWorker() -> None:
    now = getNow()
    print(f"taskWorker:{str(now)}")
    await asyncio.sleep(1)
    print("taskWorker after 1")


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    try:
        mongod = StockMongoDataSource(host="localhost", port="8082")
        scheduler = TaskScheduler(mongod.client)
        scheduler.start()
        jobs = scheduler.getJobs()
        for i in range(len(jobs)):
            fields = jobs[i].trigger.fields
            id = jobs[i].id
            print(f"reserved job #{id}: year.{str(fields[0])} month.{str(fields[1])} day.{str(fields[2])} hour.{fields[5]} minute.{fields[6]} second.{fields[7]}")
        now = getNow()

        job = scheduler.addJob(taskWorker, year="*", month="*", day="*", hour="*", minute="*", second=str(now.second+5), target="marcap")
        print(f"id: {str(job.id)}")
        print(f"now: second={str(now.second+5)}")
        jobs = scheduler.getJobs()
        for i in range(len(jobs)):
            fields = jobs[i].trigger.fields
            id = jobs[i].id
            print(f"reserved job #{id}: year.{str(fields[0])} month.{str(fields[1])} day.{str(fields[2])} hour.{fields[5]} minute.{fields[6]} second.{fields[7]}")
       
        print(f"{scheduler.jobs} - {scheduler.jobLengthMax}")
        # print(f"{jobs[0].year},{jobs[0].month},{jobs[0].day},{jobs[0].hour},{jobs[0].minute}")
        # print(str(jobs[0].trigger.fields[0]))  # year
        # print(str(jobs[0].trigger.fields[1]))  # month
        # print(str(jobs[0].trigger.fields[2]))  # day
        # print(str(jobs[0].trigger.fields[3]))  # week
        # print(str(jobs[0].trigger.fields[4]))  # dayofWeek
        # print(str(jobs[0].trigger.fields[5]))  # hour
        # print(str(jobs[0].trigger.fields[6]))  # minute
        # print(str(jobs[0].trigger.fields[7]))  # second
    except Exception as e:
        print(e)
        raise e


# pytest -s test_task_scheduler.py
def test() -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()