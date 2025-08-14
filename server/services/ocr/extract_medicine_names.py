import json
import os
from server.config import BASE_DIR

# 국내 약명 데이터셋 경로
MEDICINE_DATASET_PATH = os.path.join(BASE_DIR, "data/korean_product_name.json")

# 모국 약명 데이터셋 경로
FOREIGN_MEDICINE_DATASET_PATH = os.path.join(BASE_DIR, "data/foreign_product_name.json")


# 국내 약명 리스트 로드
def load_medicine_names() -> list:
    with open(MEDICINE_DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["제품명"].strip() for item in data if "제품명" in item]


# 모국 약명 리스트 로드
def load_foreign_medicine_names() -> list:
    with open(FOREIGN_MEDICINE_DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["제품명"].strip() for item in data if "제품명" in item]


# 텍스트에서 국내 약명 추출
def extract_medicine_names_from_text(text: str) -> list:

    medicine_names = load_medicine_names()
    extracted = []

    for name in medicine_names:
        if name in text:
            extracted.append(name)

    return extracted


# 텍스트에서 모국 약명 추출
def extract_foreign_medicine_names_from_text(text: str) -> list:

    foreign_names = load_foreign_medicine_names()

    text_norm = text.lower().replace(" ", "")

    extracted = []

    for name in foreign_names:
        name_norm = name.lower().replace(" ", "")
        if name_norm in text_norm:
            extracted.append(name)

    # 중복 제거 (순서 유지)
    unique_extracted = []
    for n in extracted:
        if n not in unique_extracted:
            unique_extracted.append(n)

    return unique_extracted