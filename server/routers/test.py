from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test():
    return {"msg" : "FastAPI 정상 작동"}