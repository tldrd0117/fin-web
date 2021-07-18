from pydantic import BaseModel


class TaskPoolInfo(BaseModel):
    poolSize: int = 0
    poolCount: int = 0
    runCount: int = 0
    queueCount: int = 0