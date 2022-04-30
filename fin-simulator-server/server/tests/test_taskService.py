
from app.tasks.stockTasks import GetStockCodeFilteringByVarientRank, GetStockDayTask, GetMarcapCodes, GetStockCodeFilteringAltmanZScore
import luigi
import json
import pandas as pd
from app.service.TaskService import TaskService

# poetry run python -m pytest -s tests/test_taskService.py

def test_taskService() -> None:
    taskService = TaskService()
    taskService.simulate("20151123")
    



    
   
