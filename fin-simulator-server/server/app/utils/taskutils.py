import hashlib
import json
import os
from typing import Any, Dict, List
import pandas as pd

def mkdir(path):
    normpath = os.path.normpath(path)
    parentfolder = os.path.dirname(normpath)
    if parentfolder:
        try:
            os.makedirs(parentfolder)
        except OSError:
            pass
    return path
    
def encMd5(data: Any) -> str:
    result = hashlib.md5(f'{str(data)}'.encode())
    return result.hexdigest()

def saveCodeList(li: List) -> str:
    result = hashlib.md5(f'{json.dumps(li)}'.encode())
    path = f"data/code/{result.hexdigest()}"
    mkdir(path)
    pd.Series(li).to_hdf(path, key='df', mode='w')
    return path

def getParsingDate(date: str) -> Dict:
    return {"year": (date[0:4]), "month": (date[4:6]), "day": (date[6:])}

def pathToList(targetPath: str) -> List:
    return pd.read_hdf(targetPath).to_list()

def dateToStr(date: pd.Timestamp) -> str:
    return date.date().strftime("%Y%m%d")

def strToDate(string: str) -> pd.Timedelta:
    return pd.to_datetime(string, format='%Y%m%d')

def pathToStr(path: str) -> str:
    return path.replace("/", "_")