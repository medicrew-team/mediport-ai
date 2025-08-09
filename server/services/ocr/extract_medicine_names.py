import json
import os
from server.config import BASE_DIR

MEDICINE_DATASET_PATH = os.path.join(BASE_DIR, "data/medicine_dataset_for_ocr.json")

def load_medicine_names() -> list:
    with open(MEDICINE_DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["제품명"].strip() for item in data if "제품명" in item]

def extract_medicine_names_from_text(text: str) -> list:
    medicine_names = load_medicine_names()
    extracted = []

    for name in medicine_names:
        if name in text:
            extracted.append(name)

    return extracted