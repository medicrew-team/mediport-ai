from fastapi import FastAPI
from server.routers import test

app = FastAPI()

# 테스트용 라우터
app.include_router(test.router)
