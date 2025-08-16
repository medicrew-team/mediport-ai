from typing import Dict, List, Any
import os

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from server.config import OPENAI_API_KEY

from server.services.retriever.lc_retriever import CurrentPipelineRetriever
from server.services.llm.prompt.builder_gpt import build_prompt

# --- 환경 변수 ---
# OPENAI_API_KEY: 필수
# OPENAI_CHAT_MODEL: 선택 (기본 gpt-4o-mini)

# Retriever & LLM 인스턴스
retriever = CurrentPipelineRetriever(top_k=1)


llm = ChatOpenAI(
    model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
    temperature=0.2,
    api_key=OPENAI_API_KEY,
)

def _select_top_doc(docs: List[Document]) -> Dict:
    if not docs:
        return {"doc": None}
    return {"doc": docs[0]}

def _make_prompt(inputs: Dict) -> str:
    # inputs: {"question": str, "doc": Document | None}
    question = inputs["question"]
    doc = inputs.get("doc")
    if doc is None:
        # 검색 실패 시에도 최소 규칙에 맞춘 프롬프트
        return f"질문: {question}\n\nAnswer:"
    # build_prompt(question, doc.metadata) 는 문자열 프롬프트를 반환한다고 가정
    return build_prompt(question, doc.metadata)

# Runnable 체인 (기존과 동일한 형태)
rag_chain = (
    {"question": RunnablePassthrough()}  # 입력 그대로 전달
    | {
        "question": RunnablePassthrough(),
        "docs": RunnableLambda(lambda x: retriever.get_relevant_documents(x["question"])),
      }
    | RunnableLambda(lambda x: {"question": x["question"], **_select_top_doc(x["docs"])})
    | RunnableLambda(_make_prompt)          # 프롬프트 생성 (str)
    | llm                                   # LLM 호출 (ChatOpenAI는 str 입력을 user 메시지로 처리)
    | StrOutputParser()                     # 문자열로 변환
)

NO_CONTEXT_MSG = (
    "질문과 관련된 일반 의약품 정보가 현재 보유 중인 약품 데이터베이스에 존재하지 않습니다 😭"
    " 증상 키워드나 약 이름을 조금 더 구체적으로 알려주시면 다시 찾아볼게요!🥺"
)

def answer_with_langchain_gpt(question: str) -> Dict:
    """
    GPT API를 사용하는 LangChain RAG. 기존 answer_with_langchain과 동일한 반환 형태:
    {"text": str, "doc": dict}
    """
    docs = retriever.get_relevant_documents(question)
    if not docs:
        return {"text": NO_CONTEXT_MSG, "doc": {}}

    prompt = _make_prompt({"question": question, "doc": docs[0]})
    text = llm.invoke(prompt)  # ChatOpenAI는 .invoke(str) 가능
    return {"text": text, "doc": docs[0].metadata}


def run_pipeline_for_test_gpt(query: str, return_docs: bool = False) -> Dict[str, Any]:
    """
    테스트용 엔트리포인트 (기존 run_pipeline_for_test와 역할 동일).
    """
    docs: List[Document] = retriever.get_relevant_documents(query)

    if not docs:
        return {"answer": NO_CONTEXT_MSG, "used_docs": 0}

    context_doc = docs[0]
    record = context_doc.metadata
    prompt = build_prompt(query, record)

    answer = llm.invoke(prompt)

    result: Dict[str, Any] = {
        "used_docs": len(docs),
        "docs_meta": [d.metadata for d in docs],
        "top_doc_meta": record,
        "answer": answer,
    }
    # 필요하면 preview 키 복구
    # if return_docs:
    #     result["docs_preview"] = [d.page_content[:200] for d in docs]
    #     result["prompt_preview"] = prompt[:400]

    return result

