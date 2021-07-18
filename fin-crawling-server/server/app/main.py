from fastapi import FastAPI
from app.module.locator import Locator
from app.setup_instance import locator
from app.router.socketEndpoint import router as socketRouter
from app.router.user import router as userRouter
from app.scheduler.TaskScheduler import TaskScheduler
from fastapi.middleware.cors import CORSMiddleware
import asyncio

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8083",
]

app = FastAPI()
app.include_router(socketRouter)
app.include_router(userRouter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/hello")
async def hello() -> dict:
    return {"message": "Hello World"}


loop = None


@app.on_event("startup")
async def startup() -> None:
    taskScheduler: TaskScheduler = Locator.getInstance().get(TaskScheduler)
    taskScheduler.start()
    # loop = asyncio.get_event_loop()
    # TasksRepository().createTaskRunner(loop)

    
