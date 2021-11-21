from app.repo.FactorRepository import FactorRepository
from app.repo.TasksRepository import TasksRepository
from app.module.socket.manager import ConnectionManager
from app.service.TaskService import TaskService
from app.model.dao import FactorDao
from app.model.dto import ProcessTask, RunFactorFileConvert

RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_START = "factor/convertFileToDbStart"
RES_SOCKET_FACTOR_UPDATE_STATE_RES = "factor/updateConvertStateRes"
RES_SOCKET_FACTOR_MOVE_FACTOR_FILE_TO_DB_END = "factor/convertFileToDbEnd"


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
    
