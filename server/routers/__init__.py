from .test import router as test_router
from .inference import router as inference_router
from .ocr import router as ocr_router


# 외부에 공개할 라우터 객체들 정의
__all__ = [
    "test_router",
    "inference_router",
    "ocr_router",
]