from fastapi import FastAPI
from .router.socket import router

app = FastAPI()
app.include_router(router)


