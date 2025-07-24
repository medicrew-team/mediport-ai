from fastapi import APIRouter, HTTPException
from server.services.inference.inference_selector import run_inference
from server.services.vector_store.vector_search import search_similar_medicines
from server.services.prompt.builder import build_prompt
from pydantic import BaseModel
from googletrans import Translator

# 라우터 객체 생성
router = APIRouter()\

# 구글 번역기 초기화
translator = Translator()



class InferenceRequest(BaseModel):
    user_input: str
    lang: str = "ko"

# 사용자 입력을 받아 LLM 모델 추론 결과를 반환하는 API
@router.post(
    "/inference",
    summary="증상 기반 일반의약품 추천 챗봇",
    description="""
        사용자의 증상 설명을 기반으로 일반의약품을 추천해주는 챗봇입니다.  
        'lang' 필드를 통해 번역 언어를 설정할 수 있습니다.  
        지원 언어:
        - `en` (영어)
        - `vi` (베트남어)
        - `th` (태국어)
        - `fil` (필리핀어)
        - `zh-cn` (중국어 간체)
        - `ko` (한국어, 기본값)
    """
)
async def post_inference(request: InferenceRequest):

    try:
        user_input = request.user_input
        target_lang = request.lang.lower()

        # 질문 기반으로 약 문서 유사도 검색
        docs = search_similar_medicines(user_input, top_k=1)

        if not docs:
            return {"result": "관련된 약 데이터 를 찾을 수 없습니다. 죄송합니다"}

        # prompt 설계
        prompt = build_prompt(user_input, docs[0])

        # 검색된 문서를 LLM에게 질문과 함께 전달
        # 실행 환경에 따른 추론 서버(local) or 추론 로직(cloud)으로 연결
        result = run_inference(prompt)

        # 약명 Placeholder 다시 원본으로 복원
        # replaced_result = result.replace("[MEDICINE_NAME]", medicine_name)

        # 번역이 필요한 경우에 번역 수행
        if target_lang != "ko":
            result = translator.translate(result, dest=target_lang).text

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


