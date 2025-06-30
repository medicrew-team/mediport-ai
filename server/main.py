from fastapi import FastAPI
from server.routers import test
from server.routers import inference

app = FastAPI()

# 테스트용 라우터
# app.include_router(test.router)

# 추후 챗봇 개발을 위한 기본적인 모델 추론 라우터 구성
app.include_router(inference.router)

