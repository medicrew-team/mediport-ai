from fastapi import APIRouter, HTTPException
from server.services.inference.inference_selector import run_inference

# 라우터 객체 생성
router = APIRouter()


# 사용자 입력을 받아 LLM 모델 추론 결과를 반환하는 API
@router.post("/inference")
async def post_inference(user_input: str):
    try:
        # run_inference 함수에 입력값 전달 하여 추론 결과 받기
        # inference_selector.INFERENCE_MODE에 따라 개발 환경 or 배포 환경으로 연결
        result = run_inference(user_input)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))