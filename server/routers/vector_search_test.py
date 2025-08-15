from fastapi import APIRouter, Request
from server.services.vector_store.vector_search import search_similar_medicines
from pydantic import BaseModel

from server.services.retriever.fake_retriever import FakeRetriever
from server.services.llm.adapters.fake_llm import FakeLLM
from server.services.llm.chains.lc_chain import run_pipeline


router = APIRouter()

class InferenceRequest(BaseModel):
    user_input: str
    top_k: int | None = 1
    return_docs: bool | None = True


# Vector 유사도 검색 테스트용 API
@router.post(
    "/pipeline_test_fake",
    summary="LLM 호출 없이 RAG 파이프라인 테스트",
    description=""
)
async def pipeline_test_fake(request: InferenceRequest):
    retriever = FakeRetriever(top_k=request.top_k or 1)
    fake_llm = FakeLLM(mode="echo")
    out = run_pipeline(request.user_input, retriever, fake_llm, return_docs=request.return_docs)

    return out