from fastapi import APIRouter, Request
from server.services.vector_store.vector_search import search_similar_medicines
from pydantic import BaseModel

router = APIRouter()

class InferenceRequest(BaseModel):
    user_input: str

# Vector 유사도 검색 테스트용 API
@router.post("/vector_search_test")
async def search_api(request: InferenceRequest):
    user_input = request.user_input
    results = search_similar_medicines(user_input, top_k=1)
    return {"results": results}