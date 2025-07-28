from fastapi import APIRouter, File, UploadFile, HTTPException
from server.services.ocr.vision_api import extract_text_from_image
from server.services.ocr.preprocess import preprocess_text
from server.services.ocr.extract_medicine_names import extract_medicine_names_from_text
from server.services.ocr.medicine_dosage_map import map_medicines_to_dosages


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
        ocr_result  = extract_text_from_image(content)

        raw_text = ocr_result["text"]
        words = ocr_result["words"]

        # 약명 리스트
        medicine_names = extract_medicine_names_from_text(raw_text)

        # 복약 정보 매핑
        mapped_result = map_medicines_to_dosages(raw_text, words, medicine_names)

        # 추출한 텍스트를 전처리 하여 깔끔한 형태로 정리
        # cleaned_text = preprocess_text(raw_text)

        # 표 기반 매핑 실행
        # result = match_table_format(raw_text)

        return {
            "raw_text": raw_text,
            "medicine_names": medicine_names,
            "mapped_result" : mapped_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

