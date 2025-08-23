import asyncio
import os
import re
import anyio


from fastapi import APIRouter, HTTPException
from server.services.inference.inference_selector import run_inference
from server.services.vector_store.vector_search import search_similar_medicines
from server.services.llm.prompt.builder import build_prompt
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from server.services.llm.chains.lc_chain import answer_with_langchain
from openai import OpenAI
from server.services.llm.chains.lc_chain_gpt import answer_with_langchain_gpt
from server.config import OPENAI_API_KEY



# 라우터 객체 생성
router = APIRouter()

# OpenAI 객체 생성
client = OpenAI(api_key=OPENAI_API_KEY)


class InferenceRequest(BaseModel):
    user_input: str
    lang: str = "ko"


NO_CONTEXT_MSG = (
    "질문과 관련된 일반 의약품 정보가 현재 보유 중인 약품 데이터베이스에 존재하지 않습니다 😭"
    " 증상 키워드나 약 이름을 조금 더 구체적으로 알려주시면 다시 찾아볼게요!🥺"
)


# --- 로컬 모델(llama) 기반 추론 엔드포인트 ---
@router.post(
    "/inference-v1",
    responses={
            200: {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "example": {
                            "result": "머리가 아프시군요! 😟 그런 증상에는 판콜에이내복액이 도움이 될 수 있어요...(생략)"
                        }
                    }
                },
            }
              },
    summary="증상 기반 일반의약품 추천 챗봇(llama-3) ",
    description="""
        사용자의 증상 설명을 기반으로 일반의약품을 추천해주는 챗봇입니다.  
        'lang' 필드를 통해 번역 언어를 설정할 수 있습니다.(※ 해당 API는 GPU Cloud 환경에서만 동작 가능하고 
        AWS 환경에선 동작 불가능 ※)\n  
        지원 언어:
        - `en` (영어)
        - `vi` (베트남어)
        - `th` (태국어)
        - `tl` (필리핀어)
        - `zh-CN` (중국어 간체)
        - `ko` (한국어, 기본값)
    """
)
async def post_inference(request: InferenceRequest):

    try:
        user_input = request.user_input
        target_lang = request.lang

        # 비한글 입력이면 한국어로 먼저 번역해서 벡터 검색에 사용
        if target_lang != "ko":
            user_input = await translate_async(user_input, source="auto", target="ko")

        # 질문 기반으로 약 문서 유사도 검색
        # docs = search_similar_medicines(user_input, top_k=1)

        # LangChain 기반 RAG 실행
        lc_out = await asyncio.to_thread(answer_with_langchain, user_input)

        if lc_out.get("doc") is not None:
            # 약명 추출
            medicine_name = lc_out["doc"].get("제품명", "")

            # 성분명(들)을 추출
            ingredient_name = lc_out["doc"].get("성분명", "")

        # prompt 설계
        # prompt = build_prompt(user_input, docs[0])

        # 검색된 문서를 LLM에게 질문과 함께 전달
        # 실행 환경에 따른 추론 서버(local) or 추론 로직(cloud)으로 연결
        # result = run_inference(prompt)

        if lc_out["text"] == NO_CONTEXT_MSG:
            # 불필요한 추가 텍스트 제거 (후처리)
            result = truncate_after_final_sentence(lc_out["text"])
        else:
            result = lc_out["text"]

        # 약명 Placeholder 다시 원본으로 복원
        # replaced_result = result.replace("[MEDICINE_NAME]", medicine_name)

        # 번역이 필요한 경우에 번역 수행
        if target_lang != "ko":
            # result = translator.translate(result, dest=target_lang).text
            result = await protect_keywords_translate(result, medicine_name, ingredient_name, target_lang)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# --- OpenAI 기반 추론 엔드포인트 ---
@router.post(
    "/inference-v2",
    summary="증상 기반 일반의약품 추천 챗봇 (openai)",
    responses={
            200: {
                "description": "Successful Response",
                "content": {
                    "application/json": {
                        "example": {
                            "result": "머리가 아프시군요! 😟 그런 증상에는 판콜에이내복액이 도움이 될 수 있어요...(생략)"
                        }
                    }
                },
            }
    },
    description="""
        기존 추론 버전과 기능은 동일하되, 로컬 모델 대신 OpenAI를 사용합니다.
        'lang' 필드로 번역 언어를 설정할 수 있습니다.\n
        지원 언어:
        - `en` (영어)
        - `vi` (베트남어)
        - `th` (태국어)
        - `tl` (필리핀어)
        - `zh-CN` (중국어 간체)
        - `ko` (한국어, 기본값)
    """
)
async def post_inference_v2(request: InferenceRequest):
    try:
        user_input = request.user_input
        target_lang = request.lang

        # 벡터 검색 기준 언어는 한국어이므로, 비한글 입력은 먼저 한국어로 번역
        if target_lang != "ko":
            user_input_for_search = await translate_async(user_input, source="auto", target="ko")
        else:
            user_input_for_search = user_input

        # LangChain(GPT) 기반 RAG 실행 (체인 내부에서 retriever + prompt + LLM 모두 처리)
        lc_out = await asyncio.to_thread(answer_with_langchain_gpt, user_input_for_search)

        text_obj = (lc_out or {}).get("text", "")
        text = getattr(text_obj, "content", text_obj) or ""
        doc_meta = (lc_out or {}).get("doc") or {}

        # 약명/성분명 추출 (번역 보호용)
        medicine_name = doc_meta.get("제품명", "") if isinstance(doc_meta, dict) else ""
        ingredient_name = doc_meta.get("성분명", "") if isinstance(doc_meta, dict) else ""

        # 결과 보정
        if not text.strip():
            text = NO_CONTEXT_MSG

        # NO_CONTEXT_MSG일 때는 후처리(truncate) 적용하지 않음
        if text != NO_CONTEXT_MSG:
            text = truncate_after_final_sentence(text)

        # 번역 처리
        if target_lang != "ko":
            if text == NO_CONTEXT_MSG:
                # 안내 문구는 키워드 보호 불필요
                text = await translate_async(text, source="auto", target=target_lang)
            else:
                # 약명/성분명 보호 번역
                text = await protect_keywords_translate(text, medicine_name, ingredient_name, target_lang)

        return {"result": text}

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
    translated = await translate_async(protected_result, source="auto", target=target_lang)

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



async def translate_async(text: str, *, source: str = "auto", target: str = "ko") -> str:
    """
        동기 방식의 GoogleTranslator.translate() 호출을 별도의 스레드에서 실행하여,
        FastAPI와 같은 비동기 환경에서도 이벤트 루프를 블로킹하지 않고 번역을 수행하는 함수.
    """
    return await anyio.to_thread.run_sync(
        lambda: GoogleTranslator(source=source, target=target).translate(text)
    )

