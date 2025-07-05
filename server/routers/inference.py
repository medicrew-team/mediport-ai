from fastapi import APIRouter, HTTPException
from server.services.inference.inference_selector import run_inference
from server.services.vector_store.vector_search import search_similar_medicines
from server.services.prompt.builder import build_prompt
from pydantic import BaseModel

# 라우터 객체 생성
router = APIRouter()


class InferenceRequest(BaseModel):
    user_input: str


# 사용자 입력을 받아 LLM 모델 추론 결과를 반환하는 API
@router.post("/inference")
async def post_inference(request: InferenceRequest):

    try:
        user_input = request.user_input

        # 질문 기반으로 약 문서 유사도 검색
        docs = search_similar_medicines(user_input, top_k=1)

        if not docs:
            return {"result": "질문의 증상과 관련된 약 데이터 를 찾을 수 없습니다. 죄송합니다"}

        # prompt 설계
        prompt = build_prompt(user_input, docs[0])

        # 검색된 문서를 LLM에게 질문과 함께 전달
        # 실행 환경에 따른 추론 서버(local) or 추론 로직(cloud)으로 연결
        result = run_inference(prompt)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


