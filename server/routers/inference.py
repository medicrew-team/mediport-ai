from fastapi import APIRouter, HTTPException
from server.services.inference.inference_selector import run_inference
from server.services.vector_store.vector_search import search_similar_medicines
from server.services.prompt.builder import build_prompt
from pydantic import BaseModel
from googletrans import Translator

import re


# 라우터 객체 생성
router = APIRouter()

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

        # 비한글 입력이면 한국어로 먼저 번역해서 벡터 검색에 사용
        if target_lang != "ko":
            user_input = translator.translate(user_input, dest="ko").text

        # 질문 기반으로 약 문서 유사도 검색
        docs = search_similar_medicines(user_input, top_k=1)

        if not docs:
            return {"result": "관련된 약 데이터 를 찾을 수 없습니다. 죄송합니다"}

        # 약명 추출
        medicine_name = docs[0].get("제품명", "")

        # 성분명(들)을 추출
        ingredient_name = docs[0].get("성분명", "")

        # prompt 설계
        prompt = build_prompt(user_input, docs[0])

        # 검색된 문서를 LLM에게 질문과 함께 전달
        # 실행 환경에 따른 추론 서버(local) or 추론 로직(cloud)으로 연결
        result = run_inference(prompt)

        # 불필요한 추가 텍스트 제거 (후처리)
        result = truncate_after_final_sentence(result)

        # 약명 Placeholder 다시 원본으로 복원
        # replaced_result = result.replace("[MEDICINE_NAME]", medicine_name)

        # 번역이 필요한 경우에 번역 수행
        if target_lang != "ko":
            # result = translator.translate(result, dest=target_lang).text
            result = await protect_keywords_translate(result, medicine_name, ingredient_name, target_lang)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# 챗봇 추론 결과에서 약명/성분명 제외하고 번역 처리 하는 함수
async def protect_keywords_translate(result: str, medicine_name: str, ingredient_name: str, target_lang: str) -> str:

    placeholder_medicine_name = "MED123456"
    placeholder_ingredient_name = "INGR"

    # 성분명 쉼표로 분리
    ingredient_list = [i.strip() for i in ingredient_name.split(",") if i.strip()]

    # 매핑: 성분명 → placeholder (예: "chlorpheniramine" → "INGR0", pseudoephedrine -> "INGR1")
    placeholder_map = {name: f"{placeholder_ingredient_name}{idx}" for idx, name in enumerate(ingredient_list)}



    # 번역 전 약명/성분명 치환
    # protected_result = (result
    #                   .replace(medicine_name, placeholder_medicine_name)
    #                   .replace(ingredient_name, placeholder_ingredient_name))


    # 번역 전 약명 placeholder로 치환
    protected_result = result.replace(medicine_name, placeholder_medicine_name)

    # 번역 전 성분명(들)을 placeholder로 치환
    for ingredient_name, ph in placeholder_map.items():
        # 대소문자 고려해서 replace
        protected_result = protected_result.replace(ingredient_name, ph)
        protected_result = protected_result.replace(ingredient_name.lower(), ph)
        protected_result = protected_result.replace(ingredient_name.capitalize(), ph)


    # 번역 수행
    translated = translator.translate(protected_result, dest=target_lang).text

    # 약명 복원 (대소문자 변형까지 고려)
    restored_result = (
        translated
        .replace(placeholder_medicine_name, medicine_name)
        .replace(placeholder_medicine_name.lower(), medicine_name)  # med123456
        .replace(placeholder_medicine_name.capitalize(), medicine_name)  # Med123456
    )

    # 성분명 복원 (대소문자 변형까지 고려)
    for ingredient_name, ph in placeholder_map.items():
        restored_result = (
            restored_result
            .replace(ph, ingredient_name)
            .replace(ph.lower(), ingredient_name)
            .replace(ph.capitalize(), ingredient_name)
        )

    return restored_result


# 모델이 생성한 응답에서 특정 문장 이후의 텍스트들을 잘라내는 역할을 하는 함수
def truncate_after_final_sentence(text: str) -> str:

    # Answer 패턴 처리 (대소문자 무시, 공백 제거)
    answer_match = re.search(r'answer\s*:\s*(.*)', text, re.IGNORECASE | re.S)
    if answer_match:
        text = answer_match.group(1).strip()

    end_marker = "정확한 정보를 얻기 위해서는 의사나 약사와 상의하는 것이 중요합니다."

    idx = text.find(end_marker)
    if idx != -1:
        return text[:idx + len(end_marker)].strip()
    return text.strip()  # 못 찾으면 원본 그대로