# server/services/rag/lc_chain.py
# 목적: Retriever(현재 파이프라인) → 프롬프트 빌드 → LLM 을 LangChain Runnable로 연결
#       build_prompt()는 기존 버전을 그대로 재사용한다.

from typing import Dict
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from server.services.retriever.lc_retriever import CurrentPipelineRetriever
from server.services.llm.adapters.lc_llm_adapter import LocalInferenceLLM

# 기존 프롬프트 생성 함수 그대로 사용
from server.services.llm.prompt.builder import build_prompt


# Retriever 인스턴스: 지금 파이프라인은 top_k=1 이므로 동일하게 맞춘다
retriever = CurrentPipelineRetriever(top_k=1)

# LLM 인스턴스: run_inference() 를 부르는 어댑터
llm = LocalInferenceLLM()

def _select_top_doc(docs: list[Document]) -> Dict:
    # 검색 결과가 없으면 빈 dict 반환
    if not docs:
        return {"doc": None}
    # 최상단 문서를 그대로 사용
    return {"doc": docs[0]}

def _make_prompt(inputs: Dict) -> str:
    # inputs: {"question": str, "doc": Document | None}
    question = inputs["question"]
    doc = inputs.get("doc")
    if doc is None:
        # 검색 실패 시 LLM에게 넘길 최소한의 프롬프트(규칙에 맞춰 간단 처리)
        return f"질문: {question}\n\nAnswer:"
    # 기존 build_prompt(user_input, docs[0]) 형식을 그대로 따른다
    return build_prompt(question, doc.metadata)


# Runnable 체인 정의
rag_chain = (
    {"question": RunnablePassthrough()}                                                     # 입력 그대로 전달
    | { "question": RunnablePassthrough(), "docs": RunnableLambda(lambda x: retriever.get_relevant_documents(x["question"])) }
    | RunnableLambda(lambda x: {"question": x["question"], **_select_top_doc(x["docs"])})
    | RunnableLambda(_make_prompt)                                                          # 프롬프트 생성
    | llm                                                                                   # LLM 호출(run_inference)
    | StrOutputParser()                                                                     # 문자열로 변환
)


def answer_with_langchain(question: str) -> Dict:
    # 체인을 실행하고, 검색된 상위 문서의 메타데이터를 함께 반환한다.
    docs = retriever.get_relevant_documents(question)
    if not docs:
        return {"text": "", "doc": None}

    prompt = _make_prompt({"question": question, "doc": docs[0]})
    text = llm.invoke(prompt)
    return {"text": text, "doc": docs[0].metadata}
