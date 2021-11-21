from app.repo.FactorRepository import FactorRepository
from app.repo.TasksRepository import TasksRepository, EVENT_TASK_REPO_TASK_COMPLETE, EVENT_TASK_REPO_UPDATE_TASKS
from app.module.socket.manager import ConnectionManager
from app.service.TaskService import TaskService
from app.model.dao import FactorDao
from app.model.dto import ListLimitData, ProcessTask, RunFactorFileConvert, StockCrawlingCompletedTasks

RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_START = "factor/convertFileToDbStart"
RES_SOCKET_FACTOR_UPDATE_STATE_RES = "factor/updateConvertStateRes"
RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_END = "factor/convertFileToDbEnd"

RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK = "factor/fetchCompletedTaskRes"
RES_SOCKET_FACTOR_FETCH_TASKS = "factor/fetchTasksRes"


class FactorService:
    def __init__(self, manager: ConnectionManager, factorRepository: FactorRepository, tasksRepository: TasksRepository, taskService: TaskService) -> None:
        self.manager = manager
        self.factorRepository = factorRepository
        self.tasksRepository = tasksRepository
        self.taskService = taskService
    
    # file에 있는 factor를 db에 저장한다.
    def convertFileToDb(self, dto: RunFactorFileConvert) -> None:
        task = ProcessTask(**{
            "market": "",
            "startDateStr": "",
            "endDateStr": "",
            "taskUniqueId": dto["taskUniqueId"],
            "taskId": dto["taskId"],
            "count": 1,
            "tasks": ["convert"],
            "restCount": 1,
            "tasksRet": [0],
            "state": "start get file"
        })
        self.tasksRepository.addTask(task)
        self.taskService.fetchTasks()
        data = self.factorRepository.getFactorsInFile()
        task.state = "start insert db"
        self.tasksRepository.updateTask(task)
        # update Db
        dao = FactorDao(**{
            "code": data["종목코드"],       # 종목코드
            "name": data["종목명"],       # 종목이름
            "dataYear": data["년"],      # 결산년
            "dataMonth": data["결산월"],  # 결산월
            "dataName": data["데이터명"],   # 데이터명
            "dataValue": (data["데이터값"] * 1000) if data["단위"] == "천원" else data["데이터값"]  # 데이터값
        })
        self.factorRepository.insertFactor(dao)
        task.state = "complete"
        self.tasksRepository.completeFactorConvertFileToDbTask(task)
    
    def createTaskRepositoryListener(self) -> None:
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_TASK_COMPLETE, self.completeTask)
        self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_UPDATE_TASKS, self.updateTasks)
    
    def updateTasks(self) -> None:
        self.manager.sendBroadCast(RES_SOCKET_FACTOR_FETCH_TASKS, self.tasksRepository.tasksdto.dict())
    
    def completeTask(self) -> None:
        dto = ListLimitData(**{
            "offset": 0,
            "limit": 20
        })
        tasks: StockCrawlingCompletedTasks = self.tasksRepository.getCompletedTask(dto)
        self.manager.sendBroadCast(RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK, tasks.dict())