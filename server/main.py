from fastapi import FastAPI
from server import routers
import uvicorn


app = FastAPI()

# 테스트용 라우터
app.include_router(routers.test_router)

# 추후 챗봇 개발을 위한 기본적인 모델 추론 라우터
app.include_router(routers.inference_router)

# Vision API 사용을 위한 라우터
app.include_router(routers.ocr_router)


# 디버깅 모드로 직접 실행 가능하게 하기 위한 코드
if __name__ == "__main__":
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=False)