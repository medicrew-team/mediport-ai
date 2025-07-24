from fastapi import APIRouter, File, UploadFile, HTTPException
from server.services.ocr.vision_api import extract_text_from_image
from server.services.ocr.preprocess import preprocess_text

router = APIRouter()

# 사용자가 업로드한 이미지에서 텍스트를 추출하여 반환하는 API
@router.post("/ocr/image",
    summary="OCR Image",
    description="이미지를 업로드하면 OCR을 통해 텍스트를 추출합니다."
)
async def ocr_image(file: UploadFile = File(...)):
    try:
        content = await file.read()

        # 텍스트 추출 함수 실행
        raw_text = extract_text_from_image(content)

        # 추출한 텍스트를 전처리 하여 깔끔한 형태로 정리
        # cleaned_text = preprocess_text(raw_text)

        return {"extracted_text": raw_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))