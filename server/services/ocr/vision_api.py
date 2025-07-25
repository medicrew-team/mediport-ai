import os
import io

from google.cloud import vision
from typing import List, Dict


# Vision API에서 제공하는 ImageAnnotatorClient 객체를 생성
client = vision.ImageAnnotatorClient()

# def extract_text_from_image(image_bytes: bytes) -> str:
#     image = vision.Image(content=image_bytes)
#     response = client.text_detection(image=image)
#     texts = response.text_annotations
#     if not texts:
#         return ""
#     return texts[0].description  # 전체 텍스트


def extract_text_from_image(image_bytes: bytes) -> List[Dict]:
    image = vision.Image(content=image_bytes)
    response = client.document_text_detection(image=image)

    results = []

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    text = ''.join([s.text for s in word.symbols])
                    box = word.bounding_box
                    results.append({
                        "text": text,
                        "x": int((box.vertices[0].x + box.vertices[2].x) / 2),  # 중간 X
                        "y": int((box.vertices[0].y + box.vertices[2].y) / 2),  # 중간 Y
                    })
    return results


def match_table_format(words: List[Dict]) -> List[Dict]:
    # 기준 열 헤더들 추출 (열 제목 기준 X 좌표 확보)
    column_keywords = ["투약량", "횟수", "일수"]
    columns = {}

    for word in words:
        if word["text"] in column_keywords:
            columns[word["text"]] = word["x"]

    result = []

    # 약명 후보: 한글+정제/정 형태로 끝나는 것만
    for word in words:
        if word["text"].endswith("정") or word["text"].endswith("캡슐"):
            y = word["y"]
            row = {"약명": word["text"]}

            for col_name, col_x in columns.items():
                candidates = [
                    w for w in words
                    if abs(w["x"] - col_x) < 20 and abs(w["y"] - y) < 15 and w["text"].isdigit()
                ]
                if candidates:
                    row[col_name] = candidates[0]["text"]

            result.append(row)

    return result