from typing import Dict
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from typing import List, Dict, Any
from sympy.polys.distributedmodules import sdm_to_dict


from server.services.retriever.lc_retriever import CurrentPipelineRetriever
from server.services.llm.adapters.lc_llm_adapter import LocalInferenceLLM
from server.services.llm.prompt.builder import build_prompt


# Retriever 인스턴스
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

NO_CONTEXT_MSG = (
    "질문과 관련된 일반의약품 정보가 현재 보유 중인 약품 데이터베이스에 존재하지 않습니다 😭"
    " 증상 키워드나 약 이름을 조금 더 구체적으로 알려주시면 다시 찾아볼게요!🥺"
)

def answer_with_langchain(question: str) -> Dict:
    """
    체인을 실행하고, 검색된 상위 문서의 메타데이터를 함께 반환.
    """
    docs = retriever.get_relevant_documents(question)
    if not docs:
        return {"text": NO_CONTEXT_MSG, "doc": {}}

    prompt = _make_prompt({"question": question, "doc": docs[0]})
    text = llm.invoke(prompt)
    return {"text": text, "doc": docs[0].metadata}



def run_pipeline_for_test(query: str, retriever, llm, return_docs: bool = False) -> Dict[str, Any]:
    """
    LangChain 기반 RAG 파이프라인 (테스트 엔트리포인트).
    """

    docs: List[Document] = retriever.get_relevant_documents(query)

    if not docs:
        return {
            "answer": NO_CONTEXT_MSG,
            "used_docs": 0
        }
    else:
        # 가장 관련도 높은 한 건만 조회
        context_doc = docs[0] if docs else Document(page_content="", metadata={})
        # Document -> dict
        record = context_doc.metadata if isinstance(context_doc, Document) else context_doc
        prompt = build_prompt(query, record)     # 프롬프트 빌더


    # 가짜 LLM 호출
    answer = llm.invoke(prompt)

    result = {"used_docs": len(docs)}
    # if return_docs:
    #     result["docs_preview"] = [d.page_content[:200] for d in docs]
    #     result["prompt_preview"] = prompt[:400]

    result["docs_meta"] = [d.metadata for d in docs]             # 전체 후보 메타
    result["top_doc_meta"] = (docs[0].metadata if docs else {})  # 최상위 1건 메타
    result["answer"] = answer                                    # 최종 답변

    return result